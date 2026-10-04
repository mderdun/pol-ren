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


# ---------------------------------------------------------------- duos
# Paired upper voices (Miki, second review of 4 October 2026, Vox: the Altus
# and Cantus "sort of coming in and out of each others rhythms but starting
# together"). The two highest voices begin new text within a semiminim; over the next
# DUO_SPAN semiminims (or until either rests) they share some of their note
# onsets but not all: shared between DUO_MIN and DUO_MAX of the onsets of the
# two. Information only, for the review page: no rule reads it.

DUO_SPAN = F(24)        # three breves
DUO_MIN, DUO_MAX = 0.3, 0.85


@dataclass
class Duo:
    voices: tuple
    start: F
    end: F
    first_where: str
    last_where: str
    shared: float                                   # fraction of onsets shared
    apart: list = field(default_factory=list)       # bar.minim where their rhythms part
    together: list = field(default_factory=list)    # ... and meet again

    def contains(self, t: F) -> bool:
        return self.start <= t < self.end


def _entries(evs) -> list:
    """Notes that begin new text: the first syllable after a rest, a break or
    a syllable ending with punctuation."""
    out, prev_punct = [], True
    for i, e in enumerate(evs):
        if e.rest:
            prev_punct = True
            continue
        ly = e.lyrics.get("1")
        if ly is None:
            continue
        if prev_punct or e.after_break or (i > 0 and evs[i - 1].rest):
            out.append(e)
        prev_punct = ly.text[-1:] in ",.:;!?"
    return out


def _run(evs, start: F, limit: F) -> list:
    """Notes of a voice from onset `start` until a rest or `limit`."""
    out = []
    for e in evs:
        if e.onset < start:
            continue
        if e.rest or e.onset >= limit:
            break
        out.append(e)
    return out


def duos(score: Score) -> list[Duo]:
    parts = score.parts
    out: list[Duo] = []
    for v1, v2 in [tuple(parts[:2])] if len(parts) >= 3 else []:
        e2s = _entries(score.voices[v2])
        if True:
            for e1 in _entries(score.voices[v1]):
                e2 = next((e for e in e2s if abs(e.onset - e1.onset) <= 1), None)
                t = min(e1.onset, e2.onset) if e2 is not None else None
                if e2 is None or any(d.contains(t) for d in out):
                    continue
                limit = t + DUO_SPAN
                r1 = _run(score.voices[v1], e1.onset, limit)
                r2 = _run(score.voices[v2], e2.onset, limit)
                end = min(r1[-1].end, r2[-1].end)
                o1 = {e.onset for e in r1 if e.onset < end}
                o2 = {e.onset for e in r2 if e.onset < end}
                if len(o1) < 4 or len(o2) < 4:
                    continue
                shared = len(o1 & o2) / len(o1 | o2)
                if not DUO_MIN <= shared <= DUO_MAX:
                    continue
                apart, together, was = [], [], True
                by = {e.onset: e for e in r1 + r2}
                for t in sorted(o1 | o2):
                    now = t in o1 and t in o2
                    if now != was:
                        (together if now else apart).append(by[t].where)
                    was = now
                if not apart:
                    continue
                last = max((e for e in r1 + r2 if e.onset < end), key=lambda e: e.onset)
                first = e1 if e1.onset <= e2.onset else e2
                out.append(Duo(voices=(v1, v2), start=t, end=end, first_where=first.where,
                               last_where=last.where, shared=round(shared, 2), apart=apart, together=together))
    out.sort(key=lambda d: (d.start, d.voices))
    return out
