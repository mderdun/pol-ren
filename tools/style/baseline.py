"""The baseline: findings the editor has looked at, keyed by fingerprint
(check | file | key | occurrence). The key is the offending word, siglum,
font, critical-note position or page, never a line number, so editing
elsewhere in a file reopens nothing. As in the underlay analyser
(tools/analyser/baseline.py), each entry has a status and a reason:

  accepted  the editor keeps it, for the reason given
  pending   present when the style CI was introduced (4 October 2026) and not
            yet decided; kept out of CI's "new" list until someone decides

Only errors and warnings are baselined; information is never new.
"""
from __future__ import annotations

import json
from pathlib import Path

from .findings import Finding

PENDING = "pending review: present when the style CI was introduced (4 October 2026)"


def load(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {e["fingerprint"]: e for e in data.get("findings", [])}


def apply(findings: list[Finding], base: dict) -> list[Finding]:
    """Mark baselined findings; return the new ones (warn or error)."""
    new = []
    for f in findings:
        e = base.get(f.fingerprint)
        if e is not None:
            f.baseline = f"{e.get('status', 'accepted')}: {e.get('reason', '')}"
        elif f.level != "info":
            new.append(f)
    return new


def stale(findings: list[Finding], base: dict, files: set[str] | None = None) -> list[dict]:
    """Baseline entries whose finding has gone (in the files checked now)."""
    live = {f.fingerprint for f in findings}
    out = []
    for fp, e in base.items():
        file = fp.split("|")[1] if fp.count("|") >= 3 else ""
        if files is not None and file not in files:
            continue
        if fp not in live:
            out.append(e)
    return out


def update(path: Path, findings: list[Finding], base: dict, files: set[str], levels=("error", "warn")) -> int:
    """Rewrite the baseline: keep entries for files not checked now, keep
    entries that still match (with their reasons), drop entries whose finding
    has gone, add new findings of the given levels as pending."""
    keep = [e for fp, e in base.items() if (fp.split("|")[1] if fp.count("|") >= 3 else "") not in files]
    added = 0
    for f in findings:
        e = base.get(f.fingerprint)
        if e is None:
            if f.level not in levels:
                continue
            added += 1
            e = {"fingerprint": f.fingerprint, "status": "pending", "reason": PENDING}
        keep.append({**e, "check": f.check, "where": f.where, "message": f.message})
    keep.sort(key=lambda e: e["fingerprint"])
    Path(path).write_text(json.dumps({"version": 1, "findings": keep}, ensure_ascii=False, indent=1) + "\n",
                          encoding="utf-8")
    return added
