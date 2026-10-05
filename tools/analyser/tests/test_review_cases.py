"""The October 2026 underlay review as evidence: on the Vox in Rama of commit
bb75083 (before the review's fixes), the model should find the eight breaks,
find a move-only fix where the review found one, and none where the review
had to drop a word; there it should propose the review's drop (10.13)
(docs/reviews/underlay-2026-10.md)."""
import pytest

from tools.analyser import edits
from tools.analyser.findings import run
from tools.analyser.tests.helpers import FIXTURES
from tools.analyser.underlay import Model

R = run(FIXTURES / "vox-in-rama-bb75083.musicxml")
BREAKS = [f for f in R.findings if f.level == "break"]


def at(voice, bar):
    return [f for f in BREAKS if f.voice == voice and f.bar == bar]


LICENSED = [f for f in R.findings if f.rule == "U106"]


def test_the_eight_breaks_under_the_new_10_1():
    # The review found eight breaks of the old 10.1. Rewritten after the
    # literature review (4 October 2026, docs/research/rule-10-1-review.md),
    # 10.1 licenses six of the seven places; only Marchesano's -di-, -ta on
    # the lone semiminims of the Altus at bar 12 stay outside (a)-(e)
    assert {(f.voice, f.bar) for f in BREAKS} == {("Altus", 12)}
    clause = {(f.voice, f.bar): f.message for f in LICENSED}
    for voice, bar, c in (("Altus", 11, "(b)"), ("Altus", 32, "(a)"), ("Bassus", 27, "(a)"),
                          ("Tenor", 6, "(a)"), ("Tenor", 37, "(a)"), ("Tenor", 40, "(a)")):
        assert c in clause[(voice, bar)], (voice, bar, clause.get((voice, bar)))


def test_altus_32_con_on_the_run_is_licensed():
    # Miki (4 October 2026): con- on the first semiminim of the run, 32.4: 10.1(a)
    fs = [f for f in LICENSED if f.voice == "Altus" and f.where == "32.4"]
    assert fs and "'con'" in fs[0].message and "(a)" in fs[0].message


def test_no_move_only_fix_where_the_review_dropped_words():
    # review: Altus 12 drop est; Tenor 37 drop et
    for voice, bar in (("Altus", 12), ("Tenor", 37)):
        for f in at(voice, bar):
            assert all(a["edit"] for a in f.alternatives), (voice, bar)


def test_the_review_drops_are_proposed():
    # The review's Tenor 37 drop of 'et' is no longer proposed: that 'et' heads
    # the 'et noluit' motif, and Miki's review of 4 October 2026 restores it
    # (test_miki_no_drop_breaks_a_motif)
    for voice, bar, word in (("Altus", 12, "est"),):
        for f in at(voice, bar):
            assert f.alternatives, (voice, bar)
            first = f.alternatives[0]
            assert first["edit"] == "drop" and first["moves"][0].startswith(f"drop '{word}'"), first
            assert any(x.startswith("edit ") for x in first["introduces"])


def test_altus_11_ra_stays_on_10_4():
    # Miki's second review (4 October 2026): "the 3 top parts are clearly
    # playing against the tactus here, so Ra on 10.4 is appropriate". Bar 10
    # is a displaced span, and no alternative draws Ra back to 10.3.
    assert not at("Altus", 11)
    for f in R.findings:
        for alt in f.alternatives:
            assert "'Ra' 10.4 -> 10.3" not in alt["moves"], (f.voice, f.where)


# ---------------------------------------------------------------------------
# Miki's review of 4 October 2026 (books/MIKI-VOX-REVIEW-2026-10-04.txt), on
# the Vox in Rama of commit c157d86, before his verdicts were applied.

M = run(FIXTURES / "vox-in-rama-c157d86.musicxml")
MA = M.analysis


def _ev(line, where):
    """Event at bar.minim, with a + for the note off the minim (33.4+)."""
    off = where.endswith("+")
    w = where.rstrip("+")
    return next(e.idx for e in line.events
                if not e.rest and e.where == w and bool(e.pos % 2) == off)


def _place(model, line, sp, moves):
    """The span's candidate with some syllables moved: {(text, from): to}."""
    st = list(model.current(sp).starts)
    for (txt, frm), to in moves.items():
        src = _ev(line, frm)
        j = next(j for j, i in enumerate(sp.syls) if line.syls[i].text.startswith(txt) and st[j] == src)
        st[j] = _ev(line, to)
    return model.evaluate_span(sp, tuple(st))


def test_miki_cantus_28_tail_voice_at_most_look():
    # "keep as is": the Cantus resolves on the A after the harmonic D, and
    # carries the old phrase across the join with the Bassus
    fs = [f for f in M.findings if f.voice == "Cantus" and f.bar == 28 and f.rule == "U301"]
    assert fs and all(f.level in ("look", "info") for f in fs)
    assert any("tail_voice×0.5" in f.gates and "melodic_resolution×0.5" in f.gates for f in fs)


