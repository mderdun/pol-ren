"""Baseline keys survive edits elsewhere in a file; the CLI fails only on new
errors; annotations are well formed."""
import json

from tools.style import baseline as B
from tools.style import report
from tools.style.__main__ import main
from tools.style.findings import _fingerprints, check_source
from tools.style.registry import ROOT, load
from tools.style.sources import SourceDoc

CHECKS = list(load().values())
TEXT = "\\cn{17-18}{A}{Emended. M has a.}\n"


def _findings(text):
    fs = check_source(SourceDoc.make("editions/x/x-critical.lytex", text), CHECKS)
    _fingerprints(fs)
    return fs


def test_fingerprints_ignore_line_numbers():
    a = {f.fingerprint for f in _findings(TEXT)}
    b = {f.fingerprint for f in _findings("\n\n% a new comment\nSome prose.\n\n" + TEXT)}
    assert a and a == b
    assert all("|editions/x/x-critical.lytex|" in fp for fp in a)


def test_apply_and_update(tmp_path):
    fs = _findings(TEXT)
    path = tmp_path / "baseline.json"
    added = B.update(path, fs, {}, {"editions/x/x-critical.lytex"})
    assert added == len([f for f in fs if f.level != "info"])
    base = B.load(path)
    assert all(e["status"] == "pending" for e in base.values())
    fs2 = _findings(TEXT)
    assert B.apply(fs2, base) == []
    # a finding that has gone is stale, and update drops it
    assert B.stale([], base, {"editions/x/x-critical.lytex"})
    B.update(path, [], base, {"editions/x/x-critical.lytex"})
    assert json.loads(path.read_text())["findings"] == []


def test_github_annotations():
    fs = _findings(TEXT)
    lines = report.github(fs)
    assert any(l.startswith("::error file=editions/x/x-critical.lytex,line=1,title=style S110") for l in lines)
    assert all("\n" not in l for l in lines)


def test_cli_fails_on_a_new_error_only(tmp_path, capsys):
    d = ROOT / "editions" / "zz-style-test"
    d.mkdir()
    try:
        (d / "zz-style-test-critical.lytex").write_text("Text — with an em dash.\n", encoding="utf-8")
        empty = tmp_path / "b.json"
        assert main(["check", "--sources", str(d), "--baseline", str(empty)]) == 1
        assert "S115" in capsys.readouterr().out
        assert main(["check", "--sources", str(d), "--baseline", str(empty), "--fail-on", "never"]) == 0
        assert main(["check", "--sources", str(d), "--baseline", str(empty), "--update-baseline"]) == 0
        assert main(["check", "--sources", str(d), "--baseline", str(empty)]) == 0
        (d / "zz-style-test-critical.lytex").write_text("Prose, plain.\n", encoding="utf-8")
        assert main(["check", "--sources", str(d), "--baseline", str(empty), "--format", "markdown"]) == 0
        assert "Baseline entries whose finding has gone" in capsys.readouterr().out
    finally:
        for f in d.iterdir():
            f.unlink()
        d.rmdir()


def test_repository_sources_run():
    """Every check runs on the repository's own sources without error."""
    from tools.style.findings import run
    fs = run(sources=True, pdfs=False)
    assert fs, "the repository has at least the sign inventory"
