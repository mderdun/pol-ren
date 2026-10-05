"""Where each syllable of an edition's underlay comes from.

    result = compute(score)        # {(voice, event idx, verse): Prov}

The rules and the evidence per edition are in provenance.yaml; this module
applies them to the analyser's score, with two comparisons:

- with a modern edition's MusicXML (Vox in Rama: Marchesano, M), note by
  note: a syllable at the same onset in the same voice with the same text is
  as that edition, any other is ours (changed from it);
- with the chant a cantus firmus paraphrases (Nunc scio vere: the introit in
  the Graduale Romanum), for the notes the edition marks \\cfStart ... \\cfEnd:
  the voice's notes are aligned to the chant's by pitch (`align`), and a
  syllable on the note that carries the same syllable in the chant is chant.

The review page (review.py) shows the result as the "Text source" layer, a
line in the inspector and a table in the About panel. See docs/analyser.md.
"""
from __future__ import annotations

import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path

import yaml

from .ingest import ROOT
from . import underlay_edits as UE

HERE = Path(__file__).resolve().parent
CATS = {"source": "Source", "edition": "Edition", "chant": "Chant", "ours": "Ours"}
# label -> (category, inspector text; {s} is the siglum)
LABELS = {
    "source": ("source", "Source: as {s}"),
    "edition": ("edition", "Source: as {s}"),
    "chant": ("chant", "Chant: as in the c.f. line"),
    "changed": ("ours", "Ours (changed from {s})"),
    "notext": ("ours", "Ours, no source text"),
    "unplaced": ("ours", "Ours (source text, not placed)"),
    "supplied_ij": ("ours", "Ours, supplied for ij ⟨ ⟩"),
    "supplied_rep": ("ours", "Ours, supplied repeat"),
    "cf_off": ("ours", "Ours (c.f., off the chant’s syllable)"),
    "cf_pending": ("ours", "Ours; c.f. line (chant), placement not yet compared"),
}


@dataclass(frozen=True)
class Prov:
    label: str
    siglum: str = ""

    @property
    def cat(self) -> str:
        return LABELS[self.label][0]

    @property
    def text(self) -> str:
        return LABELS[self.label][1].format(s=self.siglum or "the source")


def rules(slug: str) -> dict | None:
    doc = yaml.safe_load((HERE / "provenance.yaml").read_text(encoding="utf-8")) or {}
    return doc.get(slug)


def norm(t: str | None) -> str:
    """A syllable for comparison: lower case, no accents, punctuation or
    brackets; j as i (Ju-dae-o-rum = Iu-dae-o-rum)."""
    t = unicodedata.normalize("NFD", t or "")
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").lower().replace("j", "i")
    return re.sub(r"[^a-zæœ]", "", t)


# ------------------------------------------------------------------ a modern edition

def edition_lyrics(path: Path, parts: list[str], scale) -> dict:
    """voice -> {onset in semiminims: syllable}, from a MusicXML file's first
    lyric line. Read with ElementTree: onsets only, no pitches needed."""
    root = ET.parse(path).getroot()
    out = {}
    for p, v in zip(root.findall("part"), parts):
        t, div, syl = F(0), 1, {}
        for m in p.findall("measure"):
            for el in m:
                if el.tag == "attributes" and el.find("divisions") is not None:
                    div = int(el.find("divisions").text)
                elif el.tag in ("backup", "forward"):
                    d = F(int(el.find("duration").text), div)
                    t += d if el.tag == "forward" else -d
                elif el.tag == "note":
                    if el.find("chord") is not None or el.find("duration") is None:
                        continue
                    ly = el.find("lyric")
                    if ly is not None and el.find("rest") is None and ly.findtext("text"):
                        syl[t * F(scale)] = ly.findtext("text")
                    t += F(int(el.find("duration").text), div)
        out[v] = syl
    return out


# ------------------------------------------------------------------ the chant

GABC_SYL = re.compile(r"([^()]*)\(([^)]*)\)")


def gabc(path: Path) -> list[tuple[str, list[str]]]:
    """The antiphon of a gabc file as [(syllable, [steps])], up to the first
    double bar (::). Steps are letter names (C4 clef: j = c); a letter with
    x, y or # after it is an accidental sign, not a note."""
    text = path.read_text(encoding="utf-8")
    body = text.split("%%", 1)[1]
    clef = re.search(r"\(([cf])([1-4])\)", body)
    # the letter on the clef's line: lines are d f h j l from the bottom
    line_letter = "dfhjl"[int(clef.group(2)) - 1]
    base = "CF".index(clef.group(1).upper())
    out = []
    for syl, notes in GABC_SYL.findall(body):
        syl = re.sub(r"<[^>]*>|\*", "", syl).strip()
        if "::" in notes:
            break
        notes = re.sub(r"\[[^\]]*\]", "", notes)
        notes = re.sub(r"[a-m][xy#]", "", notes)
        if re.fullmatch(r"\s*[cf][1-4]\s*", notes):
            continue
        steps = []
        for c in re.findall(r"[a-mA-M]", notes):
            k = "abcdefghijklm".index(c.lower()) - "abcdefghijklm".index(line_letter)
            steps.append("CDEFGAB"[(k + (0 if base == 0 else 3)) % 7])
        if syl and steps:
            out.append((syl, steps))
    return out


