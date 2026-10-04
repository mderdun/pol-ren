"""10.6: a stressed syllable on a shorter note than the unstressed syllable
after it in the same word, and off the beat. Not checked where that next
syllable is the word's last (10.3 rules the last syllable)."""
from ..meter import on_beat


def check(ctx):
    w, k = ctx.word, ctx.syl.k
    st = w.stress
    if st is None or len(w.syls) < 2 or k != st or not (k + 1 < len(w.syls) - 1):
        return
    if len(ctx.notes) > 30:
        return
    nxt = ctx.next_note
    if nxt is None:
        return
    first = ctx.first
    if first.dur < nxt.dur and not on_beat(first):
        yield ctx.hit("U202", amount=float(min(nxt.dur / first.dur, 4)) / 2)
