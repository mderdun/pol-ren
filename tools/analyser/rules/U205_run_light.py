"""10.6: a run of four or more notes on a light word."""


def check(ctx):
    w = ctx.word
    if len(w.syls) != 1 or w.cls != "light":
        return
    nn = len(ctx.notes)
    if 4 <= nn <= 30:
        yield ctx.hit("U205", nn=nn, amount=1 + (nn - 4) / 4)
