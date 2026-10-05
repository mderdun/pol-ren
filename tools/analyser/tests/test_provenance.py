"""Underlay provenance (provenance.py, provenance.yaml): per-syllable text source."""
from collections import Counter

import pytest

from tools.analyser import provenance as P
from tools.analyser.ingest import ROOT, parse


def _ed(slug):
    return parse(ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml")


@pytest.fixture(scope="module")
def vox():
    sc = _ed("vox-in-rama")
    return sc, P.compute(sc)[0]


@pytest.fixture(scope="module")
def nunc():
    sc = _ed("nunc-scio-vere")
    return sc, P.compute(sc)


def _at(sc, prov, voice, where, verse="1"):
    e = next(e for e in sc.voices[voice] if not e.rest and e.where == where and verse in e.lyrics)
    return e.lyrics[verse].text, prov[(voice, e.idx, verse)]


def test_vox_changed_from_m_is_ours(vox):
    # critical note 38–39 C: M has -so- on the semiminim d'', -la- c''; here -so- takes c''
    sc, prov = vox
    t, p = _at(sc, prov, "Cantus", "39.2")
    assert t == "so" and p.cat == "ours" and p.text == "Ours (changed from M)"
    # 36–37 A and 38–40 T: the other departures the critical notes give
    assert _at(sc, prov, "Altus", "36.4")[1].label == "changed"
    assert _at(sc, prov, "Tenor", "38.4")[1].label == "changed"


def test_vox_unchanged_is_as_m(vox):
    sc, prov = vox
    t, p = _at(sc, prov, "Bassus", "27.1")   # 27 B: 'su-' as M (critical note)
    assert p.cat == "edition" and p.text == "Source: as M"
    assert all(p.cat == "edition" for (v, _i, _s), p in prov.items() if v == "Bassus")


def test_vox_tenor_source_ij_and_n(vox):
    sc, prov = vox
    labels = Counter(p.label for (v, _i, _s), p in prov.items() if v == "Tenor")
    assert labels["source"] > 50 and labels["supplied_ij"] == 24
    # the ij at bars 21–22 ('Rachel plorans') is supplied text
    assert _at(sc, prov, "Tenor", "21.2")[1].label == "supplied_ij"
    # Altus 5–6 follows N (critical note 5–6 A)
    p = _at(sc, prov, "Altus", "5.3")[1]
    assert p.cat == "edition" and p.siglum == "N"


def test_nunc_all_ours_but_chant(nunc):
    sc, (prov, notes) = nunc
    cats = Counter(p.cat for p in prov.values())
    assert set(cats) == {"ours", "chant"}
    # the Tenor's c.f.: Nunc on the chant's opening neume, sci- on g (critical note 3–12 T)
    assert _at(sc, prov, "Tenor", "3.3")[1].label == "chant"
    assert _at(sc, prov, "Tenor", "6.1")[1].label == "chant"
    # italic repeats are supplied, also inside a c.f. span (Cantus eripuit, 26.3)
    assert _at(sc, prov, "Cantus", "26.3")[1].label == "supplied_rep"
    # the Bassus psalm tone is not compared
    assert notes["_chant"]["Bassus"]["compared"] is False
    assert any(p.label == "cf_pending" for (v, _i, _s), p in prov.items() if v == "Bassus")
    assert all(p.label != "chant" for (v, _i, _s), p in prov.items() if v in ("Altus", "Bassus"))


def test_gabc_and_align():
    ch = P.gabc(ROOT / "tools/analyser/chant/nunc-scio-vere.gabc")
    assert ch[0] == ("NUNC", ["F", "F", "F", "D", "G", "F", "E"])
    assert ch[-1][0].startswith("rum")          # the antiphon only, up to the double bar
    # an ornament between two chant notes is left out; a neume's repeated notes sung once
    v = [("F", 4, "Nunc"), ("E", 1, ""), ("D", 4, ""), ("G", 4, "sci")]
    c = [("F", "Nunc"), ("F", "Nunc"), ("D", "Nunc"), ("G", "sci")]
    m = P.align(v, c)
    assert m[0] in (0, 1) and m[2] == 2 and m[3] == 3 and 1 not in m


def test_review_page_data(vox):
    from tools.analyser import review
    sc, prov = vox
    d = review.prov_data(prov)
    assert len(d["syl"]) == len(prov) and {c for c, _t in d["labels"]} == {"source", "edition", "ours"}
    html = review.prov_html(sc, prov, P.compute(sc)[1])
    assert 'id="prov"' in html and "Bassus" in html and "Ours (changed from M)" not in html


def test_other_editions():
    sc = _ed("juz-sie-zmierzka")
    s = P.summary(sc, P.compute(sc)[0])
    assert s["Tenor"] == Counter(source=96) and set(s["Cantus"]) == {"ours"}
    sc = _ed("plaude-euge")
    prov = P.compute(sc)[0]
    assert {p.label for (v, _i, _s), p in prov.items() if v == "Tenor"} == {"notext"}
    assert {p.label for (v, _i, _s), p in prov.items() if v != "Tenor"} == {"unplaced"}
