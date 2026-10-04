"""Findings for one edition: every rule hit on the underlay as it stands,
with its cost, the gates that applied, its regret against the best legal
alternative nearby, and up to three alternatives."""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .analysis import Analysis, analyse
from .ingest import parse
from .rules import load, settings
from .rules.base import LineCtx
from .engine import active_rules
from .text import build_lines
from .underlay import Model

LEVEL_ORDER = {"break": 0, "warn": 1, "look": 2, "info": 3}


@dataclass
class Alternative:
    moves: list
    cost: float                 # change in cost; for a break, the alternative's own cost
    fixes: list
    introduces: list
    basis: str = "change"       # change | total (the current underlay is not legal)
    edit: str = ""              # "" (syllables move), drop or repeat (10.13): the text changes
    placement: list = field(default_factory=list)   # [event, syllable] for the span under this alternative


@dataclass
class Finding:
    slug: str
    rule: str
    name: str
    level: str
    voice: str
    verse: str
    bar: int
    where: str
    word: str
    k: int                      # syllable within the word, 0-based
    text: str                   # the syllable as printed
    message: str
    principle: str
    cost: float
    regret: float | None
    gates: list = field(default_factory=list)
    breakdown: list = field(default_factory=list)
    alternatives: list = field(default_factory=list)
    src: str = ""
    fingerprint: str = ""
    baseline: str | None = None     # the reason, if the baseline accepts it
    ev: int = -1                    # event the finding points at
    notes: list = field(default_factory=list)       # events of the syllable's notes
    span: list = field(default_factory=list)        # [first, end) events of its span (rest to rest)
    placement: list = field(default_factory=list)   # [event, syllable] for the span as it stands

    def to_json(self) -> dict:
        d = asdict(self)
        d["cost"] = round(self.cost, 3)
        d["regret"] = None if self.regret is None else round(self.regret, 3)
        return d


@dataclass
class Result:
    slug: str
    path: str
    analysis: Analysis
    findings: list


def _level(native: str, hard: bool, regret: float | None) -> str:
    if hard:
        return "break"
    if native == "info":
        return "info"
    lv = settings()["levels"]
    if regret is None:
        return "look"
    if regret >= lv["warn"]:
        return "warn"
    if regret >= lv["look"]:
        return "look"
    return "info"


def _fmt_cost(p) -> str:
    g = "".join(f" {n}×{f:g}" for n, f in p.gates)
    return f"{p.rule} {p.cost:.2f}{g}"


def _own(c, rule: str, syl) -> float:
    """What `rule` costs on syllable `syl` in candidate c (0 if syl is None: dropped)."""
    if syl is None:
        return 0.0
    return sum(x.cost for x in c.priced if x.rule == rule and x.hit.syl == syl)


def _keyed(c, to_orig=None, last_of=None) -> dict:
    """(rule, original syllable) -> cost in candidate c. For an edited line,
    syllables map back to the original; a repeated copy counts with the
    word's last syllable."""
    out: dict = {}
    for x in c.priced:
        if x.cost <= 0:
            continue
        syl = x.hit.syl
        if to_orig is not None:
            syl = to_orig.get(syl)
            if syl is None:
                syl = last_of
        out[(x.rule, syl)] = out.get((x.rule, syl), 0.0) + x.cost
    return out


def _by_rule(keyed: dict) -> dict:
    out: dict = {}
    for (rule, _), v in keyed.items():
        out[rule] = out.get(rule, 0.0) + v
    return out


def _diff(cur: dict, alt: dict):
    fixes, intro = [], []
    for r in sorted(set(cur) | set(alt)):
        a, b = cur.get(r, 0.0), alt.get(r, 0.0)
        if b < a - 1e-9:
            fixes.append(f"{r} {a:.2f}->{b:.2f}")
        elif b > a + 1e-9:
            intro.append(f"{r} {a:.2f}->{b:.2f}")
    return fixes, intro


def attributable(cur_keyed: dict, alt_keyed: dict, delta: float, key, share: float) -> float:
    """The part of an alternative's improvement that belongs to one finding.

    The improvement (delta, the change in total cost) is split among the
    rule-and-syllable costs that the alternative reduces, in proportion to
    each reduction; a finding gets its key's part, times its own share of
    that key (`share`: its cost over the key's cost, when one rule fires twice
    on a syllable). Summed over the findings an alternative solves, the
    regrets add up to its improvement, never more."""
    if delta <= 0:
        return 0.0
    red = {k: cur_keyed[k] - alt_keyed.get(k, 0.0) for k in cur_keyed}
    red = {k: v for k, v in red.items() if v > 1e-9}
    total = sum(red.values())
    if total <= 0 or key not in red:
        return 0.0
    return delta * red[key] / total * share


