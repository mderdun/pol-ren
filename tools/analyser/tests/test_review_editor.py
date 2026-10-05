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


def _keys(pg, nid, verse, *seq):
    """Enter edit mode at a note, then type text or press named keys ("<Space>")."""
    pg.evaluate("([id, v]) => RV.startEdit(id, v)", [nid, verse])
    for s in seq:
        if s.startswith("<"):
            pg.keyboard.press(s.strip("<>"))
        else:
            pg.keyboard.type(s)
    pg.wait_for_timeout(50)


def _custom(pg):
    return pg.evaluate("() => Object.values(RV.edits).filter(d => !d._seed && d.kind === 'custom')"
                       ".map(d => JSON.parse(JSON.stringify(d)))")


def _id_at(pg, voice, where):
    return pg.evaluate("([v, w]) => RV.D.vnotes[v].find(id => RV.D.notes[id][0] === w)", [voice, where])


def test_nunc_cantus_vere_vere_sequence(browser, tmp_path):
    # Miki, live use: Cantus "Nunc sci-o ve-re, ve-re, sci-o ve-re". 'vere' on
    # 4.3-4.4 and the repeat on 5.1/5.3; the repeat's own 've' must not be taken
    # for the first one, and 'scio vere' at 8-11 stays where it is
    pg, errors = _page(browser, tmp_path, "nunc-scio-vere")
    _keys(pg, _id_at(pg, "Cantus", "4.4"), "1", "re", "<Space>", "ve", "<Space>", "<ArrowRight>", "re", "<Escape>")
    docs = _custom(pg)
    assert len(docs) == 1, docs
    got = [(n["where"], n["syllable"]) for n in docs[0]["notes"]]
    assert got == [("4.4", "re,"), ("5.1", "ve"), ("5.3", "re,"), ("6.2", None)], got
    n, out = _apply(docs)
    assert "REFUSED" not in out and "voices.ily is generated" in out, out
    asks = out.split("asks:")[1].splitlines()[0]
    assert "4.3 G4:ve-" in asks and "4.4 E4:re," in asks and "5.1 E4:ve-" in asks, asks
    assert not errors


def test_vox_move_later_backspace_and_reset(browser, tmp_path):
    pg, errors = _page(browser, tmp_path, "vox-in-rama")
    # a Bassus syllable with two free notes after it
    a, a1, syl = pg.evaluate("""() => {
      const v = RV.D.vnotes.Bassus, ly = id => (RV.D.ed[id][2]['1'] || null);
      for (let k = 1; k + 2 < v.length; k++)
        if (ly(v[k]) && !ly(v[k + 1]) && !ly(v[k + 2])) return [v[k], v[k + 1], ly(v[k])[0]];
    }""")
    # typing the syllable before the caret's slot moves it later, to the caret
    _keys(pg, a1, "1", syl.rstrip(",.;:!?").lower(), "<Escape>")
    got = {n["id"]: n["syllable"] for d in _custom(pg) for n in d["notes"]}
    assert got == {a: None, a1: syl}, got
    n, out = _apply(_custom(pg))
    assert n == 0 and "+bassusWords" in out, out
    # ⌫ on it moves it one note further
    _keys(pg, a1, "1", "<Backspace>", "<Escape>")
    got = {n["id"]: n["syllable"] for d in _custom(pg) for n in d["notes"]}
    assert got[a] is None and a1 not in got and syl in got.values(), got
    # Reset this voice: an inline confirm, then no custom edits left
    pg.evaluate("([id]) => RV.startEdit(id, '1')", [a])
    pg.click("#e-reset")
    assert "Withdraw" in pg.inner_text("#dock")
    pg.click("#e-reset-yes")
    pg.keyboard.press("Escape")
    assert _custom(pg) == []
    assert not errors


def _reading(pg, voice, verse="1"):
    return dict((w, s) for w, s in pg.evaluate("([v, x]) => RV.reading(v, x)", [voice, verse]))


def test_nunc_cantus_extra_vere_never_takes_scio_vere(browser, tmp_path):
    # Miki, 5 Oct 2026 (second report): writing 'vere' on 4.3-4.4, 'vere' on
    # bar 5 and then once more on bar 6 renamed and pulled back the 'sci', 'o'
    # of the next phrase, leaving bars 8-11 empty. Text that is not the next
    # syllable is inserted (or replaces the syllable on that note); nothing else moves.
    pg, errors = _page(browser, tmp_path, "nunc-scio-vere")
    _keys(pg, _id_at(pg, "Cantus", "4.3"), "1", "ve", "-", "re", "<Space>", "ve", "-", "<ArrowRight>", "re",
          "<Space>", "ve", "-", "re", "<Escape>")
    got = _reading(pg, "Cantus")
    assert (got["4.3"], got["4.4"], got["5.1"], got["5.3"]) == ("ve", "re,", "ve", "re,"), got
    assert got["6.2"] == "ve", got
    assert got["8.3"] == "sci" and got["10.1"] == "o" and got["10.2"] == "ve" and got["11.3"] == "re,", got
    assert not errors


def test_pause_mid_syllable_does_not_commit_it(browser, tmp_path):
    # a pause after 'v' must not save 'v' as the syllable (idle saving keeps the buffer)
    pg, errors = _page(browser, tmp_path, "nunc-scio-vere")
    nid = _id_at(pg, "Cantus", "4.3")
    pg.evaluate("([id, v]) => RV.startEdit(id, v)", [nid, "1"])
    pg.keyboard.type("v")
    pg.wait_for_timeout(1800)
    pg.keyboard.type("e")
    pg.keyboard.press("-")
    pg.keyboard.type("re")
    pg.keyboard.press("Escape")
    got = _reading(pg, "Cantus")
    assert got["4.3"] == "ve" and got["4.4"] == "re,", got
    assert got["8.3"] == "sci", got
    assert not errors
