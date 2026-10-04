"""10.2: a syllable on the first note after a rest, where the voice has text
around it."""
from .base import Hit


def check_line(lctx):
    line, starts = lctx.line, set(lctx.starts)
    evs = line.events
    first = min(starts) if starts else None
    for i, e in enumerate(evs):
        if e.rest or i in starts or i == 0 or first is None or i < first:
            continue
        if evs[i - 1].rest and any(j in starts for j in range(i, i + 12)):
            yield Hit("U103", ev=i, syl=_syl_before(lctx.starts, i),
                      values=dict(bar=e.bar, where=e.where, txt=""), hard=True)


def _syl_before(starts, i):
    k = 0
    for n, s in enumerate(starts):
        if s <= i:
            k = n
    return k
