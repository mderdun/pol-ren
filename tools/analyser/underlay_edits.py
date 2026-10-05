"""The lyrics in voices.ily, tied to the analyser's notes; and underlay edits
made on the review page, applied back to them.

    python -m tools.analyser edits apply EDITS.json [--dry-run] [--allow-text]

A voice's lyrics are \\lyricmode blocks (`cantusWords`, `cantusWordsTwo` for
the second stanza, or `cantusAntText` and `cantusDoxText` read in file order
as one line). Under \\lyricsto every syllable and every `_` takes one note, so
the k-th slot of a voice's lyrics belongs to its k-th sounding note (tied notes
are one note to the analyser and to LilyPond). `--` and `__` are drawn after
the syllable before them. `align()` checks the slots against the analyser's
syllables; where they disagree the voice is not tied (the review page then
shows no edits there and `apply` refuses).

The review page (review.py) uses `align()` to tag the lyric syllables of the
SVG, whose textedit links point at the tokens parsed here. `apply` takes the
edits the page saved (a JSON list of its db documents, or {"edits": [...]})
and rewrites the voice's block: syllables, `--`, `__` and `_` are rebuilt for
the whole block from the slots, which reproduces an unedited block token for
token (checked before any change). See docs/analyser.md, "The review page".
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path

from .ingest import ROOT

BLOCK = re.compile(r"^([A-Za-z]+)\s*=\s*\\lyricmode\s*\{", re.M)
TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|\S+')
VERSE_SUFFIX = {"": "1", "One": "1", "Two": "2", "Three": "3", "Four": "4", "Five": "5"}
# voices.ily is written by a script for these editions: apply reports, never rewrites
GENERATED = {"nunc-scio-vere": "editions/nunc-scio-vere/music/underlay.py (then build.py)"}


@dataclass
class Slot:
    kind: str                    # "syl" | "skip"
    text: str = ""               # the syllable, unquoted
    raw: str = ""                # the token as written
    prefix: str = ""             # a command written before it (\rep)
    line: int = 0                # 1-based line, 0-based column of the token
    col: int = 0
    conn: str = ""               # "--" | "__" | "" after it
    conn_at: tuple | None = None
    mel: int = 0                 # skips after it, as written


@dataclass
class Block:
    name: str
    voice: str
    verse: str
    start: int                   # offsets of the contents, between the braces
    end: int
    head: str = ""               # \set stanza = "1." and the like, kept as written
    slots: list = field(default_factory=list)
    ok: bool = True
    why: str = ""


def _unquote(t: str) -> str:
    return t[1:-1] if len(t) >= 2 and t[0] == '"' and t[-1] == '"' else t


def _line_col(text: str, off: int) -> tuple[int, int]:
    line = text.count("\n", 0, off) + 1
    return line, off - (text.rfind("\n", 0, off) + 1)


def parse(text: str, parts: list[str]) -> list[Block]:
    """Every \\lyricmode block whose name starts with a voice's name."""
    lower = {p.lower(): p for p in parts}
    out = []
    for m in BLOCK.finditer(text):
        name = m.group(1)
        voice = next((lower[k] for k in sorted(lower, key=len, reverse=True) if name.lower().startswith(k)), None)
        if voice is None:
            continue
        rest = name[len(voice):]
        sfx = re.sub(r"^(Words|Text|Lyrics)", "", rest)
        if sfx in VERSE_SUFFIX:
            verse = VERSE_SUFFIX[sfx]
        else:
            # sections as stanzas (Nunc: cantusAntText, cantusDoxText): the
            # export numbers them in file order
            verse = str(1 + sum(1 for o in out if o.voice == voice))
        depth, i = 1, m.end()
        while i < len(text) and depth:
            if text[i] == '"':
                j = i + 1
                while j < len(text) and text[j] != '"':
                    j += 2 if text[j] == "\\" else 1
                i = j + 1
                continue
            if text[i] == "%":
                i = text.find("\n", i)
                i = len(text) if i < 0 else i
                continue
            depth += {"{": 1, "}": -1}.get(text[i], 0)
            i += 1
        b = Block(name=name, voice=voice, verse=verse, start=m.end(), end=i - 1)
        _tokens(text, b)
        out.append(b)
    return out


