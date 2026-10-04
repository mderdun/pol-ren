"""Points of imitation (survey §3.2, item 8; after CRIM's entries and
presentation types, written from their description).

Entries are the first notes after a rest or a section break. Each entry's head
motif is its first HEAD notes: the diatonic intervals between them and their
durations. Two entries match when the intervals agree, allowing one interval
to differ by a step (a flexed entry, as CRIM's flexed_distance allows). A
point is a chain of matching entries in different voices, each within WINDOW
semiminims of the one before. Types: FUGA (three or more entries), PEN
(periodic entry: three or more at equal time distances), DUO (two entries).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from ..model import Event, Score

HEAD = 4            # notes in the head motif (Vox in Rama opens with four)
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


@dataclass
class Point:
    entries: list = field(default_factory=list)
    type: str = ""
    motif: str = ""

    @property
    def leader(self) -> Entry:
        return self.entries[0]


def entries(score: Score) -> list[Entry]:
    out = []
    for v in score.parts:
        evs = score.voices[v]
        for e in evs:
            if e.rest:
                continue
            p = evs[e.idx - 1] if e.idx > 0 else None
            if not (p is None or p.rest or e.after_break):
                continue
            head = [e]
            j = e.idx + 1
            while len(head) < HEAD and j < len(evs) and not evs[j].rest and not evs[j].after_break:
                head.append(evs[j])
                j += 1
            if len(head) < HEAD:
                continue
            ivs = tuple(b.diatonic - a.diatonic for a, b in zip(head, head[1:]))
            if all(x == 0 for x in ivs):
                continue
            out.append(Entry(voice=v, ev=e.idx, head=[h.idx for h in head], intervals=ivs,
                             durs=tuple(h.dur for h in head), onset=e.onset, where=e.where))
    return sorted(out, key=lambda x: (x.onset, x.voice))


def match(a: Entry, b: Entry) -> str | None:
    if a.intervals == b.intervals:
        return "exact"
    diff = [abs(x - y) for x, y in zip(a.intervals, b.intervals)]
    if sum(1 for d in diff if d) == 1 and max(diff) == 1 and a.intervals[0] == b.intervals[0]:
        return "flexed"
    return None


def points(score: Score) -> list[Point]:
    es = entries(score)
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
