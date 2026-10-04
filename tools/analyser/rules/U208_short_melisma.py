"""10.6: a melisma on a short syllable, one whose vowel is stopped by a plosive
or fricative (it, et, est, -tus: text.coda_class). Such a syllable cannot be
sung through; an open syllable or one closed by a sonorant (con, in, non) can.
Measured in time: from two notes lasting more than a semibreve, or three notes.

At a phrase's last syllable (word-final, before punctuation or a rest) the
vowel is held and the consonant sung at the end, as at every cadence; there
the rule counts `final` (0: not at all; the cadential tail is 10.3's)."""
from . import params


def check(ctx):
    s = ctx.syl
    if not s.short:
        return
    notes = ctx.notes
    nn, t = len(notes), ctx.time
    p = params("U208")
    if nn > 30 or nn < 2 or (nn < 3 and t <= p["two_note_time"]):
        return
    final = s.syllabic in ("end", "single") and (s.punct or ctx.next_start is None or ctx.next_start != ctx.end)
    if final and not p["final"]:
        return
    amount = float(t) / p["unit"] * (p["final"] if final else 1.0)
    yield ctx.hit("U208", nn=nn, time=t, coda="".join(c for c in s.text if c.isalpha())[-1:],
                  amount=amount, final=final)
