"""The review page's lyric editor in a browser (Playwright and LilyPond
needed; skipped otherwise): typing a syllable of the text on another note
re-places it, Sibelius-style, and the document it saves passes
`edits apply --dry-run` without --allow-text."""
import io
import shutil

import pytest

from tools.analyser import review
from tools.analyser import underlay_edits as U
from tools.analyser.ingest import ROOT

pw = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.skipif(shutil.which("lilypond") is None, reason="LilyPond 2.24 needed to render the score")


def _xml(slug):
    return ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml"


@pytest.fixture(scope="module")
def browser():
    with pw.sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception as e:  # no browser installed
            pytest.skip(f"chromium not available: {e}")
        yield b
        b.close()


BUILT = {}


def _page(browser, tmp_path, slug):
    if slug not in BUILT:
        BUILT[slug] = review.build(_xml(slug), tmp_path / f"{slug}.html")
    out = BUILT[slug]
    doc = tmp_path / f"{slug}-doc.html"
    doc.write_text("<!doctype html><html><head></head><body>" + out.read_text(encoding="utf-8") + "</body></html>",
                   encoding="utf-8")
    pg = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(doc.as_uri())
    pg.wait_for_timeout(300)
    return pg, errors


def _type_at(pg, nid, verse, text):
    pg.evaluate("([id, v]) => RV.startEdit(id, v)", [nid, verse])
    pg.keyboard.type(text)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(100)
    return pg.evaluate("() => Object.values(RV.edits).filter(d => !d._seed && d.kind === 'custom')"
                       ".map(d => JSON.parse(JSON.stringify(d)))")


def _apply(edits):
    buf = io.StringIO()
    n = U.apply_edits(edits, dry_run=True, out=buf)
    return n, buf.getvalue()


def test_nunc_move_ro_of_herodis(browser, tmp_path):
    # Nunc Altus 'He-ro-dis' at 32-33: 'ro' drawn back from 33.2 to 33.1
    pg, errors = _page(browser, tmp_path, "nunc-scio-vere")
    nid = pg.evaluate("() => RV.D.vnotes.Altus.find(id => RV.D.notes[id][0] === '33.1')")
    before = pg.evaluate("([id]) => { const v = RV.D.vnotes.Altus, i = v.indexOf(id);"
                         " return v.slice(i, i + 3).map(x => (RV.D.ed[x][2]['1'] || [null])[0]); }", [nid])
    assert before[0] is None and "ro" in before, before
    edits = _type_at(pg, nid, "1", "ro")
    assert len(edits) == 1, edits
    notes = [(n["where"], n["syllable"]) for n in edits[0]["notes"]]
    assert notes[0] == ("33.1", "ro") and ("33.2", None) in notes, notes
    n, out = _apply(edits)
    # accepted (no text change); Nunc's voices.ily is generated, so apply only prints the change
    assert "REFUSED" not in out and "voices.ily is generated" in out, out
    assert "33.1 E4:ro-" in out.split("asks:")[1].splitlines()[0], out
    assert not errors


def test_vox_draw_back_after_melisma(browser, tmp_path):
    # Vox Bassus: the first syllable after a melisma drawn back one note
    pg, errors = _page(browser, tmp_path, "vox-in-rama")
    nid, syl, old = pg.evaluate("""() => {
      const v = RV.D.vnotes.Bassus, ly = id => (RV.D.ed[id][2]['1'] || null);
      for (let k = 2; k < v.length; k++)
        if (ly(v[k]) && !ly(v[k - 1]) && ly(v[k - 2])) return [v[k - 1], ly(v[k])[0], v[k]];
    }""")
    edits = _type_at(pg, nid, "1", syl.rstrip(",.;:!?").lower())
    assert len(edits) == 1, edits
    got = {n["id"]: n["syllable"] for n in edits[0]["notes"]}
    assert got[nid] == syl and got[old] is None, got
    n, out = _apply(edits)
    assert n == 0, out
    assert "+bassusWords" in out
    assert not errors


def test_genuine_text_change_is_kept_and_refused(browser, tmp_path):
    # a syllable not in the voice's text nearby is a text change: kept, ringed, refused by apply
    pg, errors = _page(browser, tmp_path, "vox-in-rama")
    nid = pg.evaluate("() => RV.D.vnotes.Bassus[5]")
    edits = _type_at(pg, nid, "1", "zzq")
    assert any(n["syllable"] == "zzq" for d in edits for n in d["notes"])
    assert pg.evaluate("() => document.querySelectorAll('ellipse.bad').length") >= 1
    n, out = _apply(edits)
    assert n == 1 and "changes the text" in out
    assert not errors
