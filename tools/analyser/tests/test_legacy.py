"""The port of tools/underlay_audit.py gives the same results, edition by
edition, and on the Vox in Rama of commit bb75083 (before the October review
fixed its eight semiminim breaks), which exercises the firm rules."""
import importlib.util
import sys
from collections import Counter

import pytest

from tools.analyser.engine import legacy_audit
from tools.analyser.ingest import ROOT
from tools.analyser.tests.helpers import FIXTURES

spec = importlib.util.spec_from_file_location("underlay_audit", ROOT / "tools" / "underlay_audit.py")
old = importlib.util.module_from_spec(spec)
_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True     # leave tools/__pycache__ alone
spec.loader.exec_module(old)
sys.dont_write_bytecode = _dwb

PATHS = [ROOT / "editions" / s / "pdf" / f"{s}.musicxml"
         for s in ("nunc-scio-vere", "vox-in-rama", "plaude-euge", "juz-sie-zmierzka")]
PATHS.append(FIXTURES / "vox-in-rama-bb75083.musicxml")


@pytest.mark.parametrize("path", PATHS, ids=lambda p: p.stem)
def test_same_results_as_the_old_audit(path):
    want = Counter(old.audit(str(path)))
    got = Counter(legacy_audit(path))
    assert got == want


def test_the_break_fixture_has_the_reviews_eight_breaks():
    res = legacy_audit(FIXTURES / "vox-in-rama-bb75083.musicxml")
    assert sum(1 for r in res if r[0] == "BREAK") == 8
