"""The gaps closed on 4 October 2026: text edits (10.13), stanza consistency
(10.14), key words, inline acceptance, attributable regret, cadence closure
and plagal endings, stricter imitation, SARIF."""
from collections import Counter
from functools import lru_cache
from types import SimpleNamespace

import pytest

from tools.analyser import edits, fixtures, inline, report
from tools.analyser.analysis import analyse
from tools.analyser.findings import attributable, run
from tools.analyser.ingest import ROOT, parse
from tools.analyser.text import build_lines, key_word_entries

EDITIONS = ("nunc-scio-vere", "vox-in-rama", "plaude-euge", "juz-sie-zmierzka")


def an(spec):
    s = fixtures.build(spec)
    return analyse(s, build_lines(s))


@lru_cache(maxsize=None)
def edition(slug):
    return run(ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml")


# ------------------------------------------------------------------ regret

def test_attributable_splits_the_improvement():
    cur = {("U301", 5): 4.0, ("U302", 3): 2.0, ("U207", 4): 0.0}
    alt = {("U207", 4): 1.5}
    delta = 6.0 - 1.5
    a = attributable(cur, alt, delta, ("U301", 5), 1.0)
    b = attributable(cur, alt, delta, ("U302", 3), 1.0)
    assert a == pytest.approx(3.0) and b == pytest.approx(1.5)
    assert a + b == pytest.approx(delta)


@pytest.mark.parametrize("slug", EDITIONS)
def test_regret_never_exceeds_a_findings_own_cost(slug):
    for f in edition(slug).findings:
        if f.regret is not None:
            assert f.regret <= f.cost + 1e-6, f.fingerprint


@pytest.mark.parametrize("slug", EDITIONS)
def test_findings_sharing_an_alternative_share_its_improvement(slug):
    groups: dict = {}
    for f in edition(slug).findings:
        if f.regret and f.alternatives and f.alternatives[0]["basis"] == "change":
            groups.setdefault((f.voice, f.verse, tuple(f.alternatives[0]["moves"])), []).append(f)
    for key, fs in groups.items():
        if len(fs) > 1:
            gain = -fs[0].alternatives[0]["cost"]
            assert sum(f.regret for f in fs) <= gain + 1e-3, key   # costs are rounded to 3 places


# ------------------------------------------------------------------ text edits (10.13)

def _two(lower_text, lower_notes="c'2 d'1 e'2 f'2 g'4 r8"):
    return an({"voices": {
        "Cantus": {"notes": "e''8 r8", "text": "Vox"},
        "Tenor": {"notes": lower_notes, "text": lower_text}}})


def test_droppable_words():
    a = _two("et vox vox in Ra- ma", "c'2 d'2 e'2 f'2 g'2 a'4 r8")
    line = a.line("Tenor", "1")
    words = {w.norm: w for w in line.words}
    assert edits._sense_survives(line, words["et"])           # on the droppable list
    assert edits._sense_survives(line, line.words[1])         # vox vox: sung twice in a row
    assert not edits._sense_survives(line, words["in"])       # a preposition: 'vox Rama'
    assert not edits._sense_survives(line, words["rama"])     # a content word, once


def test_no_edits_in_the_top_voice():
    a = _two("et vox vox in Ra- ma", "c'2 d'2 e'2 f'2 g'2 a'4 r8")
    assert not edits.eligible(a, a.line("Cantus", "1"))
    assert edits.eligible(a, a.line("Tenor", "1"))


def test_drop_and_repeat_rebuild_the_line():
    a = _two("et vox vox in Ra- ma", "c'2 d'2 e'2 f'2 g'2 a'4 r8")
    line = a.line("Tenor", "1")
    d = edits.drop(line, 0)
    assert [s.text for s in d.line.syls] == ["vox", "vox", "in", "Ra", "ma"]
    assert d.from_orig.get(0) is None and d.to_orig[0] == 1 and d.label.startswith("drop 'et'")
    r = edits.repeat(line, 4)
    assert [s.text for s in r.line.syls] == ["et", "vox", "vox", "in", "Ra", "ma", "Ra", "ma"]
    assert r.n_new == 2 and r.to_orig[6] is None and r.line.word_of(6).norm == "rama"


def test_a_dropped_word_is_flagged_and_costed():
    # Tenor: et on a semiminim straight after a rest-free start; dropping et
    # (10.13) lets vox take the minim
    a = an({"voices": {
        "Cantus": {"notes": "e''8 r8", "text": "Vox"},
        "Tenor": {"notes": "c'2 d'1 e'1 f'2 g'2 a'4 r8", "text": "vox et in Ra- _ ma"}}})
    r = run("<fixture>", analysis=a)
    br = [f for f in r.findings if f.level == "break" and f.voice == "Tenor"]
    assert br
    alts = [x for f in br for x in f.alternatives if x["edit"] == "drop"]
    assert alts and alts[0]["moves"][0].startswith("drop 'et'")
    assert any(x == "edit 1.00" for x in alts[0]["introduces"])


# ------------------------------------------------------------------ stanzas (10.14)

def test_zmierzka_stanzas_agree_where_the_words_fall_alike():
    r = edition("juz-sie-zmierzka")
    assert not [f for f in r.findings if f.rule == "U305"]


# ------------------------------------------------------------------ key words

def test_key_word_proposals_have_no_effect_until_confirmed():
    for slug in EDITIONS:
        s = parse(ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml")
        entries = key_word_entries(s.config)
        assert entries and all(not e["confirmed"] for e in entries), slug
        assert all(e["source"] == "proposed, not confirmed" for e in entries)
        lines = build_lines(s)
        assert not any(w.cls == "key" for ln in lines for w in ln.words), slug
        # every proposal is a word of the edition's text
        words = {w.norm for ln in lines for w in ln.words}
        assert {e["word"] for e in entries} <= words, (slug, {e["word"] for e in entries} - words)


def test_a_confirmed_key_word_weighs_more():
    spec = {"notes": "r2 f1 g4 a2", "text": "Do- mi- nus"}
    plain = run("<fixture>", analysis=an(spec))
    keyed = run("<fixture>", analysis=an({**spec, "config": {"key_words": [{"word": "dominus", "source": "MD"}]}}))
    a = next(f for f in plain.findings if f.rule == "U202")
    b = next(f for f in keyed.findings if f.rule == "U202")
    assert "key_word×1.5" in b.gates and b.cost == pytest.approx(a.cost * 1.5)


# ------------------------------------------------------------------ inline acceptance

def test_inline_comments(tmp_path, monkeypatch):
    src = tmp_path / "voices.ily"
    src.write_text("\n".join([
        "%% header",
        "% underlay: ok U206 bar 34 'consolari' -- the print's long con-, 10.12",
        "cantusNotes = { c''1 }",
        "altusNotes = { a'1 }  % underlay: ok U301 U302 -- source reading",
        "% underlay: ok U201",
        "tenorNotes = { e'1 }",
    ]), encoding="utf-8")
    monkeypatch.setattr(inline, "ROOT", tmp_path)
    inline.scan.cache_clear()
    f = lambda **k: SimpleNamespace(**({"src": "voices.ily:3", "rule": "U206", "bar": 34, "word": "consolari",
                                         "text": "con"} | k))
    assert inline.find(f()).reason.startswith("the print's long con-")
    assert inline.find(f(bar=35)) is None
    assert inline.find(f(word="noluit", text="no")) is None
    assert inline.find(f(src="voices.ily:4", rule="U302")).at == 4
    assert inline.find(f(src="voices.ily:6", rule="U201")) is None      # no reason given
    assert inline.scan("voices.ily")[1] and "needs a rule and a reason" in inline.scan("voices.ily")[1][0]
    inline.scan.cache_clear()


# ------------------------------------------------------------------ cadences

def test_plagal_ending():
    a = an({"voices": {
        "Cantus": {"notes": "a'8 a'8"},
        "Bassus": {"notes": "d8 a,8"}}})
    assert [c.type for c in a.cadences] == ["plagal"]
    c = a.cadences[0]
    assert c.tone == "A" and c.functions == {"Bassus": "P", "Cantus": "H"} and c.kind == "full"


def test_a_clausula_in_passing_is_a_weak_figure():
    a = an({"voices": {
        "Cantus": {"notes": "a2 b2 c'2 d'2 e'8"},
        "Tenor": {"notes": "f2 d2 c2 b,2 c8"}}})
    c = a.cadences[0]
    assert c.type == "clausula vera" and c.closure == 0 and c.kind == "weak"


def test_cadence_counts_near_crim():
    # CRIM cadences() (survey §1): 24 in Nunc scio, 12 in Vox in Rama, counting
    # evaded and abandoned ones; ours, without the weak figures
    for slug, crim in (("nunc-scio-vere", 24), ("vox-in-rama", 12)):
        r = edition(slug)
        k = Counter(c.kind for c in r.analysis.cadences)
        assert abs(k["full"] + k["evaded"] + k["abandoned"] - crim) <= 1, (slug, k)


# ------------------------------------------------------------------ imitation

def test_same_intervals_other_rhythm_is_chance():
    a = an({"voices": {
        "Cantus": {"notes": "g'4 a'2 b'2 c''4 r8"},
        "Tenor": {"notes": "r8 c'2 d'4 e'4 f'2"}}})
    assert not a.points


def test_entry_after_a_clause_without_a_rest():
    a = an({"voices": {
        "Cantus": {"notes": "c'4 d'4 g'2 a'2 b'2 g'2 c''2 d''4", "text": "Do- mi, ve- ni- te ad nos et"},
        "Tenor": {"notes": "r8 r4 c2 d2 e2 c2 f2 g4", "text": "ve- ni- te ad nos et"}}})
    assert len(a.points) == 1
    ents = a.points[0].entries
    assert {(e.voice, e.context) for e in ents} == {("Cantus", "clause"), ("Tenor", "rest")}


def test_vox_opening_is_one_point_of_four_voices():
    r = edition("vox-in-rama")
    p = r.analysis.points[0]
    assert p.type == "FUGA" and [e.voice for e in p.entries] == ["Cantus", "Altus", "Tenor", "Bassus"]


# ------------------------------------------------------------------ SARIF

def test_sarif():
    r = edition("vox-in-rama")
    data = report.sarif([r])
    assert data["version"] == "2.1.0"
    run_ = data["runs"][0]
    ids = {x["id"] for x in run_["tool"]["driver"]["rules"]}
    assert {x["ruleId"] for x in run_["results"]} <= ids
    res = run_["results"][0]
    assert res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"].endswith("voices.ily")
    assert "underlay/v1" in res["partialFingerprints"]
