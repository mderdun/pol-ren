"""Rule registry: YAML metadata (rules/<ID>-<name>.yaml) plus a Python check
(rules/<ID>_<name>.py). The YAML holds everything a reviewer tunes (level,
weight, tier, principle, authority, message, gates, examples); the Python holds
the logic.

Scopes:
  syllable  check(ctx: SegCtx) -> hits for one syllable under one candidate
  line      check_line(lctx: LineCtx) -> hits over a whole line
  piece     check_piece(pctx, line, starts) -> hits that compare voices
"""
from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
LEVELS = ("break", "warn", "look", "info")


@dataclass
class Rule:
    id: str
    name: str
    level: str              # native level: break for firm rules, look or info otherwise
    weight: float
    tier: str
    principle: str
    authority: str
    message: str
    scope: str = "syllable"
    langs: tuple = ("la", "pl")
    legacy: bool = False    # one of the old audit's checks
    hard: bool = False      # a firm rule: decides legality
    gates: dict = field(default_factory=dict)
    examples: dict = field(default_factory=dict)
    module: object = None
    path: str = ""

    def fn(self):
        return {"syllable": getattr(self.module, "check", None),
                "line": getattr(self.module, "check_line", None),
                "piece": getattr(self.module, "check_piece", None)}[self.scope]

    def format(self, values: dict) -> str:
        try:
            return self.message.format(**values)
        except (KeyError, IndexError, ValueError):
            return self.message + " " + repr(values)


@lru_cache(maxsize=1)
def load() -> dict[str, Rule]:
    rules = {}
    for y in sorted(HERE.glob("U*.yaml")):
        d = yaml.safe_load(y.read_text(encoding="utf-8"))
        mod_name = d.get("check") or f"{d['id']}_{d['name'].replace('-', '_')}"
        mod = importlib.import_module(f"{__name__}.{mod_name}")
        r = Rule(id=d["id"], name=d["name"], level=d["level"], weight=float(d.get("weight", 0)),
                 tier=d.get("tier", ""), principle=str(d.get("principle", "")),
                 authority=d.get("authority", ""), message=d["message"],
                 scope=d.get("scope", "syllable"), langs=tuple(d.get("applies", {}).get("lang", ["la", "pl"])),
                 legacy=bool(d.get("legacy", False)), hard=bool(d.get("hard", False)),
                 gates=d.get("gates") or {}, examples=d.get("examples") or {}, module=mod,
                 path=str(y.relative_to(HERE.parent.parent.parent)))
        if r.level not in LEVELS:
            raise ValueError(f"{y.name}: level {r.level!r}")
        rules[r.id] = r
    return rules


@lru_cache(maxsize=1)
def settings() -> dict:
    return yaml.safe_load((HERE.parent / "settings.yaml").read_text(encoding="utf-8"))
