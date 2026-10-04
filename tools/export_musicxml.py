#!/usr/bin/env python3
"""Export each edition's critical score as MusicXML 4.0.

    tools/export_musicxml.py                  every edition
    tools/export_musicxml.py vox-in-rama ...  some editions
    tools/export_musicxml.py --events DIR     also keep the LilyPond event dumps in DIR

Writes editions/<slug>/pdf/<slug>.musicxml (critical score, written pitch), and
beside it <slug>.srcmap.tsv: for each note, the LilyPond file, line and column
it comes from (used by tools/analyser to point findings at voices.ily).

Polyphonic editions: the scores use house Scheme functions (\\prScore,
\\prStaff ...) that only LilyPond itself can evaluate, so the score is not
parsed. Instead LilyPond 2.24 compiles music/score.ly (no output pages) with
tools/musicxml-events.ily, which logs every note, rest, tie, lyric syllable,
bar line, repeat and rubric per voice, with exact moments. This script turns
that event stream into MusicXML: one part per voice, measures of the edition's
bar length, notes crossing a bar line split into tied notes.

Chant (Bogurodzica): the gabc file is converted directly: unmeasured
(senza-misura), each neume note an eighth note without stem, a punctum mora
a quarter, a measure per divisio.

Needs LilyPond 2.24 and Python 3.9+; no Python packages.
"""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
HOUSE_LY = ROOT / "house" / "lilypond"
EVENTS_ILY = ROOT / "tools" / "musicxml-events.ily"
EDITOR = "Mikołaj Derduń"
RIGHTS = "CC BY 4.0. Credit \u201ced. Mikołaj Derduń, Polish Early Music\u201d. The music is in the public domain."

STEPS = "CDEFGAB"
# note types by length in whole notes (undotted)
TYPES = {F(4): "long", F(2): "breve", F(1): "whole", F(1, 2): "half", F(1, 4): "quarter",
         F(1, 8): "eighth", F(1, 16): "16th", F(1, 32): "32nd", F(1, 64): "64th"}
LOG_TYPES = {-2: "long", -1: "breve", 0: "whole", 1: "half", 2: "quarter", 3: "eighth",
             4: "16th", 5: "32nd", 6: "64th"}
# values a split note may take, longest first: plain and single-dotted
PIECES = sorted([(v, 0) for v in TYPES] + [(v * F(3, 2), 1) for v in TYPES if v < 4],
                key=lambda x: -x[0])
ACC = {F(0): "natural", F(1): "sharp", F(-1): "flat", F(2): "double-sharp", F(-2): "flat-flat"}
BARSTYLE = {"||": "light-light", "|.": "light-heavy", "'": "tick", "|": "regular",
            ".|:": None, ":|.": None, ":..:": None, ",": "short"}


# ------------------------------------------------------------------ metadata

def tex_arg(text: str, cmd: str) -> str | None:
    m = re.search(r"\\" + cmd + r"(?:\[[^\]]*\])?\{([^}]*)\}", text)
    return m.group(1).strip() if m else None


