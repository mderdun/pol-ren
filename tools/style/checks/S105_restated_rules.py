"""A method sentence that shares a run of five words (three of them content
words) with a rule in docs/editorial-principles.md, or states a rule with
always/never/must, and cites no rule number."""
import re
from functools import lru_cache

from ..findings import Hit
from ..registry import ROOT
from ..sources import section_span, sentences

STOP = set("""a an the of in on at to for by and or but is are be as it its this that these those with from not no
so if then than which who whom what where when there here each every one only all any into onto also has have had
was were been being do does did their them they he she his her our we i my me""".split())
N = 5
MODAL = re.compile(r"\b(we|the edition|this edition|editions|editorial \w+)\b[^.]*\b(always|never|must)\b", re.I)
CITE = re.compile(r"principles\s+\d+(\.\d+)?", re.I)


def words(s: str) -> list[str]:
    s = re.sub(r"\\[A-Za-z@]+\*?", " ", s)
    return re.findall(r"[a-z]+(?:['’][a-z]+)?", s.lower())


def shingles(ws: list[str]):
    for i in range(len(ws) - N + 1):
        g = tuple(ws[i:i + N])
        if sum(1 for w in g if w not in STOP) >= 3:
            yield g


@lru_cache(maxsize=1)
def principle_shingles() -> dict:
    p = ROOT / "docs" / "editorial-principles.md"
    if not p.exists():
        return {}
    out = {}
    sec, rule = "?", ""
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (\d+)\.", line)
        if m:
            sec, rule = m.group(1), m.group(1)
        m2 = re.match(r"^\s*(\d+)\. ", line)
        if m2:
            rule = f"{sec}.{m2.group(1)}"
        for g in shingles(words(line)):
            out.setdefault(g, rule)
    return out


def check(doc):
    span = section_span(doc, r"editorial method|method")
    if not span:
        return
    ps = principle_shingles()
    for a, b in sentences(doc.code, *span):
        s = doc.code[a:b]
        if CITE.search(s) or s.lstrip().startswith("\\section"):
            continue
        # a rule cited in the same paragraph is being applied, not restated
        pa = doc.code.rfind("\n\n", span[0], a)
        pb = doc.code.find("\n\n", b)
        if CITE.search(doc.code[pa if pa >= 0 else span[0]:pb if pb >= 0 else span[1]]):
            continue
        prose = doc.prose[a:b]
        why = None
        for g in shingles(words(prose)):
            if g in ps:
                why = f"'{' '.join(g)}' is the wording of principles {ps[g]}" if ps[g] else f"'{' '.join(g)}'"
                break
        if why is None and MODAL.search(prose):
            why = "a rule stated as always/never/must"
        if why:
            lead = " ".join(words(prose)[:6])
            yield Hit(key=lead, offset=a + (len(s) - len(s.lstrip())), values={"why": why})