def _tokens(text: str, b: Block) -> None:
    body = text[b.start:b.end]
    body_nc = re.sub(r"%[^\n]*", lambda mm: " " * len(mm.group(0)), body)
    toks = [(t.group(0), b.start + t.start()) for t in TOKEN.finditer(body_nc)]
    k, prefix, head = 0, "", []
    while k < len(toks):
        t, off = toks[k]
        if t == "\\set" and not b.slots:
            # \set stanza = "1."
            head.append(" ".join(x for x, _ in toks[k:k + 4]))
            k += 4
            continue
        if t in ("\\override", "\\once", "\\markup", "\\set", "\\unset", "\\tweak"):
            b.ok, b.why = False, f"unsupported command {t} in {b.name}"
            k += 1
            continue
        if t.startswith("\\"):
            # a command with no argument that marks the next syllable (\rep, \ijClose, \edText)
            prefix += t + " "
            k += 1
            continue
        if t in ("--", "__"):
            if not b.slots:
                b.ok, b.why = False, f"{t} before any syllable in {b.name}"
            else:
                b.slots[-1].conn, b.slots[-1].conn_at = t, _line_col(text, off)
            k += 1
            continue
        line, col = _line_col(text, off)
        if t == "_":
            b.slots.append(Slot("skip", raw=t, line=line, col=col, prefix=prefix))
        elif t in ("{", "}"):
            b.ok, b.why = False, f"unexpected token {t} in {b.name}"
        else:
            b.slots.append(Slot("syl", text=_unquote(t), raw=t, line=line, col=col, prefix=prefix))
        prefix = ""
        k += 1
    b.head = " ".join(head)
    for i, s in enumerate(b.slots):
        if s.kind == "syl":
            j = i + 1
            while j < len(b.slots) and b.slots[j].kind == "skip":
                j += 1
            s.mel = j - i - 1


def _norm(s: str) -> str:
    return re.sub(r"[\s_~]+", " ", s or "").strip().lower()


@dataclass
class VoiceLyrics:
    """One voice's lyrics for one verse: blocks, slots, and the notes they fall on.
    pos[k] is the place in `notes` of slot k; a later block (Nunc's doxology)
    starts on the first note after the one before it that carries its first
    syllable, so the notes between two blocks have no slot."""
    voice: str
    verse: str
    blocks: list
    slots: list                  # [(block, slot)]
    notes: list                  # event indices of the voice's sounding notes, in order
    pos: list = field(default_factory=list)
    ranges: list = field(default_factory=list)   # per block: [first place, place after its room)
    ok: bool = True
    why: str = ""


def align(score, path: Path | None = None) -> dict:
    """(voice, verse) -> VoiceLyrics, with ok False and a reason where the
    slots do not fall on the analyser's syllables."""
    path = path or ROOT / "editions" / score.slug / "music" / "voices.ily"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    blocks = parse(text, score.parts)
    out = {}
    for v in score.parts:
        evs = score.voices[v]
        notes = [e.idx for e in evs if not e.rest]
        verses = sorted({b.verse for b in blocks if b.voice == v}, key=int)
        for verse in verses:
            bs = [b for b in blocks if b.voice == v and b.verse == verse]
            slots = [(b, s) for b in bs for s in b.slots]
            vl = VoiceLyrics(v, verse, bs, slots, notes)
            out[(v, verse)] = vl
            bad = next((b for b in bs if not b.ok), None)
            if bad is not None:
                vl.ok, vl.why = False, bad.why
                continue
            # a stanza that starts later (Nunc's doxology) starts on its first syllable
            p = next((q for q, n in enumerate(notes) if verse in evs[n].lyrics), 0)
            starts = []
            for bi, b in enumerate(bs):
                starts.append(p)
                for _ in b.slots:
                    vl.pos.append(p)
                    p += 1
            vl.ranges = [(s, (starts[i + 1] if i + 1 < len(starts) else len(notes))) for i, s in enumerate(starts)]
            if p > len(notes):
                vl.ok, vl.why = False, f"{len(slots)} lyric slots for {len(notes)} notes"
                continue
            used = set()
            for k, (b, s) in enumerate(slots):
                e = evs[notes[vl.pos[k]]]
                used.add(vl.pos[k])
                ly = e.lyrics.get(verse)
                if s.kind == "syl" and (ly is None or _norm(ly.text) != _norm(s.text)):
                    vl.ok = False
                    vl.why = (f"slot {k + 1} ({s.raw!r}, line {s.line}) falls on {e.where} "
                              f"where the analyser has {ly.text if ly else 'no syllable'!r}")
                    break
                if s.kind == "skip" and ly is not None:
                    vl.ok = False
                    vl.why = f"slot {k + 1} ('_', line {s.line}) falls on {e.where}, which has {ly.text!r}"
                    break
            else:
                rest = [evs[notes[q]] for q in range(len(notes)) if q not in used and verse in evs[notes[q]].lyrics]
                if rest:
                    vl.ok, vl.why = False, f"the analyser has a syllable with no slot at {rest[0].where}"
    return out


