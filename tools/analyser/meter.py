"""Mensuration-aware metre: the strength of every onset, without music21's
beatStrength (which is the modern 2/1 hierarchy, not a tactus).

The bar is a breve (principles 5.2). Under cut-C and under C the tactus falls
on the semibreve, so the half-bar is a beat (survey §3.2, item 2). What changes
between the signs is the value that may carry a syllable (principles 10.1):

  cut-C, or no sign     a minim or longer
  C                     a semiminim or longer: semiminims count as minims
                        (Stoquerus, Rotola ed., 227, 243; Towne 1990, R11)

Strength levels: 3 bar (breve), 2 half-bar (semibreve tactus), 1 minim,
0 anything smaller.
"""
from __future__ import annotations

from fractions import Fraction as F

from .model import Event

TACTUS = F(4)   # semibreve, in semiminims


def strength(e: Event) -> int:
    p = e.pos
    if p % 8 == 0:
        return 3
    if p % 4 == 0:
        return 2
    if p % 2 == 0:
        return 1
    return 0


def on_beat(e: Event) -> bool:
    """On the bar or the half-bar (the tactus)."""
    return e.pos % TACTUS == 0


def syllable_unit(e: Event) -> F:
    """The shortest value that may take a new syllable freely (10.1)."""
    return F(1) if e.sign == "C" else F(2)


def dotted_unit(e: Event) -> F:
    """The dotted value after which the next shorter note may take a syllable:
    a dotted minim under cut-C, a dotted semiminim under C."""
    return syllable_unit(e) * F(3, 2)


def syncopated(e: Event) -> bool:
    """Starts off the tactus and sounds across the next tactus."""
    if e.pos % TACTUS == 0:
        return False
    nxt = (e.pos // TACTUS + 1) * TACTUS
    return e.pos + e.dur > nxt


def describe(e: Event) -> str:
    s = strength(e)
    return ["off the minim", "on a minim", "on the half-bar", "on the bar"][s]


def mensuration_summary(events: list[Event]) -> dict:
    out: dict = {}
    for e in events:
        out[e.sign] = out.get(e.sign, 0) + 1
    return out
