"""One self-contained HTML page for reviewing the analyser on one piece.

    python -m tools.analyser review editions/vox-in-rama/pdf/vox-in-rama.musicxml --html OUT.html

The page shows the critical score as notation (LilyPond's SVG backend, with
point-and-click links tying every note to its line and column in voices.ily),
the findings ranked by regret, and the analysis layers as overlays on the
score. The source map (<slug>.srcmap.tsv) gives each analyser note its source
location; the SVG's textedit links give each drawn note the same location, so
the two meet there.

The score is rendered from a small LilyPond file that \\include's the edition's
music/score.ly (the critical score, as in the PDF), on one tall page with room
under each system for the analysis bands. LilyPond 2.24 is needed; without it
the page is written with the findings and the tables, and a note in place of
the score.

Everything is inlined: no external requests. Underlay edits made on the page
(edit.js) are saved to the artifact's db when the page is served with one,
kept in the browser otherwise, and can be copied as JSON for
`python -m tools.analyser edits apply` (underlay_edits.py). See docs/analyser.md.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import tempfile
from collections import Counter, defaultdict
from datetime import date
from fractions import Fraction as F
from pathlib import Path

import yaml

from . import baseline as B
from . import keytext as KT
from .findings import LEVEL_ORDER, run
from .ingest import ROOT
from .rules import load, settings
from .text import coverage, key_word_entries, lexicon
from . import underlay_edits as UE

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "review_assets"
HOUSE_LY = ROOT / "house" / "lilypond"
LINK = re.compile(r'<a style="color:inherit;" xlink:href="textedit://([^"]*?):(\d+):(\d+):(\d+)">')
TRANSLATE = re.compile(r'\s*<g transform="translate\(([-\d.]+), ([-\d.]+)\)">')
STAFFLINE = re.compile(r'<g transform="translate\(([-\d.]+), ([-\d.]+)\)">\s*<line[^>]*?x1="([-\d.]+)" '
                       r'y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"')

WRAPPER = r'''\version "2.24.0"
%% Review rendering of the critical score: one tall page, room under each
%% system for the analysis bands, point-and-click links on every note. No
%% ambitus: its heads carry the same links as the notes they show.
\layout { \context { \Staff \override AmbitusNoteHead.stencil = ##f
  \override AmbitusAccidental.stencil = ##f \override AmbitusLine.stencil = ##f } }
\include "score.ly"
\paper {
  page-breaking = #ly:one-page-breaking
  print-page-number = ##f
  print-first-page-number = ##f
  oddHeaderMarkup = ##f
  evenHeaderMarkup = ##f
  oddFooterMarkup = ##f
  evenFooterMarkup = ##f
  system-system-spacing.padding = #13
  score-system-spacing.padding = #13
  top-margin = 8\mm
  bottom-margin = 12\mm
}
'''

CAD_SHORT = {"authentic": "auth.", "clausula vera": "cl. vera", "phrygian": "phryg.", "plagal": "plagal",
             "evaded": "evaded", "abandoned": "aband.", "unclassified": "?"}
DIS_SHORT = {"suspension": "S", "passing": "p", "accented-passing": "ap", "neighbour": "n", "cambiata": "c",
             "anticipation": "a", "echappee": "e", "unexplained": "?"}
VALUE = {F(16): "L", F(8): "B", F(4): "S", F(2): "M", F(1): "Sm", F(1, 2): "F", F(1, 4): "Sf"}


# ------------------------------------------------------------------ rendering

def render_svg(slug: str) -> list[str]:
    """The critical score as SVG pages, with textedit links. [] without LilyPond."""
    if shutil.which("lilypond") is None:
        return []
    music = ROOT / "editions" / slug / "music"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / "review.ly").write_text(WRAPPER, encoding="utf-8")
        cmd = ["lilypond", "-dbackend=svg", "-dpoint-and-click",
               "-I", str(HOUSE_LY), "-I", str(music), "-o", str(tmp / "review"), str(tmp / "review.ly")]
        r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True)
        pages = sorted(tmp.glob("review*.svg"), key=lambda p: (len(p.name), p.name))
        if r.returncode != 0 or not pages:
            raise RuntimeError("lilypond failed:\n" + r.stderr[-2000:])
        return [p.read_text(encoding="utf-8") for p in pages]


def _rel(path: str) -> str:
    p = Path(path)
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def note_table(score) -> tuple[list, dict]:
    """notes: [{id, voice, idx, ...}]; key (file, line, char) -> [note id]."""
    notes, keys = [], defaultdict(list)
    for v in score.parts:
        for e in score.voices[v]:
            if e.rest:
                continue
            nid = f"{v}:{e.idx}"
            notes.append({"id": nid, "voice": v, "idx": e.idx, "where": e.where, "name": e.name,
                          "dur": _value(e.dur), "onset": float(e.onset)})
            for s in (e.srcs or ([e.src] if e.src else [])):
                if s:
                    keys[(s[0], int(s[1]), int(s[2]) - 1)].append(nid)
    return notes, keys


def _value(d) -> str:
    d = F(d)
    if d in VALUE:
        return VALUE[d]
    if d * 2 / 3 in VALUE:
        return VALUE[d * 2 / 3] + "."
    return str(d)


def map_svg(svg: str, keys: dict, page: int, lyr: dict | None = None, voices_ily: str = ""):
    """Replace the textedit links by groups that carry the analyser's note ids.
    Returns the new SVG, note positions {id: (page, x, y)}, the staves, and
    the lyric syllables found [(voice, verse, note id, x, y)].

    The lyrics' links point at their tokens in voices.ily; `lyr` (from
    underlay_edits.svg_tags) says which note each syllable, hyphen and
    extender belongs to, so the page can hide and redraw them.

    A note's link can appear on several grobs: its head, an accidental, a
    dot, and the ambitus at the start of the staff. The head is taken from
    the rightmost cluster of them (within 3 units), middle element: that drops
    the ambitus and steps over an accidental and a dot."""
    links = []
    for m in LINK.finditer(svg):
        key = (_rel(m.group(1)), int(m.group(2)), int(m.group(3)))
        t = TRANSLATE.match(svg, m.end())
        xy = (float(t.group(1)), float(t.group(2))) if t else None
        links.append((m, key, xy))
    by_key = defaultdict(list)
    for n, (m, key, xy) in enumerate(links):
        if xy is not None and keys.get(key):
            by_key[key].append((xy[0], n))
    chosen = set()
    pos: dict = {}
    for key, lst in by_key.items():
        mx = max(x for x, _ in lst)
        cl = sorted((x, n) for x, n in lst if x >= mx - 3)
        chosen.update(n for _, n in cl)
        head = cl[(len(cl) - 1) // 2][1]
        for nid in keys[key]:
            pos.setdefault(nid, (page, links[head][2][0], links[head][2][1]))
    out, last = [], 0
    lyr = lyr or {}
    found = []
    for n, (m, key, xy) in enumerate(links):
        out.append(svg[last:m.start()])
        tag = lyr.get((key[1], key[2])) if key[0] == voices_ily else None
        if n in chosen:
            out.append(f'<g class="nh" data-n="{" ".join(keys[key])}">')
        elif tag is not None:
            kind, v, verse, ev, nx = tag
            nid = f"{v}:{ev}"
            if kind == "syl":
                out.append(f'<g class="ly" data-n="{_esc(nid)}" data-verse="{_esc(verse)}">')
                if xy is not None:
                    found.append((v, verse, nid, xy[0], xy[1]))
            else:
                nxa = f' data-nx="{_esc(v)}:{nx}"' if nx is not None else ""
                out.append(f'<g class="lyc" data-n="{_esc(nid)}" data-verse="{_esc(verse)}"{nxa}>')
        else:
            out.append("<g>")
        last = m.end()
    out.append(svg[last:])
    s = "".join(out).replace("</a>", "</g>")
    s = re.sub(r'<svg ([^>]*?)width="[^"]*" height="[^"]*"', r'<svg \1', s, count=1)
    s = s.replace('<svg ', f'<svg class="score-page" data-page="{page}" role="img" '
                  f'aria-label="Critical score, page {page + 1}" ', 1)
    return s, pos, staves(svg), found


def staves(svg: str) -> list[dict]:
    lines = []
    for m in STAFFLINE.finditer(svg):
        tx, ty, x1, y1, x2, y2 = map(float, m.groups())
        if abs(x2 - x1) > 20 and abs(y2 - y1) < 1e-3:
            lines.append((round(tx + x1, 2), round(tx + x2, 2), round(ty + y1, 3)))
    by_x = defaultdict(list)
    for x0, x1, y in lines:
        by_x[(x0, x1)].append(y)
    out = []
    for (x0, x1), ys in by_x.items():
        ys = sorted(set(ys))
        i = 0
        while i + 4 < len(ys):
            grp = ys[i:i + 5]
            gaps = [b - a for a, b in zip(grp, grp[1:])]
            if max(gaps) - min(gaps) < 0.05:
                out.append({"x0": x0, "x1": x1, "top": grp[0], "bot": grp[-1]})
                i += 5
            else:
                i += 1
    return sorted(out, key=lambda s: s["top"])


def systems(page_staves: list, pos: dict, notes_by_id: dict, parts: list, page: int) -> list[dict]:
    """Group staves into systems and notes into staves."""
    for st in page_staves:
        st["notes"] = []
    for nid, (pg, x, y) in pos.items():
        if pg != page:
            continue
        best = None
        for st in page_staves:
            if st["x0"] - 2 <= x <= st["x1"] + 2 and st["top"] - 6 <= y <= st["bot"] + 6:
                d = abs(y - (st["top"] + st["bot"]) / 2)
                if best is None or d < best[0]:
                    best = (d, st)
        if best:
            best[1]["notes"].append(nid)
    for st in page_staves:
        vs = Counter(notes_by_id[n]["voice"] for n in st["notes"])
        st["voice"] = vs.most_common(1)[0][0] if vs else None
    out, cur = [], None
    for st in page_staves:
        voices = [s["voice"] for s in cur["staves"]] if cur else []
        new = (cur is None or st["voice"] == parts[0] or st["voice"] in voices
               or st["x0"] != cur["staves"][0]["x0"]
               or (cur["staves"][-1]["voice"] == parts[-1])
               or (st["voice"] is None and len(voices) >= len(parts)))
        if new:
            cur = {"page": page, "staves": []}
            out.append(cur)
        cur["staves"].append(st)
    for s in out:
        s["top"] = s["staves"][0]["top"]
        s["bot"] = s["staves"][-1]["bot"]
        s["x0"] = min(st["x0"] for st in s["staves"])
        s["x1"] = max(st["x1"] for st in s["staves"])
        s["notes"] = [n for st in s["staves"] for n in st["notes"]]
        tx = defaultdict(list)
        for n in s["notes"]:
            tx[notes_by_id[n]["onset"]].append(pos[n][1])
        s["timeline"] = sorted((t, sum(xs) / len(xs)) for t, xs in tx.items())
    return out


def _x_at(sys_: dict, t: float) -> float | None:
    tl = sys_["timeline"]
    if not tl or t < tl[0][0] - 1e-9 or t > tl[-1][0] + 16:
        return None
    for (t0, x0), (t1, x1) in zip(tl, tl[1:]):
        if t0 <= t <= t1:
            return x0 + (x1 - x0) * (t - t0) / (t1 - t0) if t1 > t0 else x0
    return tl[-1][1] + (t - tl[-1][0]) * 0.9


# ------------------------------------------------------------------ overlays

def _t(x, y, text, cls, anchor="middle", title=None):
    tt = f"<title>{html.escape(title)}</title>" if title else ""
    return (f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}">{tt}'
            f'{html.escape(text)}</text>')


def overlays(a, pos, syss, notes_by_id) -> dict:
    """page -> SVG fragment with one group per layer."""
    sc = a.score
    sys_of = {}
    for s in syss:
        for n in s["notes"]:
            sys_of[n] = s
    layers = defaultdict(lambda: defaultdict(list))   # page -> layer -> [svg]

    def nid(v, i):
        return f"{v}:{i}"

    def staff_of(n):
        s = sys_of.get(n)
        if s is None:
            return None
        return next((st for st in s["staves"] if n in st["notes"]), None)

    band = {}
    for s in syss:
        y0 = s["bot"] + 6.0
        band[id(s)] = y0
        L = layers[s["page"]]
        for k, (layer, label) in enumerate((("cad", "cadence"), ("imi", "imitation"), ("hom", "homorhythm"))):
            L[layer].append(_t(s["x0"] - 0.8, y0 + 2.4 * k + 0.5, label, "ov-lab", "end"))
            L[layer].append(f'<line x1="{s["x0"]:.2f}" x2="{s["x1"]:.2f}" y1="{y0 + 2.4 * k:.2f}" '
                            f'y2="{y0 + 2.4 * k:.2f}" class="ov-rule"/>')

    # cadences
    for ci, c in enumerate(a.cadences):
        ids = [nid(v, i) for v, i in c.arrivals.items() if nid(v, i) in pos]
        if not ids:
            continue
        weak = c.kind == "weak"
        fs = ", ".join(f"{v} {f}" for v, f in sorted(c.functions.items()))
        title = (f"{c.where} {c.type} on {c.tone}, {c.kind}; closure {c.closure}"
                 f"{' (' + ', '.join(c.closure_why) + ')' if c.closure_why else ''}; {fs}")
        for n in ids:
            pg, x, y = pos[n]
            v = notes_by_id[n]["voice"]
            L = layers[pg]
            L["cad"].append(f'<g class="ov-cad{" weak" if weak else ""}" data-cad="{ci}">'
                            f'<title>{html.escape(title)}</title>'
                            f'<circle cx="{x + 0.65:.2f}" cy="{y:.2f}" r="1.25"/>'
                            f'{_t(x + 2.3, y - 1.0, c.functions.get(v, ""), "ov-fn")}</g>')
        pg, x, y = pos[ids[0]]
        s = sys_of.get(ids[0])
        if s is not None:
            y0 = band[id(s)]
            label = f"{CAD_SHORT.get(c.type, c.type)} {c.tone}" + ("" if c.kind in ("full", c.type) else f" · {c.kind}")
            layers[pg]["cad"].append(
                f'<g class="ov-cad-band{" weak" if weak else ""}" data-cad="{ci}"><title>{html.escape(title)}</title>'
                f'<path d="M{x + 0.65:.2f} {y0 - 0.9:.2f} l0.8 0.9 l-0.8 0.9 l-0.8 -0.9z"/>'
                f'{_t(x + 1.8, y0 + 0.55, label, "ov-txt", "start")}</g>')

    # dissonance
    for (v, i), d in a.dissonances.items():
        n = nid(v, i)
        if n not in pos:
            continue
        pg, x, y = pos[n]
        st = staff_of(n)
        top = min(st["top"], y) if st else y
        lab = DIS_SHORT.get(d.label, d.label)
        if d.label == "suspension":
            lab = f"S{d.figure}"
        title = f"{sc.voices[v][i].where} {v}: {d.label} {d.figure} ({d.interval} against {d.against})"
        if d.label == "suspension" and d.resolution is not None:
            r = sc.voices[v][d.resolution]
            title += f"; agent {d.agent}; resolves to {r.name} at {r.where}"
        parts = [f'<g class="ov-dis {d.label}"><title>{html.escape(title)}</title>',
                 _t(x + 0.65, top - 1.3, lab, "ov-dl")]
        if d.label == "suspension" and d.resolution is not None and nid(v, d.resolution) in pos:
            _, xr, yr = pos[nid(v, d.resolution)]
            if xr > x and sys_of.get(nid(v, d.resolution)) is sys_of.get(n):
                parts.append(f'<path d="M{x + 1.4:.2f} {y - 0.9:.2f} Q{(x + xr) / 2 + 0.6:.2f} {min(y, yr) - 2.6:.2f} '
                             f'{xr:.2f} {yr - 0.9:.2f}" class="ov-arc"/>')
            p_ = sc.voices[v][i - 1] if i > 0 else None
            if p_ is not None and not p_.rest and nid(v, p_.idx) in pos:
                _, xp, yp = pos[nid(v, p_.idx)]
                parts.append(f'<circle cx="{xp + 0.65:.2f}" cy="{yp:.2f}" r="0.35" class="ov-prep"/>')
        parts.append("</g>")
        layers[pg]["dis"].append("".join(parts))

    # phrases: a line under the staff from first to last note, per system
    for ph in a.phrases:
        if ph.verse != "1" and any(p.voice == ph.voice and p.verse == "1" for p in a.phrases):
            continue
        ids = [nid(ph.voice, j) for j in range(ph.first, ph.last + 1) if nid(ph.voice, j) in pos]
        segs = defaultdict(list)
        for n in ids:
            s = sys_of.get(n)
            if s is not None:
                segs[id(s)].append(n)
        title = f"{ph.voice}: {ph.text} (ends at {ph.ends}{', ' + ph.cadence.type if ph.cadence else ''})"
        for _, ns in segs.items():
            st = staff_of(ns[0])
            if st is None:
                continue
            pg = pos[ns[0]][0]
            x0, x1 = pos[ns[0]][1], pos[ns[-1]][1] + 1.3
            y = st["bot"] + 1.15
            layers[pg]["phr"].append(
                f'<g class="ov-phr end-{ph.ends}"><title>{html.escape(title)}</title>'
                f'<path d="M{x0:.2f} {y - 0.5:.2f} V{y:.2f} H{x1:.2f} V{y - 0.5:.2f}"/></g>')

    # imitation
    for pi, p in enumerate(a.points, start=1):
        for e in p.entries:
            ids = [nid(e.voice, j) for j in e.head if nid(e.voice, j) in pos]
            if not ids:
                continue
            pg, x, y = pos[ids[0]]
            st = staff_of(ids[0])
            s = sys_of.get(ids[0])
            title = (f"P{pi} {p.type}, head {p.motif}: {e.voice} at {e.where} "
                     f"({'exact' if e.exact else 'flexed'}, after a {e.context})")
            g = [f'<g class="ov-imi" data-pt="{pi}"><title>{html.escape(title)}</title>']
            if st is not None:
                ys = st["top"] - 2.6
                x1 = pos[ids[-1]][1] + 1.3 if sys_of.get(ids[-1]) is s else st["x1"]
                g.append(f'<path d="M{x:.2f} {ys + 0.6:.2f} V{ys:.2f} H{x1:.2f}" class="ov-imi-head"/>')
                g.append(_t(x, ys - 0.5, f"P{pi}", "ov-txt", "start"))
            if s is not None:
                y0 = band[id(s)] + 2.4
                g.append(f'<circle cx="{x + 0.65:.2f}" cy="{y0:.2f}" r="0.55"/>'
                         + _t(x + 1.6, y0 + 0.55, f"P{pi} {e.voice[0]}", "ov-txt", "start"))
            g.append("</g>")
            layers[pg]["imi"].append("".join(g))

    # homorhythm: a band over the system, and a bar in the band row
    for r in a.regions:
        for s in syss:
            x0 = _x_at(s, float(r.start))
            x1 = _x_at(s, float(r.end))
            tl = s["timeline"]
            if not tl:
                continue
            lo, hi = tl[0][0], tl[-1][0]
            if float(r.end) <= lo or float(r.start) > hi:
                continue
            x0 = x0 if x0 is not None else s["x0"]
            x1 = x1 if x1 is not None else s["x1"]
            if float(r.end) > hi:
                x1 = min(s["x1"], tl[-1][1] + 2)
            title = (f"homorhythm {r.first_where}-{r.last_where}: voices {', '.join(r.voices)}; syllables together "
                     + ", ".join(f"v{k} {int(v * 100)}%" for k, v in r.syllable_match.items()))
            y0 = band[id(s)] + 4.8
            layers[s["page"]]["hom"].append(
                f'<g class="ov-hom"><title>{html.escape(title)}</title>'
                f'<rect x="{x0:.2f}" y="{s["top"] - 1:.2f}" width="{max(0.5, x1 - x0):.2f}" '
                f'height="{s["bot"] - s["top"] + 2:.2f}" class="ov-hom-area"/>'
                f'<rect x="{x0:.2f}" y="{y0 - 0.5:.2f}" width="{max(0.5, x1 - x0):.2f}" height="1"/></g>')

    out = {}
    for pg, L in layers.items():
        out[pg] = "".join(f'<g class="layer layer-{k}">{"".join(v)}</g>' for k, v in L.items()) \
                  + '<g class="layer-hl"></g>'
    return out


# ------------------------------------------------------------------ data

def principles() -> dict:
    """'10.N' -> text of principles §10 (docs/editorial-principles.md)."""
    path = ROOT / "docs" / "editorial-principles.md"
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## 10\. .*?$(.*?)^## 11\.", text, re.S | re.M)
    if not m:
        return {}
    out = {}
    for item in re.finditer(r"^(\d+)\. (.*?)(?=^\d+\. |^\*|\Z)", m.group(1), re.S | re.M):
        body = " ".join(item.group(2).split())
        body = re.sub(r"\*\*(.*?)\*\*", r"\1", body)
        body = re.sub(r"\*(.*?)\*", r"\1", body)
        out[f"10.{item.group(1)}"] = body
    return out


def _grid(f, a) -> dict | None:
    """Notes around the finding, with the syllable each reading puts on each."""
    if not f.span:
        return None
    sc = a.score
    evs = sc.voices[f.voice]
    first, end = f.span
    cur = {e: t for e, t in f.placement}
    rows_p = [dict(cur)] + [{e: t for e, t in alt["placement"]} for alt in f.alternatives]
    changed = set()
    for r in rows_p[1:]:
        for e in set(r) ^ set(cur):
            changed.add(e)
        for e in set(r) & set(cur):
            if r[e] != cur[e]:
                changed.add(e)
    core = changed | set(f.notes)
    lo = max(first, min(core) - 2)
    hi = min(end - 1, max(core) + 3)
    if hi - lo > 28:
        lo, hi = max(first, min(f.notes) - 6), min(end - 1, max(f.notes) + 8)
    idx = [j for j in range(lo, hi + 1) if not evs[j].rest]
    cols = [{"id": f"{f.voice}:{j}", "p": evs[j].name, "d": _value(evs[j].dur), "w": evs[j].where,
             "hit": j in f.notes} for j in idx]

    def cells(p):
        # the syllable sounding at each column: new text where it starts, a dash where it continues
        starts = sorted(p)
        out = []
        for j in idx:
            if j in p:
                out.append(p[j])
            else:
                prev = [s for s in starts if s < j]
                out.append("–" if prev and not any(evs[k].rest for k in range(prev[-1], j)) else "")
        return out

    rows = [{"label": "Current", "cells": cells(cur)}]
    for k, alt in enumerate(f.alternatives, start=1):
        rows.append({"label": f"Alternative {k}", "cells": cells({e: t for e, t in alt["placement"]})})
    return {"cols": cols, "rows": rows}


def _syllabics(cur: list, texts: list) -> list:
    """Syllabic (begin, middle, end, single) for an alternative's syllables:
    the current reading's, in order; a text edit's dropped word is matched
    out, and a repeated word (marked *) is divided afresh."""
    if len(texts) == len(cur):
        return [c[1] for c in cur]
    import difflib
    a = [c[0] for c in cur]
    b = [t.rstrip("*") for t in texts]
    out = [None] * len(b)
    for blk in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            if not texts[blk.b + k].endswith("*"):
                out[blk.b + k] = cur[blk.a + k][1]
    j = 0
    while j < len(out):
        if out[j] is None:
            k = j
            while k < len(out) and out[k] is None:
                k += 1
            n = k - j
            for i in range(j, k):
                out[i] = "single" if n == 1 else ("begin" if i == j else ("end" if i == k - 1 else "middle"))
            j = k
        else:
            j += 1
    return out


def _placements(f, a) -> tuple[list, list]:
    """The finding's span (note ids) and its readings: [current, alt 1, ...],
    each [[note id, syllable, syllabic], ...] for the syllables of the span."""
    if not f.span or not f.placement:
        return [], []
    evs = a.score.voices[f.voice]
    span = [f"{f.voice}:{j}" for j in range(f.span[0], f.span[1]) if not evs[j].rest]
    cur = []
    for e, t in f.placement:
        ly = evs[e].lyrics.get(f.verse)
        cur.append((t, ly.syllabic if ly else "single"))
    rows = [[[f"{f.voice}:{e}", t, sb] for (e, t), (_, sb) in zip(f.placement, cur)]]
    for alt in f.alternatives:
        texts = [t for _, t in alt["placement"]]
        sbs = _syllabics(cur, texts)
        rows.append([[f"{f.voice}:{e}", t.rstrip("*"), sb] for (e, t), sb in zip(alt["placement"], sbs)])
    return span, rows


def page_data(res, a, base: dict) -> dict:
    rules = load()
    gates_doc = yaml.safe_load((HERE / "gates.yaml").read_text(encoding="utf-8"))
    sc = a.score
    findings = []
    for n, f in enumerate(res.findings):
        status = "new" if f.level != "info" else "info"
        if f.baseline:
            status = "accepted" if f.baseline.startswith("accepted") else "pending"
        r = rules[f.rule]
        span, pl = _placements(f, a)
        findings.append({
            "n": n, "rule": f.rule, "name": f.name, "level": f.level, "voice": f.voice, "verse": f.verse,
            "where": f.where, "bar": f.bar, "word": f.word, "text": f.text, "message": f.message,
            "principle": f.principle, "cost": round(f.cost, 3),
            "regret": None if f.regret is None else round(f.regret, 3), "gates": f.gates,
            "breakdown": f.breakdown, "alternatives": [
                {k: v for k, v in alt.items() if k != "placement"} for alt in f.alternatives],
            "src": f.src, "fingerprint": f.fingerprint, "status": status, "baseline": f.baseline or "",
            "notes": [f"{f.voice}:{j}" for j in f.notes],
            "grid": _grid(f, a), "weight": r.weight, "tier": r.tier, "span": span, "pl": pl})
    used = sorted({f.rule for f in res.findings})
    rule_info = {rid: {"name": rules[rid].name, "principle": rules[rid].principle,
                       "authority": rules[rid].authority, "weight": rules[rid].weight, "tier": rules[rid].tier,
                       "firm": rules[rid].hard, "gates": rules[rid].gates, "path": rules[rid].path}
                 for rid in used}
    return {"findings": findings, "rules": rule_info,
            "gates": {k: v.get("when", "") for k, v in gates_doc.items()},
            "principles": principles(), "levels": settings()["levels"]}


def lexicon_rows(a) -> list[dict]:
    sc = a.score
    lex = lexicon(sc.lang)
    keys = {k["word"]: k for k in key_word_entries(sc.config)}
    out = []
    for row in coverage(sc, a.lines):
        e = lex.entries.get(row["word"])
        sylls = e.syllables if e else []
        stress = e.stress if e else None
        if not sylls:
            # the word as sung, from the first line that has it
            for ln in a.lines:
                w = next((w for w in ln.words if w.norm == row["word"]), None)
                if w:
                    sylls = [ln.syls[i].text.lower().strip(",.:;!?") for i in w.syls]
                    stress = w.stress
                    break
        out.append({"word": row["word"], "syls": sylls, "stress": stress, "cls": e.cls if e else "content",
                    "src": e.src if e else "fallback: penultimate rule", "known": row["known"],
                    "count": row["count"], "note": e.note if e else "",
                    "key": (keys[row["word"]]["source"] if row["word"] in keys else "")})
    return out


# ------------------------------------------------------------------ HTML

def _esc(s) -> str:
    return html.escape(str(s), quote=True)


def _notes_attr(ids) -> str:
    return _esc(" ".join(ids))


def tables(a) -> str:
    sc = a.score
    out = []
    k = Counter(c.kind for c in a.cadences)
    out.append('<section class="tbl" id="t-cad"><h3><span class="sw sw-cad"></span>Cadences</h3>'
               f'<p class="note">{k.get("full", 0)} full, {k.get("evaded", 0)} evaded, {k.get("abandoned", 0)} '
               f'abandoned, and {k.get("weak", 0)} weak figures (complete clausulae that close weakly; not '
               'counted). Closure: a point each for long arrival notes, a rest after, a suspension, a bass, '
               'the end of a clause in the text; two make a full cadence.</p>'
               '<div class="scroll"><table><thead><tr><th>Bar</th><th>Type</th><th>Tone</th><th>Kind</th>'
               '<th class="num">Closure</th><th>Why</th><th>Voices</th></tr></thead><tbody>')
    for c in a.cadences:
        ids = [f"{v}:{i}" for v, i in c.arrivals.items()]
        fs = ", ".join(f"{v} {f}" for v, f in sorted(c.functions.items()))
        out.append(f'<tr class="pick kind-{_esc(c.kind)}" data-notes="{_notes_attr(ids)}" tabindex="0">'
                   f'<td class="num">{_esc(c.where)}</td><td>{_esc(c.type)}</td><td>{_esc(c.tone)}</td>'
                   f'<td><span class="kind">{_esc(c.kind)}</span></td><td class="num">{c.closure}</td>'
                   f'<td>{_esc(", ".join(c.closure_why))}</td><td>{_esc(fs)}</td></tr>')
    out.append("</tbody></table></div></section>")

    out.append('<section class="tbl" id="t-dis"><h3><span class="sw sw-dis"></span>Dissonance</h3>')
    cnt = Counter(d.label for d in a.dissonances.values())
    out.append('<p class="note">' + _esc(", ".join(f"{v} {k_}" for k_, v in sorted(cnt.items())))
               + '. Passing notes and neighbours are marked on the score (p, n) but not listed.</p>')
    out.append('<div class="scroll"><table><thead><tr><th>Bar</th><th>Voice</th><th>Label</th><th>Note</th>'
               '<th>Against</th><th>Detail</th></tr></thead><tbody>')
    for (v, i), d in sorted(a.dissonances.items(), key=lambda kv: (kv[1].onset, kv[0])):
        if d.label in ("passing", "neighbour"):
            continue
        e = sc.voices[v][i]
        ids = [f"{v}:{i}"]
        detail = ""
        if d.label == "suspension" and d.resolution is not None:
            r = sc.voices[v][d.resolution]
            ids += [f"{v}:{i - 1}", f"{v}:{d.resolution}"]
            detail = f"{d.figure}: prepared at {sc.voices[v][i - 1].where}, agent {d.agent}, resolves to {r.name} at {r.where}"
        out.append(f'<tr class="pick" data-notes="{_notes_attr(ids)}" tabindex="0"><td class="num">{_esc(e.where)}</td>'
                   f'<td>{_esc(v)}</td><td>{_esc(d.label)}</td><td>{_esc(e.name)}</td>'
                   f'<td>{_esc(d.interval)} / {_esc(d.against)}</td><td>{_esc(detail)}</td></tr>')
    out.append("</tbody></table></div></section>")

    out.append('<section class="tbl" id="t-imi"><h3><span class="sw sw-imi"></span>Points of imitation</h3>'
               '<p class="note">Heads of four notes that agree in rhythm and intervals (one interval may be '
               'flexed by a step). Entries follow a rest, or a cadence or a clause where six notes agree.</p>'
               '<div class="scroll"><table><thead><tr><th>Point</th><th>Type</th><th>Head</th><th>Entries</th>'
               '</tr></thead><tbody>')
    for pi, p in enumerate(a.points, start=1):
        ids = [f"{e.voice}:{j}" for e in p.entries for j in e.head]
        ents = "; ".join(f"{e.voice} {e.where} ({'exact' if e.exact else 'flexed'}, after a {e.context})"
                         for e in p.entries)
        out.append(f'<tr class="pick" data-notes="{_notes_attr(ids)}" tabindex="0"><td>P{pi}</td>'
                   f'<td>{_esc(p.type)}</td><td class="num">{_esc(p.motif)}</td><td>{_esc(ents)}</td></tr>')
    out.append("</tbody></table></div></section>")

    out.append('<section class="tbl" id="t-hom"><h3><span class="sw sw-hom"></span>Homorhythm</h3>'
               '<div class="scroll"><table><thead><tr><th>Bars</th><th>Voices</th><th class="num">Slices</th>'
               '<th>Syllables together</th></tr></thead><tbody>')
    for r in a.regions:
        ids = [f"{sl_v}:{e.idx}" for sl in a.slices if r.contains(sl.onset)
               for sl_v, e in sl.sounding.items() if sl_v in sl.attacks]
        out.append(f'<tr class="pick" data-notes="{_notes_attr(ids)}" tabindex="0">'
                   f'<td class="num">{_esc(r.first_where)}–{_esc(r.last_where)}</td><td>{_esc(", ".join(r.voices))}</td>'
                   f'<td class="num">{r.slices}</td><td>'
                   + _esc(", ".join(f"verse {k_} {int(v * 100)}%" for k_, v in r.syllable_match.items()))
                   + "</td></tr>")
    out.append("</tbody></table></div></section>")

    out.append('<section class="tbl" id="t-phr"><h3><span class="sw sw-phr"></span>Phrases</h3>'
               '<div class="scroll"><table><thead><tr><th>Voice</th><th>Verse</th><th>Bars</th><th>Ends</th>'
               '<th>Text</th></tr></thead><tbody>')
    for ph in a.phrases:
        ln = a.line(ph.voice, ph.verse)
        ids = [f"{ph.voice}:{j}" for j in range(ph.first, ph.last + 1) if not sc.voices[ph.voice][j].rest]
        cad = f" ({ph.cadence.type} on {ph.cadence.tone})" if ph.cadence else ""
        out.append(f'<tr class="pick" data-notes="{_notes_attr(ids)}" tabindex="0"><td>{_esc(ph.voice)}</td>'
                   f'<td class="num">{_esc(ph.verse)}</td><td class="num">{_esc(ph.label(ln))}</td>'
                   f'<td>{_esc(ph.ends + cad)}</td><td class="txt">{_esc(ph.text)}</td></tr>')
    out.append("</tbody></table></div></section>")
    return "".join(out)


def key_context_html(a) -> str:
    """Key words in the text, line by line, with the translation beside each
    line (keytext.py); confirmed and proposed key words marked apart, the
    stressed syllable underlined."""
    sc = a.score
    keys = KT.key_entries(sc.config, sc.lang)
    if not keys:
        return '<p class="note">This edition lists no key words (editions.yaml).</p>'
    tb = KT.text_blocks(sc.slug)
    out = ['<p class="note">The text as the edition prints it, a line per row, with the edition\'s translation. '
           '<span class="kw kw-conf">Confirmed</span> key words count (gate key_word); '
           '<span class="kw kw-prop">proposed</span> ones have no effect until confirmed in editions.yaml. '
           'The stressed syllable is underlined.' + (f' Text from {_esc(tb["source"])}.' if tb["source"] else "")
           + '</p>']
    found: set = set()
    if tb["missing"]:
        out.append(f'<p class="note"><span class="pill pill-warn">no translation</span> {_esc(tb["missing"])}</p>')
    for b in tb["blocks"]:
        out.append('<div class="scroll"><table class="kwc"><thead><tr><th>Text</th><th>Translation</th></tr></thead><tbody>')
        for line, trans in b:
            toks, f = KT.mark_line(line, sc.lang, keys)
            found |= f
            cells = []
            for t, info in toks:
                if info is None:
                    cells.append(_esc(t))
                    continue
                sy = "".join(f'<u>{_esc(x)}</u>' if st else _esc(x) for x, st in info["syls"])
                cls = "kw-conf" if info["confirmed"] else "kw-prop"
                cells.append(f'<span class="kw {cls}" title="{_esc(info["source"])}; stress: {_esc(info["stress_src"])}">{sy}</span>')
            tr = _esc(trans) if trans is not None else '<span class="note">no translation for this line</span>'
            out.append(f'<tr><td class="kwl">{"".join(cells)}</td><td class="kwt">{tr}</td></tr>')
        out.append("</tbody></table></div>")
    missing = [k["word"] for n, k in keys.items() if n not in found]
    if missing and tb["blocks"]:
        out.append('<p class="note">Key words not found in the printed text: ' + _esc(", ".join(missing)) + '.</p>')
    elif missing:
        out.append('<p class="note">' + _esc(", ".join(f'{k["word"]} ({k["source"]})' for k in keys.values())) + '.</p>')
    return "".join(out)


def metre_tables(a) -> str:
    """Spans against the tactus (meter.displaced_spans) and upper-voice duos
    (texture.duos): information for the reader, from Miki's second review."""
    sc = a.score
    out = ['<section class="tbl" id="t-disp"><h3>Against the tactus</h3>'
           '<p class="note">Syncopation declaimed by two or more voices together, or a hemiola-like chain of '
           'syncopated semibreves in one voice. Inside a span U210 also accepts the displaced pulse as a beat, '
           'and U201 and U202 count half (gate against_tactus).</p>'
           '<div class="scroll"><table><thead><tr><th>From</th><th>Kind</th><th>Voices</th><th>Displaced notes</th>'
           '</tr></thead><tbody>']
    for d in a.displaced:
        ids = [f"{v}:{i}" for v, i in d.notes]
        notes = ", ".join(f"{v} {sc.voices[v][i].where}" for v, i in d.notes)
        out.append(f'<tr class="pick" data-notes="{_notes_attr(ids)}" tabindex="0"><td class="num">{_esc(d.where)}</td>'
                   f'<td>{_esc(d.kind)}</td><td>{_esc(", ".join(d.voices))}</td><td>{_esc(notes)}</td></tr>')
    if not a.displaced:
        out.append('<tr><td colspan="4" class="note">None found.</td></tr>')
    out.append("</tbody></table></div></section>")
    out.append('<section class="tbl" id="t-duo"><h3>Upper-voice duos</h3>'
               '<p class="note">The two highest voices begin new text together, then share some of their note '
               'onsets but not all: they come in and out of each other\'s rhythms. Information only.</p>'
               '<div class="scroll"><table><thead><tr><th>Bars</th><th>Voices</th><th class="num">Onsets shared</th>'
               '<th>Part at</th><th>Meet again at</th></tr></thead><tbody>')
    for d in a.duos:
        ids = [f"{v}:{e.idx}" for v in d.voices for e in sc.voices[v] if not e.rest and d.contains(e.onset)]
        out.append(f'<tr class="pick" data-notes="{_notes_attr(ids)}" tabindex="0">'
                   f'<td class="num">{_esc(d.first_where)}–{_esc(d.last_where)}</td><td>{_esc(" and ".join(d.voices))}</td>'
                   f'<td class="num">{int(d.shared * 100)}%</td><td>{_esc(", ".join(d.apart))}</td>'
                   f'<td>{_esc(", ".join(d.together))}</td></tr>')
    if not a.duos:
        out.append('<tr><td colspan="5" class="note">None found.</td></tr>')
    out.append("</tbody></table></div></section>")
    return "".join(out)