def test_miki_bassus_18_la_held_back_rather_than_tus():
    # "I would probably prefer to extend 'la' across 18.2-.3 rather than 'tus'
    # .3-19.1": both need the 'et' at 17.4 dropped; compare the two readings
    line = MA.line("Bassus", "1")
    wi = next(w.i for w in line.words
              if w.norm == "et" and line.events[line.syls[w.syls[0]].ev].where == "17.4")
    ed = edits.drop(line, wi)
    m = Model(MA, ed.line)
    sp = m.span_of_ev[_ev(ed.line, "18.3")]
    base = {("u", "18.1"): "17.4", ("lu", "18.2"): "18.1", ("la", "18.3"): "18.2"}
    la_back = _place(m, ed.line, sp, base)
    tus_back = _place(m, ed.line, sp, {**base, ("tus", "19.1"): "18.3"})
    assert not la_back.hard and la_back.total < tus_back.total
    assert any(x.rule == "U301" and "carried back" in x.hit.values["problem"] for x in tus_back.priced)


def test_miki_cantus_34_it_melisma_ranks_worst():
    # alternatives 2 and 3 of the first report put a melisma on 'it': "I would
    # not think to allow this as a legal option". Alternative 1 (so- back to
    # 35.1) passes o-n-s across the last fusa of the run.
    line = MA.line("Cantus", "1")
    m = Model(MA, line)
    sp = m.span_of_ev[_ev(line, "34.2")]
    cur = m.current(sp)
    alt1 = _place(m, line, sp, {("so", "35.2"): "35.1"})
    alt2 = _place(m, line, sp, {("con", "34.2"): "35.1"})
    alt3 = _place(m, line, sp, {("lu", "33.4+"): "34.1", ("it", "34.1"): "34.2", ("con", "34.2"): "35.1"})
    assert any(x.rule == "U209" for x in alt1.priced)
    for alt in (alt2, alt3):
        assert alt.hard or any(x.rule == "U208" and x.hit.values["txt"].startswith("it") for x in alt.priced)
        assert alt.hard or alt.total > max(cur.total, alt1.total)
    # the current reading is the best of the four: Miki's "the only legal option"
    assert cur.total <= alt1.total
    for f in M.findings:
        if f.voice == "Cantus" and f.bar == 34:
            for a in f.alternatives:
                assert not any(mv.startswith("'con' 34.2 ->") for mv in a["moves"]), a


def test_miki_et_noluit_chain_found():
    # minim, dotted minim, semiminim, minim: passed through the voices in bars
    # 28-38, including Altus 31.4 (bar 32) and the inverted Tenor 37.4-38.3
    chains = [p for p in MA.motifs if any(e.voice == "Cantus" and e.where == "33.2" for e in p.entries)]
    assert len(chains) == 1
    got = {(e.voice, e.where) for e in chains[0].entries}
    assert {("Altus", "31.4"), ("Tenor", "37.4"), ("Cantus", "29.2"), ("Bassus", "34.2"),
            ("Tenor", "28.2"), ("Cantus", "37.4")} <= got
    flagged = {(f.voice, f.where) for f in M.findings if f.rule == "U306"}
    assert {("Altus", "31.4"), ("Tenor", "37.4")} <= flagged


@pytest.mark.xfail(reason="the fix needs the dropped 'et' restored; the analyser offers drops and "
                          "repeats, never a restored word, so the U306 findings have no better legal "
                          "alternative and stay information", strict=True)
def test_miki_et_noluit_fix_is_proposed():
    fs = [f for f in M.findings if f.rule == "U306" and (f.voice, f.where) == ("Altus", "31.4")]
    assert fs and fs[0].level in ("warn", "look") and fs[0].alternatives


def test_miki_no_drop_breaks_a_motif():
    # the review's dropped 'et' at Tenor 37 broke the chain: on the pre-review
    # Vox in Rama that drop is no longer offered, and no drop anywhere takes a
    # word off a motif's head notes
    for f in at("Tenor", 37):
        assert not any(a["edit"] == "drop" and a["moves"][0].startswith("drop 'et' at 37.4")
                       for a in f.alternatives), f.alternatives
    for r in (M, R):
        heads = {(e.voice, r.analysis.score.voices[e.voice][i].where)
                 for p in r.analysis.motifs for e in p.entries for i in e.head}
        for f in r.findings:
            for a in f.alternatives:
                if a["edit"] == "drop":
                    at_ = a["moves"][0].split(" at ")[1].split(" ")[0]
                    assert (f.voice, at_) not in heads, (f.voice, f.where, a["moves"][0])


def test_miki_drop_only_findings_are_look():
    # 10.13: a dropped word is the last resort, so a finding that only a drop
    # improves is reported at look, never warn
    for r in (M, R):
        for f in r.findings:
            if f.level == "warn":
                better = [a for a in f.alternatives if a["cost"] < 0]
                assert better and not all(a["edit"] for a in better), (f.voice, f.where, f.rule)


# ---------------------------------------------------------------------------
# Miki's second review of 4 October 2026 (books/MIKI-VOX-REVIEW-2-2026-10-04.txt),
# on the Vox in Rama of commit ee0dcc9, after his first verdicts were applied.

