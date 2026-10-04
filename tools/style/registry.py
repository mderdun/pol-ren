"""Check registry: YAML metadata (checks/<ID>-<name>.yaml) plus a Python
check (checks/<ID>_<name>.py), as in the underlay analyser
(tools/analyser/rules). The YAML holds what a reviewer tunes and cites (level,
rule, authority, message, examples); the Python holds the logic.

Kinds:
  source  check(doc: SourceDoc, ctx: Context) -> hits, for one source file
          whose role is in `applies` (see sources.py for the roles)
  pdf     check(pdf: PdfDoc, ctx: Context) -> hits, for one committed PDF
          whose kind is in `applies` (critical, performance, guide)

Levels: error fails CI (unless the baseline accepts it), warn annotates,
info lists.
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LEVELS = ("error", "warn", "info")


@dataclass
class Check:
    id: str
    name: str
    level: str
    kind: str               # source | pdf
    rule: str               # the principle, house-style section or decision it enforces
    authority: str
    message: str
    applies: tuple = ()
    heuristic: bool = False
    examples: dict = field(default_factory=dict)
    module: object = None
    path: str = ""

    @property
    def fn(self):
        return self.module.check

    def format(self, values: dict) -> str:
        try:
            return self.message.format(**values)
        except (KeyError, IndexError, ValueError):
            return self.message + " " + repr(values)


@lru_cache(maxsize=1)
def load() -> dict[str, Check]:
    checks = {}
    for y in sorted((HERE / "checks").glob("[SP][0-9]*.yaml")):
        d = yaml.safe_load(y.read_text(encoding="utf-8"))
        mod_name = d.get("check") or f"{d['id']}_{d['name'].replace('-', '_')}"
        mod = importlib.import_module(f"tools.style.checks.{mod_name}")
        c = Check(id=d["id"], name=d["name"], level=d["level"], kind=d["kind"], rule=str(d["rule"]),
                  authority=d.get("authority", ""), message=d["message"],
                  applies=tuple(d.get("applies") or ()), heuristic=bool(d.get("heuristic", False)),
                  examples=d.get("examples") or {}, module=mod, path=str(y.relative_to(ROOT)))
        if c.level not in LEVELS:
            raise ValueError(f"{y.name}: level {c.level!r}")
        if c.kind not in ("source", "pdf"):
            raise ValueError(f"{y.name}: kind {c.kind!r}")
        if not c.id.startswith("S" if c.kind == "source" else "P"):
            raise ValueError(f"{y.name}: source checks are S1xx, PDF checks P2xx")
        checks[c.id] = c
    return checks
