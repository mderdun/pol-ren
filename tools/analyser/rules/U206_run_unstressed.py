"""10.6: a long melisma on an unstressed syllable that is not the word's last
(a word-final syllable may carry a cadential tail, 10.3). In an edition that
follows Wacław's practice (10.7), the last word before a cadence is left to
U302.

Long is measured in time, not notes (Miki, review of 4 October 2026: a fast
run of six quavers is short): the syllable's notes must last `min_time`
semiminims or more, over at least `min_notes` notes. The note count is kept in
the message. The old audit's test (six notes or more) stays for --legacy."""
from . import params


def vowel(syl: str) -> str:
    s = syl.lower().replace("ae", "e").replace("oe", "e")
    v = [c for c in s if c in "aeiouyąęó"]
    return v[-1] if v else ""


def check(ctx):
    w, k = ctx.word, ctx.syl.k
    st = w.stress
    if st is None or len(w.syls) < 2 or k == st or k == len(w.syls) - 1:
        return
    a = ctx.analysis
    if a is not None and a.score.config.get("waclaw_practice") and \
            (ctx.line.voice, ctx.line.verse, ctx.syl.word) in a.cadential_words:
        return      # U302 judges the last word before a cadence in these editions
    nn = len(ctx.notes)
    if ctx.legacy:
        if 6 <= nn <= 30:
            yield ctx.hit("U206", nn=nn, st=st + 1, vowel=vowel(ctx.syl.text), time="",
                          amount=1 + (nn - 6) / 4)
        return
    p = params("U206")
    t = ctx.time
    if nn > 30 or nn < p["min_notes"] or t < p["min_time"]:
        return
    yield ctx.hit("U206", nn=nn, st=st + 1, vowel=vowel(ctx.syl.text), time=f", {t} semiminims,",
                  coda=ctx.syl.coda, amount=1 + float(t - p["min_time"]) / p["step"])