def svg_tags(score, path: Path | None = None) -> dict:
    """(line, col) of each lyric token in voices.ily -> (kind, voice, verse,
    note event index, next syllable's note event index or None), for tagging
    the SVG's syllables ("syl") and hyphens and extenders ("conn")."""
    out = {}
    for (v, verse), vl in align(score, path).items():
        if not vl.ok:
            continue
        syl_ks = [k for k, (_, s) in enumerate(vl.slots) if s.kind == "syl"]
        nxt = {a: b for a, b in zip(syl_ks, syl_ks[1:])}
        for k, (_, s) in enumerate(vl.slots):
            if s.kind != "syl":
                continue
            n = vl.notes[vl.pos[k]]
            out[(s.line, s.col)] = ("syl", v, verse, n, None)
            if s.raw.startswith('"'):
                # LilyPond's link for a quoted syllable points at its closing quote
                out.setdefault((s.line, s.col + len(s.raw) - 1), ("syl", v, verse, n, None))
            if s.conn_at:
                nn = vl.notes[vl.pos[nxt[k]]] if k in nxt else None
                out[s.conn_at] = ("conn", v, verse, n, nn)
    return out


# ------------------------------------------------------------------ rewriting

def assignment(vl: VoiceLyrics, score) -> list:
    """Per sounding note: (text, syllabic, slot or None) or None for a continuation."""
    evs = score.voices[vl.voice]
    out = [None] * len(vl.notes)
    for k, (_, s) in enumerate(vl.slots):
        if s.kind == "syl":
            ly = evs[vl.notes[vl.pos[k]]].lyrics.get(vl.verse)
            out[vl.pos[k]] = (s.text, ly.syllabic if ly else "single", s)
    return out


def _quote(t: str) -> str:
    return f'"{t}"' if re.search(r'[,.;:!?"\s]', t) or t in ("_", "--", "__") else t


def render(vl: VoiceLyrics, assign: list) -> dict:
    """Block name -> new contents (tokens only, one line), from an assignment.
    Each block writes its own room (its notes up to the next block): through
    its old last slot, or further if a syllable now starts later."""
    out = {}
    slot_at = {vl.pos[k]: s for k, (_, s) in enumerate(vl.slots)}
    k0 = 0
    for bi, b in enumerate(vl.blocks):
        lo, hi = vl.ranges[bi]
        old_last = vl.pos[k0 + len(b.slots) - 1] if b.slots else lo - 1
        k0 += len(b.slots)
        new_last = max([q for q in range(lo, hi) if assign[q] is not None] + [old_last])
        toks = [b.head] if b.head else []
        for j in range(lo, new_last + 1):
            a = assign[j]
            old = slot_at.get(j)
            prefix = old.prefix if old is not None else ""
            if a is None:
                toks.append(prefix + "_")
                continue
            text, syllabic, src = a
            raw = src.raw if src is not None and src.text == text else _quote(text)
            if src is not None:
                prefix = src.prefix
            toks.append(prefix + raw)
            # what follows: a hyphen inside a word, an extender over a melisma
            nxt = next((i for i in range(j + 1, new_last + 1) if assign[i] is not None), None)
            cont = (nxt - j - 1) if nxt is not None else new_last - j
            if syllabic in ("begin", "middle"):
                toks.append("--")
            elif cont > 0 and _extender(src):
                toks.append("__")
        out[b.name] = " ".join(toks)
    return out


