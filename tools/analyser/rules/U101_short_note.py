"""10.1, the firm core (rewritten 4 October 2026): no new syllable on a dot,
on a note smaller than the dot it follows, on a fusa, on a middle or last note
of a semiminim run (outside 10.1(c)), or on a semiminim outside the licences
(a)-(c). The licences are priced by U106. The first note after a rest is free
(10.2). Under C every value counts one level down (meter.syllable_unit).

The legacy port keeps the old audit's test: a minim or longer, or the next
note after a dotted minim."""
from ..meter import syllable_unit
from ..shortnote import classify


def check(ctx):
    e, prev = ctx.first, ctx.prev
    if ctx.legacy:
        if e.dur >= 2:
            return
        after_rest = prev is None or prev.rest
        after_dotted = prev is not None and not prev.rest and prev.dur == 3
        if not after_rest and not after_dotted:
            yield ctx.hit("U101", hard=True, unit="minim", why="")
        return
    k = classify(ctx)
    if k is not None and k[0] == "firm":
        unit = syllable_unit(e)
        yield ctx.hit("U101", hard=True, unit="minim" if unit == 2 else "semiminim", why=": " + k[1])
