"""Every check ships with examples that must flag and examples that must pass,
as the analyser's rules do (tools/analyser/tests/test_rule_examples.py). A
check without both, or without a rule and authority to cite, fails here."""
import re

import pytest

from tools.style.findings import check_source
from tools.style.pdf import PdfDoc
from tools.style.pdf_fixtures import BUILDERS, build
from tools.style.registry import LEVELS, load
from tools.style.sources import SourceDoc

CHECKS = load()


def _cases(kind):
    for cid, c in sorted(CHECKS.items()):
        for n, ex in enumerate(c.examples.get(kind, [])):
            yield pytest.param(cid, ex, id=f"{cid}-{kind}-{n}")


@pytest.mark.parametrize("cid", sorted(CHECKS))
def test_check_is_complete(cid):
    c = CHECKS[cid]
    assert c.examples.get("flag"), f"{cid} has no flag example"
    assert c.examples.get("pass"), f"{cid} has no pass example"
    assert c.level in LEVELS
    assert c.message and c.authority
    # every check cites a principle, a house-style section or a decision
    assert re.search(r"principles \d|house style \d|decision", c.rule), f"{cid} cites no rule: {c.rule!r}"
    for ex in c.examples["flag"] + c.examples["pass"]:
        assert ex.get("why"), f"{cid}: an example without a why"
        if c.kind == "pdf":
            assert ex.get("fixture") in BUILDERS, f"{cid}: unknown fixture {ex.get('fixture')}"
        else:
            assert "path" in ex and "text" in ex


def _hits(cid, ex, tmp_path):
    c = CHECKS[cid]
    if c.kind == "source":
        doc = SourceDoc.make(ex["path"], ex["text"], meta=ex.get("meta") or {})
        return [f for f in check_source(doc, [c])]
    path, meta = build(ex["fixture"], tmp_path, ex.get("kind", "performance"))
    pdf = PdfDoc.open(path)
    pdf.meta = meta
    return list(c.fn(pdf))


@pytest.mark.parametrize("cid,ex", list(_cases("flag")))
def test_flags(cid, ex, tmp_path):
    assert _hits(cid, ex, tmp_path), f"{cid} should flag: {ex}"


@pytest.mark.parametrize("cid,ex", list(_cases("pass")))
def test_passes(cid, ex, tmp_path):
    hits = _hits(cid, ex, tmp_path)
    assert not hits, f"{cid} should not flag: {ex} -> {hits}"