def align(voice: list[tuple], chant: list[tuple]) -> dict:
    """Align a c.f. voice's notes [(step, dur, syllable or "")] to the chant's
    notes [(step, syllable)], end to end. A matching step scores 2; a voice
    note left out (an ornament) costs 0.4 if shorter than a semibreve, 1.2
    otherwise; a chant note left out costs 0.6 (the repeated notes of a neume
    sung once); a wrong step costs 1. Between alignments that score the same
    on pitch, the one that puts more of the voice's syllables on the chant's
    same syllable wins (0.01 each): the words only break ties, so the
    comparison is not decided by the text it measures. Returns {voice note ->
    chant note}."""
    n, m = len(voice), len(chant)
    NEG = float("-inf")
    S = [[NEG] * (m + 1) for _ in range(n + 1)]
    B = [[None] * (m + 1) for _ in range(n + 1)]
    S[0][0] = 0.0
    for j in range(1, m + 1):
        S[0][j], B[0][j] = S[0][j - 1] - 0.6, "c"
    for i in range(1, n + 1):
        step, dur, syl = voice[i - 1]
        skip_v = 0.4 if dur < 4 else 1.2
        for j in range(m + 1):
            best, how = S[i - 1][j] - skip_v, "v"
            if j:
                hit = step == chant[j - 1][0]
                d = S[i - 1][j - 1] + (2.0 if hit else -1.0)
                if hit and syl and norm(syl) == norm(chant[j - 1][1]):
                    d += 0.01
                if d > best:
                    best, how = d, "d"
                c = S[i][j - 1] - 0.6
                if c > best:
                    best, how = c, "c"
            S[i][j], B[i][j] = best, how
    i, j, out = n, m, {}
    while i > 0 or j > 0:
        how = B[i][j]
        if how == "d":
            if voice[i - 1][0] == chant[j - 1][0]:
                out[i - 1] = j - 1
            i, j = i - 1, j - 1
        elif how == "v":
            i -= 1
        else:
            j -= 1
    return out


def chant_range(chant: list, first: str, last: str) -> tuple[int, int]:
    """The chant syllables [a, b] a span paraphrases: from the first syllable
    with the span's first text to the first after it with its last text."""
    a = next((k for k, (s, _) in enumerate(chant) if norm(s) == norm(first)), 0)
    b = next((k for k in range(a, len(chant)) if norm(chant[k][0]) == norm(last)), len(chant) - 1)
    return a, b


def cf_spans(score) -> dict:
    """voice -> [event idx] of the notes between \\cfStart and \\cfEnd in
    voices.ily (the notes carrying them included)."""
    path = ROOT / "editions" / score.slug / "music" / "voices.ily"
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    marks = []                     # (line, col of the note's first character, 1-based)
    for ln, s in enumerate(lines, 1):
        for m in re.finditer(r"\\cf(Start|End)", s):
            k = s.rfind(" ", 0, m.start()) + 1
            marks.append((m.group(1), ln, k + 1))
    out = defaultdict(list)
    starts = [x for x in marks if x[0] == "Start"]
    ends = [x for x in marks if x[0] == "End"]
    for (_, l0, c0), (_, l1, c1) in zip(starts, ends):
        for v in score.parts:
            for e in score.voices[v]:
                if e.rest or not e.src:
                    continue
                key = (int(e.src[1]), int(e.src[2]))
                if (l0, c0) <= key <= (l1, c1):
                    out[v].append(e.idx)
    return dict(out)


def _bare(s: str) -> str:
    return re.sub(r"[\s,.;:]+$", "", s).lower()


