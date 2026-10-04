"""Text layer: lines of syllables per voice and verse, words, and the lexicon
(stress and word class) from lexicon/{la,pl}.yaml.

A Line is one voice's text in one verse: the syllables in order, each with the
event it starts on, grouped into words by MusicXML `syllabic`.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from .model import Event, Score

HERE = Path(__file__).resolve().parent
PUNCT = ",.:;!?"

# The old audit's tables (tools/underlay_audit.py), kept for --legacy and for
# the equivalence test. The lexicons supersede them.
LEGACY_LIGHT = set('et in de ad a ab cum per pro sub ex e nec sed ut qui quae quod te me se nos vos '
                   'i w z na do o od u ku że by się'.split())
LEGACY_STRESS = {
    'scio': 0, 'vere': 0, 'quia': 0, 'misit': 0, 'dominus': 0, 'angelum': 0, 'suum': 0, 'eripuit': 1,
    'manu': 0, 'herodis': 1, 'omni': 0, 'exspectatione': 4, 'plebis': 0, 'iudaeorum': 2, 'gloria': 0,
    'patri': 0, 'filio': 0, 'spiritui': 0, 'sancto': 0, 'sicut': 0, 'erat': 0, 'principio': 1,
    'semper': 0, 'saecula': 0, 'saeculorum': 2, 'amen': 0, 'rama': 0, 'audita': 1, 'ploratus': 1,
    'ululatus': 2, 'rachel': 0, 'plorans': 0, 'filios': 0, 'suos': 0, 'noluit': 0, 'consolari': 2,
    'plaude': 0, 'euge': 0, 'theotocos': 2, 'regina': 1, 'virginum': 0, 'salus': 0, 'hominum': 0,
    'confidencium': 2, 'laudantes': 1, 'inspice': 0, 'miseros': 0, 'despice': 0, 'misericordie': 3,
    'oculis': 0, 'respice': 0}


@dataclass
class Entry:
    word: str
    syllables: list[str]
    stress: int | None          # 0-based index of the stressed syllable, or None
    cls: str                    # light | function | content | fragment | key
    src: str
    note: str = ""
    known: bool = True


@dataclass
class Syl:
    i: int                      # index in the line
    ev: int                     # event index it starts on
    text: str
    syllabic: str
    italic: bool
    word: int = -1              # index of its word in line.words
    k: int = 0                  # position in the word

    @property
    def punct(self) -> bool:
        return self.text[-1:] in PUNCT

    @property
    def coda(self) -> str:
        """open | sonorant | obstruent: what closes the syllable's vowel
        (`coda_class`)."""
        return coda_class(self.text)

    @property
    def short(self) -> bool:
        """A short syllable for melisma purposes (Miki, review of 4 October
        2026): its vowel is stopped by a plosive or fricative (it, et, est,
        -tus), so it cannot be sung through. An open syllable or one closed by
        a sonorant (con, in, non) can carry a run."""
        return self.coda == "obstruent"


# Syllable codas (Miki, review of 4 October 2026). The first consonant after
# the syllable's last vowel decides: a sonorant (m n l r, Polish ń ł j) can be
# sung through, a plosive or fricative stops the vowel. Polish digraphs: rz is
# a fricative (ż), sz cz ch dz are obstruents.
VOWELS = set("aeiouyąęó")
SONORANTS = set("mnlrjńł")


def _letters(text: str) -> str:
    return re.sub(r"[^a-ząćęłńóśźż]", "", strip_accents(text.lower()))


def coda_class(text: str) -> str:
    s = _letters(text)
    v = max((i for i, c in enumerate(s) if c in VOWELS), default=-1)
    if v < 0:
        return "open"
    coda = s[v + 1:]
    if not coda:
        return "open"
    if coda.startswith("rz"):
        return "obstruent"
    return "sonorant" if coda[0] in SONORANTS else "obstruent"


def onset_consonants(text: str) -> int:
    """Consonants before the syllable's first vowel, counting qu, ch, sz, cz,
    rz, dz as one sound."""
    s = _letters(text)
    for d in ("qu", "ch", "sz", "cz", "rz", "dz", "ph", "th"):
        s = s.replace(d, "C")
    n = 0
    for c in s:
        if c in VOWELS:
            break
        n += 1
    return n


def coda_consonants(text: str) -> int:
    s = _letters(text)
    for d in ("ch", "sz", "cz", "rz", "dz", "x"):
        s = s.replace(d, "CC" if d == "x" else "C")
    v = max((i for i, c in enumerate(s) if c in VOWELS), default=-1)
    return 0 if v < 0 else len(s) - v - 1


@dataclass
class Word:
    i: int
    syls: list[int]
    text: str
    norm: str
    entry: Entry

    @property
    def stress(self) -> int | None:
        return self.entry.stress

    @property
    def cls(self) -> str:
        return self.entry.cls


@dataclass
class Line:
    voice: str
    verse: str
    events: list[Event]
    syls: list[Syl] = field(default_factory=list)
    words: list[Word] = field(default_factory=list)
    lang: str = "la"

    @property
    def starts(self) -> list[int]:
        return [s.ev for s in self.syls]

    def word_of(self, s: int) -> Word:
        return self.words[self.syls[s].word]


def strip_accents(s: str) -> str:
    """Remove acute accents from Latin vowels (cognovísti), keep Polish letters."""
    out = []
    for ch in s:
        if ch in "áéíóúý":
            ch = unicodedata.normalize("NFD", ch)[0]
        out.append(ch)
    return "".join(out)


def normalise(text: str, lang: str) -> str:
    t = text.lower()
    if lang == "la":
        t = strip_accents(t)
    return re.sub(r"[^a-ząćęłńóśźż]", "", t)


def legacy_norm(text: str) -> str:
    return re.sub(r"[^a-ząćęłńóśźż]", "", text.lower())


class Lexicon:
    def __init__(self, lang: str, data: dict):
        self.lang = lang
        self.rule = data.get("rule")
        self.entries: dict[str, Entry] = {}
        for word, d in (data.get("words") or {}).items():
            parts = str(d["syl"]).split("-")
            caps = [i for i, p in enumerate(parts) if p.isupper()]
            stress = caps[0] if caps else None
            self.entries[str(word)] = Entry(word=str(word), syllables=[p.lower() for p in parts],
                                            stress=stress, cls=d.get("class", "content"),
                                            src=str(d.get("src", "")), note=d.get("note", ""))

    def lookup(self, norm: str, nsyl: int) -> Entry:
        e = self.entries.get(norm)
        if e is not None:
            return e
        # unknown: the regular rule, flagged as unknown (survey §1.12)
        stress = (nsyl - 2) if nsyl >= 2 else (0 if nsyl == 1 else None)
        return Entry(word=norm, syllables=[], stress=stress, cls="content",
                     src="fallback: penultimate rule", known=False)


@lru_cache(maxsize=None)
def lexicon(lang: str) -> Lexicon:
    path = HERE / "lexicon" / f"{lang}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    return Lexicon(lang, data)


def _caps_ok(syl: str) -> bool:
    return all(p.isupper() or p.islower() for p in syl.split("-"))


def key_word_entries(config: dict) -> list[dict]:
    """editions.yaml key_words as {word, source, confirmed}."""
    out = []
    for e in config.get("key_words") or []:
        if isinstance(e, str):
            e = {"word": e, "source": "MD"}
        src = str(e.get("source", ""))
        out.append({"word": str(e["word"]), "source": src, "confirmed": not src.lower().startswith("proposed")})
    return out


def key_words(config: dict, *, proposed: bool = False) -> list[str]:
    """The confirmed key words (with proposed=True, the proposals too)."""
    return [e["word"] for e in key_word_entries(config) if e["confirmed"] or proposed]


def build_lines(score: Score, *, legacy: bool = False) -> list[Line]:
    out = []
    lang = score.lang
    lex = lexicon(lang)
    keys = {normalise(w, lang) for w in key_words(score.config)}
    for voice in score.parts:
        evs = score.voices[voice]
        for verse in score.verses(voice):
            line = Line(voice=voice, verse=verse, events=evs, lang=lang)
            for e in evs:
                if e.rest or verse not in e.lyrics:
                    continue
                ly = e.lyrics[verse]
                line.syls.append(Syl(i=len(line.syls), ev=e.idx, text=ly.text,
                                     syllabic=ly.syllabic, italic=ly.italic))
            # words, grouped as the old audit grouped them
            groups, cur = [], []
            for s in line.syls:
                if s.syllabic in ("begin", "single") and cur:
                    groups.append(cur)
                    cur = []
                cur.append(s)
                if s.syllabic in ("end", "single"):
                    groups.append(cur)
                    cur = []
            if cur:
                groups.append(cur)
            for g in groups:
                text = "".join(s.text for s in g)
                if legacy:
                    norm = legacy_norm(text)
                    st = LEGACY_STRESS.get(norm)
                    entry = Entry(word=norm, syllables=[], stress=st,
                                  cls="light" if norm in LEGACY_LIGHT else "content", src="legacy")
                else:
                    norm = normalise(text, lang)
                    entry = lex.lookup(norm, len(g))
                    if norm in keys:
                        entry = Entry(**{**entry.__dict__, "cls": "key"})
                w = Word(i=len(line.words), syls=[s.i for s in g], text=text, norm=norm, entry=entry)
                for k, s in enumerate(g):
                    s.word, s.k = w.i, k
                line.words.append(w)
            out.append(line)
    return out


def check_lexicon(lang: str) -> list[str]:
    """Problems in a lexicon file: bad capitals, Polish stress off the penult
    without a stated exception."""
    path = HERE / "lexicon" / f"{lang}.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    probs = []
    for word, d in data["words"].items():
        syl = str(d["syl"])
        if not _caps_ok(syl):
            probs.append(f"{lang}:{word}: mixed case in a syllable ({syl})")
        parts = syl.split("-")
        caps = [i for i, p in enumerate(parts) if p.isupper()]
        if len(caps) > 1:
            probs.append(f"{lang}:{word}: more than one stressed syllable ({syl})")
        if "".join(parts).lower().replace(" ", "") != str(word):
            probs.append(f"{lang}:{word}: syllables do not spell the key ({syl})")
        if not d.get("src"):
            probs.append(f"{lang}:{word}: no source")
        if data.get("rule") == "penultimate" and len(parts) >= 2 and caps and caps[0] != len(parts) - 2 \
                and not d.get("exception"):
            probs.append(f"{lang}:{word}: stress off the penult without an exception ({syl})")
    return probs


def coverage(score: Score, lines: list[Line]) -> list[dict]:
    """Words of the edition and how the lexicon knows them."""
    seen = {}
    for line in lines:
        for w in line.words:
            r = seen.setdefault(w.norm, dict(word=w.norm, known=w.entry.known, count=0,
                                             syllables=len(w.syls), lex_syllables=len(w.entry.syllables)))
            r["count"] += 1
    return sorted(seen.values(), key=lambda r: r["word"])
