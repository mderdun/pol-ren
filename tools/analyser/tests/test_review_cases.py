"""The October 2026 underlay review as evidence: on the Vox in Rama of commit
bb75083 (before the review's fixes), the model should find the eight breaks,
find a move-only fix where the review found one, and find none where the
review had to drop a word (docs/reviews/underlay-2026-10.md)."""
from tools.analyser.findings import run
from tools.analyser.tests.helpers import FIXTURES

R = run(FIXTURES / "vox-in-rama-bb75083.musicxml")
BREAKS = [f for f in R.findings if f.level == "break"]


def at(voice, bar):
    return [f for f in BREAKS if f.voice == voice and f.bar == bar]


def test_the_eight_breaks():
    assert len(BREAKS) == 8
    assert {(f.voice, f.bar) for f in BREAKS} == {
        ("Altus", 11), ("Altus", 12), ("Altus", 32), ("Bassus", 27),
        ("Tenor", 6), ("Tenor", 37), ("Tenor", 40)}


def test_bassus_27_su_on_the_semibreve():
    # review: "su- on the semibreve a, under the Tenor's su-"
    f = at("Bassus", 27)[0]
    assert f.alternatives and f.alternatives[0]["moves"] == ["'su' 27.1 -> 27.3"]


def test_altus_32_con_later():
    # review: drop this et; con- moves to f#' with the run
    f = at("Altus", 32)[0]
    assert f.alternatives and f.alternatives[0]["moves"][0].startswith("'con' 32.4 ->")


def test_tenor_40_moves_without_losing_a_word():
    # review: "con- g a, -so- b, -la- e' (minim) with the run ... No word is lost."
    f = at("Tenor", 40)[0]
    assert f.alternatives
    assert any("'la' 40.1 -> 39.4" in m for a in f.alternatives for m in a["moves"])


def test_no_move_only_fix_where_the_review_dropped_words():
    # review: Altus 12 drop est; Tenor 37 drop et
    for voice, bar in (("Altus", 12), ("Tenor", 37)):
        assert all(not f.alternatives for f in at(voice, bar)), (voice, bar)


def test_altus_11_differs_from_the_review():
    # the review drops est; the model keeps it by drawing Ra-ma back a minim,
    # onto the repeated d''. A different lawful reading, for the editor to sing.
    f = at("Altus", 11)[0]
    assert f.alternatives and f.alternatives[0]["moves"][0] == "'Ra' 10.4 -> 10.3"
