"""The underlay as an alignment, and the search for better legal ones.

For one voice and verse, the notes between two rests (or section breaks) form
a span, and the syllables that start in it are aligned to its notes: syllable
i starts on note a(i), strictly increasing, and the first syllable starts on
the span's first note (10.2). Words that cross a rest stay as they are (the
search never moves a syllable across a rest).

A candidate is legal if no hard rule (10.1-10.5) fires. Its cost is the sum of
its soft violations, each the rule's weight times the hit's amount times the
gates that apply (gates.yaml). The search is a dynamic programme over
(syllable, start note) with k-best lists (Viterbi with k paths): syllables
outside a window around the finding stay where they are. Rules that compare
voices (imitation, homorhythm) are added afterwards and the k best re-ranked.

Severity is regret: cost(current) - cost(best legal candidate in the window),
like a chess engine's loss against its best move. Nothing is ever rewritten:
the alternatives are suggestions (principles 10.6).
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from . import gates as G
from .engine import active_rules, seg_end, syllable_hits
from .rules import load, settings
from .rules.base import Hit, LineCtx
from .text import Line


@dataclass
class Span:
    n: int
    first: int
    end: int                    # exclusive
    syls: list                  # syllable indices (in the line) that start here


@dataclass
class Priced:
    hit: Hit
    cost: float
    gates: list

    @property
    def rule(self):
        return self.hit.rule


@dataclass
class Candidate:
    starts: tuple               # start event of each span syllable, in order
    local: float = 0.0
    piece: float = 0.0
    hard: bool = False
    hard_syls: set = field(default_factory=set)   # syllables with a firm-rule break
    priced: list = field(default_factory=list)

    @property
    def total(self) -> float:
        return self.local + self.piece


def spans_of(line: Line) -> list[Span]:
    evs = line.events
    out, cur = [], None
    for e in evs:
        if e.rest:
            cur = None
            continue
        if cur is None or e.after_break:
            cur = Span(n=len(out), first=e.idx, end=e.idx + 1, syls=[])
            out.append(cur)
        else:
            cur.end = e.idx + 1
    by_ev = {}
    for sp in out:
        for j in range(sp.first, sp.end):
            by_ev[j] = sp
    for s in line.syls:
        sp = by_ev.get(s.ev)
        if sp is not None:
            sp.syls.append(s.i)
    return out


class Model:
    def __init__(self, analysis, line: Line):
        self.a = analysis
        self.line = line
        self.rules = load()
        self.syl_rules = active_rules(line.lang, False, "syllable")
        self.piece_rules = active_rules(line.lang, False, "piece")
        self.cfg = settings()
        self.cur = line.starts
        self.spans = spans_of(line)
        self.span_of_ev = {j: sp for sp in self.spans for j in range(sp.first, sp.end)}
        self._seg: dict = {}
        self._search: dict = {}

    # ---------------------------------------------------------------- pricing
    def price(self, h: Hit) -> Priced:
        r = self.rules[h.rule]
        gs = G.applied(r, self.a, self.line, h)
        c = r.weight * h.amount
        for _, f in gs:
            c *= f
        return Priced(hit=h, cost=c, gates=gs)

    def seg(self, i: int, p: int, q: int | None, end: int):
        key = (i, p, q, end)
        if key not in self._seg:
            hits = syllable_hits(self.line, i, p, q, self.syl_rules, analysis=self.a, end=end)
            priced = [self.price(h) for h in hits]
            hard = any(h.hard for h in hits)
            self._seg[key] = (sum(x.cost for x in priced), hard, priced)
        return self._seg[key]

    def piece(self, starts: list[int]) -> list[Priced]:
        out = []
        for r in self.piece_rules:
            for h in r.fn()(self.a, self.line, starts):
                out.append(self.price(h))
        return out

    # ---------------------------------------------------------------- spans
    def _next_outside(self, sp: Span) -> int | None:
        last = sp.syls[-1]
        return self.cur[last + 1] if last + 1 < len(self.cur) else None

    def evaluate_span(self, sp: Span, starts: tuple) -> Candidate:
        c = Candidate(starts=starts)
        for j, i in enumerate(sp.syls):
            p = starts[j]
            if j + 1 < len(sp.syls):
                q, end = starts[j + 1], starts[j + 1]
            else:
                q, end = self._next_outside(sp), sp.end
            cost, hard, priced = self.seg(i, p, q, end)
            c.local += cost
            c.hard_syls.update(x.hit.syl for x in priced if x.hit.hard)
            c.priced.extend(priced)
        if starts and starts[0] != sp.first:
            c.hard_syls.add(sp.syls[0])
        c.hard = bool(c.hard_syls)
        full = list(self.cur)
        for j, i in enumerate(sp.syls):
            full[i] = starts[j]
        pp = [x for x in self.piece(full) if x.hit.syl in sp.syls]
        c.piece = sum(x.cost for x in pp)
        c.priced.extend(pp)
        return c

    def current(self, sp: Span) -> Candidate:
        return self.evaluate_span(sp, tuple(self.cur[i] for i in sp.syls))

    def search(self, sp: Span, window: tuple, *, anchors: bool = True) -> list[Candidate]:
        """k-best legal candidates for the span, moving only the syllables in
        `window` (indices into sp.syls). Sorted by total cost.

        With anchors, a syllable that ends a phrase (punctuation) stays where
        the editor put it: 10.6 maps the cadences and places each line's last
        syllable first. Only a 10.3 finding (U301) frees the anchors."""
        key = (sp.n, window, anchors)
        if key in self._search:
            return self._search[key]
        K = int(self.cfg.get("kbest", 12))
        n = len(sp.syls)
        affected = self.affected(sp, window)
        cur = [self.cur[i] for i in sp.syls]
        fixed = {0: sp.first}
        fixed.update({x: cur[x] for x in range(1, n) if x not in window})
        if anchors:
            fixed.update({x: cur[x] for x in range(1, n) if self.line.syls[sp.syls[x]].punct})
        allowed = []
        for j in range(n):
            if j in fixed:
                allowed.append([fixed[j]])
                continue
            lo = max(fixed[x] for x in fixed if x < j) + 1
            hi = min([fixed[x] for x in fixed if x > j] + [sp.end])
            allowed.append(list(range(lo, hi)))
        # k-best Viterbi: states[p] = list of (cost, path)
        states = {p: [(0.0, (p,))] for p in allowed[0]}
        for j in range(n - 1):
            i = sp.syls[j]
            nxt: dict = {}
            for q in allowed[j + 1]:
                cands = []
                for p, lst in states.items():
                    if q <= p:
                        continue
                    cost, hard, _ = self.seg(i, p, q, q)
                    if hard and i in affected:
                        continue
                    for c0, path in lst:
                        cands.append((c0 + cost, path + (q,)))
                if cands:
                    nxt[q] = heapq.nsmallest(K, cands)
            states = nxt
            if not states:
                break
        finals = []
        if states and n:
            i = sp.syls[-1]
            q_out = self._next_outside(sp)
            for p, lst in states.items():
                cost, hard, _ = self.seg(i, p, q_out, sp.end)
                if hard and i in affected:
                    continue
                for c0, path in lst:
                    finals.append((c0 + cost, path))
        finals = heapq.nsmallest(K, finals)
        out = [self.evaluate_span(sp, path) for _, path in finals]
        # legal where it matters: breaks elsewhere in the span stay as they are
        out = [c for c in out if not (c.hard_syls & affected)]
        out.sort(key=lambda c: (round(c.total, 6), c.starts))
        self._search[key] = out
        return out

    def affected(self, sp: Span, window: tuple) -> set:
        """Syllables whose notes a move in the window can change: the window
        and the syllable before it."""
        out = {sp.syls[j] for j in window}
        if window and window[0] > 0:
            out.add(sp.syls[window[0] - 1])
        return out

    def window_for(self, sp: Span, syl: int) -> tuple:
        W = int(self.cfg.get("window", 2))
        if syl in sp.syls:
            j = sp.syls.index(syl)
        else:
            j = 0
        return tuple(range(max(0, j - W), min(len(sp.syls), j + W + 1)))
