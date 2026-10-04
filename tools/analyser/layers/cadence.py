"""Cadences by cadential voice functions (survey §3.2, item 6).

1. Clausulae: for every pair of voices and every onset where both attack,
   one voice rises by step and the other falls by step, from a major sixth to
   the octave (or a minor third to the unison, compound intervals included).
   music21's VoiceLeadingQuartet confirms the contrary motion. The rising
   voice is C, the falling voice T; the arrival is that onset. The arrival
   must fall on the tactus (bar or half-bar) and both arrival notes last a
   minim or more; otherwise the motion is a passing 6-8 inside a line.
2. Every other voice sounding at the arrival gets B, A or b by its motion
   (cadence_tables.yaml).
3. Prepared clausulae that do not arrive: a 7-6 suspension resolving into a
   major sixth whose voices then do not open to the octave. These give
   evaded or abandoned cadences.
4. The type comes from the set of functions and the tables.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path

import yaml
from music21 import note, voiceLeading

from ..model import Event, Score
from .dissonance import Dis, neighbours
from .sonority import interval_name

HERE = Path(__file__).resolve().parent
PC_NAMES = ["C", "C#", "D", "E-", "E", "F", "F#", "G", "G#", "A", "B-", "B"]


@lru_cache(maxsize=1)
def tables() -> dict:
    return yaml.safe_load((HERE / "cadence_tables.yaml").read_text(encoding="utf-8"))


@dataclass
class Cadence:
    onset: F
    measure: str
    where: str
    tone: str
    functions: dict = field(default_factory=dict)    # voice -> function letter
    arrivals: dict = field(default_factory=dict)     # voice -> event index of its arrival note
    type: str = ""
    strength: int = 0
    phrygian: bool = False
    prepared: bool = False                           # a suspension led into it
    bass_on_tone: bool = True

    def summary(self) -> str:
        fs = "".join(sorted(self.functions.values()))
        return f"{self.where} {self.type} on {self.tone} ({fs})"


def _note_at(evs: list[Event], t: F) -> Event | None:
    for e in evs:
        if e.onset <= t < e.end:
            return e
        if e.onset > t:
            break
    return None


def _clausula(c1: Event, c2: Event, t1: Event, t2: Event) -> bool:
    """Major sixth (C above) or minor third (C below) opening or closing by
    contrary step to a perfect octave or unison."""
    if c2.diatonic - c1.diatonic != 1 or t2.diatonic - t1.diatonic != -1:
        return False
    before = interval_name(*sorted((c1, t1), key=lambda e: e.midi))
    after_semis = abs(c2.midi - t2.midi) % 12
    if after_semis != 0:
        return False
    if c1.midi > t1.midi:
        ok = before == "M6"
    else:
        ok = before == "m3"
    if not ok:
        return False
    vlq = voiceLeading.VoiceLeadingQuartet(note.Note(c1.name), note.Note(c2.name),
                                           note.Note(t1.name), note.Note(t2.name))
    return vlq.contraryMotion()


def _type(c: Cadence) -> None:
    fs = set(c.functions.values())
    for row in tables()["types"]:
        if not set(row.get("has", [])) <= fs:
            continue
        if set(row.get("lacks", [])) & fs:
            continue
        if "phrygian" in row and row["phrygian"] != c.phrygian:
            continue
        if "bass_on_tone" in row and row["bass_on_tone"] != c.bass_on_tone:
            continue
        c.type, c.strength = row["name"], row["strength"]
        return
    c.type, c.strength = "unclassified", 0


def find(score: Score, dis: dict) -> list[Cadence]:
    voices = score.parts
    found: dict = {}
    for cv in voices:
        for c2 in score.voices[cv]:
            if c2.rest:
                continue
            c1, _ = neighbours(score.voices[cv], c2)
            if c1 is None:
                continue
            t = c2.onset
            # an arrival falls on the tactus and is held at least a minim
            if c2.pos % 4 != 0 or c2.dur < 2:
                continue
            for tv in voices:
                if tv == cv:
                    continue
                t2 = _note_at(score.voices[tv], t)
                if t2 is None or t2.rest or t2.onset != t:
                    continue
                t1, _ = neighbours(score.voices[tv], t2)
                if t1 is None or t2.dur < 2:
                    continue
                if not _clausula(c1, c2, t1, t2):
                    continue
                cad = found.get(t)
                if cad is None:
                    cad = found[t] = Cadence(onset=t, measure=t2.measure, where=t2.where,
                                             tone=PC_NAMES[t2.midi % 12])
                cad.functions.setdefault(cv, "C")
                cad.functions.setdefault(tv, "T")
                cad.arrivals[cv], cad.arrivals[tv] = c2.idx, t2.idx
                cad.phrygian = cad.phrygian or (t1.midi - t2.midi == 1)
                # prepared: the note before the penultimate is a suspension resolving into it
                for v, pen in ((cv, c1), (tv, t1)):
                    d = dis.get((v, pen.idx - 1))
                    if d and d.label == "suspension" and d.resolution == pen.idx:
                        cad.prepared = True
    # other voices at each arrival
    for t, cad in found.items():
        tone_pc = PC_NAMES.index(cad.tone)
        lowest = None
        for v in voices:
            z2 = _note_at(score.voices[v], t)
            if z2 is None or z2.rest:
                continue
            if lowest is None or z2.midi < lowest.midi:
                lowest = z2
            if v in cad.functions:
                continue
            z1, _ = neighbours(score.voices[v], z2) if z2.onset == t else (None, None)
            if z2.onset == t and z1 is not None:
                semis = (z2.midi - z1.midi) % 12
                gen = z2.diatonic - z1.diatonic
                if z2.midi % 12 == tone_pc and semis == 5 and gen in (3, -4):
                    cad.functions[v], cad.arrivals[v] = "B", z2.idx
                    continue
                if z1.midi % 12 == (tone_pc + 7) % 12 and z2.midi % 12 != tone_pc and gen in (-2, -5, 1, 2):
                    cad.functions[v] = "b"
                    continue
            if z2.midi % 12 == (tone_pc + 7) % 12:
                cad.functions[v] = "A"
        cad.bass_on_tone = lowest is not None and lowest.midi % 12 == tone_pc
        _type(cad)
    # prepared clausulae (7-6 into a major sixth) that do not arrive
    for (v, idx), d in dis.items():
        if d.label != "suspension" or d.figure != "7-6" or d.resolution is None:
            continue
        evs = score.voices[v]
        r = evs[d.resolution]                     # the leading note
        nxt = evs[r.idx + 1] if r.idx + 1 < len(evs) else None
        t = r.end
        if any(abs(t - u) <= 2 for u in found):
            continue
        a = _note_at(score.voices[d.agent], r.onset)
        if a is None or a.rest:
            continue
        lo, hi = sorted((a, r), key=lambda e: e.midi)
        if interval_name(lo, hi) != "M6" or r.midi < a.midi:
            continue
        cad = Cadence(onset=t, measure=(nxt or r).measure, where=(nxt or r).where, tone="",
                      prepared=True)
        rests = nxt is None or nxt.rest
        cad.functions[v] = "c" if rests else "t"
        cad.functions[d.agent] = "t"
        cad.tone = PC_NAMES[(r.midi + 1) % 12]
        _type(cad)
        found[t] = cad
    return [found[t] for t in sorted(found)]


def arrivals(cads: list[Cadence]) -> dict:
    """(voice, event index) -> Cadence, for the voices that arrive (C, T, B)."""
    out = {}
    for c in cads:
        for v, idx in c.arrivals.items():
            if c.functions.get(v) in ("C", "T", "B"):
                out[(v, idx)] = c
    return out
