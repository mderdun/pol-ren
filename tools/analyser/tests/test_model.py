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


def test_spans_split_at_rests():
    s = fixtures.build({"notes": "f2 g2 r2 a2 b2", "text": "Do- mi- nus et"})
    line = build_lines(s)[0]
    sps = spans_of(line)
    assert [(sp.first, sp.end, sp.syls) for sp in sps] == [(0, 2, [0, 1]), (3, 5, [2, 3])]
