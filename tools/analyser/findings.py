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
    cost: float
    fixes: list
    introduces: list


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


def _own(c, h) -> float:
    """What the finding's rule costs on the finding's syllable in candidate c."""
    return sum(x.cost for x in c.priced if x.rule == h.rule and x.hit.syl == h.syl)


def _by_rule(c, wsyls) -> dict:
    out: dict = {}
    for x in c.priced:
        if x.hit.syl in wsyls and x.cost > 0:
            out[x.rule] = out.get(x.rule, 0.0) + x.cost
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


def _moves(line, sp, cur, alt) -> list[str]:
    out = []
    for j, (a, b) in enumerate(zip(cur.starts, alt.starts)):
        if a != b:
            s = line.syls[sp.syls[j]]
            out.append(f"'{s.text}' {line.events[a].where} -> {line.events[b].where}")
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
            if sp is not None and sp.syls and (sp.end - sp.first) <= settings()["max_span_notes"]:
                window = m.window_for(sp, h.syl)
                wsyls = {sp.syls[j] for j in window} | ({sp.syls[window[0] - 1]} if window[0] > 0 else set())
                cur = m.current(sp)
                cands = m.search(sp, window, anchors=h.rule != "U301")
                breakdown = [_fmt_cost(x) for x in cur.priced if x.hit.syl in wsyls and x.cost > 0]
                if cands:
                    # regret: the best candidate that solves this finding (its rule
                    # costs less on its syllable), against the underlay as it is
                    mine = _own(cur, h)
                    solving = [c for c in cands if _own(c, h) < mine - 1e-9]
                    if not cur.hard:
                        regret = max(0.0, cur.total - solving[0].total) if solving else 0.0
                    cur_rules = _by_rule(cur, wsyls)
                    for c in solving if not cur.hard else cands:
                        if c.starts == cur.starts:
                            continue
                        if not cur.hard and c.total >= cur.total - 1e-9:
                            continue
                        alt_rules = _by_rule(c, wsyls)
                        fixes, intro = _diff(cur_rules, alt_rules)
                        alts.append(Alternative(moves=_moves(line, sp, cur, c), cost=round(c.total - cur.total, 3)
                                                if not cur.hard else round(c.total, 3),
                                                fixes=fixes, introduces=intro))
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
                breakdown=breakdown, alternatives=[asdict(x) for x in alts], src=src, fingerprint=fp))
    findings.sort(key=lambda f: (LEVEL_ORDER[f.level], -(f.regret or 0), f.voice, f.verse, f.bar, f.rule))
    return Result(slug=score.slug, path=str(path), analysis=a, findings=findings)
