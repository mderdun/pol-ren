"""Unit tests for the analysis layers on small fixtures."""
from fractions import Fraction as F

from tools.analyser import fixtures, meter
from tools.analyser.analysis import analyse
from tools.analyser.text import build_lines, check_lexicon, lexicon, normalise


def an(spec):
    s = fixtures.build(spec)
    return analyse(s, build_lines(s))


# ------------------------------------------------------------------ metre

def test_strength_and_units():
    evs = fixtures.voice_events("C", "c8 c4 c2 c1 c1 c4", sign="cut")
    assert [meter.strength(e) for e in evs] == [3, 3, 2, 1, 0, 3]
    assert meter.syllable_unit(evs[0]) == 2 and meter.dotted_unit(evs[0]) == 3
    c = fixtures.voice_events("C", "c4", sign="C")[0]
    assert meter.syllable_unit(c) == 1 and meter.dotted_unit(c) == F(3, 2)


def test_syncopation():
    evs = fixtures.voice_events("C", "c2 c4 c2")
    assert meter.syncopated(evs[1]) and not meter.syncopated(evs[0])


# ------------------------------------------------------------------ text

def test_lexicons_are_clean():
    assert check_lexicon("la") == []
    assert check_lexicon("pl") == []


def test_stress_lookup():
    la, pl = lexicon("la"), lexicon("pl")
    assert la.lookup("dominus", 3).stress == 0
    assert la.lookup("consolari", 4).stress == 2
    assert la.lookup(normalise("Cognovísti", "la"), 4).stress == 2
    assert la.lookup("et", 1).cls == "light"
    assert pl.lookup("używają", 4).stress == 2
    assert pl.lookup("się", 1).cls == "light"
    unknown = la.lookup("xyzzy", 3)
    assert not unknown.known and unknown.stress == 1


