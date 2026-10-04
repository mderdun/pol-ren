import re

from ..findings import Hit

PAT = re.compile(r"\\textbf\b|\\bfseries\b|\\bf\b|\\mathbf\b|\\boldmath\b|\\fontseries\{b[a-z]*\}|"
                 r"\\bold\b|font-series\s*=?\s*#'bold|font-series\s+\.\s+bold|#:bold\b")


def check(doc):
    for m in PAT.finditer(doc.code):
        yield Hit(key=m.group(0), offset=m.start(), values={"cmd": m.group(0)})