def lexicon_html(rows: list) -> str:
    out = ['<div class="scroll"><table class="lex"><thead><tr><th>Word</th><th>Syllables</th><th>Class</th>'
           '<th class="num">Sung</th><th>Stress from</th><th>Key word</th></tr></thead><tbody>']
    for r in rows:
        syl = "-".join(f"<b>{_esc(s.upper())}</b>" if i == r["stress"] else _esc(s) for i, s in enumerate(r["syls"]))
        flag = "" if r["known"] else ' <span class="pill pill-warn">not in lexicon</span>'
        key = ""
        if r["key"]:
            key = (f'<span class="pill">{_esc(r["key"])}</span>' if r["key"].lower().startswith("proposed")
                   else f'<span class="pill pill-on">{_esc(r["key"])}</span>')
        out.append(f'<tr><td class="txt">{_esc(r["word"])}{flag}</td><td class="syl">{syl}</td><td>{_esc(r["cls"])}</td>'
                   f'<td class="num">{r["count"]}</td><td>{_esc(r["src"])}</td><td>{key}</td></tr>')
    out.append("</tbody></table></div>")
    return "".join(out)


def edit_data(sc, all_sys: list, lyr_found: list, aligned: dict) -> dict:
    """What the page needs to show and record underlay edits: each note's bar,
    position and syllables; each voice's notes in order; where each system's
    lyric lines and staves lie; which voices' lyrics are tied to voices.ily."""
    nsys, lyb, stb = {}, defaultdict(list), {}
    for i, s in enumerate(all_sys):
        for st in s["staves"]:
            if st.get("voice"):
                stb[f"{i}|{st['voice']}"] = round(st["bot"], 3)
            for n in st["notes"]:
                nsys[n] = i
    for v, verse, nid, x, y in lyr_found:
        if nid in nsys:
            lyb[f"{nsys[nid]}|{v}|{verse}"].append(y)
    ed = {}
    for v in sc.parts:
        for e in sc.voices[v]:
            if e.rest:
                continue
            ed[f"{v}:{e.idx}"] = [str(e.measure), str(F(e.pos)),
                                  {k: [l.text, l.syllabic] for k, l in e.lyrics.items()}]
    return {"slug": sc.slug, "parts": sc.parts, "ed": ed,
            "vnotes": {v: [f"{v}:{e.idx}" for e in sc.voices[v] if not e.rest] for v in sc.parts},
            "verses": {v: sorted({k for e in sc.voices[v] for k in e.lyrics}, key=int) for v in sc.parts},
            "nsys": nsys, "lyb": {k: round(sorted(ys)[len(ys) // 2], 3) for k, ys in lyb.items()}, "stb": stb,
            "tied": {f"{v}|{verse}": vl.ok for (v, verse), vl in aligned.items()},
            "generated": UE.GENERATED.get(sc.slug, "")}


def _git_rev() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()
    except OSError:
        return ""


def build(path: str | Path, out: Path, *, baseline: Path | None = None) -> Path:
    res = run(path)
    a = res.analysis
    sc = a.score
    base = B.load(baseline) if baseline else {}
    B.apply([res], base)
    notes, keys = note_table(sc)
    notes_by_id = {n["id"]: n for n in notes}
    pages_svg, pos = [], {}
    note = ""
    try:
        raw = render_svg(sc.slug)
    except RuntimeError as e:
        raw, note = [], str(e)
    all_sys = []
    mapped = []
    lyr_found = []
    voices_ily = f"editions/{sc.slug}/music/voices.ily"
    aligned = UE.align(sc)
    lyr = UE.svg_tags(sc)
    for i, svg in enumerate(raw):
        s, p, st, fl = map_svg(svg, keys, i, lyr, voices_ily)
        pos.update(p)
        lyr_found.extend(fl)
        syss = systems(st, pos, notes_by_id, sc.parts, i)
        all_sys.extend(syss)
        mapped.append(s)
    ov = overlays(a, pos, all_sys, notes_by_id) if mapped else {}
    for i, s in enumerate(mapped):
        k = s.rfind("</svg>")
        pages_svg.append(s[:k] + ov.get(i, "") + s[k:])
    unmapped = [n for n in notes if n["id"] not in pos]
    data = page_data(res, a, base)
    data["pos"] = {k: [v[0], round(v[1], 2), round(v[2], 2)] for k, v in pos.items()}
    data["notes"] = {n["id"]: [n["where"], n["name"], n["dur"]] for n in notes}
    data.update(edit_data(sc, all_sys, lyr_found, aligned))

    c = Counter(f.level for f in res.findings)
    st = Counter(f["status"] for f in data["findings"])
    kinds = Counter(cd.kind for cd in a.cadences)
    lex = lexicon_rows(a)
    kws = key_word_entries(sc.config)
    title = f"{sc.title} underlay"
    tops = [f for f in data["findings"] if f["regret"] and f["status"] != "accepted"]
    tops = sorted(tops, key=lambda f: -f["regret"])[:5]

    css = (ASSETS / "page.css").read_text(encoding="utf-8") + "\n" + (ASSETS / "edit.css").read_text(encoding="utf-8")
    js = (ASSETS / "page.js").read_text(encoding="utf-8") + "\n" + (ASSETS / "edit.js").read_text(encoding="utf-8")
    level_cards = "".join(
        f'<button type="button" class="lvl lvl-{lv}" data-level="{lv}"><span class="lvl-n">{c.get(lv, 0)}</span>'
        f'<span class="lvl-l">{lv}</span></button>' for lv in ("break", "warn", "look", "info"))
    top_html = "".join(
        f'<li><button type="button" class="link" data-f="{f["n"]}"><span class="rg">{f["regret"]:.2f}</span> '
        f'{_esc(f["rule"])} {_esc(f["voice"])} {_esc(f["where"])}: {_esc(f["message"])}</button></li>' for f in tops)
    kw_conf = [k["word"] for k in kws if k["confirmed"]]
    kw_prop = [k["word"] for k in kws if not k["confirmed"]]
    rules_opts = "".join(f'<option value="{rid}">{rid} {_esc(r["name"])}</option>' for rid, r in data["rules"].items())
    voice_opts = "".join(f'<option value="{_esc(v)}">{_esc(v)}</option>' for v in sc.parts)
    score_html = ("".join(f'<div class="page">{s}</div>' for s in pages_svg) if pages_svg else
                  f'<p class="note pad">The score could not be rendered here (LilyPond 2.24 is needed). {_esc(note)}</p>')
    layer_boxes = "".join(
        f'<label class="tog"><input type="checkbox" id="lay-{k}" data-layer="{k}"{" checked" if on else ""}>'
        f'<span class="sw sw-{k}"></span>{label}</label>'
        for k, label, on in (("cad", "Cadences", True), ("dis", "Dissonance", False), ("phr", "Phrases", False),
                             ("imi", "Imitation", True), ("hom", "Homorhythm", True)))
    mens = sc.config.get("mensuration_note", "")

    doc = f"""<title>{_esc(title)}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
{css}
</style>
<div class="wrap">
<header class="head">
  <p class="eyebrow">Polish Early Music · underlay analyser · review</p>
  <h1>{_esc(sc.title)}</h1>
  <p class="sub">{_esc(sc.slug)} · generated {date.today().isoformat()}{(' from ' + _esc(_git_rev())) if _git_rev() else ''} ·
  mensuration {_esc(sc.config.get('mensuration', ''))}{(' (' + _esc(mens) + ')') if mens else ''}</p>
</header>

<section class="summary" aria-label="Summary">
  <div class="sum-block">
    <h2 class="h-small">Findings by level</h2>
    <div class="lvls">{level_cards}</div>
    <p class="note">Levels are set by regret (warn {data['levels']['warn']}, look {data['levels']['look']}); a break
    is a firm rule (10.1, 10.2, 10.4, 10.5). Baseline: {st.get('accepted', 0)} accepted, {st.get('pending', 0)} pending
    review, {st.get('new', 0)} new (information findings are not tracked).</p>
  </div>
  <div class="sum-block">
    <h2 class="h-small">Biggest regrets, open</h2>
    <ol class="tops">{top_html or '<li class="note">None.</li>'}</ol>
  </div>
  <div class="sum-block">
    <h2 class="h-small">Analysis</h2>
    <p class="facts">{kinds.get('full', 0)} cadences, {kinds.get('evaded', 0) + kinds.get('abandoned', 0)} evaded or
    abandoned, {kinds.get('weak', 0)} weak figures · {len(a.points)} points of imitation ·
    {len(a.regions)} homorhythmic passages · {len(a.displaced)} spans against the tactus · {len(a.duos)} upper-voice duos · {sum(1 for d in a.dissonances.values() if d.label == 'suspension')} suspensions ·
    {len(lex)} words, {sum(1 for r in lex if not r['known'])} not in the lexicon.</p>
    <p class="note">Key words: {len(kw_conf)} confirmed, {len(kw_prop)} proposed (not yet in effect);
    <a href="#keywords">read them in the text, with the translation</a>.</p>
  </div>
</section>

<section class="edits" id="edits" aria-label="Underlay edits">
  <div class="edits-head">
    <h2 class="h-small">Underlay edits <span id="ed-count"></span></h2>
    <div class="edits-actions">
      <button type="button" class="btn primary" id="ed-copy">Copy edits as JSON</button>
      <button type="button" class="btn" id="ed-showjson">Show JSON</button>
      <span class="note" id="ed-copied" role="status"></span>
    </div>
  </div>
  <p class="note ed-db" id="ed-db" role="status"></p>
  <ol class="ed-list" id="ed-list"></ol>
  <textarea id="ed-json" class="ed-json mono" rows="8" readonly hidden aria-label="Edits as JSON"></textarea>
</section>

<div class="work">
<aside class="list" aria-label="Findings">
  <div class="filters">
    <label for="f-level">Level</label>
    <select id="f-level"><option value="open">look or worse</option><option value="all">all</option>
      <option value="break">break</option><option value="warn">warn</option><option value="look">look</option>
      <option value="info">info</option></select>
    <label for="f-rule">Rule</label>
    <select id="f-rule"><option value="">all rules</option>{rules_opts}</select>
    <label for="f-voice">Voice</label>
    <select id="f-voice"><option value="">all voices</option>{voice_opts}</select>
    <label class="tog small"><input type="checkbox" id="f-acc"> hide accepted</label>
  </div>
  <p class="note" id="f-count"></p>
  <ol class="findings" id="findings"></ol>
</aside>

<main class="main">
  <section class="detail" id="detail" aria-live="polite">
    <p class="note pad">Choose a finding to see its rule, why it costs what it costs, and the readings the
    analyser would sing instead. Its notes light up in the score.</p>
  </section>
  <section class="score" aria-label="Score">
    <div class="toolbar">
      <div class="togs">{layer_boxes}</div>
      <button type="button" class="btn" id="ed-mode" aria-pressed="false">Edit underlay</button>
      <div class="zoom"><button type="button" id="z-out" aria-label="Smaller">−</button>
        <button type="button" id="z-in" aria-label="Larger">+</button></div>
    </div>
    <div class="ed-note" id="ed-note" hidden></div>
    <div class="paper" id="paper">{score_html}</div>
    <p class="note">Critical score, rendered by LilyPond from editions/{_esc(sc.slug)}/music/score.ly. Hover a mark for
    its detail. Bands under each system: cadences (◆, with type and tone), entries of each point of imitation,
    homorhythmic passages. On the staff: rings at cadence arrivals with the voice's function, dissonance labels
    above the notes (S suspension with its figure and an arc to the resolution, p passing, ap accented passing,
    n neighbour, c cambiata, a anticipation, e échappée, ? unexplained), phrase brackets under each staff.
    {len(unmapped)} of {len(notes)} notes could not be tied to the drawing.</p>
  </section>
</main>
</div>

<section class="layers" aria-label="Analysis layers">
  <h2>Analysis layers</h2>
  <p class="note">Positions are bar.minim (16.3 is the third minim of bar 16). Click a row to find its notes in the score.</p>
  {tables(a)}
  {metre_tables(a)}
</section>

<section class="keywords" id="keywords" aria-label="Key words in context">
  <h2>Key words in context</h2>
  {key_context_html(a)}
</section>

<section class="lexicon" aria-label="Lexicon">
  <h2>Words and their stress</h2>
  <p class="note">Every word the piece sings, as the lexicon divides it, the stressed syllable in capitals. Check the
  stresses: the stress rules (U202, U206, U302) rest on them.</p>
  {lexicon_html(lex)}
</section>

<footer class="foot"><p class="note">The analyser advises; it never changes an edition. Alternatives are readings to
sing (principles 10.6). docs/analyser.md explains the rules, the costs and the regret.</p></footer>
</div>
<script type="application/json" id="data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>
<script>
{js}
</script>
"""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    return out
