import re

from ..findings import Hit

SIGNS = [
    (r"\\fi\b", "\\fi", "editorial accidental"),
    (r"\\opt(?:Flat|Sharp|Natural)\b", "\\optFlat/Sharp/Natural", "optional accidental"),
    (r"\\ed\b", "\\ed", "note supplied"),
    (r"\\sup\b", "\\sup", "note illegible, supplied"),
    (r"\\sugg\b", "\\sugg", "editorial suggestion"),
    (r"\\divTie\b", "\\divTie", "source note divided for text"),
    (r"\\col(?:Start|End|Note)\b", "\\colStart/End/Note", "coloration"),
    (r"\\cf(?:Start)?\b", "\\cf", "cantus firmus"),
    (r"\\rep\b", "\\rep", "italic syllable"),
    (r"\\edText\b", "\\edText", "italic underlay"),
    (r"⟨", "⟨ ⟩", "text written out from ij"),
    (r"\\\[|\\\]|\\startLigature\b", "ligature bracket", "ligature"),
    (r"\\mensSign\b|\\prMens\b", "\\mensSign", "mensuration sign"),
]


def check(doc):
    code = doc.code
    for pat, sign, meaning in SIGNS:
        ms = list(re.finditer(pat, code))
        if ms:
            n = len(ms)
            yield Hit(key=sign, offset=ms[0].start(), values={"sign": sign, "meaning": meaning, "n": n})
