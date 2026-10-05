"""10.9: repeated notes take a new syllable. The exception (Stoquerus ch. 15):
the first of the two is a semiminim or shorter (under C a fusa or shorter)
and follows a note, or a dot, of its own value."""
from ..meter import syllable_unit


def check(ctx):
    notes = ctx.notes
    for a, b in zip(notes, notes[1:]):
        if b.idx != a.idx + 1 or a.midi != b.midi or ctx.has_syl(b.idx):
            continue
        if a.dur < syllable_unit(a) and a.idx > 0:
            p = ctx.events[a.idx - 1]
            if not p.rest and (p.dur == a.dur or p.dur == 3 * a.dur):
                continue
        yield ctx.hit("U207", ev=b.idx, pitch=b.name)
        return
