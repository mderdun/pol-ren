"""Per-edition facts the checks need.

The text language comes from the analyser's tools/analyser/editions.yaml
(shared, so the two CIs cannot disagree). The sigla of each edition (what each
one is, and whether it is lost) are read from the critical edition's Sources
section; tools/style/editions.yaml overrides what that reading gets wrong.
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml

from .registry import HERE, ROOT

LOST_RE = re.compile(r"\b(lost|destroyed|no copy (?:is )?known|burnt|burned)\b", re.I)


@lru_cache(maxsize=1)
def _analyser_cfg() -> dict:
    p = ROOT / "tools" / "analyser" / "editions.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


@lru_cache(maxsize=1)
def _style_cfg() -> dict:
    p = HERE / "editions.yaml"
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


def edition(slug: str) -> dict:
    out = dict(_analyser_cfg().get(slug) or {})
    out.update(_style_cfg().get(slug) or {})
    if slug == "bogurodzica":
        out.setdefault("lang", "pl")
    return out


def critical_file(slug: str) -> Path | None:
    for ext in (".lytex", ".tex"):
        p = ROOT / "editions" / slug / f"{slug}-critical{ext}"
        if p.exists():
            return p
    return None


def parse_sigla(code: str) -> list[dict]:
    """Entries of every sigla environment: siglum, its text, offset, and the
    kind the context suggests (edition for a list introduced as collated
    editions or recordings, otherwise source)."""
    out = []
    for env in re.finditer(r"\\begin\{sigla\}(.*?)\\end\{sigla\}", code, re.S):
        lead = code[max(0, env.start() - 400):env.start()]
        lead = lead[lead.rfind("\\end{sigla}") + 1:] if "\\end{sigla}" in lead else lead
        collated = bool(re.search(r"(editions?|recordings?)(?: and \w+)?\s+collated|collated (editions|recordings)",
                                  lead, re.I))
        body = env.group(1)
        base = env.start(1)
        marks = [(m.start(), m.end(), m.group(1) or m.group(2))
                 for m in re.finditer(r"\\siglum\{([^{}]*)\}|\\item\[([^\]]*)\]", body)]
        for i, (a, b, sig) in enumerate(marks):
            e = marks[i + 1][0] if i + 1 < len(marks) else len(body)
            text = body[b:e]
            kind = "source"
            if collated:
                kind = "recording" if re.search(r"\b(recording|CD|Supraphon|records?)\b", text, re.I) else "edition"
            out.append(dict(siglum=sig.strip(), text=text, offset=base + a, kind=kind,
                            lost=bool(LOST_RE.search(text)), library=bool(marks and body[a:b].startswith("\\item"))))
    return out


@lru_cache(maxsize=None)
def sigla(slug: str) -> dict[str, dict]:
    """siglum -> {kind, lost, text}; the first entry for a siglum wins
    ("As above" repeats are skipped)."""
    from .sources import blank_comments
    f = critical_file(slug)
    out: dict[str, dict] = {}
    if f is not None:
        for e in parse_sigla(blank_comments(f.read_text(encoding="utf-8"))):
            if e["siglum"] not in out:
                out[e["siglum"]] = e
    for sig, over in ((edition(slug).get("sigla") or {}).items()):
        out.setdefault(sig, dict(siglum=sig, text="", offset=0, kind="source", lost=False, library=False))
        out[sig].update(over)
    return out


def lost_sigla(slug: str) -> set[str]:
    return {s for s, e in sigla(slug).items() if e.get("lost")}
