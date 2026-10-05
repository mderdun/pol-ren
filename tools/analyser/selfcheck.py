"""Export self-check (survey §3.5): before judging an underlay, check that the
MusicXML carries it. For each voice and verse, count the syllables

  source    the \\lyricmode blocks in editions/<slug>/music/voices.ily
  musicxml  the <lyric> elements in the MusicXML (read independently by music21)
  model     what the analyser ingests (ties merged, divided notes kept)
  legacy    what the old audit ingested (every tie merged)

and report every disagreement with where it happens. A disagreement is a
problem to look at, never a crash.

The October 2026 review recorded an export bug: the Plaude Tenor loses
syllables of confidencium inside the repeat. The counts show the MusicXML
carries all 53 Tenor syllables; it is the old audit's tie merging that dropped
three of them (bars 14 and 18, on notes divided with a dashed tie, 10.13).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from music21 import converter

from .ingest import ROOT, parse, slug_of

BLOCK = re.compile(r"^(\w+)\s*=\s*\\lyricmode\s*\{", re.M)


@dataclass
class Check:
    voice: str
    verse: str
    source: int | None
    musicxml: int
    model: int
    legacy: int
    notes: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        vals = {self.musicxml, self.model} | ({self.source} if self.source is not None else set())
        return len(vals) == 1


def _block_body(text: str, start: int) -> str:
    depth, i = 1, start
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start:i - 1]


def count_lyricmode(body: str) -> int:
    body = re.sub(r"%[^\n]*", "", body)
    toks = re.findall(r'"[^"]*"|\S+', body)
    n, skip = 0, 0
    for t in toks:
        if skip:
            skip -= 1
            continue
        if t == "\\set":
            skip = 3          # \set stanza = "1."
            continue
        if t in ("--", "__", "_", "{", "}", "<<", ">>") or t.startswith("\\") or t.startswith("#"):
            continue
        n += 1
    return n


def source_counts(slug: str, voices: list[str]) -> dict:
    """(voice, verse) -> syllables in voices.ily, or {} if there is none."""
    path = ROOT / "editions" / slug / "music" / "voices.ily"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    out: dict = {}
    seen: dict = {}
    for m in BLOCK.finditer(text):
        name = m.group(1)
        voice = next((v for v in voices if name.lower().startswith(v.lower())), None)
        if voice is None:
            continue
        # the export numbers a voice's Lyrics contexts in order (musicxml-events.ily),
        # so the nth block for a voice is its verse n (Nunc scio: antiphon 1, doxology 2)
        seen[voice] = seen.get(voice, 0) + 1
        verse = str(seen[voice])
        out[(voice, verse)] = out.get((voice, verse), 0) + count_lyricmode(_block_body(text, m.end()))
    return out


def music21_counts(path: Path) -> dict:
    s = converter.parse(str(path), forceSource=True)
    out: dict = {}
    for p in s.parts:
        name = (p.partName or "").strip("[]")   # editorial names print as [Cantus] (principles 6.1)
        for n in p.recurse().notes:
            for ly in n.lyrics:
                if ly.text:
                    key = (name, str(ly.number))
                    out[key] = out.get(key, 0) + 1
    return out


def check(path: str | Path) -> list[Check]:
    path = Path(path)
    slug = slug_of(path)
    new, old = parse(path), parse(path, legacy=True)
    src = source_counts(slug, new.parts)
    mx = music21_counts(path)
    out = []
    for v in new.parts:
        for verse in new.verses(v):
            m = sum(1 for e in new.voices[v] if verse in e.lyrics)
            lg = sum(1 for e in old.voices[v] if verse in e.lyrics)
            c = Check(voice=v, verse=verse, source=src.get((v, verse)), musicxml=mx.get((v, verse), 0),
                      model=m, legacy=lg)
            if lg != m:
                lost = [e for e in new.voices[v] if e.divided and verse in e.lyrics]
                c.notes.append("the old audit's tie merging drops %d syllable(s) on divided notes: %s"
                               % (m - lg, ", ".join(f"'{e.lyrics[verse].text}' bar {e.measure}" for e in lost)))
            if c.source is not None and c.source != c.musicxml:
                c.notes.append(f"voices.ily has {c.source} syllables, the MusicXML {c.musicxml}: the export loses or adds text")
            if c.musicxml != m:
                c.notes.append(f"the MusicXML has {c.musicxml} syllables, the analyser read {m}")
            out.append(c)
    return out


def report(checks: list[Check]) -> list[str]:
    lines = []
    for c in checks:
        status = "ok" if c.ok and not c.notes else "CHECK"
        lines.append(f"{status:5} {c.voice:9} v{c.verse}  source {c.source if c.source is not None else '-':>3}"
                     f"  musicxml {c.musicxml:>3}  model {c.model:>3}  old audit {c.legacy:>3}")
        for n in c.notes:
            lines.append(f"      {n}")
    return lines
