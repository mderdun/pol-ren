"""The raster reading the PDF checks rely on: staves, systems, gaps in staff
spaces, extenders, and the page-turn mapping."""
import pytest

from tools.style.pdf import PdfDoc, extenders_below
from tools.style.pdf_fixtures import build
from tools.style.turns import playing_through, read_musicxml, system_ends


def test_staves_systems_and_gaps(tmp_path):
    path, _ = build("gould-fail", tmp_path)
    pdf = PdfDoc.open(path)
    [page] = pdf.music_pages
    assert len(page.staves) == 8
    assert [len(s.staves) for s in page.systems] == [4, 4]
    for s in page.staves:
        assert s.space == pytest.approx(4.75 * 200 / 72, abs=0.5)
    assert all(g == pytest.approx(10, abs=0.3) for s in page.systems for g in s.gaps)
    a, b = page.systems
    assert (b.top - a.bottom) / a.space == pytest.approx(8, abs=0.3)


def test_extenders_found_and_ledger_lines_ignored(tmp_path):
    path, _ = build("gould-pass", tmp_path)
    pdf = PdfDoc.open(path)
    [page] = pdf.music_pages
    st = page.staves[3]          # the staff with ledger lines under it
    ext = extenders_below(page.raster, st, page.staves[4].top)
    dists = [(y - st.bottom) / st.space for y, _, _ in ext]
    assert dists and all(d == pytest.approx(3, abs=0.3) for d in dists)


def test_staff_extent_in_points(tmp_path):
    path, _ = build("wide-system", tmp_path)
    pdf = PdfDoc.open(path)
    [page] = pdf.music_pages
    assert max(s.x1_pt for s in page.staves) == pytest.approx(565, abs=2)


def test_turn_mapping(tmp_path):
    path, meta = build("turn-mid-phrase", tmp_path)
    data = read_musicxml(meta["musicxml"])
    ends = system_ends(meta["breaks"], data, 4)
    assert ends == ["5", "10", "15", "20"]
    assert playing_through(data, "10") == ["Cantus", "Altus", "Tenor", "Bassus"]
    assert playing_through(data, "20") == []          # the final bar line ends a section
    assert system_ends(meta["breaks"], data, 7) is None   # a count that does not match is not trusted