@dataclass
class _Option:
    total: float                # the candidate's total, plus the edit's cost
    cand: object
    edit: object = None         # edits.Edit, or None for a move-only candidate
    own: float = 0.0            # the finding's rule on the finding's syllable
    keyed: dict = field(default_factory=dict)


def _w(e) -> str:
    """Bar and minim, with a + for a note off the minim (12.3+ is the second
    semiminim of the third minim)."""
    return e.where + ("+" if e.pos % 2 else "")


def _moves(line, sp, cur, alt) -> list[str]:
    out = []
    for j, (a, b) in enumerate(zip(cur.starts, alt.starts)):
        if a != b:
            s = line.syls[sp.syls[j]]
            out.append(f"'{s.text}' {_w(line.events[a])} -> {_w(line.events[b])}")
    return out


def _edit_moves(line, ed, sp2, c) -> list[str]:
    out = [ed.label]
    copies = []
    for j, b in enumerate(c.starts):
        i2 = sp2.syls[j]
        o = ed.to_orig.get(i2)
        s = ed.line.syls[i2]
        if o is None:
            copies.append(f"'{s.text}' {_w(line.events[b])}")
        elif line.syls[o].ev != b:
            out.append(f"'{s.text}' {_w(line.events[line.syls[o].ev])} -> {_w(line.events[b])}")
    if copies:
        out.insert(1, "sung again: " + " ".join(copies))
    return out


def _edit_options(a, m, line, sp, h, cache: dict, eps=1e-9) -> list:
    from . import edits
    W = int(settings().get("window", 2))
    out = []
    for ed in edits.candidates(a, line, sp, h):
        key = (ed.kind, ed.word)
        if key not in cache:
            cache[key] = (ed, Model(a, ed.line))
        ed, m2 = cache[key]
        first2 = next((ed.from_orig[i] for i in sp.syls if i in ed.from_orig), None)
        if first2 is None:
            continue
        sp2 = m2.span_of_ev.get(sp.first)
        if sp2 is None or not sp2.syls:
            continue
        n = len(sp2.syls)
        pos = [sp2.syls.index(x) for x in (ed.from_orig.get(h.syl), ed.first_new) if x in sp2.syls]
        if not pos:
            pos = [0]
        lo = max(0, min(pos) - W)
        hi = min(n, max(pos) + ed.n_new + W)
        window = tuple(range(lo, hi))
        anchors = False     # the text changes, so its anchors may move with it
        last_of = line.words[ed.word].syls[-1]
        for c in m2.search(sp2, window, anchors=anchors)[:3]:
            fsyl = ed.from_orig.get(h.syl)
            out.append((ed, sp2, _Option(total=c.total + ed.cost, cand=c, edit=ed,
                                         own=_own(c, h.rule, fsyl),
                                         keyed=_keyed(c, ed.to_orig, last_of))))
    return out


def _syllable_notes(line, syl: int, ev: int) -> list[int]:
    """The notes the finding concerns: its syllable's notes, or the event."""
    if syl >= len(line.syls):
        return [ev]
    a = line.syls[syl].ev
    b = line.syls[syl + 1].ev if syl + 1 < len(line.syls) else len(line.events)
    out = []
    for j in range(a, b):
        if line.events[j].rest or (j > a and line.events[j].after_break):
            break
        out.append(j)
    if ev not in out:
        out.append(ev)
    return out


