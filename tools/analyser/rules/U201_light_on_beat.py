"""10.6: a light word on the bar or half-bar inside a moving figure (minims
or shorter), where it could sit off the beat and lead in."""
from ..meter import on_beat


def check(ctx):
    w = ctx.word
    if len(w.syls) != 1 or w.cls != "light":
        return
    notes = ctx.notes
    nn, first = len(notes), ctx.first
    if nn > 30 or not on_beat(first):
        return
    if first.dur <= 2 and nn <= 2:
        value = ["", "semiminim", "minim"][int(first.dur)]
        yield ctx.hit("U201", place="bar" if first.pos == 0 else "half-bar", value=value)
