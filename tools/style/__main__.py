"""Style and editorial checks for the Polish Early Music editions.

    python -m tools.style check [--sources] [--pdfs] [paths ...]
    python -m tools.style list                   # the checks, with their rules
    python -m tools.style check editions/vox-in-rama --info -v

With neither --sources nor --pdfs, both run. Paths may be files or
directories; without paths, every edition, guide, the house files and the
committed PDFs are checked. See docs/style-checks.md. The checks advise and
gate; they never change an edition.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import baseline as B
from . import report
from .registry import HERE, ROOT, load

DEFAULT_BASELINE = HERE / "baseline.json"


def cmd_check(a) -> int:
    from .findings import discover, pdf_paths, run
    both = not a.sources and not a.pdfs
    only = set(a.only.split(",")) if a.only else None
    findings = run(a.paths or None, sources=a.sources or both, pdfs=a.pdfs or both, only=only)
    base = B.load(a.baseline)
    new = B.apply(findings, base)
    files = set()
    if a.sources or both:
        files |= {p.relative_to(ROOT).as_posix() for p in discover(a.paths or None)}
    if a.pdfs or both:
        files |= {p.relative_to(ROOT).as_posix() for p in pdf_paths(a.paths or None)}
    if only:
        stale = []
    else:
        stale = B.stale(findings, base, files)
    if a.update_baseline:
        if only:
            print("--update-baseline needs every check (no --only)", file=sys.stderr)
            return 2
        n = B.update(a.baseline, findings, base, files)
        print(f"baseline {a.baseline}: {n} new entries added as pending; {len(stale)} gone entries dropped")
        for f in findings:
            f.baseline = None
        new, stale = B.apply(findings, B.load(a.baseline)), []
    fmts = set(a.format.split(","))
    out = Path(a.out) if a.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    if "text" in fmts:
        print(report.text(findings, show_info=a.info, verbose=a.verbose))
    if "json" in fmts:
        if out:
            (out / "style.json").write_text(report.to_json(findings), encoding="utf-8")
        else:
            print(report.to_json(findings))
    if "markdown" in fmts:
        md = report.markdown(findings, new, stale)
        if out:
            (out / "style.md").write_text(md, encoding="utf-8")
        else:
            print(md)
    if "github" in fmts:
        for line in report.github(new):
            print(line)
    new_errors = [f for f in new if f.level == "error"]
    fail = (a.fail_on == "error" and bool(new_errors)) or (a.fail_on == "warn" and bool(new))
    if fail:
        print(f"style: {len(new_errors)} new error(s) not in the baseline", file=sys.stderr)
    return 1 if fail else 0


def cmd_list(a) -> int:
    for c in load().values():
        h = " (heuristic)" if c.heuristic else ""
        print(f"{c.id} {c.kind:6} {c.level:5} {c.name}{h}: {c.rule}")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in ("check", "list", "-h", "--help"):
        argv.insert(0, "check")
    ap = argparse.ArgumentParser(prog="python -m tools.style", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="run the checks")
    c.add_argument("paths", nargs="*")
    c.add_argument("--sources", action="store_true", help="source checks only (fast, no PDFs)")
    c.add_argument("--pdfs", action="store_true", help="checks of the committed PDFs only")
    c.add_argument("--only", help="comma list of check ids (S109,P208)")
    c.add_argument("--format", default="text", help="comma list: text, json, markdown, github")
    c.add_argument("--out", help="directory for style.json and style.md")
    c.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    c.add_argument("--update-baseline", action="store_true",
                   help="add new errors as pending, drop entries whose finding has gone")
    c.add_argument("--fail-on", choices=["never", "error", "warn"], default="error",
                   help="exit 1 on a new error (default), on any new finding, or never")
    c.add_argument("--info", action="store_true", help="also list information")
    c.add_argument("-v", "--verbose", action="store_true", help="rules and fingerprints")
    c.set_defaults(fn=cmd_check)
    ls = sub.add_parser("list", help="list the checks")
    ls.set_defaults(fn=cmd_list)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