def run(path: str | Path, *, analysis: Analysis | None = None) -> Result:
    if analysis is None:
        score = parse(path)
        analysis = analyse(score, build_lines(score))
    a = analysis
    score = a.score
    rules = load()
    findings: list[Finding] = []
    occ: Counter = Counter()
    edit_cache: dict = {}
    for line in a.lines:
        m = Model(a, line)
        priced = []
        for sp in m.spans:
            if sp.syls:
                priced.extend((sp, p) for p in m.current(sp).priced)
        lctx = LineCtx(line, line.starts, analysis=a)
        for r in active_rules(line.lang, False, "line"):
            for h in r.fn()(lctx):
                priced.append((m.span_of_ev.get(h.ev), m.price(h)))
        for sp, p in priced:
            h = p.hit
            r = rules[h.rule]
            if h.values.get("side") == "leader":
                continue
            if not h.hard and p.cost <= 0 and r.level != "info":
                continue
            regret, alts, breakdown = None, [], []
            span, placement = [], []
            if sp is not None and sp.syls:
                span = [sp.first, sp.end]
                placement = [[line.syls[i].ev, line.syls[i].text] for i in sp.syls]
            if sp is not None and sp.syls and (sp.end - sp.first) <= settings()["max_span_notes"]:
                window = m.window_for(sp, h.syl)
                wsyls = {sp.syls[j] for j in window} | ({sp.syls[window[0] - 1]} if window[0] > 0 else set())
                cur = m.current(sp)
                cands = m.search(sp, window, anchors=h.rule != "U301")
                cur_hard = bool(cur.hard_syls & m.affected(sp, window))
                breakdown = [_fmt_cost(x) for x in cur.priced if x.hit.syl in wsyls and x.cost > 0]
                cur_keyed = _keyed(cur)
                key = (h.rule, h.syl)
                mine = _own(cur, h.rule, h.syl)
                share = p.cost / cur_keyed[key] if cur_keyed.get(key) else 1.0
                opts = [(None, sp, _Option(total=c.total, cand=c, own=_own(c, h.rule, h.syl), keyed=_keyed(c)))
                        for c in cands if c.starts != cur.starts]
                opts += _edit_options(a, m, line, sp, h, edit_cache.setdefault(id(line), {}))
                opts.sort(key=lambda t: (round(t[2].total, 6), t[2].edit is not None))
                if not opts and not cands:
                    pass
                elif not cur_hard:
                    # regret: the best option that solves this finding (its rule costs
                    # less on its syllable), against the underlay as it is, and only
                    # the part of the improvement this finding accounts for
                    solving = [t for t in opts if t[2].own < mine - 1e-9]
                    if solving:
                        best = solving[0][2]
                        regret = attributable(cur_keyed, best.keyed, cur.total - best.total, key, share)
                    else:
                        regret = 0.0
                    listed = [t for t in solving if t[2].total < cur.total - 1e-9]
                else:
                    listed = opts
                cur_rules = _by_rule(cur_keyed)
                for ed, sp2, o in listed:
                    fixes, intro = _diff(cur_rules, _by_rule(o.keyed))
                    if ed is not None:
                        intro.append(f"edit {ed.cost:.2f}")
                        moves = _edit_moves(line, ed, sp2, o.cand)
                        place = [[b, ed.line.syls[i].text + ("*" if ed.to_orig.get(i) is None else "")]
                                 for i, b in zip(sp2.syls, o.cand.starts)]
                    else:
                        moves = _moves(line, sp, cur, o.cand)
                        place = [[b, line.syls[i].text] for i, b in zip(sp.syls, o.cand.starts)]
                    alts.append(Alternative(moves=moves, cost=round(o.total - cur.total, 3)
                                            if not cur_hard else round(o.total, 3),
                                            fixes=fixes, introduces=intro,
                                            basis="total" if cur_hard else "change",
                                            edit=ed.kind if ed is not None else "", placement=place))
                    if len(alts) >= settings()["alternatives"]:
                        break
            syl = line.syls[h.syl] if h.syl < len(line.syls) else None
            w = line.word_of(h.syl) if syl is not None else None
            word = w.norm if w else ""
            k = syl.k if syl else 0
            ev = line.events[h.ev]
            key = (score.slug, line.voice, line.verse, h.rule, word, k)
            occ[key] += 1
            fp = f"{score.slug}|{line.voice}|v{line.verse}|{h.rule}|{word}#{k}|{occ[key]}"
            src = f"{ev.src[0]}:{ev.src[1]}" if ev.src else ""
            findings.append(Finding(
                slug=score.slug, rule=h.rule, name=r.name, level=_level(r.level, h.hard, regret),
                voice=line.voice, verse=line.verse, bar=ev.bar, where=ev.where, word=word, k=k,
                text=syl.text if syl else "", message=r.format(h.values), principle=r.principle,
                cost=p.cost, regret=regret, gates=[f"{n}×{f:g}" for n, f in p.gates],
                breakdown=breakdown, alternatives=[asdict(x) for x in alts], src=src, fingerprint=fp,
                ev=h.ev, notes=_syllable_notes(line, h.syl, h.ev), span=span, placement=placement))
    findings.sort(key=lambda f: (LEVEL_ORDER[f.level], -(f.regret or 0), f.voice, f.verse, f.bar, f.rule))
    return Result(slug=score.slug, path=str(path), analysis=a, findings=findings)
