"""The review page: one self-contained HTML file per piece."""
import json
import re
import shutil

import pytest

from tools.analyser import review
from tools.analyser.ingest import ROOT

VOX = ROOT / "editions" / "vox-in-rama" / "pdf" / "vox-in-rama.musicxml"


def _data(text):
    m = re.search(r'<script type="application/json" id="data">(.*?)</script>', text, re.S)
    return json.loads(m.group(1))


def _common(text):
    title = re.search(r"<title>(.*?)</title>", text).group(1)
    assert 2 <= len(title.split()) <= 4
    # nothing loads from outside: the only URLs are the SVG namespaces
    urls = set(re.findall(r'https?://[^"\s)<]+', text))
    assert urls <= {"http://www.w3.org/2000/svg", "http://www.w3.org/1999/xlink"}, urls
    # browser storage only as a convenience, behind try; no dialogs, no downloads;
    # the db only through claude.use(), never window.claude.db
    ls = [ln for ln in text.splitlines() if "window.localStorage" in ln]
    assert len(ls) == 2 and all(re.search(r"try \{.*window\.localStorage", ln) for ln in ls), ls
    for bad in ("alert(", "confirm(", "prompt(", "download=", "window.claude.db", "fetch("):
        assert bad not in text, bad
    assert 'window.claude.use' in text
    assert ':root:not([data-theme="light"])' in text and ':root[data-theme="dark"]' in text
    assert len(text.encode("utf-8")) < 16 * 1024 * 1024
    # page contract: content only, the title first; one screen (no document scroll)
    assert text.startswith("<title>")
    assert not re.search(r"<(!doctype|html|head|body)[\s>]", text, re.I)
    assert "html, body { height: 100%; margin: 0; overflow: hidden; }" in text
    assert "prefers-reduced-motion" in text and "#9a1e1e" in text.lower()
    # the main view carries no summary tiles, regrets list or edits box
    for gone in ('class="summary"', 'class="tops"', 'id="ed-list"', 'id="edits"'):
        assert gone not in text, gone
    d = _data(text)
    assert d["findings"] and all(f["notes"] for f in d["findings"])
    return d


def test_page_without_lilypond(tmp_path, monkeypatch):
    monkeypatch.setattr(review, "render_svg", lambda slug: [])
    out = review.build(VOX, tmp_path / "vox.html")
    text = out.read_text(encoding="utf-8")
    d = _common(text)
    assert "could not be rendered" in text and not d["pos"]
    f = next(f for f in d["findings"] if f["alternatives"])
    assert f["grid"]["rows"][0]["label"] == "Current" and len(f["grid"]["rows"]) == len(f["alternatives"]) + 1
    assert d["principles"]["10.3"].startswith("The last syllable of a phrase")


@pytest.mark.skipif(shutil.which("lilypond") is None, reason="LilyPond 2.24 needed to render the score")
def test_page_with_the_score(tmp_path):
    out = review.build(VOX, tmp_path / "vox.html")
    text = out.read_text(encoding="utf-8")
    d = _common(text)
    # every note of the analyser is tied to a note head in the drawing
    assert len(d["pos"]) == len(d["notes"])
    assert text.count('class="nh"') >= len(d["notes"])
    assert "textedit://" not in text
    for layer in ("cad", "dis", "phr", "imi", "hom", "tac", "kw"):
        assert f'class="layer layer-{layer}"' in text
    # every syllable the analyser sees is tagged with its note in the drawing,
    # and each voice's lyric line has a baseline in each system
    sylls = sum(1 for n in d["ed"].values() for _ in n[2])
    tagged = re.findall(r'<g class="ly" data-n="([^"]+)" data-verse="(\d+)">', text)
    assert len(set(tagged)) == sylls
    assert all(d["tied"].values()) and d["lyb"]