def test_editions_fully_covered():
    from tools.analyser.ingest import ROOT, parse
    from tools.analyser.text import coverage
    for slug in ("nunc-scio-vere", "vox-in-rama", "plaude-euge", "juz-sie-zmierzka"):
        s = parse(ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml")
        rows = coverage(s, build_lines(s))
        missing = [r["word"] for r in rows if not r["known"]]
        assert not missing, (slug, missing)
        wrong = [r["word"] for r in rows if r["lex_syllables"] != r["syllables"] and r["lex_syllables"]]
        assert not wrong, (slug, wrong)


def test_lexicon_agrees_with_old_stress_table():
    from tools.analyser.text import LEGACY_STRESS
    la = lexicon("la")
    for w, st in LEGACY_STRESS.items():
        assert la.entries[w].stress == st, w


# ------------------------------------------------------------------ dissonance

def test_suspension_7_6():
    # Cantus takes c'' over the Tenor's e' (a sixth), holds it while the Tenor
    # moves to d' (a seventh), resolves to b' (a sixth), then the octave
    a = an({"voices": {
        "Cantus": {"notes": "r2 c'4 b2 c'4"},
        "Tenor": {"notes": "e4 d4 c4"}}})
    d = a.dissonances[("Cantus", 1)]
    assert d.label == "suspension" and d.agent == "Tenor" and d.figure == "7-6"
    assert a.score.voices["Cantus"][d.resolution].name == "B4"


def test_suspension_4_3_against_bass():
    a = an({"voices": {
        "Cantus": {"notes": "r2 c'4 b2 c'4"},
        "Bassus": {"notes": "c,4 g,4 c,4"}}})
    d = a.dissonances[("Cantus", 1)]
    assert d.label == "suspension" and d.figure == "4-3"


def test_passing_and_neighbour():
    a = an({"voices": {
        "Cantus": {"notes": "e2 f2 g2 a2 g2 a2"},
        "Tenor": {"notes": "c,8 c,4"}}})
    labels = {e.idx: a.dissonances[("Cantus", e.idx)].label
              for e in a.score.voices["Cantus"] if ("Cantus", e.idx) in a.dissonances}
    assert labels.get(1) == "passing"          # f against c: a fourth over the bass
    a2 = an({"voices": {
        "Cantus": {"notes": "e2 d2 e4"},
        "Tenor": {"notes": "c4 c4"}}})
    assert a2.dissonances[("Cantus", 1)].label == "neighbour"


def test_cambiata():
    a = an({"voices": {
        "Cantus": {"notes": "d'2 c'2 a2 b2 c'4"},
        "Tenor": {"notes": "d4 f4 c4"}}})
    assert a.dissonances[("Cantus", 1)].label == "cambiata"


# ------------------------------------------------------------------ cadence

def test_authentic_cadence():
    a = an({"voices": {
        "Cantus": {"notes": "a4 b4 c'8"},
        "Tenor": {"notes": "e4 d4 c8"},
        "Bassus": {"notes": "f,4 g,4 c,8"}}})
    assert len(a.cadences) == 1
    c = a.cadences[0]
    assert c.type == "authentic" and c.tone == "C"
    assert c.functions == {"Cantus": "C", "Tenor": "T", "Bassus": "B"}


def test_phrygian_cadence():
    # Tenor above: f' falls a semitone to e', the Cantus rises d'-e' a whole tone below it
    a = an({"voices": {
        "Cantus": {"notes": "g'4 d'4 e'8"},
        "Tenor": {"notes": "a4 f4 e8"}}})
    assert a.cadences and a.cadences[0].type == "phrygian"


def test_evaded_by_the_bass():
    a = an({"voices": {
        "Cantus": {"notes": "a4 b4 c'8"},
        "Tenor": {"notes": "e4 d4 c8"},
        "Bassus": {"notes": "f,4 g,4 a,8"}}})
    assert a.cadences[0].type == "evaded"
    assert a.cadences[0].functions["Bassus"] == "b"


def test_passing_six_eight_is_not_a_cadence():
    # the same motion on a weak minim, in moving notes
    a = an({"voices": {
        "Cantus": {"notes": "a2 b2 c'1 d'1 e'2"},
        "Tenor": {"notes": "f2 d2 c2 c2"}}})
    assert not a.cadences


# ------------------------------------------------------------------ phrases

def test_phrases_cut_at_rest_cadence_and_punctuation():
    a = an({"voices": {
        "Cantus": {"notes": "a4 b4 c'4 d'4 e'4 r4 f'4", "text": "Do- mi- nus, qui- a et"},
        "Tenor": {"notes": "e4 d4 c8 c4 r4 c4", "text": "Do- mi- nus, qui- et"}}})
    ph = [p for p in a.phrases if p.voice == "Cantus"]
    assert [p.text for p in ph] == ["Dominus,", "quia", "et"]
    assert ph[0].ends == "cadence" and ph[0].cadence.type == "clausula vera"
    assert ph[1].ends == "rest"


# ------------------------------------------------------------------ imitation

def test_fuga_at_the_fifth():
    a = an({"voices": {
        "Cantus": {"notes": "g'4 g'2 a'2 b'4 c''4 r8 r8"},
        "Tenor": {"notes": "r8 c'4 c'2 d'2 e'4 f'4 r8"},
        "Bassus": {"notes": "r8 r8 g4 g2 a2 b4 c'4"}}})
    assert len(a.points) == 1
    p = a.points[0]
    assert p.type == "PEN" and p.leader.voice == "Cantus"
    assert [e.voice for e in p.entries] == ["Cantus", "Tenor", "Bassus"]
    assert [e.transposition for e in p.entries] == [0, -4, -7]


def test_no_point_without_matching_heads():
    a = an({"voices": {
        "Cantus": {"notes": "g'4 g'2 a'2 b'4 r8"},
        "Tenor": {"notes": "r8 c'4 e'2 d'2 g4"}}})
    assert not a.points


# ------------------------------------------------------------------ texture

def test_homorhythm_region_and_syllable_match():
    a = an({"voices": {
        "Cantus": {"notes": "c'2 d'2 e'2 f'2 g'2 r8", "text": "Do- mi- nus et in"},
        "Altus": {"notes": "a2 b2 c'2 d'2 e'2 r8", "text": "Do- mi- nus et in"},
        "Tenor": {"notes": "f2 g2 a2 b2 c'2 r8", "text": "Do- _ mi- nus et"}}})
    assert len(a.regions) == 1
    r = a.regions[0]
    assert r.slices == 5 and r.syllable_match["1"] == 0.8


def test_polyphony_is_not_homorhythm():
    a = an({"voices": {
        "Cantus": {"notes": "c'4 d'2 e'2 f'4"},
        "Altus": {"notes": "a2 b4 c'2 d'4"},
        "Tenor": {"notes": "f4 g4 a4"}}})
    assert not a.regions
