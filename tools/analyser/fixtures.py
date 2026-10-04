"""Compact notation for rule examples and layer tests (no LilyPond needed).

    notes: "f2 g1 a2 r2 c'4"     pitch, octave marks, duration in semiminims
    text:  "Do- mi- nus _ _"     one token per note (rests take none)

Pitches: a-g with is/es (fis, bes), ' and , for octaves; plain c is C4 (middle
C), c' is C5, c, is C3. r is a rest. Durations in semiminims: 1 semiminim, 2
minim, 4 semibreve, 8 breve; a trailing . multiplies by 3/2; fractions such
as 1/2 (a fusa) are allowed. Text: a token ending in - continues the word, _
is a note without a new syllable. Bars are breves (8) from offset 0, unless
`offset` (semiminims) moves the first note.

A multi-voice fixture is {voices: {Cantus: {notes, text}, Tenor: {...}}} with
optional sign (cut | C), lang (la | pl) and config.
"""
from __future__ import annotations

import re
from fractions import Fraction as F

from .model import Event, Lyric, Score

TOKEN = re.compile(r"^([a-gr])((?:is|es|s)?)([',]*)(\d+(?:/\d+)?)(\.?)$")


def parse_notes(spec: str):
    out = []
    for tok in spec.split():
        m = TOKEN.match(tok)
        if not m:
            raise ValueError(f"bad note token {tok!r}")
        letter, acc, octs, dur, dot = m.groups()
        d = F(dur) * (F(3, 2) if dot else 1)
        if letter == "r":
            out.append((None, 0, 0, d))
            continue
        alter = {"": 0, "is": 1, "es": -1, "s": -1}[acc]
        octave = 4 + octs.count("'") - octs.count(",")
        out.append((letter.upper(), alter, octave, d))
    return out


def parse_text(spec: str, n_notes: int):
    toks = spec.split() if spec else []
    if len(toks) != n_notes:
        raise ValueError(f"{len(toks)} text tokens for {n_notes} notes: {spec!r}")
    out, in_word = [], False
    for tok in toks:
        if tok == "_":
            out.append(None)
            continue
        cont = tok.endswith("-")
        txt = tok[:-1] if cont else tok
        if cont:
            syl = "middle" if in_word else "begin"
        else:
            syl = "end" if in_word else "single"
        in_word = cont
        out.append(Lyric(text=txt, syllabic=syl))
    return out


def voice_events(name: str, notes: str, text: str = "", *, sign="cut", offset=F(0), bar_len=F(8),
                 verses: dict | None = None) -> list[Event]:
    parsed = parse_notes(notes)
    n_notes = sum(1 for p in parsed if p[0] is not None)
    texts = {"1": parse_text(text, n_notes)} if text else {}
    for v, t in (verses or {}).items():
        texts[str(v)] = parse_text(t, n_notes)
    evs, t, k = [], F(offset), 0
    for step, alter, octave, d in parsed:
        bar = int(t // bar_len) + 1
        e = Event(voice=name, idx=len(evs), onset=t, dur=d, rest=step is None, bar=bar,
                  measure=str(bar), pos=t - (bar - 1) * bar_len, bar_len=bar_len, sign=sign,
                  step=step, octave=octave if step else None, alter=alter)
        if step is not None:
            for v, lst in texts.items():
                if lst[k] is not None:
                    e.lyrics[v] = lst[k]
            k += 1
        evs.append(e)
        t += d
    return evs


def build(spec: dict) -> Score:
    sign = spec.get("sign", "cut")
    lang = spec.get("lang", "la")
    score = Score(slug=spec.get("slug", "fixture"), path="<fixture>", title="fixture",
                  config=spec.get("config", {}), lang=lang)
    voices = spec.get("voices") or {spec.get("voice", "Cantus"): spec}
    for name, v in voices.items():
        score.voices[name] = voice_events(name, v["notes"], v.get("text", ""), sign=sign,
                                          offset=F(v.get("offset", 0)), verses=v.get("verses"))
    return score
