"""Build a music21 Score from our model, so that the music layers can use
music21's timespan tree, intervals and voice-leading objects while every
music21 note still points back at our event (note.id = 'Voice:idx').

We build the stream ourselves instead of re-parsing the MusicXML: ties are
already merged our way, divided notes stay divided, and offsets are exactly our
onsets (semiminim = quarterLength in unreduced values).
"""
from __future__ import annotations

from music21 import note, pitch, stream, tree

from ..model import Score


def build(score: Score) -> stream.Score:
    s = stream.Score()
    for voice in score.parts:
        p = stream.Part()
        p.partName = voice
        p.id = voice
        for e in score.voices[voice]:
            if e.rest:
                r = note.Rest(quarterLength=e.dur)
                r.id = f"{voice}:{e.idx}"
                p.insert(e.onset, r)
                continue
            n = note.Note(pitch.Pitch(e.name), quarterLength=e.dur)
            n.id = f"{voice}:{e.idx}"
            p.insert(e.onset, n)
            e.m21 = n
        s.insert(0, p)
    return s


def verticalities(s: stream.Score):
    """music21 timespan-tree verticalities over the notes of every part."""
    ts = tree.fromStream.asTimespans(s, flatten=True, classList=(note.Note,))
    return list(ts.iterateVerticalities())


def ref(n) -> tuple[str, int]:
    voice, idx = n.id.rsplit(":", 1)
    return voice, int(idx)
