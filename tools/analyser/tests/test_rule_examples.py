"""Every rule ships with examples that must flag and examples that must pass
(the LanguageTool discipline, survey §3.4). A rule without both fails here."""
import pytest

from tools.analyser.rules import load

from tools.analyser.tests.helpers import edition_hits, fixture_hits

RULES = load()


def _cases(kind):
    for rid, r in sorted(RULES.items()):
        for n, ex in enumerate(r.examples.get(kind, [])):
            yield pytest.param(rid, ex, id=f"{rid}-{kind}-{n}")


@pytest.mark.parametrize("rid", sorted(RULES))
def test_rule_has_examples(rid):
    r = RULES[rid]
    assert r.examples.get("flag"), f"{rid} has no flag example"
    assert r.examples.get("pass"), f"{rid} has no pass example"
    assert r.principle and r.authority and r.message


def _hits(rid, ex):
    if "ref" in ex:
        slug, voice, verse, bar = ex["ref"].rsplit("/", 3)
        _, hits = edition_hits(slug)
        return [h for line, h in hits if h.rule == rid and line.voice == voice and line.verse == verse
                and h.values.get("bar") == int(bar)]
    spec = dict(ex)
    _, hits = fixture_hits(spec)
    out = [(line, h) for line, h in hits if h.rule == rid]
    if ex.get("rule_voice"):
        out = [(line, h) for line, h in out if line.voice == ex["rule_voice"]]
    return [h for _, h in out]


@pytest.mark.parametrize("rid,ex", list(_cases("flag")))
def test_flags(rid, ex):
    hits = _hits(rid, ex)
    assert hits, f"{rid} should flag: {ex}"
    if "at" in ex:
        assert any(h.syl == ex["at"] for h in hits), f"{rid} flags {[h.syl for h in hits]}, expected {ex['at']}"


@pytest.mark.parametrize("rid,ex", list(_cases("pass")))
def test_passes(rid, ex):
    hits = _hits(rid, ex)
    assert not hits, f"{rid} should not flag: {ex} -> {[h.values for h in hits]}"
