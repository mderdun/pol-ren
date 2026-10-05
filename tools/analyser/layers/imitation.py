"""Points of imitation (survey §3.2, item 8; after CRIM's entries and
presentation types, written from their description).

Entries are the first notes after a rest or a section break. Each entry's head
motif is its first HEAD notes: the diatonic intervals between them and their
durations. Two entries match when their heads are close in both: at most one
interval may differ, by a step (a flexed entry, as CRIM's flexed_distance
allows; this covers a tonal answer, a fifth answered by a fourth), and the
number of flexed intervals plus the number of values that differ (all notes
but the last) is at most MAX_DISTANCE. A four-note match on intervals alone
can be chance, so the rhythm counts.

Where the evidence is strong an entry need not follow a rest: a note straight
after a cadence arrival in its voice, or the first note of a new clause of the
text (the syllable before it ends with punctuation), counts as an entry if it
matches another entry exactly in intervals and rhythm over LONG notes.

A point is a chain of matching entries in different voices, each within
WINDOW semiminims of the one before. Types: FUGA (three or more entries), PEN
(periodic entry: three or more at equal time distances), DUO (two entries).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from ..model import Event, Score

HEAD = 4            # notes in the head motif (Vox in Rama opens with four)
MAX_DISTANCE = 2    # intervals flexed by a step plus values that differ, in a head
LONG = 6            # notes that must agree for an entry that does not follow a rest
WINDOW = F(32)      # four breves


@dataclass
class Entry:
    voice: str
    ev: int                     # first event of the head
    head: list                  # event indices of the head notes
    intervals: tuple
    durs: tuple
    onset: F
    where: str
    exact: bool = True
    transposition: int = 0      # diatonic steps from the leader's first note
    context: str = "rest"       # rest | cadence | clause: what the entry follows
    long_intervals: tuple = ()  # intervals and values over LONG notes, for entries
    long_durs: tuple = ()       # that do not follow a rest


@dataclass
class Point:
    entries: list = field(default_factory=list)
    type: str = ""
    motif: str = ""

    @property
    def leader(self) -> Entry:
        return self.entries[0]


def _clause_starts(lines) -> set:
    """(voice, event) of the first note of each clause in verse 1: the syllable
    before it ends with punctuation."""
    out = set()
    for ln in lines or []:
        if ln.verse != "1":
            continue
        for a, b in zip(ln.syls, ln.syls[1:]):
            if a.punct:
                out.add((ln.voice, b.ev))
    return out


def entries(score: Score, lines=None, arrivals=None) -> list[Entry]:
    clause = _clause_starts(lines)
    arrivals = arrivals or {}
    out = []
    for v in score.parts:
        evs = score.voices[v]
        for e in evs:
            if e.rest:
                continue
            p = evs[e.idx - 1] if e.idx > 0 else None
            if p is None or p.rest or e.after_break:
                ctx = "rest"
            elif (v, p.idx) in arrivals and arrivals[(v, p.idx)].kind in ("full", "evaded"):
                ctx = "cadence"
            elif (v, e.idx) in clause:
                ctx = "clause"
            else:
                continue
            want = HEAD if ctx == "rest" else LONG
            head = [e]
            j = e.idx + 1
            while len(head) < LONG and j < len(evs) and not evs[j].rest and not evs[j].after_break:
                head.append(evs[j])
                j += 1
            if len(head) < want:
                continue
            ivs = tuple(b.diatonic - a.diatonic for a, b in zip(head, head[1:]))
            if all(x == 0 for x in ivs[:HEAD - 1]):
                continue
            out.append(Entry(voice=v, ev=e.idx, head=[h.idx for h in head[:HEAD]], intervals=ivs[:HEAD - 1],
                             durs=tuple(h.dur for h in head[:HEAD]), onset=e.onset, where=e.where,
                             context=ctx, long_intervals=ivs, long_durs=tuple(h.dur for h in head)))
    return sorted(out, key=lambda x: (x.onset, x.voice))


def match(a: Entry, b: Entry) -> str | None:
    """'exact', 'flexed' or None (module docstring)."""
    if a.context != "rest" or b.context != "rest":
        if len(a.long_intervals) < LONG - 1 or len(b.long_intervals) < LONG - 1:
            return None
        if a.long_intervals[:LONG - 1] == b.long_intervals[:LONG - 1] \
                and a.long_durs[:LONG - 1] == b.long_durs[:LONG - 1]:
            return "exact"
        return None
    rhythm = sum(1 for x, y in zip(a.durs[:-1], b.durs[:-1]) if x != y)
    diff = [abs(x - y) for x, y in zip(a.intervals, b.intervals)]
    flex = sum(1 for d in diff if d)
    if flex > 1 or max(diff) > 1 or flex + rhythm > MAX_DISTANCE:
        return None
    return "exact" if flex == 0 else "flexed"


def points(score: Score, lines=None, arrivals=None) -> list[Point]:
    es = entries(score, lines, arrivals)
    used = set()
    out = []
    for i, lead in enumerate(es):
        if id(lead) in used:
            continue
        chain = [lead]
        voices = {lead.voice}
        last = lead.onset
        for b in es[i + 1:]:
            if b.onset - last > WINDOW:
                break
            if b.voice in voices or id(b) in used or b.onset == lead.onset:
                continue
            m = match(lead, b)
            if m:
                b.exact = m == "exact"
                chain.append(b)
                voices.add(b.voice)
                last = b.onset
        if len(chain) < 2:
            continue
        for b in chain:
            used.add(id(b))
            b.transposition = _transposition(score, lead, b)
        gaps = [y.onset - x.onset for x, y in zip(chain, chain[1:])]
        if len(chain) >= 3:
            typ = "PEN" if len(set(gaps)) == 1 else "FUGA"
        else:
            typ = "DUO"
        out.append(Point(entries=chain, type=typ, motif=" ".join(f"{x:+d}" for x in lead.intervals)))
    return out


def _transposition(score: Score, lead: Entry, b: Entry) -> int:
    x = score.voices[lead.voice][lead.ev]
    y = score.voices[b.voice][b.ev]
    return y.diatonic - x.diatonic


def interval_word(steps: int) -> str:
    s = abs(steps) % 7
    name = ["unison", "second", "third", "fourth", "fifth", "sixth", "seventh"][s]
    if s == 0 and steps:
        name = "octave"
    return name + (" below" if steps < 0 else " above" if steps else "")


# ---------------------------------------------------------------- motifs
#
# Points (above) join entries after rests, each voice once. They miss a motif
# that the voices pass round while they keep singing: in *Vox in Rama* the
# 'et noluit' head (minim, dotted minim, semiminim, minim; the repeated note on
# the dotted figure) recurs a dozen times in bars 28-38, mostly straight after
# a word or a weak clausula rather than after a rest, several times in the same
# voice, at the fourth and the fifth, and once inverted (Tenor 37.4) (Miki,
# review of 4 October 2026). A motif is found from an entry after a rest whose
# head has a dotted value (a distinctive rhythm), and then sought at every
# note: the same values (all but the last), repeated notes in the same places,
# and each other interval within a step of the leader's, in the same direction
# throughout or inverted throughout. The leader must leap (a third or more):
# dotted scale figures are common coin. Occurrences within WINDOW of each other
# form one chain, and an inversion joins it only inside the span of the direct
# occurrences; a chain needs MOTIF_MIN occurrences in two voices or more.

MOTIF_MIN = 3


def _dotted(d) -> bool:
    d = F(d)
    return d.numerator == 3


def _heads(score: Score):
    for v in score.parts:
        evs = score.voices[v]
        for e in evs:
            if e.rest:
                continue
            head = [e]
            j = e.idx + 1
            while len(head) < HEAD and j < len(evs) and not evs[j].rest and not evs[j].after_break:
                head.append(evs[j])
                j += 1
            if len(head) < HEAD:
                continue
            ivs = tuple(b.diatonic - a.diatonic for a, b in zip(head, head[1:]))
            yield v, e, head, ivs


def motif_match(lead_ivs, lead_durs, ivs, durs) -> str | None:
    """'exact', 'flexed', 'inverted' or None (see above)."""
    if tuple(durs[:-1]) != tuple(lead_durs[:-1]):
        return None
    if any((x == 0) != (y == 0) for x, y in zip(lead_ivs, ivs)):
        return None
    moving = [(x, y) for x, y in zip(lead_ivs, ivs) if x]
    if not moving:
        return None
    for sign, name in ((1, "exact"), (-1, "inverted")):
        if all((y > 0) == (sign * x > 0) and abs(abs(x) - abs(y)) <= 1 for x, y in moving):
            if name == "exact" and any(x != y for x, y in moving):
                return "flexed"
            return name
    return None


def motifs(score: Score) -> list[Point]:
    heads = list(_heads(score))
    seeds = [(v, e, h, ivs) for v, e, h, ivs in heads
             if (e.idx == 0 or score.voices[v][e.idx - 1].rest or e.after_break)
             and any(_dotted(x.dur) for x in h[:-1]) and max(abs(x) for x in ivs) >= 2]
    seeds.sort(key=lambda t: t[1].onset)
    taken: set = set()
    out = []
    for v0, e0, h0, iv0 in seeds:
        if (v0, e0.idx) in taken:
            continue
        d0 = tuple(x.dur for x in h0)
        occ = []
        for v, e, h, ivs in heads:
            m = motif_match(iv0, d0, ivs, tuple(x.dur for x in h))
            if m:
                occ.append(Entry(voice=v, ev=e.idx, head=[x.idx for x in h], intervals=ivs,
                                 durs=tuple(x.dur for x in h), onset=e.onset, where=e.where,
                                 exact=m == "exact",
                                 context="rest" if (e.idx == 0 or score.voices[v][e.idx - 1].rest) else m))
        occ.sort(key=lambda x: (x.onset, x.voice))
        # the chain that contains the seed
        k = next(i for i, x in enumerate(occ) if x.voice == v0 and x.ev == e0.idx)
        lo = k
        while lo > 0 and occ[lo].onset - occ[lo - 1].onset <= WINDOW:
            lo -= 1
        hi = k
        while hi + 1 < len(occ) and occ[hi + 1].onset - occ[hi].onset <= WINDOW:
            hi += 1
        chain = [x for x in occ[lo:hi + 1] if (x.voice, x.ev) not in taken]
        # an inversion belongs to the chain only inside the span of its direct
        # occurrences (Tenor 37.4 does; 'rans, filios' at Tenor 24.3 does not)
        direct = [x for x in chain if x.context != "inverted"]
        if direct:
            t0, t1 = direct[0].onset, direct[-1].onset
            chain = [x for x in chain if x.context != "inverted" or t0 <= x.onset <= t1]
        if len(chain) < MOTIF_MIN or len({x.voice for x in chain}) < 2:
            continue
        for x in chain:
            taken.add((x.voice, x.ev))
            x.transposition = _transposition(score, chain[0], x)
        out.append(Point(entries=chain, type="MOTIF", motif=" ".join(f"{x:+d}" for x in iv0)))
    return out
