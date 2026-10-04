"""10.7 (Wacław's practice, editions that follow it): one melisma before each
cadence, on the stressed syllable of the last word. Flags a run of three or
more notes on another non-final syllable of that word."""


def check(ctx):
    a = ctx.analysis
    if a is None or not a.score.config.get("waclaw_practice"):
        return
    line, w, k = ctx.line, ctx.word, ctx.syl.k
    if (line.voice, line.verse, ctx.syl.word) not in a.cadential_words:
        return
    st = w.stress
    if st is None or len(w.syls) < 2 or k == st or k == len(w.syls) - 1:
        return
    nn = len(ctx.notes)
    if nn >= 3:
        yield ctx.hit("U302", nn=nn, st=st + 1, amount=nn / 3)
