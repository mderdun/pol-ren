import re

from ..findings import Hit
from ..sources import mask_quotes


def check(doc):
    if not doc.is_tex:
        return          # the principles Markdown is converted to single quotes by tools/principles_guide.py
    code = doc.code
    inside = mask_quotes(code)
    for m in re.finditer(r"``|''|“|”|(?<![\\=#])\"", code):
        t = m.group(0)
        if t in "“”" and inside[m.start()] == " " and code[m.start()] != " ":
            continue    # inside a single-quoted quotation
        if t == '"' and re.match(r"[`'=~a-zA-Z|-]", code[m.end():m.end() + 1] or " ") and doc.lang == "pl":
            continue    # babel-polish shorthand
        what = {"``": "TeX opening double quotes", "''": "TeX closing double quotes"}.get(
            t, "curly double quotes outside a quotation" if t in "“”" else "straight double quotes")
        yield Hit(key=what, offset=m.start(), values={"what": what})
