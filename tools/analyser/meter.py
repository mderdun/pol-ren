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

from dataclasses import dataclass, field
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


@dataclass
class Displaced:
    """A span where the music plays against the tactus (Miki, second review
    of 4 October 2026: Vox Altus 10.4, 'the 3 top parts are clearly playing
    against the tactus here'; Altus 15, 'la' in a figure 'suggesting
    hemiola'). Inside it, for the voices listed, the pulse falls `shift`
    semiminims after the tactus."""
    t0: F                   # onset of the first displaced note
    t1: F                   # end of the last, plus a tactus
    voices: tuple
    kind: str               # shared (syncopation in 2+ voices together) | hemiola (one voice)
    shift: F
    where: str              # bar.minim of the first displaced note
    notes: list = field(default_factory=list)   # (voice, event idx)
    phrase_start: tuple = ()    # voices for which the span begins a phrase (mark_phrase_starts)

    def contains(self, voice: str, t) -> bool:
        return voice in self.voices and self.t0 <= t < self.t1


def mark_phrase_starts(score, spans, new_text: dict, verse: str = "1") -> None:
    """Miki, third review of 5 October 2026: the play against the tactus is
    most obvious, and so meant to be brought out, when it begins a phrase
    (doubly so in homorhythm); in the middle of a phrase it is a hint. A
    span begins a phrase for a voice when that voice's first displaced note
    in it, or the note up to a minim before it, begins new text."""
    starts = {(t, v) for t, v in new_text.get(verse, ())}
    for d in spans:
        out = []
        for v in d.voices:
            mine = [score.voices[vv][i] for vv, i in d.notes if vv == v]
            if not mine:
                continue
            e = min(mine, key=lambda x: x.onset)
            if any((t, v) in starts for t in {e.onset, *[p.onset for p in score.voices[v][max(0, e.idx - 2):e.idx]
                                                        if not p.rest and e.onset - p.onset <= 2]}):
                out.append(v)
        d.phrase_start = tuple(out)


@dataclass
class Contour:
    """A contour accent (information only, under investigation): after a run
    of short notes, a longer note that the melody leans on, so that it can
    carry an agogic accent against the tactus (Miki, third review of
    5 October 2026, Vox Altus 33.3, his '34.4': "something about the melodic
    shape that makes the G the centre of gravity that side of the run, which
    also when sung actually encourages a strong beat against the tactus
    there"). Kinds: goal (the first longer note after the run), turn (a
    local high or low point), centre (the pitch the run circles: its most
    frequent pitch, counting the note before it)."""
    voice: str
    ev: int
    where: str
    kinds: tuple
    on_tactus: bool


def contour_accents(score, voices=None) -> list[Contour]:
    out = []
    for v in voices or score.parts:
        evs = score.voices[v]
        i = 0
        while i < len(evs):
            e = evs[i]
            if e.rest or e.dur >= syllable_unit(e):
                i += 1
                continue
            j = i
            while j < len(evs) and not evs[j].rest and evs[j].dur < syllable_unit(evs[j]):
                j += 1
            run = evs[i:j]
            if len(run) >= 2:
                before = [evs[i - 1]] if i > 0 and not evs[i - 1].rest else []
                pitches = [x.midi for x in before + run]
                centre = max(set(pitches), key=lambda p: (pitches.count(p), -pitches.index(p)))
                centre = centre if pitches.count(centre) >= 2 else None
                after = []
                for k in range(j, min(j + 3, len(evs))):
                    if evs[k].rest or evs[k].dur < syllable_unit(evs[k]):
                        break
                    after.append(k)
                for n, k in enumerate(after):
                    x = evs[k]
                    kinds = []
                    if n == 0:
                        kinds.append("goal")
                    prv, nxt = evs[k - 1], evs[k + 1] if k + 1 < len(evs) else None
                    if nxt is not None and not nxt.rest and not prv.rest and \
                            ((x.midi > prv.midi and x.midi > nxt.midi) or (x.midi < prv.midi and x.midi < nxt.midi)):
                        kinds.append("turn")
                    if centre is not None and x.midi == centre:
                        kinds.append("centre")
                    if kinds:
                        out.append(Contour(voice=v, ev=x.idx, where=x.where, kinds=tuple(kinds),
                                           on_tactus=x.pos % TACTUS == 0))
            i = max(j, i + 1)
    return out


