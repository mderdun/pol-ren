"""10.10: a recurring motif (the imitation layer's motif chains) carries the
same text wherever it recurs, and its notes are syllabic where the others'
are. The motif's text is the one most of its occurrences carry as the
underlay stands (the earliest breaks a tie); each occurrence is compared,
head note by head note, with it: a syllable where it has none, none where it
has one, or another syllable. Evaluated for the line under a candidate
underlay against that text.

Miki, review of 4 October 2026: 'et noluit' in *Vox in Rama* (minim, dotted
minim, semiminim, minim) "means the only real legal option for the start is
for those four notes to be purely syllabic"; Altus 32 and Tenor 37.4 break
the chain. A motif texted differently weighs heavily (the YAML's weight), so
that the search keeps it as its neighbours have it."""
from bisect import bisect_right
from collections import Counter

from .base import Hit


def _sung(line, starts, head):
    pos = {ev: i for i, ev in enumerate(starts)}
    out = []
    for idx in head:
        i = pos.get(idx)
        out.append(None if i is None else line.syls[i].text.strip(",.:;!?").lower())
    return tuple(out)


def reference(a, motif, verse):
    cache = a.__dict__.setdefault("_motif_text", {})
    key = (id(motif), verse)
    if key not in cache:
        texts = []
        for e in motif.entries:
            ln = a.line(e.voice, verse)
            if ln is not None:
                texts.append(_sung(ln, ln.starts, e.head))
        c = Counter(texts)
        best = max(c.values()) if c else 0
        ref = next((t for t in texts if c[t] == best), None)
        lead = next((e for e in motif.entries
                     if a.line(e.voice, verse) is not None
                     and _sung(a.line(e.voice, verse), a.line(e.voice, verse).starts, e.head) == ref), None)
        cache[key] = (ref, lead, best, len(texts))
    return cache[key]


def _fmt(t):
    return " ".join(x if x is not None else "_" for x in t)


def check_piece(a, line, starts):
    if a is None:
        return
    for m in getattr(a, "motifs", ()):
        ref, lead, n_ref, n = reference(a, m, line.verse)
        if ref is None or n_ref < 2:
            continue
        for e in m.entries:
            if e.voice != line.voice:
                continue
            got = _sung(line, starts, e.head)
            if got == ref:
                continue
            diff = sum(1 for x, y in zip(got, ref) if x != y)
            k = bisect_right(list(starts), e.head[0]) - 1
            if k < 0:
                continue
            yield Hit("U306", ev=e.ev, syl=k, amount=diff / 2,
                      values=dict(entry=f"{e.voice} {e.where}", got=_fmt(got), ref=_fmt(ref),
                                  leader=f"{lead.voice} {lead.where}" if lead else "", count=n_ref, n=n,
                                  bar=line.events[e.ev].bar, where=line.events[e.ev].where,
                                  txt=line.syls[k].text, word=line.word_of(k).norm,
                                  how=e.context))