def test_edit_data(tmp_path, monkeypatch):
    monkeypatch.setattr(review, "render_svg", lambda slug: [])
    d = _data(review.build(VOX, tmp_path / "vox.html").read_text(encoding="utf-8"))
    assert d["slug"] == "vox-in-rama" and set(d["vnotes"]) == set(d["parts"])
    f = next(f for f in d["findings"] if len(f["pl"]) > 1)
    assert len(f["pl"]) == len(f["alternatives"]) + 1
    # each reading puts its syllables on notes of the span, with a syllabic
    for row in f["pl"]:
        assert all(p[0] in f["span"] and p[2] in ("begin", "middle", "end", "single") for p in row)
    # the current reading is the score's
    for nid, syl, sb in f["pl"][0]:
        assert d["ed"][nid][2][f["verse"]] == [syl, sb]
    # a dropped word: the alternative has one syllable fewer, and the rest keep theirs
    alt = next((f for f in d["findings"] if any(a.get("edit") == "drop" for a in f["alternatives"])), None)
    if alt is not None:
        k = next(i for i, a in enumerate(alt["alternatives"], 1) if a.get("edit") == "drop")
        assert len(alt["pl"][k]) == len(alt["pl"][0]) - 1


def test_plain_lines_and_systems(tmp_path, monkeypatch):
    # v3 (Miki: "so much text on the pages that it all reads as noise"): each
    # finding has a one-line plain reading, with no rule id or number in it
    monkeypatch.setattr(review, "render_svg", lambda slug: [])
    d = _data(review.build(VOX, tmp_path / "vox.html").read_text(encoding="utf-8"))
    for f in d["findings"]:
        assert f["plain"] and "\n" not in f["plain"] and not re.search(r"\bU\d{3}\b|\d\.\d\d", f["plain"]), f["plain"]
        assert isinstance(f["t"], float)
    u301 = next(f for f in d["findings"] if f["rule"] == "U301")
    assert re.match(r"‘.+’ comes after the cadence on \w", u301["plain"]), u301["plain"]
    assert set(d["on"]) == set(d["ed"]) and d["mens"]
    assert d["sys"] == [] and d["seed"] == []


def test_plain_cadence_line():
    class Fk:
        rule, text, word = "U301", "ple", "plebis"
        message = "the arrival carries 'ple', and 'bis,' comes after it (clausula vera cadence on C, full)"
    assert review.plain(Fk) == "‘bis’ comes after the cadence on C"


def test_recommendations_are_seeded():
    # Claude's recommendations for Nunc travel with the page, as suggestions
    seeds = review.seeds("nunc-scio-vere")
    assert seeds and all(s["reason"].startswith("Claude's recommendation:") for s in seeds)
    assert review.seeds("vox-in-rama") == []


def test_key_words_in_context(tmp_path, monkeypatch):
    # Miki, second review: key words "in context of the verse (and with
    # translations), rather than alphabetically"
    monkeypatch.setattr(review, "render_svg", lambda slug: [])
    text = review.build(VOX, tmp_path / "vox.html").read_text(encoding="utf-8")
    sec = text[text.index('id="keywords"'):]
    lines = re.findall(r'<td class="kwl">(.*?)</td><td class="kwt">(.*?)</td>', sec)
    assert len(lines) == 5
    assert lines[0][1] == "A voice was heard in Rama," and "Rama" in re.sub(r"<[^>]+>", "", lines[0][0])
    assert lines[3][1] == "and she would not be comforted,"
    # consolari: confirmed (Miki, 5 Oct 2026, secondary to noluit), the stress
    # on -la- underlined, in the text's order
    assert '<span class="kw kw-conf"' in lines[3][0] and "<u>la</u>" in lines[3][0]
    assert sec.index("A voice was heard") < sec.index("because they are not.")


def test_key_words_without_translation(monkeypatch):
    from tools.analyser import keytext
    tb = keytext.text_blocks("bogurodzica")
    assert not tb["blocks"] and "No text-and-translation table" in tb["missing"]
