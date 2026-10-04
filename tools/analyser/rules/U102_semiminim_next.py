"""10.1: when the semiminim after a dotted minim takes a syllable, the note
after it takes one too."""
from ..meter import dotted_unit, syllable_unit


def check(ctx):
    e, prev = ctx.first, ctx.prev
    if ctx.legacy:
        short, dotted = 1, 3
    else:
        short, dotted = syllable_unit(e) / 2, dotted_unit(e)
    if e.dur != short or prev is None or prev.rest or prev.dur != dotted:
        return
    nx = ctx.after
    if nx is not None and not nx.rest and not ctx.has_syl(ctx.start + 1):
        yield ctx.hit("U102", hard=True)
