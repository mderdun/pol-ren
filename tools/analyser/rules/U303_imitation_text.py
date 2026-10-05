"""10.10: a point of imitation carries the words of its head motif wherever it
recurs. For each entry that starts with the same word as the point's leading
entry, compare which head notes start a syllable. Evaluated for the line under
a candidate underlay against the other lines as they stand."""
from .base import Hit


def pattern(line, starts, head):
    pos = {ev: n for n, ev in enumerate(starts)}
    pat = tuple(k for k, idx in enumerate(head) if idx in pos)
    first = pos.get(head[0])
    word = line.word_of(first).norm if first is not None else None
    return pat, word, first


def _fmt(p):
    return "".join("x" if k in p else "-" for k in range(max(p) + 1 if p else 0))


def check_piece(a, line, starts):
    if a is None:
        return
    for p in a.points:
        lead = p.leader
        lead_line = line if lead.voice == line.voice else a.line(lead.voice, line.verse)
        if lead_line is None:
            continue
        lead_starts = starts if lead_line is line else lead_line.starts
        lpat, lword, _ = pattern(lead_line, lead_starts, lead.head)
        if lword is None:
            continue
        for e in p.entries[1:]:
            if e.voice != line.voice and lead.voice != line.voice:
                continue
            eline = line if e.voice == line.voice else a.line(e.voice, line.verse)
            if eline is None:
                continue
            est = starts if eline is line else eline.starts
            pat, word, first = pattern(eline, est, e.head)
            if word != lword or pat == lpat:
                continue
            n = len(set(pat) ^ set(lpat))
            # attribute to the syllable of this line that the difference touches
            if eline is line:
                ev, syl = e.ev, first
            else:
                ev, syl = lead.ev, pattern(line, starts, lead.head)[2]
            if syl is None:
                continue
            yield Hit("U303", ev=ev, syl=syl, amount=n / 2,
                      values=dict(ptype=p.type, entry=f"{e.voice} {e.where}", word=word,
                                  leader=f"{lead.voice} at {lead.where}", pattern=_fmt(pat),
                                  lead_pattern=_fmt(lpat), entries=len(p.entries),
                                  bar=line.events[ev].bar, where=line.events[ev].where,
                                  txt=line.syls[syl].text, side="entry" if eline is line else "leader"))
