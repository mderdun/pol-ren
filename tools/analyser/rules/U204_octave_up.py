"""10.6: a rising octave is taken inside one syllable."""


def check(ctx):
    prev, e = ctx.prev, ctx.first
    if prev is None or prev.rest or e.rest:
        return
    if prev.step == e.step and e.octave - prev.octave == 1:
        yield ctx.hit("U204")
