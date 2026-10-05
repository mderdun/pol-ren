"""The score model the analyser works on.

Durations and onsets are Fractions in semiminims (1 = semiminim, 2 = minim,
4 = semibreve, 8 = breve), which in our unreduced editions is also music21's
quarterLength. Ties are merged (except the dashed ties of divided notes,
principles 10.13); rests are kept as events so that the rules can see them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F
from functools import cached_property

STEPS = "CDEFGAB"
SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


@dataclass
class Lyric:
    text: str
    syllabic: str          # single | begin | middle | end
    italic: bool = False


@dataclass(eq=False)
class Event:
    voice: str
    idx: int               # position in the voice's event list
    onset: F               # semiminims from the start of the piece
    dur: F
    rest: bool
    bar: int               # digits of the measure number (v1 -> 1)
    measure: str           # the measure number as written in the MusicXML
    pos: F                 # position in the measure, semiminims
    bar_len: F             # length of the measure, semiminims
    sign: str = "cut"      # mensuration in force: cut | C | none | free
    step: str | None = None
    octave: int | None = None
    alter: int = 0
    lyrics: dict = field(default_factory=dict)     # verse -> Lyric
    divided: bool = False  # continuation of a dashed tie (a note divided for text, 10.13)
    after_break: bool = False   # first event after a section break or a second ending
    src: tuple | None = None    # (file, line, column) in the LilyPond source
    m21: object = None          # the music21 Note built by layers.m21

    def __repr__(self):
        what = "r" if self.rest else self.name
        return f"<{self.voice}[{self.idx}] {what} {self.dur} @{self.measure}+{self.pos}>"

    @property
    def end(self) -> F:
        return self.onset + self.dur

    @property
    def name(self) -> str:
        """Step, alteration and octave, as music21 spells it (B-3, F#4)."""
        if self.rest:
            return "rest"
        acc = {-2: "--", -1: "-", 0: "", 1: "#", 2: "##"}[self.alter]
        return f"{self.step}{acc}{self.octave}"

    @property
    def legacy_p(self) -> str | None:
        """Pitch as the old audit kept it: step and octave, no alteration."""
        return None if self.rest else f"{self.step}{self.octave}"

    @cached_property
    def diatonic(self) -> int | None:
        """Diatonic step number (C4 = 28), for generic intervals."""
        return None if self.rest else self.octave * 7 + STEPS.index(self.step)

    @cached_property
    def midi(self) -> int | None:
        return None if self.rest else 12 * (self.octave + 1) + SEMITONES[self.step] + self.alter

    @property
    def where(self) -> str:
        """Bar and minim within the bar, 1-based: '16.3' is the third minim of bar 16."""
        return f"{self.measure}.{int(self.pos // 2) + 1}"


@dataclass
class Score:
    slug: str
    path: str
    title: str = ""
    voices: dict = field(default_factory=dict)     # name -> [Event]
    config: dict = field(default_factory=dict)     # this edition's entry in editions.yaml
    lang: str = "la"

    @property
    def parts(self) -> list[str]:
        """The polyphonic voices: everything except a chant part."""
        return [v for v in self.voices
                if "chant" not in v.lower() and "versus" not in v.lower()]

    def notes(self, voice: str) -> list[Event]:
        return [e for e in self.voices[voice] if not e.rest]

    def verses(self, voice: str) -> list[str]:
        return sorted({k for e in self.voices[voice] for k in e.lyrics}, key=int)
