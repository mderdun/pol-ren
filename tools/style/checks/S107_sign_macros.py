import re

from ..findings import Hit

RAW = [
    (r"\\tieDashed\b|Tie\.dash-definition|\\tieDotted\b", "dashed tie", "\\divTie"),
    (r"LyricText\.font-shape", "italic lyrics", "\\rep or \\edText"),
    (r"suggestAccidentals", "suggested accidental", "\\fi"),
    (r"⌜|⌝", "corner bracket", "\\colStart, \\colEnd or \\colNote"),
    (r"\"\[c\.f\.\]\"", "[c.f.] markup", "\\cf or \\cfStart"),
    (r"bracketify-stencil|pr-bracket-head", "bracketed notehead", "\\sup"),
    (r"(?:\\tweak|\\override)\s+(?:NoteHead\.)?font-size\s+#-|NoteHead\.font-size", "small notehead", "\\ed or \\sugg"),
    (r"accidentals\.(?:leftparen|rightparen|leftbracket|rightbracket)|\\cautionary\b", "bracketed accidental",
     "\\optFlat, \\optSharp, \\optNatural (or the house cautionary)"),
]


def check(doc):
    code = doc.code
    for pat, raw, use in RAW:
        for m in re.finditer(pat, code):
            yield Hit(key=raw, offset=m.start(), values={"raw": raw, "use": use})
    for m in re.finditer(r"\\parenthesize\b", code):
        # round brackets round a note are the suggestion sign: only with \sugg
        before = code[max(0, m.start() - 200):m.start()]
        if "\\sugg" not in before:
            yield Hit(key="parenthesize", offset=m.start(), values={"raw": "\\parenthesize", "use": "\\sugg"})
