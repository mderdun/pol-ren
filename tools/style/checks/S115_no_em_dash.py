import re

from ..findings import Hit


def check(doc):
    # the code, not the prose: an em dash is wrong in quotations and lists too
    # (a quoted dash is a source's punctuation only in the diplomatic text)
    code = doc.code
    pat = r"—" if doc.suffix == ".md" else r"—|(?<!-)---(?!-)|\\textemdash\b"   # --- is a rule in Markdown
    for m in re.finditer(pat, code):
        before = code[max(0, m.start() - 40):m.start()]
        context = re.sub(r"\s+", " ", before[-20:] + m.group(0) + code[m.end():m.end() + 20])
        yield Hit(key=context.strip(), offset=m.start(), values={"dash": m.group(0)})
