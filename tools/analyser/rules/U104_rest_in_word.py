"""10.4: no rest divides a word. Reported at every rest between a syllable
that continues its word and the next syllable, as the old audit did."""
from .base import Hit


def check_line(lctx):
    line = lctx.line
    pos = {ev: n for n, ev in enumerate(lctx.starts)}
    cur = None
    for i, e in enumerate(line.events):
        if i in pos:
            cur = line.syls[pos[i]]
            continue
        if e.rest and cur is not None and cur.syllabic in ("begin", "middle"):
            yield Hit("U104", ev=i, syl=cur.i, values=dict(txt=cur.text, bar=e.bar, where=e.where),
                      hard=True)