N = run(FIXTURES / "vox-in-rama-ee0dcc9.musicxml")
NA = N.analysis


def _u210(voice, where):
    return [f for f in N.findings if f.rule == "U210" and f.voice == voice and f.where == where]


def _onset(voice, where):
    return next(e.onset for e in NA.score.voices[voice] if e.where == where and not e.rest)


def test_miki2_quia_not_flagged():
    # Altus 41.4: QUI-a; qui has no beat it could take, 'a' on the bar is fine
    from tools.analyser.text import lexicon
    assert lexicon("la").entries["quia"].stress == 0
    assert not _u210("Altus", "41.4")


def test_miki2_bar_10_plays_against_the_tactus():
    # Altus 10.4 'Ra': "the 3 top parts are clearly playing against the tactus"
    t = _onset("Altus", "10.4")
    assert any(d.kind == "shared" and {"Cantus", "Altus", "Tenor"} <= set(d.voices) and d.contains("Altus", t)
               for d in NA.displaced)
    assert not _u210("Altus", "10.4")


def test_miki2_bar_15_hemiola():
    # Altus 15.4 'la' of ululatus off the tactus, the note values suggesting hemiola
    t = _onset("Altus", "15.4")
    assert any(d.kind == "hemiola" and d.contains("Altus", t) for d in NA.displaced)
    assert not _u210("Altus", "15.4")


def test_miki2_u208_latin_only_and_fricatives_mild():
    from tools.analyser.rules import load
    assert load()["U208"].langs == ("la",)
    sib = [f for f in N.findings if f.rule == "U208" and f.text.startswith("os")]
    stop = [f for f in N.findings if f.rule == "U208" and f.text.startswith("it")]
    assert sib and stop and max(f.cost for f in sib) < min(f.cost for f in stop)


def test_miki2_upper_duo():
    # the Altus and Cantus "coming in and out of each others rhythms but
    # starting together": the top two voices are labelled as a duo
    assert NA.duos and all(d.voices == ("Cantus", "Altus") for d in NA.duos)
    assert all(d.apart for d in NA.duos)


# ------------------------------------------------- Miki's third review (5 Oct 2026)
# On the Vox of commit 9227043 (tests/fixtures/vox-in-rama-9227043.musicxml),
# before this round's edits; books/MIKI-VOX-REVIEW-3-2026-10-05.txt.

M3 = run(FIXTURES / "vox-in-rama-9227043.musicxml")
M3A = M3.analysis


def _m3_onset(voice, where):
    return next(e.onset for e in M3A.score.voices[voice] if e.where == where and not e.rest)


def test_miki3_cantus_39_landing_note_is_not_a_late_last_syllable():
    # "Stress syllable 'la' arrives on cadence and strong beat (and the
    # temporal centre of the phrase, that being the 'landing' semibreve ...),
    # and the final syllable 'ri' occurs on the last minim of the phrase"
    ph = next(p for p in M3A.phrases if p.voice == "Cantus" and "consolari" in p.text
              and M3A.score.voices["Cantus"][p.last].where == "40.1")
    assert ph.landing is not None and M3A.score.voices["Cantus"][ph.landing].where == "39.3"
    assert not [f for f in M3.findings if f.rule == "U301" and f.voice == "Cantus" and f.where == "39.3"]


def test_miki3_cantus_40_qui_lands_on_the_semibreve():
    # "'Qui' in the following must land on 40.2 again as it's the stress of the
    # word and that's the temporal centre of the phrase"
    ph = next(p for p in M3A.phrases if p.voice == "Cantus" and p.text.startswith("quia"))
    assert M3A.score.voices["Cantus"][ph.first].where == "40.2"
    assert not [f for f in M3.findings if f.voice == "Cantus" and f.where == "40.2" and f.level != "info"]


def test_miki3_rachel_plorans_homorhythm_from_the_offbeat_tutti_entry():
    # "the homorhythmic section of Rachel pleading that I would argue runs from
    # 23.2 (with the offbeat tutti entry) through to the end of 27"
    r = next(r for r in M3A.regions if r.contains(_m3_onset("Cantus", "25.2")))
    assert r.first_where == "23.2"
    assert r.contains(_m3_onset("Bassus", "27.3"))


def test_miki3_altus_33_contour_centre():
    # Altus 33.3 (his '34.4'): "the G the centre of gravity that side of the
    # run"; information only, no rule reads it
    c = [c for c in M3A.contours if c.voice == "Altus" and c.where == "33.3"]
    assert c and "centre" in c[0].kinds


def test_miki3_tactus_play_counts_fully_at_a_phrase_start():
    # "when the play is most obvious, is when it begins a phrase (and its
    # doubly obvious when these phrases are in homorhythm)"; mid-phrase a hint
    t = _m3_onset("Cantus", "24.4")
    span = next(d for d in M3A.displaced if d.contains("Cantus", t))
    assert set(span.phrase_start) == {"Cantus", "Altus", "Tenor", "Bassus"}
    mid = next(d for d in M3A.displaced if d.where == "38.4")
    assert not mid.phrase_start
    from tools.analyser.gates import definitions
    assert "against_tactus_mid" in definitions()
