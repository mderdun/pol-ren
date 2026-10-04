"""Underlay analyser for the Polish Early Music editions.

    python -m tools.analyser [check] editions/*/pdf/*.musicxml [options]
    python -m tools.analyser analyse <musicxml> --layers
    python -m tools.analyser selfcheck editions/*/pdf/*.musicxml
    python -m tools.analyser lexicon
    python -m tools.analyser golden [--update]
    python -m tools.analyser legacy <musicxml>      # the old audit's output

See docs/analyser.md. The analyser advises; it never changes an edition.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import baseline as B
from . import report
from .ingest import ROOT, editions_config, slug_of

COMMANDS = ("check", "analyse", "selfcheck", "lexicon", "golden", "legacy")
DEFAULT_BASELINE = Path(__file__).resolve().parent / "baseline.json"
GOLDEN = Path(__file__).resolve().parent / "tests" / "golden"


def _paths(args) -> list[Path]:
    paths = [Path(p) for p in args]
    cfg = editions_config()
    return [p for p in paths if not (cfg.get(slug_of(p)) or {}).get("skip")]


def cmd_check(a) -> int:
    from .findings import run
    results = [run(p) for p in _paths(a.paths)]
    base = B.load(a.baseline)
    new = B.apply(results, base)
    if a.update_baseline:
        n = B.update(a.baseline, results, base)
        print(f"baseline {a.baseline}: {n} new entries added as pending")
    fmts = set(a.format.split(","))
    out = Path(a.out) if a.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    if "text" in fmts:
        for r in results:
            print(report.text(r, show_info=a.info, verbose=a.verbose))
    if "json" in fmts:
        data = [report.to_json(r) for r in results]
        if out:
            (out / "analyser.json").write_text(report.dumps(data), encoding="utf-8")
        else:
            print(report.dumps(data))
    if "markdown" in fmts:
        md = report.markdown(results, new=new)
        if out:
            (out / "analyser.md").write_text(md, encoding="utf-8")
        else:
            print(md)
    if "github" in fmts:
        for line in report.github(results, new):
            print(line)
    fail = False
    if a.fail_on == "new-break":
        fail = any(f.level == "break" for fs in new.values() for f in fs)
    elif a.fail_on == "break":
        fail = any(f.level == "break" for r in results for f in r.findings)
    elif a.fail_on == "new":
        fail = bool(new)
    if fail:
        print("analyser: failing on " + a.fail_on, file=sys.stderr)
    return 1 if fail else 0


def cmd_analyse(a) -> int:
    from .findings import run
    for p in _paths(a.paths):
        r = run(p)
        if a.layers or not a.findings:
            print(report.layers(r))
        if a.findings:
            print(report.text(r, show_info=True, verbose=True))
    return 0


def cmd_selfcheck(a) -> int:
    from .selfcheck import check, report as rep
    bad = 0
    for p in _paths(a.paths):
        print(f"== {slug_of(p)}")
        cs = check(p)
        print("\n".join(rep(cs)))
        bad += sum(1 for c in cs if not c.ok)
    return 1 if (bad and a.strict) else 0


def cmd_lexicon(a) -> int:
    from .text import check_lexicon, lexicon
    probs = check_lexicon("la") + check_lexicon("pl")
    for p in probs:
        print(p)
    for lang in ("la", "pl"):
        lex = lexicon(lang)
        n = len(lex.entries)
        unconf = [w for w, e in lex.entries.items() if "MD" not in e.src]
        print(f"{lang}: {n} entries, {len(unconf)} not yet confirmed by the editor")
    return 1 if probs else 0


def golden_data(path: Path) -> dict:
    from .findings import run
    from .selfcheck import check
    r = run(path)
    a = r.analysis
    return {
        "edition": r.slug,
        "findings": [{k: f.to_json()[k] for k in ("fingerprint", "level", "where", "message", "cost", "regret")}
                     | {"alternative": f.alternatives[0]["moves"] if f.alternatives else []}
                     for f in r.findings],
        "cadences": [c.summary() for c in a.cadences],
        "dissonance": sorted(f"{a.score.voices[v][i].where} {v} {d.label} {d.figure}".strip()
                             for (v, i), d in a.dissonances.items() if d.label != "passing"),
        "points": [f"{p.type} {p.motif}: " + ", ".join(f"{e.voice} {e.where}" for e in p.entries)
                   for p in a.points],
        "homorhythm": [f"{x.first_where}-{x.last_where}" for x in a.regions],
        "phrases": [f"{ph.voice} v{ph.verse} {ph.label(a.line(ph.voice, ph.verse))} {ph.ends}: {ph.text}"
                    for ph in a.phrases],
        "selfcheck": [f"{c.voice} v{c.verse} {c.source} {c.musicxml} {c.model} {c.legacy}" for c in check(path)],
    }


def cmd_golden(a) -> int:
    GOLDEN.mkdir(parents=True, exist_ok=True)
    cfg = editions_config()
    changed = 0
    for slug, c in cfg.items():
        if (c or {}).get("skip"):
            continue
        path = ROOT / "editions" / slug / "pdf" / f"{slug}.musicxml"
        data = golden_data(path)
        g = GOLDEN / f"{slug}.json"
        old = json.loads(g.read_text(encoding="utf-8")) if g.exists() else None
        if old != data:
            changed += 1
            if a.update:
                g.write_text(report.dumps(data), encoding="utf-8")
                print(f"updated {g.relative_to(ROOT)}")
            else:
                print(f"{slug}: differs from {g.relative_to(ROOT)} (run with --update to accept)")
    return 1 if (changed and not a.update) else 0


def cmd_legacy(a) -> int:
    from .engine import legacy_audit
    for p in a.paths:
        res = legacy_audit(p)
        order = {"BREAK": 0, "LOOK": 1}
        res.sort(key=lambda r: (order[r[0]], r[1], r[2], r[3]))
        for kind, voice, n, bar, msg in res:
            print(f"{kind:5} {voice:9} v{n} bar {bar:<3} {msg}")
        print(f"-- {sum(1 for r in res if r[0] == 'BREAK')} breaks, {sum(1 for r in res if r[0] == 'LOOK')} places to look at")
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] not in COMMANDS + ("-h", "--help"):
        argv.insert(0, "check")
    ap = argparse.ArgumentParser(prog="python -m tools.analyser", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check", help="findings for one or more editions")
    c.add_argument("paths", nargs="+")
    c.add_argument("--format", default="text", help="comma list: text, json, markdown, github")
    c.add_argument("--out", help="directory for analyser.json and analyser.md")
    c.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    c.add_argument("--update-baseline", action="store_true")
    c.add_argument("--fail-on", choices=["never", "new-break", "break", "new"], default="never")
    c.add_argument("--info", action="store_true", help="also list information-level findings")
    c.add_argument("-v", "--verbose", action="store_true", help="costs, alternatives, source lines")
    c.set_defaults(fn=cmd_check)
    an = sub.add_parser("analyse", help="human-readable report of the analysis layers")
    an.add_argument("paths", nargs="+")
    an.add_argument("--layers", action="store_true")
    an.add_argument("--findings", action="store_true")
    an.set_defaults(fn=cmd_analyse)
    s = sub.add_parser("selfcheck", help="does the MusicXML carry the underlay?")
    s.add_argument("paths", nargs="+")
    s.add_argument("--strict", action="store_true")
    s.set_defaults(fn=cmd_selfcheck)
    lx = sub.add_parser("lexicon", help="check the lexicons")
    lx.set_defaults(fn=cmd_lexicon)
    g = sub.add_parser("golden", help="compare or update the golden snapshots")
    g.add_argument("--update", action="store_true")
    g.set_defaults(fn=cmd_golden)
    lg = sub.add_parser("legacy", help="the old audit's output, from the ported rules")
    lg.add_argument("paths", nargs="+")
    lg.set_defaults(fn=cmd_legacy)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