def tex_plain(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.replace("\\,", "\u202f").replace("~", "\u00a0").replace("--", "–")
    s = re.sub(r"\\[a-zA-Z]+\s*", "", s)
    return s.replace("{", "").replace("}", "").strip()


def edition_meta(ed: Path) -> dict:
    src = next(iter(sorted(ed.glob("*-critical.lytex")) + sorted(ed.glob("*-critical.tex"))), None)
    text = src.read_text(encoding="utf-8") if src else ""
    return {
        "title": tex_plain(tex_arg(text, "title")) or ed.name,
        "subtitle": tex_plain(tex_arg(text, "subtitle")),
        "composer": tex_plain(tex_arg(text, "composer")) or "",
    }


# ------------------------------------------------------------------ event stream

def frac(s: str) -> F:
    return F(s)


@dataclass
class Ev:
    kind: str            # note | rest
    voice: str
    t: F
    bar: int
    pos: F
    mlen: F
    timed: bool
    log: int
    dots: int
    scale: F
    length: F
    octave: int | None = None
    step: int | None = None
    alter: F = F(0)
    flags: set = field(default_factory=set)
    keyalts: str = ""
    tie: bool = False
    lyric: dict | None = None
    texts: list = field(default_factory=list)
    lig: list = field(default_factory=list)
    slur: list = field(default_factory=list)
    arts: list = field(default_factory=list)
    origin: tuple | None = None      # (file, line, column) of the note in the LilyPond source


@dataclass
class Segment:          # one \score block
    events: list = field(default_factory=list)
    voices: dict = field(default_factory=dict)      # id -> header fields
    bars: list = field(default_factory=list)        # (t, type)
    marks: list = field(default_factory=list)       # (t, text)
    voltas: set = field(default_factory=set)        # (t, start|stop, numbers)
    repeats: set = field(default_factory=set)       # (t, start|end)


def parse_events(lines: list[str]) -> list[Segment]:
    segs: list[Segment] = []
    pending = defaultdict(list)   # (voice, t) -> [(kind, value)] for tie/slur/... events
    lyr = defaultdict(dict)       # (voice, t, verse) -> lyric dict
    for line in lines:
        f = line.split("\t")
        kind = f[0]
        if kind == "score":
            segs.append(Segment())
            pending.clear()
            continue
        seg = segs[-1]
        voice, t = f[1], f[2]
        if kind == "voice":
            seg.voices.setdefault(voice, {
                "clef": f[3], "clefpos": int(f[4] or 0), "cleftr": int(f[5] or 0),
                "keyalts": f[6], "time": f[7], "name": f[8], "short": f[9] if len(f) > 9 else ""})
        elif kind in ("note", "rest"):
            e = Ev(kind=kind, voice=voice, t=frac(t), bar=int(f[3] or 1), pos=frac(f[4]),
                   mlen=frac(f[5]), timed=f[6] == "timed", log=int(f[7]), dots=int(f[8]),
                   scale=frac(f[9]), length=frac(f[10]))
            if kind == "note":
                e.octave, e.step, e.alter = int(f[11]), int(f[12]), frac(f[13])
            e.flags = set(x for x in f[14].split(",") if x)
            if len(f) > 15 and f[15]:
                e.keyalts = f[15].split("|")[2]
            seg.events.append(e)
        elif kind in ("tie", "slur", "lig", "art", "text"):
            pending[(voice, frac(t))].append((kind, f[3] if len(f) > 3 else ""))
        elif kind == "origin":
            pending[(voice, frac(t))].append((kind, (f[3], f[4], f[5])))
        elif kind == "lyric":
            text = f[3]
            verse = f[7] if len(f) > 7 and f[7] else "1"
            if text.strip():
                lyr[(voice, frac(t), verse)].update(text=text, italic=f[6] == "italic")
        elif kind == "lyric-hyphen":
            lyr[(voice, frac(t), f[3] if len(f) > 3 and f[3] else "1")]["hyphen"] = True
        elif kind == "lyric-extender":
            lyr[(voice, frac(t), f[3] if len(f) > 3 and f[3] else "1")]["extender"] = True
        elif kind == "bar":
            seg.bars.append((frac(t), f[3]))
        elif kind == "mark":
            seg.marks.append((frac(t), f[3]))
        elif kind == "volta":
            seg.voltas.add((frac(t), f[3], f[4].strip("()").replace(" ", ",")))
        elif kind in ("repeat-start", "repeat-end"):
            seg.repeats.add((frac(t), kind[7:]))
    segs = [s for s in segs if s.events]
    # second pass: attach per (voice, t)
    for seg in segs:
        for e in seg.events:
            for k, v in pending.get((e.voice, e.t), []):
                if e.kind != "note":
                    continue
                if k == "tie":
                    e.tie = True
                elif k == "slur":
                    e.slur.append(v)
                elif k == "lig":
                    e.lig.append(v)
                elif k == "art":
                    e.arts.append(v)
                elif k == "text":
                    e.texts.append(v)
                elif k == "origin" and e.origin is None:
                    e.origin = v
            if e.kind == "note":
                verses = {k[2]: v for k, v in lyr.items()
                          if k[0] == e.voice and k[1] == e.t and "text" in v}
                if verses:
                    e.lyric = dict(sorted(verses.items(), key=lambda kv: int(kv[0])))
    return segs


def parse_events_all(path: Path) -> list[Segment]:
    """Split the dump at each \\score (ties, lyrics etc. are keyed by moment,
    which restarts at 0 in every score) and parse each part."""
    chunks: list[list[str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("score\t") or not chunks:
            chunks.append([])
        chunks[-1].append(line)
    return [seg for c in chunks for seg in parse_events(c)]


# ------------------------------------------------------------------ measures

@dataclass
class Measure:
    number: str
    start: F
    length: F
    implicit: bool = False
    free: bool = False
    time: tuple | None = None        # (beats, beat-type, print?) when it changes here
    left: list = field(default_factory=list)    # barline xml
    right: list = field(default_factory=list)
    right_style: str | None = None
    marks: list = field(default_factory=list)   # (t, text)


def seg_end(seg: Segment) -> F:
    return max(e.t + e.length for e in seg.events)


def build_measures(seg: Segment, prefix: str) -> list[Measure]:
    end = seg_end(seg)
    timed = all(e.timed for e in seg.events)
    ms: list[Measure] = []
    if not timed:
        cuts = sorted({t for t, b in seg.bars if 0 < t < end})
        bounds = [F(0)] + cuts + [end]
        for i in range(len(bounds) - 1):
            ms.append(Measure(number=f"{prefix}{i + 1}", start=bounds[i],
                              length=bounds[i + 1] - bounds[i], implicit=True, free=True))
    else:
        by_start = {}
        for e in seg.events:
            by_start.setdefault(e.t - e.pos, e.mlen)
        t, mlen = F(0), by_start.get(F(0), seg.events[0].mlen)
        while t < end:
            mlen = by_start.get(t, mlen)
            ms.append(Measure(number="", start=t, length=min(mlen, end - t)))
            t += mlen
        # number from LilyPond's bar numbers: most common offset
        offs = defaultdict(int)
        starts = [m.start for m in ms]
        for e in seg.events:
            if e.t > 0:
                i = starts.index(e.t - e.pos) if (e.t - e.pos) in starts else None
                if i is not None:
                    offs[e.bar - i] += 1
        off = max(offs, key=offs.get) if offs else 1
        for i, m in enumerate(ms):
            m.number = str(i + off)
    # bar lines, repeats, endings, marks
    def at_end(t):
        return next((m for m in ms if m.start + m.length == t), None)

    def at_start(t):
        return next((m for m in ms if m.start == t), None)

    for t, b in seg.bars:
        m = at_end(t)
        if m and BARSTYLE.get(b):
            m.right_style = BARSTYLE[b]
    for t, kind in sorted(seg.repeats):
        if kind == "start" and at_start(t):
            at_start(t).left.append('<repeat direction="forward"/>')
        elif kind == "end" and at_end(t):
            m = at_end(t)
            m.right_style = "light-heavy"
            m.right.append('<repeat direction="backward"/>')
    for t, kind, nums in sorted(seg.voltas):
        if kind == "start" and at_start(t):
            at_start(t).left.insert(0, f'<ending number="{nums}" type="start">{nums.replace(",", ", ")}.</ending>')
        elif kind == "stop" and at_end(t):
            at_end(t).right.insert(0, f'<ending number="{nums}" type="stop"/>')
    for t, text in seg.marks:
        m = next((m for m in ms if m.start <= t < m.start + m.length), None) or ms[-1]
        m.marks.append((t, text))
    return ms


# ------------------------------------------------------------------ notes to xml

def pieces(length: F) -> list[tuple[F, int]]:
    out = []
    while length > 0:
        for v, d in PIECES:
            if v <= length:
                out.append((v, d))
                length -= v
                break
        else:
            raise ValueError(f"cannot notate remaining length {length}")
    return out


def fifths_of(keyalts: str) -> int:
    alts = {}
    for item in filter(None, keyalts.split(",")):
        n, a = item.split(":")
        alts[int(n)] = F(a)
    flats = [6, 2, 5, 1, 4, 0, 3]
    sharps = [3, 0, 4, 1, 5, 2, 6]
    nf = sum(1 for n in flats if alts.get(n, 0) < 0)
    ns = sum(1 for n in sharps if alts.get(n, 0) > 0)
    return ns - nf


def key_alter(keyalts: str, step: int) -> F:
    for item in filter(None, keyalts.split(",")):
        n, a = item.split(":")
        if int(n) == step:
            return F(a) * 2
    return F(0)


def clef_xml(v: dict) -> str:
    glyph, pos, tr = v["clef"], v["clefpos"], v["cleftr"]
    sign = {"clefs.G": "G", "clefs.F": "F", "clefs.C": "C"}.get(glyph, "G")
    line = pos // 2 + 3
    oc = f"<clef-octave-change>{tr // 7}</clef-octave-change>" if tr else ""
    return f"<clef><sign>{sign}</sign><line>{line}</line>{oc}</clef>"


class PartWriter:
    def __init__(self, divisions: int):
        self.div = divisions
        self.in_word = {}
        self.srcmap = []      # (measure number, position in the measure, origin)

    def dur(self, length: F) -> int:
        d = length * 4 * self.div
        assert d.denominator == 1, length
        return int(d)

    def lyric_xml(self, ly: dict, verse: str = "1") -> str:
        hy = ly.get("hyphen", False)
        inw = self.in_word.get(verse, False)
        if hy:
            syl = "middle" if inw else "begin"
        else:
            syl = "end" if inw else "single"
        self.in_word[verse] = hy
        text = ly["text"].replace("_", " ")
        style = ' font-style="italic"' if ly.get("italic") else ""
        parts = text.split("~")
        body = f"<syllabic>{syl}</syllabic>" + "<elision>\u203f</elision>".join(
            f"<text{style}>{escape(p)}</text>" for p in parts)
        ext = "<extend/>" if ly.get("extender") else ""
        return f'<lyric number="{verse}">{body}{ext}</lyric>'

    def note_xml(self, e: Ev | None, length: F, ntype: str, dots: int, *, first: bool, last: bool,
                 tie_in: bool, tie_out: bool, chant: bool = False, measure_rest: bool = False,
                 stemless: bool = False) -> str:
        x = ["<note>"]
        if e is None or e.kind == "rest":
            hidden = e is None and not measure_rest
            if measure_rest:
                x[0] = "<note>"
                x.append('<rest measure="yes"/>')
            else:
                x.append("<rest/>")
            x.append(f"<duration>{self.dur(length)}</duration>")
            if not measure_rest:
                x.append(f"<type>{ntype}</type>" + "<dot/>" * dots)
            if hidden:
                x[0] = '<note print-object="no">'
            x.append("</note>")
            return "".join(x)
        x.append(f"<pitch><step>{STEPS[e.step]}</step>")
        alter = e.alter * 2
        if alter:
            x.append(f"<alter>{alter.numerator if alter.denominator == 1 else float(alter)}</alter>")
        x.append(f"<octave>{e.octave + 4}</octave></pitch>")
        x.append(f"<duration>{self.dur(length)}</duration>")
        if tie_in:
            x.append('<tie type="stop"/>')
        if tie_out:
            x.append('<tie type="start"/>')
        if first and "supplied" in e.flags:
            x.append('<level bracket="yes" reference="no">supplied</level>')
        size = ' size="cue"' if "editorial-note" in e.flags else ""
        x.append(f"<type{size}>{ntype}</type>" + "<dot/>" * dots)
        if first:
            ficta = "ficta" in e.flags
            if alter != key_alter(e.keyalts, e.step) or ficta:
                acc = ACC.get(alter, "natural")
                x.append(f'<accidental editorial="yes">{acc}</accidental>' if ficta
                         else f"<accidental>{acc}</accidental>")
        if stemless or chant:
            x.append("<stem>none</stem>")
        n = []
        if tie_in:
            n.append('<tied type="stop"/>')
        if tie_out:
            dashed = ' line-type="dashed"' if ("tie-dashed" in e.flags and last) else ""
            n.append(f'<tied type="start"{dashed}/>')
        if first:
            for s in e.slur:
                n.append(f'<slur type="{s}" number="1"/>')
        if last and "fermata" in e.arts:
            n.append('<fermata type="upright"/>')
        if n:
            x.append("<notations>" + "".join(n) + "</notations>")
        if first and e.lyric:
            x.extend(self.lyric_xml(ly, v) for v, ly in e.lyric.items())
        x.append("</note>")
        return "".join(x)


def words(text: str, italic=True, placement="above") -> str:
    st = ' font-style="italic"' if italic else ""
    return (f'<direction placement="{placement}"><direction-type><words{st}>{escape(text)}</words>'
            f"</direction-type></direction>")


def bracket(kind: str) -> str:
    return (f'<direction placement="above"><direction-type><bracket type="{kind}" number="1" '
            f'line-end="down" line-type="solid"/></direction-type></direction>')


def all_lengths(segs) -> list[F]:
    out = []
    for seg in segs:
        for e in seg.events:
            out += [e.length, e.t, e.pos]
    return out


def divisions_for(lengths) -> int:
    d = 1
    for L in lengths:
        q = F(L) * 4
        d = d * q.denominator // math.gcd(d, q.denominator)
    return d


def render_voice_measures(pw: PartWriter, seg: Segment, voice: str, ms: list[Measure],
                          top: bool) -> list[str]:
    """XML bodies (notes and directions) for every measure of one voice in one segment."""
    evs = sorted((e for e in seg.events if e.voice == voice), key=lambda e: e.t)
    out = []
    chant = any(not e.timed for e in evs)
    # events (or rests filling gaps) in time order
    filled = []
    t = F(0)
    for e in evs:
        if e.t > t:
            filled.append((t, e.t - t, None))
        if e.t < t:      # chord or overlap: not expected in these scores
            raise ValueError(f"overlapping events in {voice} at {e.t}")
        filled.append((e.t, e.length, e))
        t = e.t + e.length
    end = ms[-1].start + ms[-1].length
    if t < end:
        filled.append((t, end - t, None))
    bodies = {m.number: [] for m in ms}
    prev_tie = False
    for (t0, L, e) in filled:
        # fragments by measure
        frags = []
        for m in ms:
            a, b = max(t0, m.start), min(t0 + L, m.start + m.length)
            if a < b:
                frags.append((m, a, b - a))
        split = len(frags) > 1
        notes = []   # (measure, t, length, type, dots)
        for (m, a, la) in frags:
            if e is not None and not split and (e.scale != 1 or e.length == la) and e.log in LOG_TYPES:
                # one note in one measure: keep the edition's own value (also a
                # scaled final such as \longa*1/2, or a head drawn as a longa)
                hl = next((int(f.split("=")[1]) for f in e.flags if f.startswith("head-log=")), None)
                log = hl if (hl is not None and e.kind == "note") else e.log
                notes.append((m, a, la, LOG_TYPES[log], e.dots))
            else:
                tt = a
                for v, d in pieces(la):
                    base = v if d == 0 else v * F(2, 3)
                    notes.append((m, tt, v, TYPES[base], d))
                    tt += v
        is_note = e is not None and e.kind == "note"
        for i, (m, a, la, ntype, dots) in enumerate(notes):
            first, last = i == 0, i == len(notes) - 1
            body = bodies[m.number]
            if is_note and first:
                if e.origin:
                    pw.srcmap.append((m.number, a - m.start, e.origin))
                for tx in e.texts:
                    body.append(words(tx, italic=tx.startswith("[")))
                if "start" in e.lig:
                    body.append(bracket("start"))
            body.append(pw.note_xml(e, la, ntype, dots, first=first, last=last,
                                    tie_in=(first and prev_tie) or (not first and is_note),
                                    tie_out=(not last and is_note) or (last and is_note and e.tie),
                                    chant=chant))
            if is_note and last and "stop" in e.lig:
                body.append(bracket("stop"))
        prev_tie = is_note and e.tie
    # whole-measure rests where the voice is silent for a full measure (instead of split rests)
    res = []
    for m in ms:
        b = bodies[m.number]
        if all('<rest' in x for x in b if x.startswith("<note")) and \
           all(x.startswith("<note") for x in b) and b:
            b = [pw.note_xml(None, m.length, "", 0, first=True, last=True, tie_in=False,
                             tie_out=False, measure_rest=True)]
        if top:
            for (t, text) in m.marks:
                if t == m.start + m.length:
                    b = b + [words(text)]
                else:
                    b = [words(text)] + b
        res.append("".join(b))
    return res


def silent_measures(pw: PartWriter, ms: list[Measure]) -> list[str]:
    return [pw.note_xml(None, m.length, "", 0, first=True, last=True, tie_in=False,
                        tie_out=False, measure_rest=True) for m in ms]


# Source map of the last write_score: (part name, measure number, position in
# the measure in whole notes, (file, line, column)). Written beside the
# MusicXML as <slug>.srcmap.tsv so that tools/analyser can point at voices.ily.
SRCMAP: list = []


def write_srcmap(ed: Path, path: Path) -> None:
    rows = ["part\tmeasure\tposition\tfile\tline\tcolumn"]
    for part, measure, pos, (fname, line, col) in SRCMAP:
        fp = Path(fname)
        if not fp.is_absolute():
            fp = (ed / "music" / fp) if (ed / "music" / fp).exists() else (ROOT / fp)
        try:
            fname = fp.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            fname = fp.name
        rows.append(f"{part}\t{measure}\t{pos}\t{fname}\t{line}\t{col}")
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_score(meta: dict, segs: list[Segment], sign_symbol: str | None) -> str:
    SRCMAP.clear()
    # parts in order of first appearance
    order, heads = [], {}
    for seg in segs:
        for v, h in seg.voices.items():
            if v not in heads:
                order.append(v)
                heads[v] = h
    div = divisions_for(all_lengths(segs) + [F(1, 4)])
    seg_ms = []
    free_n = 0
    for seg in segs:
        free = not all(e.timed for e in seg.events)
        if free:
            free_n += 1
        ms = build_measures(seg, prefix=("v" if free_n == 1 else f"v{free_n}-") if free else "")
        seg_ms.append(ms)
    pid = {v: f"P{i + 1}" for i, v in enumerate(order)}
    part_names = {}
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0">']
    out.append(f"<work><work-title>{escape(meta['title'])}</work-title></work>")
    if meta.get("subtitle"):
        out.append(f"<movement-title>{escape(meta['subtitle'])}</movement-title>")
    out.append("<identification>")
    if meta["composer"]:
        out.append(f'<creator type="composer">{escape(meta["composer"])}</creator>')
    out.append(f'<creator type="editor">{escape(EDITOR)}</creator>')
    out.append(f"<rights>{escape(RIGHTS)}</rights>")
    out.append("<encoding><software>Polish Early Music tools/export_musicxml.py "
               "(from the LilyPond 2.24 event stream)</software>"
               '<supports element="accidental" type="yes"/>'
               '<supports element="beam" type="no"/>'
               '<supports element="stem" type="no"/>'
               "</encoding>")
    out.append("</identification>")
    out.append(f'<credit page="1"><credit-type>title</credit-type><credit-words justify="center" '
               f'valign="top">{escape(meta["title"])}</credit-words></credit>')
    if meta.get("subtitle"):
        out.append(f'<credit page="1"><credit-type>subtitle</credit-type><credit-words justify="center" '
                   f'valign="top">{escape(meta["subtitle"])}</credit-words></credit>')
    if meta["composer"]:
        out.append(f'<credit page="1"><credit-type>composer</credit-type><credit-words justify="right" '
                   f'valign="top">{escape(meta["composer"])}</credit-words></credit>')
    out.append(f'<credit page="1"><credit-type>arranger</credit-type><credit-words justify="right" '
               f'valign="top">ed. {escape(EDITOR)}</credit-words></credit>')
    out.append(f'<credit page="1"><credit-type>rights</credit-type><credit-words justify="center" '
               f'valign="bottom">{escape("CC BY 4.0")}</credit-words></credit>')
    out.append("<part-list>")
    for v in order:
        h = heads[v]
        name = h["name"] or v.capitalize()
        short = h["short"]
        if name == "℣.":       # the chant psalm verse of Nunc scio vere
            name, short = "Versus (chant)", "℣."
        part_names[v] = name
        out.append(f'<score-part id="{pid[v]}"><part-name>{escape(name)}</part-name>'
                   + (f"<part-abbreviation>{escape(short)}</part-abbreviation>" if short else "")
                   + "</score-part>")
    out.append("</part-list>")
    for v in order:
        pw = PartWriter(div)
        out.append(f'<part id="{pid[v]}">')
        first_attr = True
        last_clef = None
        for si, (seg, ms) in enumerate(zip(segs, seg_ms)):
            present = v in seg.voices
            seg_top = next(x for x in order if x in seg.voices)
            h = seg.voices.get(v) or heads[v]       # clef: the part's own
            ref = seg.voices[seg_top]               # key and time: as the voices sounding here
            if present:
                bodies = render_voice_measures(pw, seg, v, ms, top=(v == seg_top))
            else:
                bodies = silent_measures(pw, ms)
            for mi, (m, body) in enumerate(zip(ms, bodies)):
                attrs = []
                if first_attr:
                    attrs.append(f"<divisions>{div}</divisions>")
                if mi == 0:
                    attrs.append(f"<key><fifths>{fifths_of(ref['keyalts'])}</fifths></key>")
                    if m.free:
                        attrs.append("<time><senza-misura/></time>")
                    else:
                        ts = ref["time"] or "2/1"
                        b_, bt = ts.split("/")
                        sym = f' symbol="{sign_symbol}"' if sign_symbol and sign_symbol != "none" else ""
                        po = ' print-object="no"' if sign_symbol == "none" else ""
                        attrs.append(f"<time{sym}{po}><beats>{b_}</beats><beat-type>{bt}</beat-type></time>")
                    clef = clef_xml(h) if present else last_clef
                    if clef and clef != last_clef or first_attr:
                        attrs.append(clef or clef_xml(h))
                        last_clef = clef or clef_xml(h)
                elif not m.free and mi > 0 and m.length != ms[mi - 1].length:
                    # a final bar of another length (\finalis): unprinted time change
                    beats = m.length / F(1, 1)
                    if beats.denominator == 1:
                        attrs.append(f'<time print-object="no"><beats>{beats.numerator}</beats>'
                                     f"<beat-type>1</beat-type></time>")
                    else:
                        q = m.length * 4
                        attrs.append(f'<time print-object="no"><beats>{q.numerator}</beats>'
                                     f"<beat-type>{4 * q.denominator}</beat-type></time>")
                implicit = ' implicit="yes"' if m.implicit else ""
                out.append(f'<measure number="{m.number}"{implicit}>')
                if attrs:
                    out.append("<attributes>" + "".join(attrs) + "</attributes>")
                if m.left:
                    out.append('<barline location="left">' + "".join(m.left) + "</barline>")
                out.append(body)
                if m.right or m.right_style:
                    style = f"<bar-style>{m.right_style}</bar-style>" if m.right_style else ""
                    # MusicXML order: bar-style, ..., ending, repeat
                    ending = [x for x in m.right if x.startswith("<ending")]
                    rep = [x for x in m.right if x.startswith("<repeat")]
                    out.append('<barline location="right">' + style + "".join(ending + rep) + "</barline>")
                out.append("</measure>")
                first_attr = False
        SRCMAP.extend((part_names[v],) + x for x in pw.srcmap)
        out.append("</part>")
    out.append("</score-partwise>")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ LilyPond run

def run_lilypond(ed: Path, tmp: Path) -> Path:
    music = ed / "music"
    events = tmp / f"{ed.name}.events"
    wrapper = tmp / f"{ed.name}-wrapper.ly"
    wrapper.write_text(
        '\\version "2.24.0"\n'
        f'#(define prx-out "{events.as_posix()}")\n'
        f'\\include "{EVENTS_ILY.as_posix()}"\n'
        '\\include "score.ly"\n', encoding="utf-8")
    cmd = ["lilypond", "-dno-print-pages", "-I", str(HOUSE_LY), "-I", str(music),
           "-o", str(tmp / ed.name), str(wrapper)]
    r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
    if r.returncode != 0 or not events.exists():
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit(f"lilypond failed for {ed.name}")
    return events


# ------------------------------------------------------------------ chant (gabc)

GABC_BARS = {",": "tick", ";": "short", ":": "regular", "::": "light-light"}


def gabc_to_musicxml(meta: dict, gabc: Path) -> tuple[str, int]:
    text = gabc.read_text(encoding="utf-8")
    body = text.split("%%", 1)[1]
    clef = re.search(r"\((c[1-4]|f[1-4])\)", body)
    assert clef and clef.group(1) == "c4", "only the c4 clef is supported"
    body = body[clef.end():]
    # c4: line 4 is c' (MusicXML C4); gabc letter a = lowest space below the staff
    base_letter = ord("j")             # j = c' with c4

    def pitch(ch):
        n = ord(ch.lower()) - base_letter     # diatonic steps from c'
        return STEPS[n % 7], 4 + n // 7

    tokens = re.findall(r"([^()]*)\(([^)]*)\)", body)
    measures, cur = [], []
    nnotes = 0
    for raw, neume in tokens:
        syl_text = re.sub(r"<[^>]+>", "", raw)
        syl_text = syl_text.strip()
        neume = neume.strip()
        if neume in GABC_BARS:
            measures.append((cur, GABC_BARS[neume]))
            cur = []
            continue
        if neume == "z":
            continue      # forced line break
        if not neume:
            continue      # stanza numbers <b>2.</b>() and empty syllables
        notes = []
        for ch in neume:
            if ch.lower() in "abcdefghijklm":
                notes.append([ch, F(1, 8)])
            elif ch == "." and notes:
                notes[-1][1] = F(1, 4)        # punctum mora: doubled
        # word boundaries: the next token starting with whitespace ends a word
        cur.append({"text": syl_text, "notes": notes, "space_before": raw[:1].isspace()})
        nnotes += len(notes)
    if cur:
        measures.append((cur, None))
    # syllabic
    syls = [s for m, _ in measures for s in m]
    for i, s in enumerate(syls):
        nxt_space = i + 1 >= len(syls) or syls[i + 1]["space_before"]
        s["hyphen"] = not nxt_space
    div = 2
    x = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
         '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
         '"http://www.musicxml.org/dtds/partwise.dtd">',
         '<score-partwise version="4.0">',
         f"<work><work-title>{escape(meta['title'])}</work-title></work>",
         "<identification>",
         f'<creator type="composer">{escape(meta["composer"])}</creator>' if meta["composer"] else "",
         f'<creator type="editor">{escape(EDITOR)}</creator>',
         f"<rights>{escape(RIGHTS)}</rights>",
         "<encoding><software>Polish Early Music tools/export_musicxml.py (from gabc)</software>"
         '<supports element="stem" type="yes"/></encoding>',
         "</identification>",
         f'<credit page="1"><credit-type>title</credit-type><credit-words justify="center" valign="top">'
         f'{escape(meta["title"])}</credit-words></credit>',
         f'<credit page="1"><credit-type>composer</credit-type><credit-words justify="right" valign="top">'
         f'{escape(meta["composer"])}</credit-words></credit>',
         f'<credit page="1"><credit-type>arranger</credit-type><credit-words justify="right" valign="top">'
         f'ed. {escape(EDITOR)}</credit-words></credit>',
         '<credit page="1"><credit-type>rights</credit-type><credit-words justify="center" valign="bottom">'
         'CC BY 4.0</credit-words></credit>',
         '<part-list><score-part id="P1"><part-name>Cantus</part-name></score-part></part-list>',
         '<part id="P1">']
    in_word = False
    for mi, (syl_list, bar) in enumerate(measures):
        x.append(f'<measure number="{mi + 1}" implicit="yes">')
        if mi == 0:
            x.append(f"<attributes><divisions>{div}</divisions><key><fifths>0</fifths></key>"
                     "<time><senza-misura/></time><clef><sign>C</sign><line>4</line></clef></attributes>")
        for s in syl_list:
            ns = s["notes"]
            for i, (ch, L) in enumerate(ns):
                step, octave = pitch(ch)
                typ = "eighth" if L == F(1, 8) else "quarter"
                n = [f"<note><pitch><step>{step}</step><octave>{octave}</octave></pitch>",
                     f"<duration>{int(L * 4 * div)}</duration><voice>1</voice><type>{typ}</type>",
                     "<stem>none</stem>"]
                sl = []
                if len(ns) > 1 and i == 0:
                    sl.append('<slur type="start" number="1"/>')
                if len(ns) > 1 and i == len(ns) - 1:
                    sl.append('<slur type="stop" number="1"/>')
                if sl:
                    n.append("<notations>" + "".join(sl) + "</notations>")
                if i == 0 and s["text"]:
                    hy = s["hyphen"]
                    syl = ("middle" if in_word else "begin") if hy else ("end" if in_word else "single")
                    in_word = hy
                    n.append(f'<lyric number="1"><syllabic>{syl}</syllabic>'
                             f"<text>{escape(s['text'])}</text></lyric>")
                n.append("</note>")
                x.append("".join(n))
        if bar:
            x.append(f'<barline location="right"><bar-style>{bar}</bar-style></barline>')
        x.append("</measure>")
    x.append("</part></score-partwise>")
    return "\n".join(filter(None, x)) + "\n", nnotes


# ------------------------------------------------------------------ main

def export(ed: Path, keep: Path | None) -> Path:
    meta = edition_meta(ed)
    out = ed / "pdf" / f"{ed.name}.musicxml"
    out.parent.mkdir(exist_ok=True)
    score = ed / "music" / "score.ly"
    if score.exists():
        with tempfile.TemporaryDirectory(prefix="prx-") as td:
            events = run_lilypond(ed, Path(td))
            if keep:
                keep.mkdir(parents=True, exist_ok=True)
                shutil.copy(events, keep / events.name)
            segs = parse_events_all(events)
        src = score.read_text(encoding="utf-8")
        sign = "none" if re.search(r'^\s*prSign\s*=\s*""', src, re.M) else "cut"
        out.write_text(write_score(meta, segs, sign), encoding="utf-8")
        write_srcmap(ed, out.with_suffix(".srcmap.tsv"))
    else:
        gabc = sorted(p for p in (ed / "music").glob("*.gabc") if "performance" not in p.name)
        if not gabc:
            raise SystemExit(f"{ed.name}: no score.ly or gabc")
        xml, _ = gabc_to_musicxml(meta, gabc[0])
        out.write_text(xml, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--events", type=Path, help="keep the LilyPond event dumps in this directory")
    a = ap.parse_args()
    eds = [ROOT / "editions" / s for s in a.slugs] if a.slugs else \
        sorted(p for p in (ROOT / "editions").iterdir() if (p / "music").is_dir())
    for ed in eds:
        if not ed.is_dir():
            raise SystemExit(f"no edition {ed.name}")
        export(ed, a.events)


if __name__ == "__main__":
    main()
