"""Dissonance labelling: a subset of Alexander Morgan's taxonomy for
Renaissance dissonance (as implemented in humlib `dissonant`; survey §1.2),
written from its published definitions, not from its code.

For every dissonant pair in a slice (sonority.py) the analyser decides which
note is the dissonant one and why:

  passing          approached and left by step in the same direction
  accented-passing a passing note on the tactus (bar or half-bar)
  neighbour        approached by step, left by step back to the same pitch
  cambiata         down a step, down a third, then up a step
  anticipation     approached by step, left by repeating its pitch
  echappee         approached by step, left by a third the other way
  suspension       held over from a consonance while another voice (the agent)
                   moves against it, then resolved down by step
  unexplained      none of these

Decision order: if one note attacks and the other is held, and the attack
falls on the tactus, the held note is tested as a suspension first (the agent
of a 7-6 usually moves by step, and would otherwise pass for a passing note);
then the attacking note is tested for a melodic figure; then, off the tactus,
the held note as a suspension; failing all, the attacking note is unexplained. If both attack, each is tested and the
one that fits is labelled.

Left out for now: ornamental and fake suspensions, the chanson idiom, the
dissonant third quarter, ternary suspensions as a separate label. Their notes
come out as unexplained, so the report shows where the taxonomy runs out.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

from ..meter import strength
from ..model import Event, Score
from .sonority import Slice, interval_name, is_dissonant


@dataclass
class Dis:
    voice: str
    ev: int
    label: str
    onset: F                 # the slice where the dissonance sounds
    against: str             # the voice it is dissonant with
    interval: str
    accented: bool = False
    agent: str | None = None         # suspension: the voice that moves against it
    resolution: int | None = None    # suspension: event index of the resolution
    figure: str = ""                 # suspension: e.g. 7-6, 4-3, 2-3


def neighbours(evs: list[Event], e: Event):
    """Previous and next notes in the voice, if they touch this one."""
    p = evs[e.idx - 1] if e.idx > 0 else None
    n = evs[e.idx + 1] if e.idx + 1 < len(evs) else None
    if p is not None and (p.rest or p.end != e.onset or e.after_break):
        p = None
    if n is not None and (n.rest or n.onset != e.end or n.after_break):
        n = None
    return p, n


def figure(evs: list[Event], e: Event) -> str | None:
    p, n = neighbours(evs, e)
    if p is None or n is None:
        return None
    dp, dn = e.diatonic - p.diatonic, n.diatonic - e.diatonic
    if abs(dp) == 1 and dn == dp:
        return "accented-passing" if strength(e) >= 2 else "passing"
    if abs(dp) == 1 and dn == -dp:
        return "neighbour"
    if dp == -1 and dn == -2:
        nn = evs[n.idx + 1] if n.idx + 1 < len(evs) else None
        if nn is not None and not nn.rest and nn.onset == n.end and nn.diatonic - n.diatonic == 1:
            return "cambiata"
    if abs(dp) == 1 and dn == 0 and e.dur <= p.dur:
        return "anticipation"
    if abs(dp) == 1 and abs(dn) == 2 and (dn > 0) != (dp > 0):
        return "echappee"
    return None


def _sounding_at(evs: list[Event], t: F) -> Event | None:
    for e in evs:
        if not e.rest and e.onset <= t < e.end:
            return e
    return None


def suspension(score: Score, sl: Slice, held: str, agent: str) -> Dis | None:
    evs = score.voices[held]
    y = sl.sounding[held]
    if y.onset >= sl.onset:
        return None
    r = evs[y.idx + 1] if y.idx + 1 < len(evs) else None
    if r is None or r.rest or r.onset != y.end or r.after_break:
        return None
    if r.diatonic - y.diatonic != -1:
        return None
    # preparation: consonant with the agent's note sounding when y began
    a_prev = _sounding_at(score.voices[agent], y.onset)
    if a_prev is not None:
        lo, hi = (a_prev, y) if a_prev.midi <= y.midi else (y, a_prev)
        if is_dissonant(lo, hi, False):
            return None
    x = sl.sounding[agent]
    lo, hi = (x, y) if x.midi <= y.midi else (y, x)
    name = interval_name(lo, hi)
    # the interval of resolution against the agent's note at that moment
    a_res = _sounding_at(score.voices[agent], r.onset) or x
    lo2, hi2 = (a_res, r) if a_res.midi <= r.midi else (r, a_res)
    fig = f"{_gen(name)}-{_gen(interval_name(lo2, hi2))}"
    return Dis(voice=held, ev=y.idx, label="suspension", onset=sl.onset, against=agent,
               interval=name, accented=strength_at(sl.onset, y) >= 2, agent=agent,
               resolution=r.idx, figure=fig)


def _gen(name: str) -> str:
    return name[1:]


def strength_at(t: F, e: Event) -> int:
    pos = e.pos + (t - e.onset)
    if pos % 8 == 0:
        return 3
    if pos % 4 == 0:
        return 2
    if pos % 2 == 0:
        return 1
    return 0


def label(score: Score, slices: list[Slice]) -> dict:
    """(voice, event index) -> Dis, first label wins."""
    out: dict = {}

    def put(d: Dis):
        out.setdefault((d.voice, d.ev), d)

    for sl in slices:
        for lo, hi in sl.dissonant:
            name = interval_name(sl.sounding[lo], sl.sounding[hi])
            att = [v for v in (lo, hi) if v in sl.attacks]
            if len(att) == 1:
                x = att[0]
                y = hi if x == lo else lo
                xe = sl.sounding[x]
                # an agent striking on the tactus against a held note: suspension first
                if strength(xe) >= 2:
                    s = suspension(score, sl, y, x)
                    if s:
                        put(s)
                        continue
                f = figure(score.voices[x], xe)
                if f:
                    put(Dis(voice=x, ev=xe.idx, label=f, onset=sl.onset, against=y, interval=name,
                            accented=strength(xe) >= 2))
                    continue
                s = suspension(score, sl, y, x)
                if s:
                    put(s)
                    continue
                put(Dis(voice=x, ev=xe.idx, label="unexplained", onset=sl.onset, against=y,
                        interval=name, accented=strength(xe) >= 2))
            elif len(att) == 2:
                found = False
                for x, y in ((lo, hi), (hi, lo)):
                    xe = sl.sounding[x]
                    f = figure(score.voices[x], xe)
                    if f:
                        found = True
                        put(Dis(voice=x, ev=xe.idx, label=f, onset=sl.onset, against=y, interval=name,
                                accented=strength(xe) >= 2))
                if not found:
                    for x, y in ((lo, hi), (hi, lo)):
                        xe = sl.sounding[x]
                        put(Dis(voice=x, ev=xe.idx, label="unexplained", onset=sl.onset, against=y,
                                interval=name, accented=strength(xe) >= 2))
    return out
