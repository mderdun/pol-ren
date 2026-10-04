"""Baseline fingerprints rest on word and syllable identity, not bars."""
import json

from tools.analyser import baseline as B
from tools.analyser.__main__ import DEFAULT_BASELINE, main
from tools.analyser.findings import run
from tools.analyser.ingest import ROOT


def test_fingerprints_ignore_bar_numbers():
    r = run(ROOT / "editions" / "vox-in-rama" / "pdf" / "vox-in-rama.musicxml")
    fps = [f.fingerprint for f in r.findings]
    assert len(fps) == len(set(fps))
    for fp in fps:
        slug, voice, verse, rule, word, occ = fp.split("|")
        assert verse.startswith("v") and "#" in word and occ.isdigit()


def test_every_baseline_entry_has_a_reason_and_status():
    data = json.loads(DEFAULT_BASELINE.read_text(encoding="utf-8"))
    for e in data["findings"]:
        assert e["status"] in ("accepted", "pending") and e["reason"], e


def test_accepted_findings_are_marked_and_not_new():
    r = run(ROOT / "editions" / "vox-in-rama" / "pdf" / "vox-in-rama.musicxml")
    new = B.apply([r], B.load(DEFAULT_BASELINE))
    con = [f for f in r.findings if f.rule == "U206" and f.word == "consolari"]
    # accepted (baseline or inline), or fallen to information since melismas are
    # measured in time and 'con' can be sung through (Miki's review, 4 Oct 2026)
    assert con and all((f.baseline or "").startswith("accepted") or f.level == "info" for f in con)
    assert not new.get("vox-in-rama")


def test_cli_fails_only_on_new_breaks(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text('{"version": 1, "findings": []}')
    path = str(ROOT / "editions" / "vox-in-rama" / "pdf" / "vox-in-rama.musicxml")
    assert main(["check", path, "--baseline", str(empty), "--fail-on", "new-break", "--format", "json",
                 "--out", str(tmp_path)]) == 0
    assert main(["check", path, "--baseline", str(empty), "--fail-on", "new", "--format", "json",
                 "--out", str(tmp_path)]) == 1
    bad = str(ROOT / "tools" / "analyser" / "tests" / "fixtures" / "vox-in-rama-bb75083.musicxml")
    assert main(["check", bad, "--baseline", str(empty), "--fail-on", "new-break", "--format", "json",
                 "--out", str(tmp_path)]) == 1
