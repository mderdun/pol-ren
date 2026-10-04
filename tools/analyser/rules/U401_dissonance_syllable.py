"""Vicentino rule 12: a new syllable on a dissonant note. Information: the
theorists themselves did not keep it (Towne 1990, R27)."""


def check(ctx):
    a = ctx.analysis
    if a is None:
        return
    d = a.dissonances.get((ctx.line.voice, ctx.start))
    if d is None:
        return
    yield ctx.hit("U401", label=d.label, interval=d.interval, against=d.against)
