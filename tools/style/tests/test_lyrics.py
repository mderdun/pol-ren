"""Latin carry-over division (decision 2 of 4 Oct 2026) and the lyric reader."""
import pytest

from tools.style.lyrics import division_problem, words


@pytest.mark.parametrize("word", [
    "o-mnis", "San-cto", "co-gno-vi", "Chri-stus", "pa-tris", "ex-spe-cta-ti-o", "Is-ra-el", "il-le",
    "Iu-dae-o-rum", "e-ius", "re-dem-ptor", "ma-gnus", "a-gnus", "Do-mi-nus", "san-cti-fi-ca", "glo-ri-a",
    "ab-sti-ne-re", "con-so-la-ri", "in-tel-le-ctus", "Spi-ri-tu-i", "sae-cu-lo-rum",
])
def test_carry_over_passes(word):
    assert division_problem(word.split("-")) == []


@pytest.mark.parametrize("word,expected", [
    ("om-ni", "o-mni"), ("Sanc-to", "san-cto"), ("cog-no-vi", "co-gno"), ("Chris-tus", "chri-stus"),
    ("pat-ris", "pa-tris"), ("mag-nus", "ma-gnus"), ("Sa-nctus", "san-ctus"), ("in-tel-lec-tus", "le-ctus"),
])
def test_against_carry_over(word, expected):
    probs = division_problem(word.split("-"))
    assert probs, word
    assert any(expected in e for _, e in probs), (word, probs)


def test_reader_joins_syllables_and_skips_commands():
    code = 't = \\lyricmode { \\set stanza = "1." Nunc __ _ sci -- o \\rep ve -- \\rep re, "ma," _ om -- ni }'
    ws = [[s.text for s in w] for w in words(code)]
    assert ws == [["Nunc"], ["sci", "o"], ["ve", "re,"], ["ma,"], ["om", "ni"]]
    # offsets point into the code
    w = words(code)[-1]
    assert code[w[0].offset:w[0].offset + 2] == "om"
