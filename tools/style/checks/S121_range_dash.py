import re

from ..findings import Hit

# A range of bars, pages or years: two numbers of 1-4 digits, the second
# larger (17-18, 1550-1556) or abbreviated (1550-56). Catalogue numbers
# (SU 3807-2) follow capitals; URLs are masked.
RANGE = re.compile(r"(?<![\w./-])(\d{1,4})-(\d{1,4})(?![\w/-])")


def check(doc):
    prose = doc.prose
    for m in RANGE.finditer(prose):
        a, b = int(m.group(1)), int(m.group(2))
        if b <= a and not (len(m.group(2)) < len(m.group(1)) and b < 100):
            continue
        before = prose[max(0, m.start() - 6):m.start()]
        if re.search(r"[A-Z]{2,}\s*$", before):
            continue        # SU 3807-2, a catalogue number
        yield Hit(key=m.group(0), offset=m.start(), values={"found": m.group(0)})
