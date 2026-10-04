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
    assert "localStorage" not in text
    assert ':root:not([data-theme="light"])' in text and ':root[data-theme="dark"]' in text
    assert len(text.encode("utf-8")) < 16 * 1024 * 1024
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
    for layer in ("cad", "dis", "phr", "imi", "hom"):
        assert f'class="layer layer-{layer}"' in text
