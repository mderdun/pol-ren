"""Read an edition's MusicXML (from `make musicxml`) into the score model.

The parser follows the one in tools/underlay_audit.py, which is correct for our
export, and adds what the analyser needs: alterations, the mensuration sign,
section breaks (second endings, unmeasured chant sections), the dashed ties of
divided notes, and the source map (<slug>.srcmap.tsv, written by the export).

legacy=True reproduces the old audit exactly: every tie is merged, including
the dashed ties of divided notes, and a merged note keeps only its first
syllable. That is how the old audit lost three syllables of the Plaude Tenor
(bars 14 and 18); see selfcheck.py.
"""
from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from fractions import Fraction as F
from pathlib import Path

import yaml

from .model import Event, Lyric, Score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def editions_config() -> dict:
    return yaml.safe_load((HERE / "editions.yaml").read_text(encoding="utf-8"))


def slug_of(path: Path) -> str:
    return path.name.split(".")[0]


def _measure_digits(num: str | None) -> int:
    return int("".join(c for c in (num or "0") if c.isdigit()) or 0)


def load_srcmap(path: Path) -> dict:
    """(part, measure, position in whole notes) -> (file, line, column)."""
    side = path.with_suffix(".srcmap.tsv")
    if not side.exists():
        return {}
    out = {}
    with side.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            key = (row["part"], row["measure"], F(row["position"]))
            out.setdefault(key, (row["file"], int(row["line"]), int(row["column"]) + 1))
    return out


def parse(path: str | Path, *, legacy: bool = False, config: dict | None = None) -> Score:
    path = Path(path)
    slug = slug_of(path)
    cfg = (config if config is not None else editions_config()).get(slug, {}) or {}
    root = ET.parse(path).getroot()
    names = {p.get("id"): p.findtext("part-name") for p in root.iter("score-part")}
    title = root.findtext("work/work-title") or slug
    srcmap = {} if legacy else load_srcmap(path)
    score = Score(slug=slug, path=str(path), title=title, config=cfg, lang=cfg.get("lang", "la"))
    for part in root.findall("part"):
        name = names[part.get("id")]
        div, t, beats = 1, F(0), F(8)
        sign = None
        raw: list[dict] = []
        pending_break = False
        for m in part.findall("measure"):
            mstart = t
            mnum = m.get("number") or ""
            num = _measure_digits(mnum)
            for el in m:
                if el.tag == "barline":
                    end = el.find("ending")
                    if el.get("location") == "left" and end is not None and end.get("type") == "start" \
                            and (end.get("number") or "1").split(",")[0].strip() != "1":
                        pending_break = True
                if el.tag == "attributes":
                    if el.findtext("divisions"):
                        div = int(el.findtext("divisions"))
                    tm = el.find("time")
                    if tm is not None:
                        if tm.find("senza-misura") is not None:
                            if sign != "free":
                                pending_break = True
                            sign = "free"
                        else:
                            if sign == "free":
                                pending_break = True
                            if tm.get("symbol") == "cut":
                                sign = "cut"
                            elif tm.get("symbol") == "common":
                                sign = "C"
                            elif tm.get("print-object") == "no":
                                sign = sign if sign not in (None, "free") else "none"
                            else:
                                sign = sign or "C"
                        if tm.findtext("beats"):
                            beats = F(int(tm.findtext("beats")) * 4, int(tm.findtext("beat-type")))
                if el.tag == "backup":
                    t -= F(int(el.findtext("duration")), div)
                if el.tag == "forward":
                    t += F(int(el.findtext("duration")), div)
                if el.tag != "note" or el.find("chord") is not None or el.find("grace") is not None:
                    continue
                d = F(int(el.findtext("duration") or 0), div)
                rest = el.find("rest") is not None
                ties = [x.get("type") for x in el.findall("tie")]
                dashed_out = any(x.get("type") == "start" and x.get("line-type") == "dashed"
                                 for x in el.findall("notations/tied"))
                ly = {}
                for lyr in el.findall("lyric"):
                    tx = lyr.find("text")
                    ly[lyr.get("number") or "1"] = Lyric(
                        text=lyr.findtext("text") or "", syllabic=lyr.findtext("syllabic") or "single",
                        italic=tx is not None and tx.get("font-style") == "italic")
                ev = dict(t=t, pos=t - mstart, bar=num, measure=mnum, d=d, rest=rest, ties=ties,
                          dashed_out=dashed_out, ly=ly, blen=beats, sign=sign or "none",
                          brk=pending_break)
                pending_break = False
                if not rest:
                    ev["step"] = el.findtext("pitch/step")
                    ev["octave"] = int(el.findtext("pitch/octave"))
                    ev["alter"] = int(float(el.findtext("pitch/alter") or 0))
                raw.append(ev)
                t += d
        events: list[Event] = []
        prev_dashed = False
        for r in raw:
            last = events[-1] if events else None
            tied_in = last is not None and not r["rest"] and "stop" in r["ties"] and not last.rest
            if tied_in and (legacy or not prev_dashed):
                last.dur += r["d"]
                for k, v in r["ly"].items():
                    last.lyrics.setdefault(k, v)
                prev_dashed = r["dashed_out"]
                continue
            e = Event(voice=name, idx=len(events), onset=r["t"], dur=r["d"], rest=r["rest"],
                      bar=r["bar"], measure=r["measure"], pos=r["pos"], bar_len=r["blen"],
                      sign=r["sign"], step=r.get("step"), octave=r.get("octave"),
                      alter=r.get("alter", 0), lyrics=dict(r["ly"]), divided=tied_in,
                      after_break=r["brk"] and not legacy)
            if srcmap and not e.rest:
                e.src = srcmap.get((name, e.measure, e.pos / 4))
            events.append(e)
            prev_dashed = r["dashed_out"]
        score.voices[name] = events
    # the edition's own mensuration wins where the score prints none
    want = cfg.get("mensuration")
    if want and not legacy:
        for evs in score.voices.values():
            for e in evs:
                if e.sign in ("none",) or (e.sign == "cut" and want == "C"):
                    e.sign = want
    return score
