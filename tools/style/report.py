"""Output: text (as the analyser's, one block per file), JSON, Markdown (the
CI job summary) and GitHub annotations."""
from __future__ import annotations

import json
from collections import Counter, defaultdict

from .findings import Finding
from .registry import LEVELS, load


def text(findings: list[Finding], *, show_info: bool = False, verbose: bool = False) -> str:
    out = []
    by_file = defaultdict(list)
    for f in findings:
        by_file[f.file].append(f)
    for file, fs in by_file.items():
        shown = [f for f in fs if show_info or f.level != "info"]
        if not shown:
            continue
        out.append(f"== {file}")
        for f in shown:
            where = f":{f.line}" if f.line is not None else (f" p.{f.page}" if f.page else "")
            mark = " [baseline]" if f.baseline else ""
            out.append(f"{f.level.upper():5} {f.check} {where:7} {f.name}: {f.message}{mark}")
            if verbose:
                out.append(f"      rule: {f.rule}; fingerprint {f.fingerprint}")
                if f.baseline:
                    out.append(f"      {f.baseline}")
    c = Counter(f.level for f in findings)
    out.append("-- " + ", ".join(f"{c.get(lv, 0)} {lv}" for lv in LEVELS)
               + f"; {sum(1 for f in findings if f.baseline)} in the baseline")
    return "\n".join(out)


def to_json(findings: list[Finding]) -> str:
    return json.dumps([f.to_json() for f in findings], ensure_ascii=False, indent=1) + "\n"


def _md(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def markdown(findings: list[Finding], new: list[Finding], stale: list[dict], *, limit: int = 60) -> str:
    checks = load()
    out = ["## Style and editorial checks", "",
           "Every check cites the principle or house-style section it enforces (docs/style-checks.md). "
           "CI fails on a new error; warnings are annotated; information is listed.", ""]
    out += ["| Check | Rule | Level | Findings | In baseline | New |", "|---|---|---|---|---|---|"]
    per = defaultdict(list)
    for f in findings:
        per[f.check].append(f)
    newc = Counter(f.check for f in new)
    for cid in sorted(per):
        c = checks.get(cid)
        fs = per[cid]
        out.append(f"| {cid} {fs[0].name} | {_md(c.rule if c else '')} | {fs[0].level} | {len(fs)} | "
                   f"{sum(1 for f in fs if f.baseline)} | {newc.get(cid, 0)} |")
    if not per:
        out.append("| (none) | | | 0 | 0 | 0 |")
    for level, title in (("error", "New errors"), ("warn", "New warnings")):
        fs = [f for f in new if f.level == level]
        if fs:
            out += ["", f"### {title} ({len(fs)})", ""]
            for f in fs[:limit]:
                out.append(f"- `{f.where}` {f.check} {f.name}: {_md(f.message)}")
            if len(fs) > limit:
                out.append(f"- … and {len(fs) - limit} more (see the job log)")
    pend = [f for f in findings if f.baseline and f.baseline.startswith("pending")]
    if pend:
        out += ["", f"### Pending in the baseline ({len(pend)})", ""]
        for f in pend[:limit]:
            out.append(f"- `{f.where}` {f.check}: {_md(f.message)}")
    info = [f for f in findings if f.level == "info"]
    if info:
        out += ["", "<details><summary>Information</summary>", ""]
        for f in info[:200]:
            out.append(f"- `{f.where}` {f.check}: {_md(f.message)}")
        out += ["", "</details>"]
    if stale:
        out += ["", f"### Baseline entries whose finding has gone ({len(stale)})", "",
                "Remove them with `python -m tools.style check --update-baseline`.", ""]
        for e in stale[:limit]:
            out.append(f"- `{e['fingerprint']}`")
    return "\n".join(out) + "\n"


def _esc(s: str) -> str:
    return s.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _esc_prop(s: str) -> str:
    return _esc(s).replace(":", "%3A").replace(",", "%2C")


def github(new: list[Finding], *, per_check: int = 30) -> list[str]:
    """Workflow-command annotations for new errors and warnings, at file:line."""
    out = []
    count = Counter()
    for f in new:
        count[f.check] += 1
        if count[f.check] > per_check:
            continue
        kind = "error" if f.level == "error" else "warning"
        params = [f"file={_esc_prop(f.file)}"]
        if f.line is not None:
            params.append(f"line={f.line}")
        params.append(f"title={_esc_prop(f'style {f.check} {f.name}')}")
        where = f" (p.{f.page})" if f.page and f.line is None else ""
        out.append(f"::{kind} {','.join(params)}::{_esc(f.message + where + ' [' + f.rule + ']')}")
    return out
