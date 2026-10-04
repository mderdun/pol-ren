"""10.6: a long run on a light word. Long is measured in time (Miki, review of
4 October 2026): the word's notes last `min_time` semiminims or more over at
least `min_notes` notes. The old audit's test (four notes or more) stays for
--legacy."""
from . import params


def check(ctx):
    w = ctx.word
    if len(w.syls) != 1 or w.cls != "light":
        return
    nn = len(ctx.notes)
    if ctx.legacy:
        if 4 <= nn <= 30:
            yield ctx.hit("U205", nn=nn, time="", amount=1 + (nn - 4) / 4)
        return
    p = params("U205")
    t = ctx.time
    if nn > 30 or nn < p["min_notes"] or t < p["min_time"]:
        return
    yield ctx.hit("U205", nn=nn, time=f", {t} semiminims", coda=ctx.syl.coda,
                  amount=1 + float(t - p["min_time"]) / p["step"])
