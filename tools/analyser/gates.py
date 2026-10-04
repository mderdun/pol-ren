"""Context gates (gates.yaml): each is a predicate over (analysis, line, hit).
A rule opts into a gate in its YAML with a factor; when the predicate holds,
the rule's cost for that hit is multiplied by the factor."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent


@lru_cache(maxsize=1)
def definitions() -> dict:
    return yaml.safe_load((HERE / "gates.yaml").read_text(encoding="utf-8"))


def cadence_approach(a, line, hit) -> bool:
    if a is None or hit.syl >= len(line.syls):
        return False
    return (line.voice, line.verse, line.syls[hit.syl].word) in a.cadential_words


def cadence_lower_note(a, line, hit) -> bool:
    return a is not None and hit.ev > 0 and (line.voice, hit.ev - 1) in a.arrivals


def evaded_cadence(a, line, hit) -> bool:
    return hit.values.get("cadence_type") in ("evaded", "abandoned")


def weak_cadence(a, line, hit) -> bool:
    return hit.values.get("cadence_kind") == "weak"


def key_word(a, line, hit) -> bool:
    return hit.syl < len(line.syls) and line.word_of(hit.syl).cls == "key"


def suspension(a, line, hit) -> bool:
    return hit.values.get("label") == "suspension"


def full_point(a, line, hit) -> bool:
    return hit.values.get("entries", 0) >= 3


def homorhythm(a, line, hit) -> bool:
    return a is not None and a.homorhythmic(line.events[hit.ev].onset)


def older_practice(a, line, hit) -> bool:
    return a is not None and bool(a.score.config.get("older_practice"))


def sung_through(a, line, hit) -> bool:
    return hit.syl < len(line.syls) and not line.syls[hit.syl].short


def melodic_resolution(a, line, hit) -> bool:
    return bool(hit.values.get("melodic"))


def tail_voice(a, line, hit) -> bool:
    return bool(hit.values.get("tail"))


def against_tactus(a, line, hit) -> bool:
    return a is not None and bool(getattr(a, "displaced", None)) and \
        a.against_tactus(line.voice, line.events[hit.ev].onset)


GATES = {name: globals()[name] for name in
         ("cadence_approach", "cadence_lower_note", "evaded_cadence", "weak_cadence", "key_word", "suspension", "full_point",
          "homorhythm", "older_practice", "sung_through", "melodic_resolution", "tail_voice", "against_tactus")}


def applied(rule, a, line, hit) -> list[tuple[str, float]]:
    out = []
    for name, factor in (rule.gates or {}).items():
        fn = GATES.get(name)
        if fn is None:
            raise KeyError(f"{rule.id}: unknown gate {name}")
        if fn(a, line, hit):
            out.append((name, float(factor)))
    return out
