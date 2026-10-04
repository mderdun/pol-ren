"""10.6: a stressed syllable off the tactus while the next syllable of its word
falls on it. Unlike U202 it applies where that next syllable is the word's
last (con-so-LA-ri). The search then prefers a placement that pins the stress
to the bar or half-bar wherever the line allows it; where it does not, the
finding has no regret and stays information."""
from ..meter import on_beat


def check(ctx):
    w, k = ctx.word, ctx.syl.k
    st = w.stress
    if st is None or len(w.syls) < 2 or k != st or k + 1 >= len(w.syls):
        return
    nxt = ctx.next_note
    if nxt is None or nxt.rest or len(ctx.notes) > 30:
        return
    first = ctx.first
    if not on_beat(first) and on_beat(nxt):
        yield ctx.hit("U210", place="bar" if nxt.pos == 0 else "half-bar", nxt=ctx.next_syl.text)
