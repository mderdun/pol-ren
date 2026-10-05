"""Homorhythm (survey §3.2, item 9), after humlib's homorhythm weighting:
each slice scores 1.0 when every sounding voice attacks and there are at least
three of them (or all voices of a three-voice piece), 0.5 when all but one
attack, otherwise 0. A run of slices whose score adds up to THRESHOLD or more is a
homorhythmic region. For each region we also measure, per verse, how often
the attacking voices start a syllable together (CRIM's syllable match), the
measure 10.6 and 10.14 care about."""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from ..model import Score

THRESHOLD = 4.0


@dataclass
class Region:
    start: F
    end: F
    first_where: str
    last_where: str
    voices: list = field(default_factory=list)
    slices: int = 0
    syllable_match: dict = field(default_factory=dict)    # verse -> fraction

    def contains(self, t: F) -> bool:
        return self.start <= t < self.end


def score_slice(sl, nvoices: int) -> float:
    n = len(sl.sounding)
    a = len(sl.attacks)
    need = 3 if nvoices >= 4 else min(3, nvoices)
    if n >= need and a == n:
        return 1.0
    if n >= need and a == n - 1 and a >= 2:
        return 0.5
    return 0.0


def regions(score: Score, slices: list) -> list[Region]:
    nv = len(score.parts)
    out = []
    run, total = [], 0.0

    def close():
        if total >= THRESHOLD and run:
            first, last = run[0], run[-1]
            end = max(e.end for e in last.sounding.values())
            r = Region(start=first.onset, end=end, first_where=_where(first), last_where=_where(last),
                       voices=sorted({v for s in run for v in s.attacks}), slices=len(run))
            for verse in sorted({k for s in run for e in s.sounding.values() for k in e.lyrics}, key=int):
                together = 0
                counted = 0
                for s in run:
                    starts = [v for v in s.attacks if verse in s.sounding[v].lyrics]
                    if not starts:
                        continue
                    counted += 1
                    if len(starts) == len(s.attacks):
                        together += 1
                r.syllable_match[verse] = round(together / counted, 2) if counted else 0.0
            out.append(r)

    for sl in slices:
        sc = score_slice(sl, nv)
        if sc > 0:
            run.append(sl)
            total += sc
        else:
            close()
            run, total = [], 0.0
    close()
    return out


def _where(sl) -> str:
    return sl.sounding[sorted(sl.attacks)[0]].where
