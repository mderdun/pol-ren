"""10.6 (Lanfranco VI): a new syllable on the white note straight after a run
of short notes, where it could come before the run. Evaluated on the syllable
that holds the run, reported on the next syllable."""
from ..text import PUNCT

LEGACY_PUNCT = ",.:;"


def check(ctx):
    q = ctx.next_start
    nxt = ctx.next_syl
    if q is None or nxt is None or q < 3:
        return
    evs = ctx.events
    e = evs[q]
    punct = LEGACY_PUNCT if ctx.legacy else PUNCT
    if e.rest or e.dur < 2 or nxt.text[-1:] in punct or nxt.syllabic not in ("begin", "middle", "single"):
        return
    j = q
    while j > 0 and not evs[j - 1].rest and evs[j - 1].dur < 2 and not ctx.has_syl(j - 1):
        if not ctx.legacy and evs[j].after_break:
            break
        j -= 1
    run = q - j
    if run < 2 or j - 1 < ctx.start:
        return
    before = evs[j - 1]
    if before.rest or before.dur < 2 or ctx.has_syl(j - 1):
        return
    h = ctx.hit("U203", ev=q, syl=ctx.i + 1, run=run)
    h.values["txt"] = nxt.text
    h.values["word"] = ctx.line.word_of(ctx.i + 1).norm
    yield h
