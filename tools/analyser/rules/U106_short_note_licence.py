"""10.1, the licences (rewritten 4 October 2026): a new syllable on a
semiminim is legal under (a) the first of a run on a minim beat, (b) straight
after a dotted minim, or a lone semiminim on a repeated pitch after a longer
note, (c) a later note of a run where every voice moves in semiminims or the
line leaps. Each costs a little (settings.yaml: licences_10_1), so the
default, a minim or longer, wins where it is as good; the critical note names
the clause. (d) is priced by U203; (e) is accepted beside the note."""
from ..shortnote import classify, costs

CLAUSE = {"a": "(a)", "b_dotted": "(b)", "b_repeat": "(b)", "c": "(c)"}


def check(ctx):
    k = classify(ctx)
    if k is None or k[0] == "firm":
        return
    c = float(costs().get(k[0], 0.5))
    if c <= 0:
        return
    yield ctx.hit("U106", amount=c, clause=CLAUSE[k[0]], why=k[1])
