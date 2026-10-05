from tools.analyser.ingest import ROOT
from tools.analyser.selfcheck import check, count_lyricmode, report


def path(slug):
    return ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml"


def test_count_lyricmode():
    body = r'''\set stanza = "1." Plau -- de __ _ \edText the -- o "ma," _ cos'''
    assert count_lyricmode(body) == 6


def test_plaude_tenor_divided_notes_are_reported_not_fatal():
    cs = {(c.voice, c.verse): c for c in check(path("plaude-euge"))}
    t = cs[("Tenor", "1")]
    assert t.source == t.musicxml == t.model == 53
    assert t.legacy < t.model
    assert any("divided notes" in n and "bar 14" in n and "bar 18" in n for n in t.notes)
    assert "CHECK" in "\n".join(report(list(cs.values())))


def test_every_edition_exports_its_text():
    for slug in ("nunc-scio-vere", "vox-in-rama", "plaude-euge", "juz-sie-zmierzka"):
        for c in check(path(slug)):
            assert c.source == c.musicxml == c.model, (slug, c)
