"""10.3: the last syllable of a phrase on its cadence note.

Two ways to miss it, at an arrival this voice makes (C, T or B):
  late   the arrival note carries a syllable that is not the phrase's last,
         and the last syllable (the next one, ending its word and the phrase)
         comes on the note straight after the arrival;
  early  the phrase's last syllable starts before the arrival and holds
         through it, unless the notes between are a run (the syllable starts
         on the run or the longer note before it: Stoquerus R3; Towne R16).
A phrase ends at punctuation or at a word that a rest follows."""
from ..meter import syllable_unit


def phrase_final(ctx, i, end_next):
    line = ctx.line
    s = line.syls[i]
    if s.syllabic not in ("end", "single"):
        return False
    if s.punct:
        return True
    return end_next


def check(ctx):
    a = ctx.analysis
    if a is None:
        return
    voice = ctx.line.voice
    arr = [j for j in range(ctx.start, ctx.end) if (voice, j) in a.arrivals]
    if not arr:
        return
    j = arr[-1]
    cad = a.arrivals[(voice, j)]
    evs = ctx.events
    rest_after = ctx.next_start is None or ctx.next_start != ctx.end
    vals = dict(cadence_type=cad.type, tone=cad.tone)
    if phrase_final(ctx, ctx.i, rest_after):
        if j == ctx.start:
            return
        between = [e for e in evs[ctx.start + 1:j] if not e.rest]
        if between and all(e.dur < syllable_unit(e) for e in between):
            return
        yield ctx.hit("U301", ev=j, problem=f"'{ctx.syl.text}' starts before the arrival", **vals)
        return
    nxt = ctx.next_syl
    # late: the last syllable falls on the note straight after the arrival;
    # if the voice runs on past the arrival, it is not closing there
    if nxt is None or ctx.next_start != ctx.end or ctx.next_start != j + 1:
        return
    k2 = ctx.i + 1
    nxt_end = ctx.line.syls[k2 + 1].ev if k2 + 1 < len(ctx.line.syls) else None
    after_rest = nxt_end is None or any(e.rest for e in evs[ctx.next_start:nxt_end])
    if nxt.syllabic in ("end", "single") and (nxt.punct or after_rest):
        yield ctx.hit("U301", ev=j, problem=f"the arrival carries '{ctx.syl.text}', and '{nxt.text}' comes after it", **vals)
