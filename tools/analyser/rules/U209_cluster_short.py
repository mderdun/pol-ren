"""10.6: a syllable change through a consonant cluster on a very short note.
Where this syllable's coda and the next syllable's onset make two consonants
or more (con|so: o-n-s), the mouth needs time for them at the end of the
syllable's last note. Flagged where that note is shorter than a semiminim
(amount 1), or a semiminim ending a figure of shorter notes (amount 0.5).

Polish (Miki, second review of 4 October 2026: "we can't 'solve' polish
clusters - we can remove them in particularly tricky spots like short note
changes"): the amount is multiplied by `params.pl_factor`, and a cluster of
`pl_cluster` consonants or more also counts at a change after the shortest
value that may take a syllable (a minim under cut-C, a semiminim under C),
amount `pl_short`."""
from . import params
from ..meter import syllable_unit
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
    p = params("U209")
    pl = ctx.line.lang == "pl"
    if last.dur < 1:
        amount, value = 1.0, "fusa"
    elif last.dur == 1 and q - 2 >= ctx.start and not ctx.events[q - 2].rest and ctx.events[q - 2].dur < 1:
        amount, value = 0.5, "semiminim after a fusa"
    elif pl and n >= p["pl_cluster"] and last.dur <= syllable_unit(last):
        amount, value = p["pl_short"], {1: "semiminim", 2: "minim"}.get(int(last.dur), "short note")
    else:
        return
    if pl:
        amount *= p["pl_factor"]
    h = ctx.hit("U209", ev=q, syl=ctx.i, amount=amount, nxt=nxt.text, n=n, value=value)
    yield h
