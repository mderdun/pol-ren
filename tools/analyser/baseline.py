"""The baseline: findings the editor has looked at, keyed by word and syllable
identity (edition, voice, verse, rule, word, syllable in the word,
occurrence), not by bar, so renumbering bars reopens nothing.

Each entry has a status and a reason:
  accepted  the editor keeps the underlay, for the reason given (for example a
            source reading kept under principles 10.12)
  pending   present when the analyser was introduced and not yet reviewed;
            kept out of CI's "new" list until someone decides
"""
from __future__ import annotations

import json
from pathlib import Path

from .findings import Finding, Result

PENDING = "pending review: present when the analyser was introduced (4 October 2026)"


def load(path: Path | None) -> dict:
    if path is None or not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {e["fingerprint"]: e for e in data.get("findings", [])}


def apply(results: list[Result], base: dict) -> dict:
    """Mark baselined findings (and those accepted by a comment in the
    LilyPond source, inline.py); return slug -> new findings (look or worse)."""
    from . import inline
    new = {}
    for r in results:
        for f in r.findings:
            acc = inline.find(f)
            if acc is not None:
                f.baseline = f"accepted: {acc.reason} (inline, {acc.file}:{acc.at})"
                continue
            e = base.get(f.fingerprint)
            if e is not None:
                f.baseline = f"{e.get('status', 'accepted')}: {e.get('reason', '')}"
            elif f.level != "info":
                new.setdefault(r.slug, []).append(f)
    return new


def update(path: Path, results: list[Result], base: dict) -> int:
    """Rewrite the baseline: keep every entry of the editions not analysed now,
    keep entries that still match (with their reasons), add new findings
    (look or worse) as pending. Returns the number added."""
    slugs = {r.slug for r in results}
    keep = [e for e in base.values() if e["fingerprint"].split("|")[0] not in slugs]
    added = 0
    for r in results:
        for f in r.findings:
            e = base.get(f.fingerprint)
            if f.level == "info" and not (e and e.get("status") == "accepted"):
                continue
            if e is None:
                added += 1
                e = {"fingerprint": f.fingerprint, "status": "pending", "reason": PENDING}
            e = {**e, "rule": f.rule, "where": f"{f.voice} v{f.verse} bar {f.where}", "message": f.message}
            keep.append(e)
    keep.sort(key=lambda e: e["fingerprint"])
    Path(path).write_text(json.dumps({"version": 1, "findings": keep}, ensure_ascii=False, indent=1) + "\n",
                          encoding="utf-8")
    return added


def entry_for(f: Finding, status: str, reason: str) -> dict:
    return {"fingerprint": f.fingerprint, "status": status, "reason": reason, "rule": f.rule,
            "where": f"{f.voice} v{f.verse} bar {f.where}", "message": f.message}
