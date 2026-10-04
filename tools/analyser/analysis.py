"""All analysis layers of one edition, built once and shared by the rules."""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass, field

from .ingest import parse
from .model import Score
from .text import Line, build_lines
from . import meter
from .layers import cadence, dissonance, imitation, m21, phrase, sonority, texture


@dataclass
class Analysis:
    score: Score
    lines: list
    stream: object = None
    slices: list = field(default_factory=list)
    dissonances: dict = field(default_factory=dict)   # (voice, ev) -> Dis
    cadences: list = field(default_factory=list)
    arrivals: dict = field(default_factory=dict)      # (voice, ev) -> Cadence
    phrases: list = field(default_factory=list)
    points: list = field(default_factory=list)
    regions: list = field(default_factory=list)
    cadential_words: dict = field(default_factory=dict)   # (voice, verse, word) -> Cadence
    entry_of: dict = field(default_factory=dict)          # (voice, ev of a head note) -> (Point, Entry)
    resolutions: dict = field(default_factory=dict)       # (voice, arrival ev) -> ev of the voice's own resolution
    new_text: dict = field(default_factory=dict)          # verse -> [(onset, voice)] where new text begins
    motifs: list = field(default_factory=list)            # imitation.Point(type MOTIF): recurring texted motifs
    displaced: list = field(default_factory=list)         # meter.Displaced: spans played against the tactus
    duos: list = field(default_factory=list)              # texture.Duo: paired upper voices

    def against_tactus(self, voice: str, t) -> bool:
        return any(d.contains(voice, t) for d in self.displaced)

    def tail_voice(self, voice: str, verse: str, t0, t1) -> bool:
        """Has another voice begun new text strictly between t0 and t1?"""
        return any(t0 < t < t1 and v != voice for t, v in self.new_text.get(verse, ()))

    def homorhythmic(self, t) -> bool:
        return any(r.contains(t) for r in self.regions)

    def line(self, voice: str, verse: str) -> Line | None:
        return next((ln for ln in self.lines if ln.voice == voice and ln.verse == verse), None)


def analyse(score: Score, lines: list[Line] | None = None) -> Analysis:
    if lines is None:
        lines = build_lines(score)
    a = Analysis(score=score, lines=lines)
    a.stream = m21.build(score)
    a.slices = sonority.slices(score, a.stream)
    a.dissonances = dissonance.label(score, a.slices)
    a.cadences = cadence.find(score, a.dissonances)
    cadence.closure(score, lines, a.cadences)
    a.arrivals = cadence.arrivals(a.cadences)
    a.phrases = phrase.phrases(score, lines, a.stream, a.arrivals)
    a.points = imitation.points(score, lines, a.arrivals)
    a.regions = texture.regions(score, a.slices)
    for line in lines:
        starts = line.starts
        for (v, idx), cad in a.arrivals.items():
            if v != line.voice or not starts:
                continue
            k = bisect_right(starts, idx) - 1
            if k >= 0:
                a.cadential_words[(line.voice, line.verse, line.syls[k].word)] = cad
    for p in a.points:
        for e in p.entries:
            for idx in e.head:
                a.entry_of[(e.voice, idx)] = (p, e)
    a.resolutions = cadence.melodic_resolutions(score, a.arrivals)
    a.new_text = _new_text(lines)
    a.motifs = imitation.motifs(score)
    a.displaced = meter.displaced_spans(score)
    a.duos = texture.duos(score)
    return a


def _new_text(lines) -> dict:
    """verse -> sorted (onset, voice) of each syllable that begins new text:
    the first after a rest, or after a syllable ending with punctuation."""
    out: dict = {}
    for ln in lines:
        evs = ln.events
        prev = None
        for s in ln.syls:
            e = evs[s.ev]
            after_rest = s.ev == 0 or evs[s.ev - 1].rest or e.after_break
            if prev is None or prev.punct or after_rest:
                out.setdefault(ln.verse, []).append((e.onset, ln.voice))
            prev = s
    for v in out.values():
        v.sort()
    return out


def analyse_path(path) -> Analysis:
    return analyse(parse(path))
