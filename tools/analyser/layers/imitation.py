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
