import re

from ..findings import Hit


def check(doc):
    prose = doc.prose
    for m in re.finditer(r"\b(we|We|our|Our|us|ours|ourselves)\b", prose):
        w = m.group(1)
        if w == "us" and re.search(r"\bU\.?S\b", prose[m.start() - 2:m.end() + 2]):
            continue
        tail = prose[m.end():m.end() + 30]
        yield Hit(key=f"{w.lower()} {tail.split()[0] if tail.split() else ''}".strip(), offset=m.start(),
                  values={"found": (w + " " + " ".join(tail.split()[:3])).strip()})
