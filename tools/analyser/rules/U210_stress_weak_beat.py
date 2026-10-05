"""10.6: a stressed syllable off the beat where the line offers it a beat.
Unlike U202 it applies where the next syllable is the word's last
(con-so-LA-ri, QUI-a).

The cost belongs to the stressed syllable alone: an unstressed syllable on a
strong beat is not at fault by itself (Miki, second review of 4 October 2026,
Altus 41.4 'quia': "there's no reason to force 'a' off a strong beat"), so
moving it does not answer the finding. And a stressed syllable that no legal
reading could put on a beat is not flagged at all: within its reach (after
the syllable two before it, or the previous one where that one is pinned by a
rest or punctuation, and before the syllable two after it, or the next one
where that one ends with punctuation, leaving a note for each syllable in
between) there must be a note on the beat that may take a
syllable (10.1).

The beat is the tactus, or inside a span where the voice plays against the
tactus (meter.displaced_spans: Vox Altus 10.4 'Ra', Altus 15.4 'la'), the
displaced pulse as well."""
from ..meter import pulse_on_beat, syllable_unit


def _legal(e) -> bool:
    return not e.rest and not e.divided and e.dur >= syllable_unit(e)


def _reach(ctx):
    """Event indices the stressed syllable could start on in some reading."""
    evs, line, i = ctx.events, ctx.line, ctx.i
    starts = line.starts
    lo = ctx.start
    while lo > 0 and not evs[lo - 1].rest and not evs[lo].after_break:
        lo -= 1
    hi = ctx.start
    while hi + 1 < len(evs) and not evs[hi + 1].rest and not evs[hi + 1].after_break:
        hi += 1
    # syllables before: the previous one moves unless pinned
    prev = i - 1
    need_before = 0
    left = lo - 1
    if prev >= 0 and starts[prev] >= lo:
        pinned = starts[prev] == lo or line.syls[prev].punct
        if pinned:
            left = starts[prev]
        else:
            need_before = 1
            left = starts[prev - 1] if prev - 1 >= 0 and starts[prev - 1] >= lo else lo - 1
    right = hi + 1
    need_after = 0
    if i + 1 < len(starts) and starts[i + 1] <= hi:
        if line.syls[i + 1].punct:
            right = starts[i + 1]
        else:
            need_after = 1
            right = starts[i + 2] if i + 2 < len(starts) and starts[i + 2] <= hi else hi + 1
    out = []
    for p in range(left + 1, right):
        if not _legal(evs[p]):
            continue
        before = sum(1 for j in range(left + 1, p) if _legal(evs[j]))
        after = sum(1 for j in range(p + 1, right) if not evs[j].rest)
        if before >= need_before and after >= need_after:
            out.append(p)
    return out


def check(ctx):
    w, k = ctx.word, ctx.syl.k
    st = w.stress
    if st is None or len(w.syls) < 2 or k != st or k + 1 >= len(w.syls):
        return
    if len(ctx.notes) > 30:
        return
    spans = ctx.analysis.displaced if ctx.analysis is not None else ()
    first = ctx.first
    if pulse_on_beat(first, spans):
        return
    beats = [p for p in _reach(ctx) if pulse_on_beat(ctx.events[p], spans)]
    if not beats:
        return
    against = any(d.contains(first.voice, first.onset) for d in spans)
    yield ctx.hit("U210", free=ctx.events[beats[0]].where,
                  pulse="the displaced pulse" if against else "the tactus")
