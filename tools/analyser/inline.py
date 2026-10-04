"""Inline acceptance: a comment in the LilyPond source beside the note.

    cantusNotes = { ... c''1 b'1  % underlay: ok U301 -- the print's own reading, 10.12
    % underlay: ok U206 bar 34 'consolari' -- the long con- of the print
    tenorNotes = { ... }

A comment applies to the findings whose note the source map puts on its line
(a trailing comment), or on the first code line after a block of comment lines
(a comment above). Where one line holds a whole voice, narrow it with `bar N`
(the finding's bar) and/or a quoted word ('consolari', as the lexicon spells
it, or the syllable as printed). Several rules may be listed: `ok U206 U302`.
The reason after `--` is required; a comment without one is ignored and
reported by `problems`.

The baseline file stays the place for long-lived decisions; an inline comment
keeps the decision next to the music it concerns (survey §3.6).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .ingest import ROOT

PAT = re.compile(r"%+\s*underlay:\s*ok\s+(?P<body>.*)$")
RULE = re.compile(r"^U\d{3}$")


@dataclass
class Accept:
    file: str
    line: int               # the line the comment applies to
    at: int                 # the line the comment is on
    rules: tuple
    bar: int | None
    word: str | None
    reason: str

    def matches(self, f) -> bool:
        if f.rule not in self.rules:
            return False
        if self.bar is not None and f.bar != self.bar:
            return False
        if self.word is not None and self.word not in (f.word, f.text.lower().strip(",.:;!?")):
            return False
        return True


def _parse_body(body: str):
    if "--" not in body:
        return None
    head, reason = body.split("--", 1)
    reason = reason.strip()
    if not reason:
        return None
    rules, bar, word = [], None, None
    toks = re.findall(r"'[^']*'|\S+", head)
    i = 0
    while i < len(toks):
        t = toks[i]
        if RULE.match(t):
            rules.append(t)
        elif t == "bar" and i + 1 < len(toks) and toks[i + 1].isdigit():
            bar = int(toks[i + 1])
            i += 1
        elif t.startswith("'") and t.endswith("'"):
            word = t[1:-1].lower()
        i += 1
    if not rules:
        return None
    return tuple(rules), bar, word, reason


@lru_cache(maxsize=None)
def scan(file: str) -> tuple:
    """(accepts, problems) for one source file, path relative to the repo root."""
    path = ROOT / file
    if not path.exists():
        return (), ()
    lines = path.read_text(encoding="utf-8").split("\n")
    accepts, problems, pending = [], [], []
    for n, text in enumerate(lines, start=1):
        m = PAT.search(text)
        code = text.split("%", 1)[0].strip()
        if m:
            parsed = _parse_body(m.group("body"))
            if parsed is None:
                problems.append(f"{file}:{n}: underlay comment needs a rule and a reason after --")
            else:
                rules, bar, word, reason = parsed
                if code:
                    accepts.append(Accept(file, n, n, rules, bar, word, reason))
                else:
                    pending.append((n, rules, bar, word, reason))
                    continue
        if code:
            for at, rules, bar, word, reason in pending:
                accepts.append(Accept(file, n, at, rules, bar, word, reason))
            pending = []
        elif not text.strip():
            pending = []        # a blank line ends a comment block with no code after it
    return tuple(accepts), tuple(problems)


def find(f) -> Accept | None:
    if not f.src:
        return None
    file, line = f.src.rsplit(":", 1)
    accepts, _ = scan(file)
    for a in accepts:
        if a.line == int(line) and a.matches(f):
            return a
    return None


def problems(results) -> list[str]:
    files = {f.src.rsplit(":", 1)[0] for r in results for f in r.findings if f.src}
    out = []
    for file in sorted(files):
        out.extend(scan(file)[1])
    return out
