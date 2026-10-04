"""10.5: no elision in Latin. (In Polish the verse's syllable count decides;
the analyser does not judge that.)"""
from .base import Hit

TIES = ("‿", "~")


def check_line(lctx):
    for s in lctx.line.syls:
        if any(t in s.text for t in TIES):
            e = lctx.line.events[s.ev]
            yield Hit("U105", ev=s.ev, syl=s.i, values=dict(txt=s.text, bar=e.bar, where=e.where),
                      hard=True)
