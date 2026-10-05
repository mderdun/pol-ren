"""Sonorities: vertical slices from the music21 timespan tree. Per slice, the
sounding notes, which voices attack and which sustain, the lowest voice, and
the interval of every pair (fourths against the lowest voice count as
dissonant, as in CRIM's markFourths)."""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F
from functools import lru_cache

from music21 import interval, pitch

from ..model import Event, Score
from . import m21

CONSONANT = {"P1", "P8", "m3", "M3", "P5", "m6", "M6"}


@lru_cache(maxsize=4096)
def _iv(lo: str, hi: str):
    i = interval.Interval(pitch.Pitch(lo), pitch.Pitch(hi))
    return i.simpleName, i.generic.simpleUndirected, i.semitones


def interval_name(lo: Event, hi: Event) -> str:
    return _iv(lo.name, hi.name)[0]


def is_dissonant(lo: Event, hi: Event, lo_is_bass: bool) -> bool:
    name = interval_name(lo, hi)
    if name in CONSONANT:
        return False
    if name == "P4":
        return lo_is_bass
    return True


@dataclass
class Slice:
    onset: F
    sounding: dict = field(default_factory=dict)    # voice -> Event
    attacks: set = field(default_factory=set)       # voices whose note starts here
    lowest: str = ""
    dissonant: list = field(default_factory=list)   # (lower voice, upper voice)

    def pairs(self):
        vs = sorted(self.sounding, key=lambda v: self.sounding[v].midi)
        for a in range(len(vs)):
            for b in range(a + 1, len(vs)):
                yield vs[a], vs[b]


def slices(score: Score, s=None) -> list[Slice]:
    if s is None:
        s = m21.build(score)
    out = []
    for v in m21.verticalities(s):
        sl = Slice(onset=F(v.offset).limit_denominator(1024))
        for ts in v.startTimespans:
            voice, idx = m21.ref(ts.element)
            sl.sounding[voice] = score.voices[voice][idx]
            sl.attacks.add(voice)
        for ts in v.overlapTimespans:
            voice, idx = m21.ref(ts.element)
            sl.sounding.setdefault(voice, score.voices[voice][idx])
        if not sl.sounding:
            continue
        sl.lowest = min(sl.sounding, key=lambda x: (sl.sounding[x].midi, x))
        for lo, hi in sl.pairs():
            if is_dissonant(sl.sounding[lo], sl.sounding[hi], lo == sl.lowest):
                sl.dissonant.append((lo, hi))
        out.append(sl)
    return out
