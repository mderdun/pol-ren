"""10.14: in a strophic piece (editions.yaml: strophic), a later stanza
follows stanza 1's underlay where its words fall alike. The voice is cut into
segments at the notes where both stanzas start a word (and at rests). In a
segment where a later stanza has as many syllables as stanza 1, with the
stresses and word breaks in the same places, the two should start their
syllables on the same notes; each syllable placed differently costs. Where the
words fall differently (another stress pattern, an extra syllable), a later
stanza may take its own underlay, and nothing is flagged.

Stanza 1 is the model ("stanza 1 goes under the notes and the rest follow"),
so the rule judges the later stanzas only, against stanza 1 as it stands."""
from .base import Hit


def _shape(line, idx):
    out = []
    for i in idx:
        s = line.syls[i]
        w = line.word_of(i)
        out.append((s.k == w.stress, s.syllabic in ("begin", "single")))
    return tuple(out)


def _spans(line):
    """Rest-bounded spans of the voice: list of (first, end) event indices."""
    out, cur = [], None
    for e in line.events:
        if e.rest:
            cur = None
            continue
        if cur is None or e.after_break:
            cur = [e.idx, e.idx + 1]
            out.append(cur)
        else:
            cur[1] = e.idx + 1
    return out


def check_piece(a, line, starts):
    if a is None or not a.score.config.get("strophic") or line.verse == "1":
        return
    ref = a.line(line.voice, "1")
    if ref is None:
        return
    for first, end in _spans(line):
        mine = [s.i for s in line.syls if first <= s.ev < end]
        theirs = [s.i for s in ref.syls if first <= s.ev < end]
        wm = {starts[i] for i in mine if line.syls[i].syllabic in ("begin", "single")}
        wt = {ref.syls[j].ev for j in theirs if ref.syls[j].syllabic in ("begin", "single")}
        cuts = sorted((wm & wt) | {first}) + [end]
        for b0, b1 in zip(cuts, cuts[1:]):
            yield from _segment(line, ref, starts, [i for i in mine if b0 <= starts[i] < b1],
                                [j for j in theirs if b0 <= ref.syls[j].ev < b1])


def _segment(line, ref, starts, mine, theirs):
        if not mine or len(mine) != len(theirs):
            return
        if _shape(line, mine) != _shape(ref, theirs):
            return
        for i, j in zip(mine, theirs):
            p, q = starts[i], ref.syls[j].ev
            if p == q:
                continue
            e, f = line.events[p], ref.events[q]
            yield Hit("U305", ev=p, syl=i, amount=1.0,
                      values=dict(verse=line.verse, txt=line.syls[i].text, ref_txt=ref.syls[j].text,
                                  where=e.where, ref_where=f.where, nsyl=len(mine), bar=e.bar))
