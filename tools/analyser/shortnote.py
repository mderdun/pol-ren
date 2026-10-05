"""Principles 10.1 (rewritten 4 October 2026 after docs/research/rule-10-1-review.md):
what a new syllable on a note shorter than the syllable value is.

Values are under cut-C; under C every value counts one level down (the unit is
then the semiminim). `classify` returns (kind, detail) for a syllable that
starts on event `e`:

  None                     a note of the syllable value or longer, or the
                           first note after a rest (10.2): nothing to say
  ("firm", why)            the firm core: a dot, a note smaller than the dot
                           it follows, a fusa, a middle or last note of a run
                           (outside (c)), or a semiminim outside (a)-(c)
  ("a", why)               the first semiminim of a run, on a minim beat
  ("b_dotted", why)        a semiminim straight after a dotted minim
  ("b_repeat", why)        a lone semiminim on a repeated pitch, after a
                           longer note
  ("c", why)               a later note of a run where every sounding voice
                           moves in semiminims, or which the line reaches by
                           a leap

(d), the white note straight after a run at a phrase end, is priced by U203;
(e), what a period source shows, is the editor's, accepted beside the note
(inline.py) with the clause named.
"""
from __future__ import annotations

from bisect import bisect_right
from fractions import Fraction as F
from functools import lru_cache

from .meter import dotted_unit, syllable_unit


@lru_cache(maxsize=1)
def costs() -> dict:
    from .rules import settings
    return dict(settings().get("licences_10_1") or {})


def _note(e) -> bool:
    return e is not None and not e.rest


def _dotted(d: F) -> bool:
    """A dotted value: three times a power-of-two value."""
    k = F(d) / 3
    if k <= 0:
        return False
    while k < 1:
        k *= 2
    while k > 1 and k.denominator == 1 and k % 2 == 0:
        k /= 2
    return k == 1


def run_bounds(evs, i: int, unit: F) -> tuple[int, int]:
    """The run of notes shorter than `unit` containing event i: (first, last),
    inclusive. A rest or a section break ends it."""
    j = i
    while j > 0 and _note(evs[j - 1]) and evs[j - 1].dur < unit and not evs[j].after_break:
        j -= 1
    k = i
    while k + 1 < len(evs) and _note(evs[k + 1]) and evs[k + 1].dur < unit and not evs[k + 1].after_break:
        k += 1
    return j, k


def lone(evs, i: int, unit: F) -> bool:
    j, k = run_bounds(evs, i, unit)
    return j == k == i


def _all_voices_short(analysis, e, unit: F) -> bool:
    """Every other voice sounding at e's onset strikes a note shorter than the
    syllable value there too (Stoquerus R1, 243: 'all voices move in
    semiminims')."""
    if analysis is None or getattr(analysis, "score", None) is None:
        return False
    sounding = 0
    for v, evs in analysis.score.voices.items():
        if v == e.voice:
            continue
        on = _onsets(analysis, v)
        j = bisect_right(on, e.onset) - 1
        if j < 0:
            continue
        o = evs[j]
        if o.rest or o.end <= e.onset:
            continue
        sounding += 1
        if o.onset != e.onset or o.dur >= unit:
            return False
    return sounding > 0


def _onsets(analysis, v):
    """Onsets of voice v, cached on the analysis itself (an id()-keyed cache
    goes stale when a freed analysis's id is reused)."""
    cache = analysis.__dict__.setdefault("_shortnote_onsets", {})
    if v not in cache:
        cache[v] = [x.onset for x in analysis.score.voices[v]]
    return cache[v]


def classify(ctx):
    e, prev = ctx.first, ctx.prev
    unit = syllable_unit(e)
    if e.dur >= unit:
        return None
    if prev is None or prev.rest:
        return None
    evs = ctx.events
    i = ctx.start
    if prev.dur > e.dur and _dotted(prev.dur) and e.dur < prev.dur / 3:
        return ("firm", "smaller than the dot it follows")
    if e.dur < unit / 2:
        return ("firm", "a fusa" if unit == 2 else "a note shorter than a semiminim")
    j, k = run_bounds(evs, i, unit)
    if i > j:
        # a middle or last note of a run
        if _all_voices_short(ctx.analysis, e, unit):
            return ("c", "every sounding voice moves in short notes")
        if prev.midi is not None and abs(e.midi - prev.midi) >= 3:
            return ("c", "the line leaps to it")
        return ("firm", "a middle or last note of a run")
    if prev.dur == dotted_unit(e):
        return ("b_dotted", "straight after a dotted note")
    if k > i:
        if e.pos % unit == 0:
            return ("a", "the first of a run, on a beat")
        return ("firm", "the first of a run, off the beat")
    nxt = evs[i + 1] if i + 1 < len(evs) else None
    if prev.dur > e.dur and (prev.midi == e.midi or (_note(nxt) and nxt.midi == e.midi)):
        return ("b_repeat", "a lone short note on a repeated pitch")
    return ("firm", "a lone short note")
