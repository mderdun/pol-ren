"""Underlay edits from the review page, applied to voices.ily (underlay_edits.py)."""
import io
from fractions import Fraction as F

import pytest

from tools.analyser import underlay_edits as U
from tools.analyser.findings import run
from tools.analyser.ingest import ROOT


def _score(slug):
    return run(ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml").analysis.score


@pytest.fixture(scope="module")
def vox():
    return _score("vox-in-rama")


@pytest.fixture(scope="module")
def zmierzka():
    return _score("juz-sie-zmierzka")


def _rec(e, syl, sb):
    return {"id": f"{e.voice}:{e.idx}", "bar": str(e.measure), "pos": str(F(e.pos)), "pitch": e.name,
            "syllable": syl, "syllabic": sb if syl else None}


def _apply(edits, **kw):
    buf = io.StringIO()
    n = U.apply_edits(edits, dry_run=True, out=buf, **kw)
    return n, buf.getvalue()


@pytest.mark.parametrize("slug", ["vox-in-rama", "juz-sie-zmierzka", "nunc-scio-vere", "plaude-euge"])
def test_every_voice_is_tied_and_round_trips(slug):
    sc = _score(slug)
    al = U.align(sc)
    text = (ROOT / "editions" / slug / "music" / "voices.ily").read_text(encoding="utf-8")
    assert al
    for key, vl in al.items():
        assert vl.ok, (key, vl.why)
        same = U.render(vl, U.assignment(vl, sc))
        for b in vl.blocks:
            assert U._strip_comments(text[b.start:b.end]) == same[b.name], b.name


def _move_back(sc, voice, verse="1"):
    """A custom edit: the first syllable after a melisma drawn back one note."""
    vl = U.align(sc)[(voice, verse)]
    a = U.assignment(vl, sc)
    evs = sc.voices[voice]
    for k in range(2, len(a)):
        if a[k] is not None and a[k - 1] is None and a[k - 2] is not None:
            e_new, e_old = evs[vl.notes[k - 1]], evs[vl.notes[k]]
            return {"id": f"{sc.slug}__test", "slug": sc.slug, "kind": "custom", "finding": None, "voice": voice,
                    "verse": verse, "alternative": None, "reason": "test", "status": "proposed",
                    "updatedAt": "2026-10-05T00:00:00Z", "by": None,
                    "notes": [_rec(e_new, a[k][0], a[k][1]), _rec(e_old, None, None)]}, a[k][0]
    raise AssertionError("no melisma")


def test_custom_edit_vox(vox):
    edit, syl = _move_back(vox, "Bassus")
    n, out = _apply([edit])
    assert n == 0, out
    assert "--- a/editions/vox-in-rama/music/voices.ily" in out and "+bassusWords" in out
    assert "now:" in out and "asks:" in out


def test_declined_suggestion_changes_nothing(vox):
    # review page v3: a suggestion the editor declines stays in the db, marked declined
    edit, _ = _move_back(vox, "Bassus")
    edit["status"] = "declined"
    edit["recommendation"] = "Claude's recommendation: test"
    n, out = _apply([edit])
    assert n == 0 and "declined on the page" in out and "+bassusWords" not in out


def test_alternative_vox(vox):
    res = run(ROOT / "editions" / "vox-in-rama" / "pdf" / "vox-in-rama.musicxml")
    f = next(f for f in res.findings if f.alternatives and not f.alternatives[0].get("edit"))
    evs = vox.voices[f.voice]
    at = {e: t for e, t in f.alternatives[0]["placement"]}
    cur = {e: evs[e].lyrics[f.verse].syllabic for e, _ in f.placement}
    sbs = [cur[e] for e, _ in f.placement]
    sb_at = {e: s for (e, _), s in zip(f.alternatives[0]["placement"], sbs)}
    notes = [_rec(evs[j], at.get(j), sb_at.get(j)) for j in range(*f.span) if not evs[j].rest]
    edit = {"id": "vox__alt", "slug": "vox-in-rama", "kind": "alternative", "finding": f.fingerprint,
            "voice": f.voice, "verse": f.verse, "alternative": 1, "notes": notes, "reason": "",
            "status": "proposed", "updatedAt": "2026-10-05T00:00:00Z", "by": None}
    n, out = _apply([edit])
    assert n == 0, out
    assert f"+{f.voice.lower()}Words" in out


def test_zmierzka_second_stanza(zmierzka):
    edit, _ = _move_back(zmierzka, "Altus", "2")
    n, out = _apply([edit])
    assert n == 0, out
    # the block is on its own lines: only the line of syllables changes, \set stanza stays
    assert "+++ b/editions/juz-sie-zmierzka/music/voices.ily" in out
    assert "\\set stanza" not in out and "altusWordsTwo" not in out


def test_refusals(vox):
    edit, _ = _move_back(vox, "Bassus")
    # a new word
    bad = dict(edit, notes=[dict(edit["notes"][0], syllable="TEST")])
    n, out = _apply([bad])
    assert n == 1 and "changes the text" in out
    # a note that is not there
    bad = dict(edit, notes=[dict(edit["notes"][0], bar="999")])
    n, out = _apply([bad])
    assert n == 1 and "no note" in out
    # Nunc's voices.ily is generated: report, never rewrite
    nunc = _score("nunc-scio-vere")
    e2, _ = _move_back(nunc, "Tenor")
    n, out = _apply([e2])
    assert n == 1 and "underlay.py" in out
