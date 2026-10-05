"""What a rule check sees, and what it returns.

A syllable-scope check sees one syllable of one line under one candidate
underlay: the syllable starts on event `start`, and the next syllable of the
line starts on `next_start` (None if it is the last). Its notes run from start
to `end` (exclusive). Under the old audit's semantics (legacy) a syllable runs
up to the next syllable whatever lies between; otherwise it stops at a rest or
a section break, and notes after a rest without a syllable belong to nobody
(that is a 10.2 break).

Checks only read; they never change the underlay.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..model import Event
from ..text import Line, Syl, Word


@dataclass
class Hit:
    rule: str
    ev: int                 # event the finding points at
    syl: int                # syllable it belongs to
    values: dict = field(default_factory=dict)
    amount: float = 1.0     # cost units before weight and gates
    hard: bool = False      # a firm-rule violation: the candidate is not legal


class SegCtx:
    def __init__(self, line: Line, i: int, start: int, next_start: int | None, end: int,
                 legacy: bool = False, analysis=None):
        self.line = line
        self.i = i
        self.start = start
        self.next_start = next_start
        self.end = end
        self.legacy = legacy
        self.analysis = analysis

    # the text
    @property
    def syl(self) -> Syl:
        return self.line.syls[self.i]

    @property
    def word(self) -> Word:
        return self.line.word_of(self.i)

    @property
    def next_syl(self) -> Syl | None:
        return self.line.syls[self.i + 1] if self.i + 1 < len(self.line.syls) else None

    @property
    def prev_syl(self) -> Syl | None:
        return self.line.syls[self.i - 1] if self.i > 0 else None

    # the notes
    @property
    def events(self) -> list[Event]:
        return self.line.events

    @property
    def first(self) -> Event:
        return self.events[self.start]

    @property
    def notes(self) -> list[Event]:
        return [e for e in self.events[self.start:self.end] if not e.rest]

    @property
    def prev(self) -> Event | None:
        """The event before the syllable's first note (a note or a rest);
        None at the start, or after a section break."""
        if self.start == 0:
            return None
        if not self.legacy and self.first.after_break:
            return None
        return self.events[self.start - 1]

    @property
    def after(self) -> Event | None:
        """The event straight after the first note."""
        j = self.start + 1
        if j >= len(self.events):
            return None
        e = self.events[j]
        if not self.legacy and e.after_break:
            return None
        return e

    @property
    def next_note(self) -> Event | None:
        """The first note of the next syllable."""
        return self.events[self.next_start] if self.next_start is not None else None

    @property
    def time(self):
        """How long the syllable sounds, in semiminims (its notes' values)."""
        return sum((e.dur for e in self.notes), 0)

    def has_syl(self, j: int) -> bool:
        """Does event j start a syllable under this candidate? Defined for
        start <= j <= next_start."""
        return j == self.start or j == self.next_start

    def hit(self, rule: str, ev: int | None = None, amount: float = 1.0, hard: bool = False,
            syl: int | None = None, **values) -> Hit:
        e = self.events[self.start if ev is None else ev]
        base = dict(txt=self.syl.text, word=self.word.norm, bar=e.bar, where=e.where)
        base.update(values)
        return Hit(rule=rule, ev=e.idx, syl=self.i if syl is None else syl, values=base,
                   amount=amount, hard=hard)


@dataclass
class LineCtx:
    line: Line
    starts: list[int]
    legacy: bool = False
    analysis: object = None
