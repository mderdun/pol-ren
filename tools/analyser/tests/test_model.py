"""The underlay model: legality, the k-best search, regret, gates, anchors."""
from tools.analyser import fixtures
from tools.analyser.analysis import analyse
from tools.analyser.findings import run
from tools.analyser.text import build_lines
from tools.analyser.underlay import Model, spans_of


def setup(spec):
    s = fixtures.build(spec)
    a = analyse(s, build_lines(s))
    return a, run("<fixture>", analysis=a)


def test_regret_ranks_a_run_on_an_unstressed_syllable():
    # eight minims on -mi- of DOminus (long in time, not only in notes: Miki,
    # 4 Oct 2026)
    a, r = setup({"notes": "f4 g2 a2 g2 f2 e2 d2 e2 f2 g4", "text": "Do- mi- _ _ _ _ _ _ _ nus"})
    f = next(f for f in r.findings if f.rule == "U206")
    assert f.regret and f.regret >= 2.0 and f.level == "warn"
    assert f.alternatives and len(f.alternatives) <= 3
    # the cheapest fix now hands the run to -nus, the word's last syllable (10.3)
    assert any("'nus'" in m or "'mi'" in m for m in f.alternatives[0]["moves"])
    assert any(x.startswith("U206") for x in f.alternatives[0]["fixes"])


def test_no_regret_when_nothing_better_is_legal():
    # et on the half-bar, but it is the first note after a rest (10.2 pins it)
    a, r = setup({"notes": "r4 g2 a2 b4", "text": "et in te"})
    f = next(f for f in r.findings if f.rule == "U201")
    assert f.regret == 0 and f.level == "info"


def test_alternatives_are_always_legal():
    a, r = setup({"notes": "f2 g1 a1 b2 c'2 d'2 c'4", "text": "Do- _ _ mi- nus et in"})
    line = a.lines[0]
    m = Model(a, line)
    for sp in m.spans:
        for c in m.search(sp, tuple(range(len(sp.syls)))):
            assert not c.hard
            for i, p in zip(sp.syls, c.starts):
                # 10.1(a): the run's first semiminim (g, on the minim beat) is
                # legal; its second note (a) never is
                assert line.events[p].dur >= 2 or p == sp.first or p == 1


def test_a_break_is_reported_with_a_legal_alternative():
    # mi- on the run's second note, by step: outside 10.1(a)-(c)
    a, r = setup({"notes": "f2 g1 a1 b2 c'4 d'4", "text": "Do- _ mi- nus et _"})
    f = next(f for f in r.findings if f.rule == "U101")
    assert f.level == "break" and f.regret is None
    assert f.alternatives and all("'mi'" in " ".join(x["moves"]) for x in f.alternatives)


def test_phrase_ends_stay_anchored():
    a, r = setup({"notes": "f4 g2 a1 g1 f1 e1 d1 e1 f2 g4 a4", "text": "Do- mi- _ _ _ _ _ _ _ nus, _"})
    f = next(f for f in r.findings if f.rule == "U206")
    for alt in f.alternatives:
        assert not any(m.startswith("'nus,'") for m in alt["moves"])


def test_cadence_gate_halves_the_run_rule():
    # Vox in Rama, Tenor 16: u-LU-la-tus, the run on -lu- before the cadence
    from tools.analyser.ingest import ROOT
    r = run(ROOT / "editions" / "vox-in-rama" / "pdf" / "vox-in-rama.musicxml")
    f = next(f for f in r.findings if f.rule == "U206" and f.voice == "Tenor" and f.bar == 16)
    assert "cadence_approach×0.5" in f.gates
    assert "sung_through×0.5" in f.gates     # -lu- is open (Miki, 4 Oct 2026)
    assert abs(f.cost - 0.5) < 1e-9          # weight 2.0, a breve long (amount 1), halved twice


def test_cantus_firmus_gate_halves_the_run_rules_only_in_its_span():
    # a run on -mi-: in a cantus firmus span the notes are the chant's, so the
    # run rule counts half there (gate cantus_firmus, editions.yaml)
    spec = {"notes": "f4 g2 a1 g1 f1 e1 d1 e1 f2", "text": "Do- mi- _ _ _ _ _ _ nus"}
    _, free = setup(spec)
    _, cf = setup({**spec, "config": {"cantus_firmus": [{"voice": "Cantus", "from": 1, "to": 9}]}})
    _, other = setup({**spec, "config": {"cantus_firmus": [{"voice": "Tenor", "from": 1, "to": 9}]}})
    f0 = next(f for f in free.findings if f.rule == "U206")
    f1 = next(f for f in cf.findings if f.rule == "U206")
    f2 = next(f for f in other.findings if f.rule == "U206")
    assert "cantus_firmus×0.5" in f1.gates and abs(f1.cost - f0.cost / 2) < 1e-9
    assert "cantus_firmus×0.5" not in f2.gates and f2.cost == f0.cost


def test_cantus_firmus_gate_on_nunc_scio():
    # Nunc scio: the Cantus carries the chant from bar 13 to 56; its run rules
    # are gated there, its stress rule (U210) is not
    from tools.analyser.ingest import ROOT
    r = run(ROOT / "editions" / "nunc-scio-vere" / "pdf" / "nunc-scio-vere.musicxml")
    f = next(f for f in r.findings if f.rule == "U208" and f.voice == "Cantus" and f.bar == 28)
    assert "cantus_firmus×0.5" in f.gates
    assert not any("cantus_firmus" in g for f in r.findings if f.rule == "U210" for g in f.gates)
    assert not any("cantus_firmus" in g for f in r.findings if f.voice == "Altus" for g in f.gates)


def test_spans_split_at_rests():
    s = fixtures.build({"notes": "f2 g2 r2 a2 b2", "text": "Do- mi- nus et"})
    line = build_lines(s)[0]
    sps = spans_of(line)
    assert [(sp.first, sp.end, sp.syls) for sp in sps] == [(0, 2, [0, 1]), (3, 5, [2, 3])]
