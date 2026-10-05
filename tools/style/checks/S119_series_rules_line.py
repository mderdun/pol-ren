import re

from ..findings import Hit
from ..sources import section_span


def check(doc):
    if "\\maketitlepage" not in doc.code and "\\section" not in doc.code:
        return
    span = section_span(doc, r"^editorial method$")
    if span is None:
        if re.search(r"\\maketitlepage", doc.code):
            yield Hit(key="no-method", offset=0, line=1,
                      values={"what": "no Editorial method section (principles 13: Critical edition paratext)"})
        return
    body = doc.code[span[0]:span[1]]
    first = body.lstrip()
    if not first.startswith("\\seriesrules"):
        yield Hit(key="seriesrules", offset=max(0, span[0] - 1),
                  values={"what": "the Editorial method section does not open with \\seriesrules (principles 13.4)"})
