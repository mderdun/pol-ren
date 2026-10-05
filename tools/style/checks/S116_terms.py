import re

from ..findings import Hit

TERMS = [
    (r"\bcopy[ -]text\b", "'base text'"),
    (r"\b(?:whole|half|quarter|eighth|sixteenth)[ -]notes?\b", "semibreve, minim, semiminim, fusa"),
    (r"\btext[ -]setting\b", "'underlay'"),
    (r"\blyrics\b", "'underlay' (or 'text', 'words')"),
    (r"\boriginal pitch\b", "'written pitch'"),
    (r"\bresolution\b", "'cadence' or 'clausula'"),
]
HEAD_TERMS = [(r"\b(?:commentary|apparatus)\b", "'Critical notes'")]


def check(doc):
    prose = doc.prose
    for pat, use in TERMS:
        for m in re.finditer(pat, prose, re.I):
            # a gloss for singers straight after the house term: 'semibreve (whole note)'
            if re.search(r"(semibreve|minim|semiminim|fusa|breve|underlay)\s*(\(|=)\s*$",
                         prose[max(0, m.start() - 20):m.start()]):
                continue
            if m.group(0).lower() == "resolution" and re.search(r"suspen|dissonan", prose[max(0, m.start() - 120):m.end() + 120]):
                continue          # the resolution of a suspension is the right word
            yield Hit(key=m.group(0).lower(), offset=m.start(), values={"found": m.group(0), "use": use})
    for m in re.finditer(r"\\(?:section\*?|opensection|subsection\*?)\s*\{([^}]*)\}|^#+ (.*)$", doc.code, re.M):
        title = m.group(1) or m.group(2) or ""
        for pat, use in HEAD_TERMS:
            mm = re.search(pat, title, re.I)
            if mm:
                yield Hit(key=f"heading:{mm.group(0).lower()}", offset=m.start(), values={"found": title, "use": use})
