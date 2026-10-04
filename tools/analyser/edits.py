"""Text edits as alternatives (principles 10.13; 10.9 for repetition).

The search in underlay.py moves syllables only. Principles 10.13 also lets an
editorially texted lower voice skip words to keep long notes, as long as its
text makes sense alone, and 10.9 lets a long free melisma be replaced by
repeating the words. This module builds the edited lines and searches them the
same way, so that an alternative may say "drop 'est'" or "repeat 'Rama'".

Every edit is flagged as such and carries a cost (settings.yaml: text_edits),
so a reading that keeps the text wins whenever it is about as good.

Which edits are offered:
  drop     a word in the finding's neighbourhood (the finding's word and the
           words either side), in a voice below the top one, whose loss
           leaves the sense: a conjunction or auxiliary on the droppable list
           (et, est ...), or one of a word sung twice in a row
  repeat   the finding's word, sung again straight after itself, where the
           finding is a long melisma (run rules U205, U206, U302)
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .rules import settings
from .text import Line, Word

MELISMA_RULES = {"U205", "U206", "U302"}


@dataclass
class Edit:
    kind: str                   # drop | repeat
    word: int                   # index of the word in the original line
    line: Line                  # the edited line
    to_orig: dict               # edited syllable index -> original syllable index (None: a repeated copy)
    from_orig: dict             # original syllable index -> edited index (absent: dropped)
    first_new: int              # edited index of the first syllable the edit concerns
    n_new: int                  # how many syllables it inserts (repeat) or 0
    cost: float
    label: str


def edit_costs() -> dict:
    return settings().get("text_edits") or {}


def eligible(analysis, line: Line) -> bool:
    if not edit_costs().get("enabled", True):
        return False
    if analysis.score.config.get("text_edits") is False:
        return False
    parts = analysis.score.parts
    return bool(parts) and line.voice != parts[0]


def _sense_survives(line: Line, w: Word) -> bool:
    """A conjunction or auxiliary the clause can do without (settings:
    text_edits.droppable), or a word sung twice in a row ('plebis, plebis'):
    dropping one statement leaves the other whole. A content word inside a
    repeated clause is not droppable: that statement would no longer make
    sense alone."""
    if w.norm in set(edit_costs().get("droppable") or ()):
        return True
    for d in (-1, 1):
        j = w.i + d
        if 0 <= j < len(line.words) and line.words[j].norm == w.norm and line.words[j].syls:
            return True
    return False


def _rebuild(line: Line, syls: list, words_syls: dict, extra_word: Word | None) -> Line:
    words = []
    for w in line.words:
        words.append(Word(i=w.i, syls=words_syls.get(w.i, []), text=w.text, norm=w.norm, entry=w.entry))
    if extra_word is not None:
        words.append(extra_word)
    return Line(voice=line.voice, verse=line.verse, events=line.events, syls=syls, words=words,
                lang=line.lang)


def drop(line: Line, wi: int) -> Edit:
    w = line.words[wi]
    gone = set(w.syls)
    syls, to_orig, from_orig, words_syls = [], {}, {}, {}
    first_new = None
    for s in line.syls:
        if s.i in gone:
            if first_new is None:
                first_new = len(syls)
            continue
        n = len(syls)
        syls.append(replace(s, i=n))
        to_orig[n], from_orig[s.i] = s.i, n
        words_syls.setdefault(s.word, []).append(n)
    c = edit_costs()
    cost = float(c.get("drop_light", 1.0) if w.norm in set(c.get("droppable") or ()) else c.get("drop", 1.5))
    return Edit(kind="drop", word=wi, line=_rebuild(line, syls, words_syls, None), to_orig=to_orig,
                from_orig=from_orig, first_new=first_new if first_new is not None else len(syls),
                n_new=0, cost=cost, label=f"drop '{w.text.rstrip(',.:;!?')}' at {line.events[line.syls[w.syls[0]].ev].where} (10.13)")


def repeat(line: Line, wi: int) -> Edit:
    w = line.words[wi]
    new_i = len(line.words)
    syls, to_orig, from_orig, words_syls = [], {}, {}, {}
    first_new = None
    copy_syls = []
    for s in line.syls:
        n = len(syls)
        syls.append(replace(s, i=n))
        to_orig[n], from_orig[s.i] = s.i, n
        words_syls.setdefault(s.word, []).append(n)
        if s.i == w.syls[-1]:
            first_new = len(syls)
            for k, si in enumerate(w.syls):
                src = line.syls[si]
                m = len(syls)
                # a copy starts, for now, where the word's last syllable does;
                # the search places it
                syls.append(replace(src, i=m, word=new_i, k=k, ev=s.ev))
                to_orig[m] = None
                copy_syls.append(m)
    extra = Word(i=new_i, syls=copy_syls, text=w.text, norm=w.norm, entry=w.entry)
    return Edit(kind="repeat", word=wi, line=_rebuild(line, syls, words_syls, extra), to_orig=to_orig,
                from_orig=from_orig, first_new=first_new, n_new=len(w.syls),
                cost=float(edit_costs().get("repeat", 1.0)),
                label=f"repeat '{w.text.rstrip(',.:;!?')}' (10.9, 10.13)")


def candidates(analysis, line: Line, sp, hit) -> list[Edit]:
    """The edits worth searching for a finding in span sp."""
    if not eligible(analysis, line) or hit.syl >= len(line.syls):
        return []
    inside = set(sp.syls)
    out = []
    wi = line.syls[hit.syl].word
    for d in (-1, 0, 1):
        j = wi + d
        if not (0 <= j < len(line.words)):
            continue
        w = line.words[j]
        if not w.syls or not set(w.syls) <= inside or len(w.syls) >= len(sp.syls):
            continue
        if _sense_survives(line, w):
            out.append(drop(line, j))
    if hit.rule in MELISMA_RULES:
        w = line.words[wi]
        if w.syls and set(w.syls) <= inside:
            out.append(repeat(line, wi))
    return out
