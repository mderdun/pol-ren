"""Shared helpers: run every rule on a fixture or an edition passage."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from tools.analyser import fixtures
from tools.analyser.analysis import analyse
from tools.analyser.engine import active_rules, evaluate
from tools.analyser.ingest import ROOT, parse
from tools.analyser.text import build_lines

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def all_hits(score):
    """(line, hit) for every rule on the underlay as it stands."""
    lines = build_lines(score)
    a = analyse(score, lines)
    out = []
    for line in lines:
        for h in evaluate(line, analysis=a):
            out.append((line, h))
        for r in active_rules(line.lang, False, "piece"):
            for h in r.fn()(a, line, line.starts):
                if h.values.get("side") != "leader":
                    out.append((line, h))
    return a, out


def fixture_hits(spec: dict):
    return all_hits(fixtures.build(spec))


@lru_cache(maxsize=None)
def edition_hits(slug: str):
    if slug.startswith("fixture:"):
        path = FIXTURES / f"{slug[8:]}.musicxml"
    else:
        path = ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml"
    return all_hits(parse(path))