def chant_compare(score, cfg: dict) -> tuple[dict, dict]:
    """(voice, idx, verse) -> label for the syllables in c.f. spans; and a
    summary per voice {compared, on_chant, chant_syllables}."""
    labels, summary = {}, {}
    chant = gabc(ROOT / cfg["gabc"])
    spans = cf_spans(score)
    for v, idxs in spans.items():
        evs = [score.voices[v][i] for i in idxs]
        compare = cfg.get("compare", {}).get(v, False)
        if not compare:
            for e in evs:
                for verse in e.lyrics:
                    labels[(v, e.idx, verse)] = "cf_pending"
            summary[v] = {"compared": False, "syllables": sum(len(e.lyrics) for e in evs)}
            continue
        own = [(k, ly) for k, e in enumerate(evs) for ly in [e.lyrics.get("1")] if ly and not ly.italic]
        if not own:
            continue
        c0, c1 = chant_range(chant, own[0][1].text, own[-1][1].text)
        flat = [(si, st) for si in range(c0, c1 + 1) for st in chant[si][1]]
        vsyl = [(e.lyrics["1"].text if "1" in e.lyrics and not e.lyrics["1"].italic else "") for e in evs]
        amap = align([(e.step, e.dur, vsyl[k]) for k, e in enumerate(evs)],
                     [(st, chant[si][0]) for si, st in flat])
        starts = [k for k, e in enumerate(evs) if e.lyrics]
        on = n = 0
        for k, e in enumerate(evs):
            for verse, ly in e.lyrics.items():
                if ly.italic:
                    continue                # a supplied repeat: not the chant's statement
                n += 1
                # the syllable's note, or the first of its notes the chant has (past ornaments)
                nxt = next((s for s in starts if s > k), len(evs))
                hit = next((amap[q] for q in range(k, nxt) if q in amap), None)
                if hit is not None and norm(chant[flat[hit][0]][0]) == norm(ly.text):
                    labels[(v, e.idx, verse)] = "chant"
                    on += 1
                else:
                    labels[(v, e.idx, verse)] = "cf_off"
        carrier = {flat[c][0] for c in amap.values()}
        used = sorted(carrier)
        summary[v] = {"compared": True, "syllables": n, "on_chant": on,
                      "chant_range": (f"{_bare(chant[used[0]][0])} … {_bare(chant[used[-1]][0])}" if used else ""),
                      "aligned_notes": len(amap), "notes": len(evs)}
    return labels, summary


# ------------------------------------------------------------------ supplied text

def ij_syllables(score) -> set:
    """(voice, idx, verse) inside the ⟨ ⟩ of voices.ily (\\ijOpen ... \\ijClose,
    both syllables included)."""
    out = set()
    for (v, verse), vl in UE.align(score).items():
        if not vl.ok:
            continue
        inside = False
        for k, (_, s) in enumerate(vl.slots):
            if "\\ijOpen" in s.prefix:
                inside = True
            if inside and s.kind == "syl":
                out.add((v, vl.notes[vl.pos[k]], verse))
            if "\\ijClose" in s.prefix:
                inside = False
    return out


# ------------------------------------------------------------------ the result

def compute(score, cfg: dict | None = None) -> tuple[dict, dict]:
    """{(voice, idx, verse): Prov} for every syllable of the score's voices,
    and notes {voice: note, "_chant": summary}. Empty where provenance.yaml has
    no entry for the edition."""
    cfg = cfg if cfg is not None else rules(score.slug)
    if not cfg:
        return {}, {}
    comp = cfg.get("compare")
    other = {}
    if comp:
        other = edition_lyrics(ROOT / comp["file"], comp["parts"], comp.get("scale", 1))
    supplied = cfg.get("supplied") or []
    ij = ij_syllables(score) if "ij" in supplied else set()
    cf_labels, cf_sum = chant_compare(score, cfg["chant"]) if cfg.get("chant") else ({}, {})
    vcfg = cfg.get("voices") or {}
    out = {}
    for v in score.parts:
        vc = vcfg.get(v, {})
        notes = [e for e in score.voices[v] if not e.rest]
        for k, e in enumerate(notes):
            for verse, ly in e.lyrics.items():
                key = (v, e.idx, verse)
                sig = vc.get("siglum", "")
                differs = None
                if comp and "same" in vc:
                    m = other.get(v, {}).get(e.onset)
                    differs = not (m is not None and norm(m) == norm(ly.text))
                    p = Prov(vc["differs"], vc.get("compare_siglum", sig)) if differs else Prov(vc["same"], sig)
                elif "one_per_note" in vc:
                    mel = k + 1 < len(notes) and verse not in notes[k + 1].lyrics
                    differs = mel
                    p = Prov(vc["differs"], sig) if mel else Prov(vc["one_per_note"], sig)
                elif "label" in vc:
                    p = Prov(vc["label"], sig)
                else:
                    p = Prov(cfg.get("default", "notext"))
                for sp in cfg.get("spans") or []:
                    if (sp["voice"] == v and sp["bars"][0] <= e.bar <= sp["bars"][1]
                            and (sp.get("when") != "differs" or differs)):
                        p = Prov(sp["label"], sp.get("siglum", ""))
                if key in cf_labels:
                    p = Prov(cf_labels[key])
                if key in ij:
                    p = Prov("supplied_ij")
                elif "italic" in supplied and ly.italic:
                    p = Prov("supplied_rep")
                out[key] = p
    notes = {v: vcfg[v]["note"] for v in vcfg if vcfg[v].get("note")}
    notes["_chant"] = cf_sum
    return out, notes


def summary(score, prov: dict) -> dict:
    """voice -> Counter of categories (all verses)."""
    out = {v: Counter() for v in score.parts}
    for (v, _i, _verse), p in prov.items():
        out[v][p.cat] += 1
    return out
