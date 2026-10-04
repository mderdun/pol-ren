"""Which bar ends each page of a performance score, and what each voice does
there (for P210, page turns).

Systems are counted on the committed PDF (pdf.py) and mapped to bars through
the edition's own break lists (music/engraving.ily, prBreaksPerformance...)
plus the end of each score block. Where the count of polyphonic systems on
the pages does not match the break list, the mapping is not trusted and no
finding is made.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .registry import ROOT

SECTION_STYLES = {"light-light", "light-heavy", "heavy-light", "heavy-heavy"}


def break_lists(slug: str) -> list[int]:
    f = ROOT / "editions" / slug / "music" / "engraving.ily"
    if not f.exists():
        return []
    out = set()
    for m in re.finditer(r"^prBreaksPerformance\w*\s*=\s*#'\(([^)]*)\)", f.read_text(encoding="utf-8"), re.M):
        out |= {int(x) for x in m.group(1).split()}
    return sorted(out)


def read_musicxml(path: Path) -> dict:
    """measures (in order, as written), the bars that end a section, and for
    each part, per measure: does it end with a rest, does it begin with one."""
    root = ET.parse(path).getroot()
    names = {p.get("id"): (p.findtext("part-name") or "").strip("[]") for p in root.iter("score-part")}
    measures: list[str] = []
    section_end: set[str] = set()
    parts: dict[str, dict] = {}
    for part in root.findall("part"):
        name = names[part.get("id")]
        if "chant" in name.lower() or "versus" in name.lower():
            continue
        per: dict[str, tuple[bool, bool]] = {}
        for m in part.findall("measure"):
            num = m.get("number") or ""
            if num not in measures:
                measures.append(num)
            evs = [n for n in m.findall("note") if n.find("chord") is None and n.find("grace") is None]
            if evs:
                per[num] = (evs[0].find("rest") is not None, evs[-1].find("rest") is not None)
            for bl in m.findall("barline"):
                if bl.get("location", "right") != "right":
                    continue
                rep = bl.find("repeat")
                end = bl.find("ending")
                if (bl.findtext("bar-style") in SECTION_STYLES or (rep is not None and rep.get("direction") == "backward")
                        or (end is not None and end.get("type") in ("stop", "discontinue"))):
                    section_end.add(num)
        parts[name] = per
    return {"measures": measures, "section_end": section_end, "parts": parts}


def system_ends(breaks: list[int], data: dict, n_systems: int) -> list[str] | None:
    """The last bar of each polyphonic system, or None if no reading of the
    break list matches the number of systems on the pages."""
    ms = data["measures"]
    numeric = [m for m in ms if m.isdigit()]
    if not numeric:
        return None
    final = numeric[-1]
    before_other = {ms[i] for i in range(len(ms) - 1) if ms[i].isdigit() and not ms[i + 1].isdigit()}
    options = [
        set(map(str, breaks)) | {final},
        set(map(str, breaks)) | {final} | before_other,
        set(map(str, breaks)) | {final} | before_other | data["section_end"],
    ]
    for o in options:
        ends = [m for m in ms if m in o]
        if len(ends) == n_systems:
            return ends
    return None


def playing_through(data: dict, bar: str) -> list[str]:
    """Voices that neither rest at the end of `bar` (or the start of the next)
    nor reach a section end there."""
    if bar in data["section_end"]:
        return []
    ms = data["measures"]
    nxt = ms[ms.index(bar) + 1] if bar in ms and ms.index(bar) + 1 < len(ms) else None
    out = []
    for name, per in data["parts"].items():
        ends_rest = per.get(bar, (False, False))[1]
        next_rest = per.get(nxt, (False, False))[0] if nxt else True
        if not (ends_rest or next_rest):
            out.append(name)
    return out
