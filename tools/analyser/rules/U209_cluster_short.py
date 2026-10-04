"""10.6: a syllable change through a consonant cluster on a very short note.
Where this syllable's coda and the next syllable's onset make two consonants
or more (con|so: o-n-s), the mouth needs time for them at the end of the
syllable's last note. Flagged where that note is shorter than a semiminim
(amount 1), or a semiminim ending a figure of shorter notes (amount 0.5)."""
from ..text import coda_consonants, onset_consonants


def check(ctx):
    nxt = ctx.next_syl
    q = ctx.next_start
    if nxt is None or q is None or q != ctx.end or q - 1 < ctx.start:
        return
    n = coda_consonants(ctx.syl.text) + onset_consonants(nxt.text)
    if n < 2:
        return
    last = ctx.events[q - 1]
    if last.rest:
        return
    if last.dur < 1:
        amount = 1.0
    elif last.dur == 1 and q - 2 >= ctx.start and not ctx.events[q - 2].rest and ctx.events[q - 2].dur < 1:
        amount = 0.5
    else:
        return
    h = ctx.hit("U209", ev=q, syl=ctx.i, amount=amount, nxt=nxt.text, n=n,
                value="fusa" if last.dur < 1 else "semiminim after a fusa")
    yield h
