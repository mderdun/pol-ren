import re

from ..findings import Hit

WRONG_ANGLE = re.compile(r"[〈〉〈〉‹›]|\\(?:langle|rangle)\b|\$<\$|\$>\$")


def _definition(code: str, name: str):
    """(start, end) of a Scheme definition (define (name ...) ...) or a
    LilyPond assignment name = ..., up to the next top-level definition."""
    m = re.search(r"\(define\s+\(" + re.escape(name) + r"\b|^" + re.escape(name) + r"\s*=", code, re.M)
    if not m:
        return None
    nxt = re.compile(r"^(?:#\(define\b|[A-Za-z]+\s*=|%%)", re.M).search(code, m.end())
    return m.start(), (nxt.start() if nxt else len(code))


def check(doc):
    code = doc.code
    if doc.role == "house" and doc.is_lily:
        span = _definition(code, "pr-opt-markup")
        if span:
            body = code[span[0]:span[1]]
            if re.search(r"leftparen|rightparen|parenthesize|\"\(\"", body):
                yield Hit(key="optional-accidental-round", offset=span[0],
                          values={"what": "optional editorial accidentals (\\optFlat, \\optSharp, \\optNatural) are "
                                          "drawn in round brackets; the decision of 4 Oct 2026 puts editorial "
                                          "suggestions in square brackets (round brackets are for cautionaries)"})
    for m in WRONG_ANGLE.finditer(code):
        yield Hit(key=f"angle:{m.group(0)}", offset=m.start(),
                  values={"what": f"'{m.group(0)}' used as an angle bracket; text written out from ij is "
                                  "bracketed ⟨ ⟩ (U+27E8, U+27E9) throughout the series"})
    if doc.is_tex:
        prose = doc.prose
        for m in re.finditer(r"(?<![\\$<\-])<([A-Za-z][^<>\n]{0,40})>(?![>\-])", prose):
            yield Hit(key=f"angle:<{m.group(1)}>", offset=m.start(),
                      values={"what": "ASCII < > used as angle brackets; use ⟨ ⟩ (U+27E8, U+27E9)"})
