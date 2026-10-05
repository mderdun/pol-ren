"""Golden snapshots (survey §3.5): the findings and the analysis layers of
every edition, frozen. A change is either a fix or a regression; look at the
diff, then accept it with `python -m tools.analyser golden --update`."""
import json

import pytest

from tools.analyser.__main__ import GOLDEN, golden_data
from tools.analyser.ingest import ROOT, editions_config

SLUGS = [s for s, c in editions_config().items() if not (c or {}).get("skip")]


@pytest.mark.parametrize("slug", SLUGS)
def test_golden(slug):
    path = ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml"
    want = json.loads((GOLDEN / f"{slug}.json").read_text(encoding="utf-8"))
    got = golden_data(path)
    for key in want:
        assert got[key] == want[key], f"{slug}: {key} changed; run python -m tools.analyser golden --update if intended"
