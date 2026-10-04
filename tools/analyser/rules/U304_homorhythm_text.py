"""Information only: inside a homorhythmic passage, a slice where every other
attacking voice changes syllable and this one does not (or the reverse)."""
from .base import Hit


def check_piece(a, line, starts):
    if a is None or not a.regions:
        return
    mine = set(starts)
    others = {ln.voice: set(ln.starts) for ln in a.lines if ln.verse == line.verse and ln.voice != line.voice}
    for r in a.regions:
        for sl in a.slices:
            if not r.contains(sl.onset) or line.voice not in sl.attacks or len(sl.attacks) < 3:
                continue
            e = sl.sounding[line.voice]
            rest = [v for v in sl.attacks if v != line.voice and v in others]
            if len(rest) < 2:
                continue
            theirs = [sl.sounding[v].idx in others[v] for v in rest]
            me = e.idx in mine
            if all(theirs) and not me:
                how, other = "holds its syllable", "change"
            elif not any(theirs) and me:
                how, other = "changes syllable", "hold theirs"
            else:
                continue
            syl = max((n for n, s in enumerate(starts) if s <= e.idx), default=None)
            if syl is None:
                continue
            yield Hit("U304", ev=e.idx, syl=syl,
                      values=dict(region=f"{r.first_where}-{r.last_where}", how=how, other=other,
                                  txt=line.syls[syl].text, bar=e.bar, where=e.where))
