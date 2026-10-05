import re

from ..findings import Hit

PAT = re.compile(r"\b(TODO|FIXME|TBD|XXX)\b|\[(?:check|verify|ref|citation needed|sic\?|\?+)\]|\?\?+|"
                 r"\\(?:todo|fixme|marginpar)\b", re.I)


def check(doc):
    for m in PAT.finditer(doc.code):
        t = m.group(0)
        if t in ("XXX",) and re.search(r"\b[MDCLXVI]+XXX", doc.code[max(0, m.start() - 4):m.end()]):
            continue      # a roman numeral
        yield Hit(key=t, offset=m.start(), values={"found": t})
