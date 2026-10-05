"""tools/lint.sh in Python, with line numbers and annotations. lint.sh
still runs before every build; this is the same rule in CI."""
import re

from ..findings import Hit

PAT = re.compile(r"\\(v|h)space|\\fontsize|\\setlength|\\geometry|\\linespread|"
                 r"\\(small|large|Large|footnotesize|normalsize)\b|\\color|\\textcolor|staffsize=|\\override|"
                 r"\\paper|set-global-staff-size|\\layout *\{ *[^} ]|#\(set-")
ENG = re.compile(r"\\fontsize|\\color|\\textcolor|staffsize=|set-global-staff-size|font-(name|family|size)|color")


def check(doc):
    eng = doc.rel.endswith("/music/engraving.ily")
    pat = ENG if eng else PAT
    for m in pat.finditer(doc.code):
        line_end = doc.code.find("\n", m.start())
        line = doc.code[doc.code.rfind("\n", 0, m.start()) + 1:line_end if line_end >= 0 else None]
        if "layout { $(pr-layout) }" in line:
            continue
        yield Hit(key=m.group(0).strip(), offset=m.start(), values={"cmd": m.group(0).strip()})
