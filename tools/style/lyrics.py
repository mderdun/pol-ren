"""Lyrics in LilyPond sources, and Latin syllable division.

`words(code)` reads every \\lyricmode { ... } (and \\lyricsto ... { ... })
block and returns its words as lists of syllables, with the offset of each
syllable, so that a finding points at the source line.

Latin division (decision 2 of 4 Oct 2026; Caldwell 42; Gould 445-446): one
system for the series, the carry-over division singers use: a consonant
group that can begin a Latin word goes with the following syllable
(o-mnis, San-cto, co-gno, Chri-stus, pa-tris), and a compound divides at the
prefix (ex-spe-cta-ti-o, ab-sti-ne-re).
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .sources import match_brace

VOWELS = set("aeiouyæœáéíóúàèìòùâêîôûäëïöüāēīōū")
# consonant groups that can begin a Latin syllable under carry-over
ONSETS = {
    "bl", "br", "cl", "cr", "dr", "fl", "fr", "gl", "gr", "pl", "pr", "tr", "vr",
    "ch", "chr", "chl", "ph", "phr", "phl", "th", "thr", "rh", "gn", "mn", "ct", "pt", "ps", "pn", "tm",
    "sc", "scr", "sp", "spr", "spl", "st", "str", "squ", "sch", "sph", "sm", "sq", "qu", "gu",
}
PREFIXES = ("abs", "ab", "ad", "circum", "con", "com", "dis", "ex", "in", "inter", "ob", "per", "post", "prae",
            "pro", "red", "sub", "super", "trans", "sus")


@dataclass
class Syl:
    text: str
    offset: int


def lyric_blocks(code: str):
    """(start, end) of the inside of every lyricmode / lyricsto block."""
    for m in re.finditer(r"\\(?:lyricmode|lyricsto\s+\"?[\w-]+\"?|addlyrics)\s*\{", code):
        a = m.end() - 1
        b = match_brace(code, a)
        yield a + 1, b


TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|\S+')


def words(code: str) -> list[list[Syl]]:
    out = []
    for a, b in lyric_blocks(code):
        cur: list[Syl] = []
        join = False
        skip_next = 0
        for m in TOKEN.finditer(code, a, b):
            t = m.group(0)
            if skip_next:
                skip_next -= 1
                continue
            if t == "--":
                join = True
                continue
            if t in ("__", "_", "{", "}", "|") or t.startswith("%"):
                continue
            if t.startswith("\\"):
                if t in ("\\set", "\\override", "\\once"):
                    skip_next = 0
                if t in ("\\set", "\\override"):
                    skip_next = 3        # Context.prop = value
                continue
            if t.startswith("#") or re.fullmatch(r"\d+\.?|=", t):
                continue
            text = t[1:-1] if t.startswith('"') and t.endswith('"') else t
            syl = Syl(text=text, offset=m.start())
            if join and cur:
                cur.append(syl)
            else:
                if cur:
                    out.append(cur)
                cur = [syl]
            join = False
        if cur:
            out.append(cur)
    return out


def letters(s: str) -> str:
    s = s.replace("~", "").lower()
    return "".join(c for c in s if c.isalpha())


def _lead_cons(s: str) -> str:
    i = 0
    while i < len(s) and (s[i] not in VOWELS or (s[i] == "u" and i > 0 and s[i - 1] in "qg"
                                                 and i + 1 < len(s) and s[i + 1] in VOWELS)):
        i += 1
    return s[:i]


def _trail_cons(s: str) -> str:
    i = len(s)
    while i > 0 and s[i - 1] not in VOWELS:
        i -= 1
    return s[i:]


def onset_ok(c: str) -> bool:
    return len(c) <= 1 or c in ONSETS


def division_problem(word: list[str]) -> list[tuple[int, str]]:
    """For a word given as syllables, the splits that break carry-over
    division: (index of the syllable after the split, the expected
    division of the two syllables)."""
    syls = [letters(s) for s in word]
    out = []
    for i in range(1, len(syls)):
        left, right = syls[i - 1], syls[i]
        if not left or not right:
            continue
        L, R = _trail_cons(left), _lead_cons(right)
        if L == left or R == right:          # no vowel on one side: elision or a stray token
            continue
        cluster = L + R
        if "x" in cluster or "j" in cluster or "h" == cluster or not cluster:
            continue
        if L and "".join(syls[:i]) in PREFIXES:
            continue                          # a compound divides at its prefix
        best = ""
        for k in range(len(cluster)):
            if onset_ok(cluster[k:]):
                best = cluster[k:]
                break
        if R == best:
            continue
        # i, u and v as consonants: "Iu-dae", "e-ius" are fine either way
        if set(cluster) <= set("iuv"):
            continue
        stay = cluster[:len(cluster) - len(best)]
        exp = left[:len(left) - len(L)] + stay + "-" + best + right[len(R):]
        out.append((i, exp))
    return out
