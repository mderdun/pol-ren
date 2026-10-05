"""10.6 (Lanfranco VI): a new syllable on the white note straight after a run
of short notes, where it could come before the run. Evaluated on the syllable
that holds the run, reported on the next syllable.

10.1(d) (4 October 2026): at a phrase end, where the words leave no other
place (Vicentino rule 2; Calvisius, especially the phrase's penultimate), the
white note after a run may take a new syllable; it costs only the licence
(settings.yaml: licences_10_1.d)."""
from ..shortnote import costs
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
    if e.rest or e.dur < 2 or nxt.syllabic not in ("begin", "middle", "single", "end"):
        return
    phrase_end = nxt.text[-1:] in punct
    if ctx.legacy and (phrase_end or nxt.syllabic == "end"):
        return
    if not ctx.legacy and not phrase_end:
        after = ctx.line.syls[ctx.i + 2] if ctx.i + 2 < len(ctx.line.syls) else None
        phrase_end = after is not None and after.text[-1:] in punct
        if not phrase_end and nxt.syllabic == "end":
            return
    j = q
    while j > 0 and not evs[j - 1].rest and evs[j - 1].dur < 2 and not ctx.has_syl(j - 1):
        if not ctx.legacy and evs[j].after_break:
            break
        j -= 1
    run = q - j
    on_run = (not ctx.legacy and j - 1 == ctx.start and not evs[j - 1].rest
              and evs[j - 1].dur < 2)
    if on_run:
        # 10.1(a): the syllable began on the run's first semiminim; the run
        # and the white note after it keep it
        run += 1
    if run < 2 or (j - 1 < ctx.start and not on_run):
        return
    if not on_run:
        before = evs[j - 1]
        if before.rest or before.dur < 2 or ctx.has_syl(j - 1):
            return
    if phrase_end:
        c = float(costs().get("d", 0.25))
        if c <= 0:
            return
        h = ctx.hit("U203", ev=q, syl=ctx.i + 1, run=run, amount=c / 0.75,
                    licence="; at the phrase end, 10.1(d)")
    else:
        h = ctx.hit("U203", ev=q, syl=ctx.i + 1, run=run, licence="")
    h.values["txt"] = nxt.text
    h.values["word"] = ctx.line.word_of(ctx.i + 1).norm
    yield h