def _displaced_long(e: Event) -> bool:
    """Starts a minim (or a minim and a half) off the tactus, is a dotted minim
    or longer, and sounds across the next tactus."""
    return (not e.rest and e.pos % 2 == 0 and e.pos % TACTUS != 0
            and e.dur >= 3 and syncopated(e))


def displaced_spans(score, voices=None, verse: str = "1") -> list[Displaced]:
    """Displaced accent: (1) syncopation shared by two or more voices, their
    displaced long notes starting within a semiminim of each other, and at
    least two of them taking a new syllable (the words are declaimed on the
    displaced pulse), extended by any displaced long note within a tactus of
    the span; (2) a hemiola-like figure in one voice, two or more displaced
    notes of a semibreve or more in a row, the first taking a syllable. Each
    span lasts until a tactus after its last displaced note. A suspension
    held over in one voice is not a span: the other voices keep the tactus."""
    voices = list(voices or score.parts)
    disp = {v: [e for e in score.voices[v] if _displaced_long(e)] for v in voices}
    out: list[Displaced] = []
    allnotes = sorted(((e.onset, v, e) for v in voices for e in disp[v]), key=lambda x: (x[0], x[1]))
    used: set = set()
    for i, (t, v, e) in enumerate(allnotes):
        if (v, e.idx) in used:
            continue
        partners = [(v2, e2) for t2, v2, e2 in allnotes if v2 != v and abs(t2 - t) <= 1]
        if not partners:
            continue
        members = {(v, e.idx): e, **{(v2, e2.idx): e2 for v2, e2 in partners}}
        if sum(1 for x in members.values() if verse in x.lyrics) < 2:
            continue
        t0, t1 = min(x.onset for x in members.values()), max(x.end for x in members.values())
        grew = True
        while grew:
            grew = False
            for t2, v2, e2 in allnotes:
                if (v2, e2.idx) not in members and t0 - TACTUS <= t2 <= t1 + TACTUS:
                    members[(v2, e2.idx)] = e2
                    t0, t1 = min(t0, t2), max(t1, e2.end)
                    grew = True
        used.update(members)
        first = min(members.values(), key=lambda x: x.onset)
        out.append(Displaced(t0=t0, t1=t1 + TACTUS, voices=tuple(sorted({k[0] for k in members})),
                             kind="shared", shift=first.pos % TACTUS, where=first.where,
                             notes=sorted(members)))
    for v in voices:
        evs = score.voices[v]
        run: list = []
        for e in evs + [None]:
            if e is not None and _displaced_long(e) and e.dur >= TACTUS and (not run or run[-1].idx == e.idx - 1):
                run.append(e)
                continue
            if len(run) >= 2 and verse in run[0].lyrics and not any(d.contains(v, run[0].onset) for d in out):
                out.append(Displaced(t0=run[0].onset, t1=run[-1].end + TACTUS, voices=(v,), kind="hemiola",
                                     shift=run[0].pos % TACTUS, where=run[0].where,
                                     notes=[(v, x.idx) for x in run]))
            run = [e] if e is not None and _displaced_long(e) and e.dur >= TACTUS else []
    out.sort(key=lambda d: (d.t0, d.voices))
    return out


def pulse_on_beat(e: Event, spans=()) -> bool:
    """On a beat: the tactus, or inside a displaced span for this voice, the
    tactus or the displaced pulse (the music plays against the tactus there
    without abolishing it)."""
    if on_beat(e):
        return True
    return any(d.contains(e.voice, e.onset) and (e.pos - d.shift) % TACTUS == 0 for d in spans)


def describe(e: Event) -> str:
    s = strength(e)
    return ["off the minim", "on a minim", "on the half-bar", "on the bar"][s]


def mensuration_summary(events: list[Event]) -> dict:
    out: dict = {}
    for e in events:
        out[e.sign] = out.get(e.sign, 0) + 1
    return out