def _extender(src) -> bool:
    # keep the source's choice where the syllable held a melisma already;
    # a syllable that now holds a new one gets an extender
    if src is not None and src.mel > 0:
        return src.conn == "__"
    return True


def _block_text(text: str, b: Block) -> str:
    return " ".join(text[b.start:b.end].split())


def _strip_comments(s: str) -> str:
    return " ".join(re.sub(r"%[^\n]*", " ", s).split())


# ------------------------------------------------------------------ applying

def _note_key(e) -> tuple:
    return (str(e.measure), str(F(e.pos)), e.name)


class Refused(Exception):
    pass


def _resolve(edit: dict, score, vl: VoiceLyrics) -> list:
    """The edit's notes as (position in vl.notes, syllable or None, syllabic)."""
    evs = score.voices[vl.voice]
    where = {}
    for k, n in enumerate(vl.notes):
        where[_note_key(evs[n])] = k
    out = []
    for nt in edit.get("notes") or []:
        key = (str(nt.get("bar")), str(F(str(nt.get("pos")))), str(nt.get("pitch")))
        if key not in where:
            raise Refused(f"no note {nt.get('pitch')} at bar {nt.get('bar')}, position {nt.get('pos')} "
                          f"in the {vl.voice}")
        out.append((where[key], nt.get("syllable") or None, nt.get("syllabic") or "single"))
    if not out:
        raise Refused("the edit lists no notes")
    return out


def _fmt(score, vl, assign, lo, hi) -> str:
    evs = score.voices[vl.voice]
    cells = []
    for k in range(lo, hi + 1):
        e = evs[vl.notes[k]]
        a = assign[k]
        cells.append(f"{e.where} {e.name}:{(a[0] + ('-' if a[1] in ('begin', 'middle') else '')) if a else '·'}")
    return "  ".join(cells)


