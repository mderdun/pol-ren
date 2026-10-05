"""10.1, firm: a lone semiminim that takes a syllable passes one to the next
note (Lanfranco V, Zarlino VI, Stoquerus O2, Towne 1991, 19d). So does the
semiminim straight after a dotted minim, run or not. The first of a run under
10.1(a) does not: the run and the white note after it keep its syllable."""
from ..meter import dotted_unit, syllable_unit
from ..shortnote import lone


def check(ctx):
    e, prev = ctx.first, ctx.prev
    if ctx.legacy:
        if e.dur != 1 or prev is None or prev.rest or prev.dur != 3:
            return
    else:
        unit = syllable_unit(e)
        if e.dur >= unit or e.dur < unit / 2:
            return
        after_dotted = prev is not None and not prev.rest and prev.dur == dotted_unit(e)
        if not after_dotted and not lone(ctx.events, ctx.start, unit):
            return
    nx = ctx.after
    if nx is not None and not nx.rest and not ctx.has_syl(ctx.start + 1):
        yield ctx.hit("U102", hard=True)
