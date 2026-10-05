"""A word the lexicon does not know, or knows with a different number of
syllables than the edition sings."""
from .base import Hit


def check_line(lctx):
    line = lctx.line
    seen = set()
    for w in line.words:
        if w.norm in seen:
            continue
        seen.add(w.norm)
        s = line.syls[w.syls[0]]
        e = line.events[s.ev]
        vals = dict(word=w.norm, lang=line.lang, txt=s.text, bar=e.bar, where=e.where)
        if not w.entry.known:
            yield Hit("U501", ev=s.ev, syl=s.i, values=vals)