def apply_edits(edits: list, *, dry_run: bool = True, allow_text: bool = False, out=sys.stdout) -> int:
    """Apply (or with dry_run show) edits. Returns the number refused."""
    from .findings import run
    by_piece: dict = {}
    for e in edits:
        by_piece.setdefault(e.get("slug"), []).append(e)
    refused = 0
    for slug, es in by_piece.items():
        xml = ROOT / "editions" / str(slug) / "pdf" / f"{slug}.musicxml"
        if not xml.exists():
            for e in es:
                print(f"REFUSED {e.get('id', '?')}: no edition {slug!r}", file=out)
            refused += len(es)
            continue
        score = run(xml).analysis.score
        path = ROOT / "editions" / slug / "music" / "voices.ily"
        text = path.read_text(encoding="utf-8")
        lyr = align(score, path)
        new_text = text
        groups: dict = {}
        for e in es:
            groups.setdefault((e.get("voice"), str(e.get("verse") or "1")), []).append(e)
        changes = []    # (block, new contents)
        for (voice, verse), ge in groups.items():
            vl = lyr.get((voice, verse))
            if vl is None or not vl.ok:
                why = vl.why if vl is not None else f"no lyrics for {voice}, verse {verse} in voices.ily"
                for e in ge:
                    print(f"REFUSED {e.get('id', '?')}: cannot tie the lyrics to the notes: {why}", file=out)
                refused += len(ge)
                continue
            base = assignment(vl, score)
            # an unedited block must come back token for token
            same = render(vl, base)
            for b in vl.blocks:
                if _strip_comments(text[b.start:b.end]) != same[b.name]:
                    for e in ge:
                        print(f"REFUSED {e.get('id', '?')}: {b.name} does not round-trip; edit it by hand", file=out)
                    refused += len(ge)
                    break
            else:
                cur = list(base)
                touched = []
                for e in sorted(ge, key=lambda d: d.get("updatedAt") or ""):
                    eid = e.get("id") or e.get("finding") or "?"
                    try:
                        notes = _resolve(e, score, vl)
                    except Refused as r:
                        print(f"REFUSED {eid}: {r}", file=out)
                        refused += 1
                        continue
                    if e.get("kind") == "alternative" and not e.get("alternative"):
                        print(f"{eid}: keeps the current reading (nothing to change)", file=out)
                        continue
                    trial = list(cur)
                    for k, syl, sb in notes:
                        trial[k] = (syl, sb, None) if syl else None
                    lo, hi = min(k for k, _, _ in notes), max(k for k, _, _ in notes)
                    # keep the original slot (its quoting, its \rep) where the text is unchanged
                    olds = [a for a in cur if a]
                    trial = [((a[0], a[1], next((o[2] for o in olds if o[0] == a[0] and o[2] is not None), None))
                              if a else None) for a in trial]
                    before = [a[0] for a in cur if a]
                    after = [a[0] for a in trial if a]
                    diff_at = [i for i in range(len(cur)) if (cur[i] or (None,))[:2] != (trial[i] or (None,))[:2]]
                    if diff_at:
                        lo, hi = diff_at[0], diff_at[-1]
                    lo2, hi2 = max(0, lo - 2), min(len(cur) - 1, hi + 2)
                    if not diff_at:
                        print(f"{eid}: the score already reads so (nothing to change)", file=out)
                        continue
                    print(f"{eid}  ({e.get('kind')}{' ' + str(e.get('alternative')) if e.get('alternative') else ''}, "
                          f"{voice} verse {verse}){': ' + e['reason'] if e.get('reason') else ''}", file=out)
                    print(f"  now:  {_fmt(score, vl, cur, lo2, hi2)}", file=out)
                    print(f"  asks: {_fmt(score, vl, trial, lo2, hi2)}", file=out)
                    if before != after and not allow_text:
                        sm = difflib.SequenceMatcher(a=before, b=after)
                        d = [f"{' '.join(before[i1:i2]) or '∅'} → {' '.join(after[j1:j2]) or '∅'}"
                             for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
                        print(f"REFUSED {eid}: it changes the text ({'; '.join(d)}); "
                              "pass --allow-text if that is meant (10.13)", file=out)
                        refused += 1
                        continue
                    if trial and trial[0] is None and cur[0] is not None:
                        print(f"REFUSED {eid}: the voice's first note would have no syllable", file=out)
                        refused += 1
                        continue
                    cur = trial
                    touched.append(eid)
                if touched:
                    new = render(vl, cur)
                    for b in vl.blocks:
                        if new[b.name] != same[b.name]:
                            changes.append((b, new[b.name]))
        if not changes:
            continue
        if slug in GENERATED:
            print(f"{slug}: voices.ily is generated; apply the change in {GENERATED[slug]}, "
                  "using the 'asks' lines above", file=out)
            refused += 1
            continue
        for b, contents in sorted(changes, key=lambda t: -t[0].start):
            old = text[b.start:b.end]
            # keep the block's layout: one line stays one line; a block on its own lines is re-indented
            if "\n" in old:
                indent = re.match(r"\n([ \t]*)", old)
                ind = indent.group(1) if indent else "  "
                body = contents
                if b.head:
                    body = b.head + "\n" + ind + contents[len(b.head):].lstrip()
                rep = "\n" + ind + body + "\n"
            else:
                rep = " " + contents + " "
            new_text = new_text[:b.start] + rep + new_text[b.end:]
        diff = difflib.unified_diff(text.splitlines(), new_text.splitlines(), f"a/{path.relative_to(ROOT)}",
                                    f"b/{path.relative_to(ROOT)}", lineterm="", n=0)
        for line in diff:
            print(_clip(line), file=out)
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")
            print(f"wrote {path.relative_to(ROOT)}", file=out)
    return refused


def _clip(line: str, width: int = 400) -> str:
    return line if len(line) <= width else line[:width] + " …"


def load_edits(path: Path) -> list:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("edits", [])
    return [d for d in data if isinstance(d, dict)]


def main(argv: list) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="python -m tools.analyser edits")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply", help="show, and unless --dry-run write, edits saved on the review page")
    a.add_argument("edits")
    a.add_argument("--dry-run", action="store_true", help="print the change only")
    a.add_argument("--allow-text", action="store_true", help="allow edits that change the words (10.13)")
    ns = ap.parse_args(argv)
    n = apply_edits(load_edits(Path(ns.edits)), dry_run=ns.dry_run, allow_text=ns.allow_text)
    return 1 if n else 0
