"""Run the rules over one line under one candidate underlay.

`evaluate` is used both for the underlay as it stands and, by underlay.py, for
every candidate the search considers, so a rule has one definition for
checking and for searching.
"""
from __future__ import annotations

from .rules import Rule, load
from .rules.base import Hit, LineCtx, SegCtx
from .text import Line


def seg_end(line: Line, start: int, next_start: int | None, legacy: bool) -> int:
    evs = line.events
    limit = next_start if next_start is not None else len(evs)
    if legacy:
        return limit
    j = start + 1
    while j < limit and not evs[j].rest and not evs[j].after_break:
        j += 1
    return j


def active_rules(lang: str, legacy: bool, scope: str | None = None) -> list[Rule]:
    out = []
    for r in load().values():
        if legacy and not r.legacy:
            continue
        if lang not in r.langs:
            continue
        if scope and r.scope != scope:
            continue
        out.append(r)
    return out


def syllable_hits(line: Line, i: int, start: int, next_start: int | None, rules: list[Rule], *,
                  legacy: bool = False, analysis=None, end: int | None = None) -> list[Hit]:
    if end is None:
        end = seg_end(line, start, next_start, legacy)
    ctx = SegCtx(line, i, start, next_start, end, legacy=legacy, analysis=analysis)
    out = []
    for r in rules:
        fn = r.fn()
        if fn is not None:
            out.extend(fn(ctx))
    return out


def evaluate(line: Line, starts: list[int] | None = None, *, legacy: bool = False,
             analysis=None) -> list[Hit]:
    starts = list(line.starts if starts is None else starts)
    syl_rules = active_rules(line.lang, legacy, "syllable")
    line_rules = active_rules(line.lang, legacy, "line")
    hits: list[Hit] = []
    for i, s in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else None
        hits.extend(syllable_hits(line, i, s, nxt, syl_rules, legacy=legacy, analysis=analysis))
    lctx = LineCtx(line, starts, legacy=legacy, analysis=analysis)
    for r in line_rules:
        hits.extend(r.fn()(lctx))
    return hits


def legacy_audit(path) -> list[tuple]:
    """The old audit's output, from the ported rules: (KIND, voice, verse, bar, message)."""
    from .ingest import parse
    from .text import build_lines
    score = parse(path, legacy=True)
    rules = load()
    out = []
    for line in build_lines(score, legacy=True):
        for h in evaluate(line, legacy=True):
            r = rules[h.rule]
            msg = r.format(h.values)
            kind = "BREAK" if r.level == "break" else "LOOK"
            if kind == "LOOK":
                msg = f"{r.name}: {msg}"
            out.append((kind, line.voice, line.verse, h.values["bar"], msg))
    return out
