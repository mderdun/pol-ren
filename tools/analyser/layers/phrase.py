"""Phrases per voice and verse (survey §3.2, item 7): from rest to rest
(music21's segmentByRests), cut at section breaks, after each cadence arrival
in that voice where a word ends, and after each syllable that ends with
punctuation. Each phrase
records the words it carries and the cadence it ends on, which is what 10.3
needs."""
from __future__ import annotations

from dataclasses import dataclass, field

from music21.analysis import segmentByRests

from ..model import Score
from ..text import Line
from . import m21


@dataclass
class Phrase:
    voice: str
    verse: str
    first: int                  # event index of its first note
    last: int                   # event index of its last note
    syls: list = field(default_factory=list)     # syllable indices that start inside it
    text: str = ""
    cadence: object = None      # the Cadence its last note arrives on, if any
    ends: str = ""              # rest | cadence | punctuation | end

    def label(self, line: Line) -> str:
        a, b = line.events[self.first], line.events[self.last]
        return f"{a.where}-{b.where}"


def rest_segments(score: Score, s) -> dict:
    """voice -> list of (first, last) event indices, from segmentByRests."""
    out = {}
    for part in s.parts:
        segs = []
        for seg in segmentByRests.Segmenter.getSegmentsList(part):
            idx = [m21.ref(n)[1] for n in seg]
            segs.append((min(idx), max(idx)))
        out[part.partName] = segs
    return out


def phrases(score: Score, lines: list[Line], s, arrivals: dict) -> list[Phrase]:
    segs = rest_segments(score, s)
    out = []
    for line in lines:
        evs = line.events
        starts = {sy.ev: sy for sy in line.syls}
        punct_end = {}
        for k, sy in enumerate(line.syls):
            if sy.punct:
                nxt = line.syls[k + 1].ev if k + 1 < len(line.syls) else None
                j = sy.ev
                while j + 1 < len(evs) and not evs[j + 1].rest and (nxt is None or j + 1 < nxt) \
                        and not evs[j + 1].after_break:
                    j += 1
                punct_end[j] = True
        for a, b in segs.get(line.voice, []):
            cur = a
            for j in range(a, b + 1):
                cut_before = j > cur and evs[j].after_break
                if cut_before:
                    out.append(_mk(line, cur, j - 1, starts, arrivals, "end"))
                    cur = j
                cad = arrivals.get((line.voice, j))
                if cad is not None and not _word_ends_at(line, j):
                    cad = None
                if j == b or cad is not None or j in punct_end:
                    why = "rest" if j == b else ("cadence" if cad is not None else "punctuation")
                    out.append(_mk(line, cur, j, starts, arrivals, why))
                    cur = j + 1
                    if cur > b:
                        break
    return out


def _word_ends_at(line: Line, j: int) -> bool:
    """Does the syllable sounding at event j end its word?"""
    cur = None
    for sy in line.syls:
        if sy.ev <= j:
            cur = sy
        else:
            break
    return cur is not None and cur.syllabic in ("end", "single")


def _mk(line, a, b, starts, arrivals, why):
    ph = Phrase(voice=line.voice, verse=line.verse, first=a, last=b, ends=why)
    ph.syls = [starts[j].i for j in range(a, b + 1) if j in starts]
    ph.text = " ".join(line.syls[i].text + ("-" if line.syls[i].syllabic in ("begin", "middle") else "")
                       for i in ph.syls).replace("- ", "")
    ph.cadence = arrivals.get((line.voice, b))
    return ph
