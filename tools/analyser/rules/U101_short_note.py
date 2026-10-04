"""10.1: a new syllable only on a minim or longer (a semiminim or longer under
C), or on the next smaller note straight after a dotted note of the syllable
value. The first note after a rest is free (10.2)."""
from ..meter import dotted_unit, syllable_unit


def check(ctx):
    e, prev = ctx.first, ctx.prev
    if ctx.legacy:
        unit, dotted = 2, 3
    else:
        unit, dotted = syllable_unit(e), dotted_unit(e)
    if e.dur >= unit:
        return
    after_rest = prev is None or prev.rest
    after_dotted = prev is not None and not prev.rest and prev.dur == dotted \
        and (ctx.legacy or e.dur == unit / 2)
    if not after_rest and not after_dotted:
        yield ctx.hit("U101", hard=True, unit="minim" if unit == 2 else "semiminim")
