"""10.3: the last syllable of a phrase on its cadence note.

Three ways to miss it, at an arrival this voice makes (C, T or B):
  late    the arrival note carries a syllable that is not the phrase's last,
          and the last syllable (the next one, ending its word and the phrase)
          comes on the note straight after the arrival;
  early   the phrase's last syllable starts before the arrival and holds
          through it, unless the notes between are a run (the syllable starts
          on the run or the longer note before it: Stoquerus R3; Towne R16);
  back    the voice resolves its own line after the arrival (the cadence
          layer's melodic resolution: its last melodic move, before a rest),
          and the phrase's last syllable starts at or before the arrival and
          is carried back across that final move.

Miki's review of 4 October 2026 sets the voice's own resolution above the
harmonic arrival: a vowel on the final move "acts as a kind of full stop", and
when a syllable must be held, the mouth prefers the smaller movement (Bassus
18.3: 'la' over 18.2-18.3 and 'tus' on 19.1, not 'tus' over 18.3-19.1). So a
late last syllable that falls on the voice's own resolution is marked
`melodic` (gate melodic_resolution), and one sung while other voices have
already begun new text is marked `tail` (gate tail_voice: Cantus 28.1, which
carries the old phrase across the join with the Bassus).

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
    res = getattr(a, "resolutions", {}).get((voice, j))
    rest_after = ctx.next_start is None or ctx.next_start != ctx.end
    vals = dict(cadence_type=cad.type, tone=cad.tone, cadence_kind=cad.kind)
    if phrase_final(ctx, ctx.i, rest_after):
        if j == ctx.start:
            if res is not None and ctx.start < res < ctx.end:
                yield ctx.hit("U301", ev=j, amount=0.75,
                              problem=f"'{ctx.syl.text}' is carried back from the voice's own resolution "
                                      f"at {evs[res].where} across its last move", **vals)
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
        melodic = res is not None and res == ctx.next_start
        last = evs[res] if melodic else evs[ctx.next_start]
        tail = a.tail_voice(voice, ctx.line.verse, evs[j].onset, last.end) if hasattr(a, "tail_voice") else False
        problem = f"the arrival carries '{ctx.syl.text}', and '{nxt.text}' comes after it"
        if melodic:
            problem += ", on the voice's own resolution"
        if tail:
            problem += ", while other voices begin new text"
        yield ctx.hit("U301", ev=j, problem=problem, melodic=melodic, tail=tail, **vals)
