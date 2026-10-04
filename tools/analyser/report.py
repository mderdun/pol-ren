"""Output: text (the old audit's shape, extended), JSON (the golden snapshots),
Markdown (the CI job summary and review notes), GitHub annotations, and the
human-readable report of the analysis layers."""
from __future__ import annotations

import json
from collections import Counter

from .findings import Finding, Result
from .layers.imitation import interval_word
from .meter import mensuration_summary
from .text import coverage

LEVELS = ("break", "warn", "look", "info")


# ------------------------------------------------------------------ findings

def text(res: Result, *, show_info: bool = False, verbose: bool = False) -> str:
    out = [f"== {res.slug}  ({res.path})"]
    for f in res.findings:
        if f.level == "info" and not show_info:
            continue
        mark = " [baseline]" if f.baseline else ""
        rg = "" if f.regret is None else f" regret {f.regret:.2f}"
        out.append(f"{f.level.upper():5} {f.rule} {f.voice:9} v{f.verse} {f.where:7} {f.name}: {f.message}{rg}{mark}")
        if verbose:
            if f.src:
                out.append(f"      at {f.src}")
            if f.breakdown:
                out.append("      costs here: " + "; ".join(f.breakdown))
            for a in f.alternatives:
                out.append(f"      try: {', '.join(a['moves'])} ({a['cost']:+.2f}"
                           + (f"; fixes {', '.join(a['fixes'])}" if a['fixes'] else "")
                           + (f"; costs {', '.join(a['introduces'])}" if a['introduces'] else "") + ")")
            if f.baseline:
                out.append(f"      accepted: {f.baseline}")
    c = Counter(f.level for f in res.findings)
    out.append("-- " + ", ".join(f"{c.get(lv, 0)} {lv}" for lv in LEVELS)
               + f"; {sum(1 for f in res.findings if f.baseline)} accepted in the baseline")
    return "\n".join(out)


def to_json(res: Result) -> dict:
    return {"edition": res.slug, "findings": [f.to_json() for f in res.findings]}


def _dedupe_top(findings: list[Finding], n: int) -> list[Finding]:
    """The biggest regrets, one per window (findings that share an
    alternative are one problem)."""
    seen, out = set(), []
    for f in sorted(findings, key=lambda f: -(f.regret or 0)):
        if f.regret is None or f.regret <= 0:
            continue
        key = (f.voice, f.verse, tuple(f.alternatives[0]["moves"]) if f.alternatives else f.where)
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
        if len(out) >= n:
            break
    return out


def markdown(results: list[Result], *, new: dict | None = None, top: int = 8) -> str:
    out = ["## Underlay analyser", ""]
    out.append("Severity is regret: how much better the best legal underlay nearby scores. "
               "Alternatives are suggestions to sing, never changes (principles 10.6).")
    out.append("")
    out.append("| Edition | break | warn | look | info | in baseline | new |")
    out.append("|---|---|---|---|---|---|---|")
    for r in results:
        c = Counter(f.level for f in r.findings)
        acc = sum(1 for f in r.findings if f.baseline)
        nw = len((new or {}).get(r.slug, []))
        out.append(f"| {r.slug} | {c.get('break', 0)} | {c.get('warn', 0)} | {c.get('look', 0)} | "
                   f"{c.get('info', 0)} | {acc} | {nw} |")
    for r in results:
        # open findings: not information, not accepted (pending ones stay open)
        fs = [f for f in r.findings if f.level != "info" and not (f.baseline or "").startswith("accepted")]
        new_here = (new or {}).get(r.slug, [])
        if new_here:
            out += ["", f"### {r.slug}: new since the baseline", ""]
            for f in new_here:
                out.append(f"- {f.level}: {f.rule} {f.voice} v{f.verse} bar {f.where}: {f.message}"
                           + (f" (`{f.src}`)" if f.src else ""))
        tops = _dedupe_top(fs, top)
        if tops:
            out += ["", f"### {r.slug}: biggest regrets (open findings)", "",
                    "| Regret | Rule | Voice | Bar | Finding | Try | Status |",
                    "|---|---|---|---|---|---|---|"]
            for f in tops:
                alt = "; ".join(f.alternatives[0]["moves"]) if f.alternatives else ""
                status = "pending" if f.baseline else "new"
                out.append(f"| {f.regret:.2f} | {f.rule} | {f.voice} v{f.verse} | {f.where} | "
                           f"{_md(f.message)} | {_md(alt)} | {status} |")
    return "\n".join(out) + "\n"


def _md(s: str) -> str:
    return s.replace("|", "\\|")


def github(results: list[Result], new: dict, limit: int = 40) -> list[str]:
    """Workflow-command annotations for new findings only, at voices.ily file:line."""
    out = []
    for r in results:
        for f in new.get(r.slug, [])[:limit]:
            kind = "error" if f.level == "break" else "warning"
            loc = ""
            if f.src:
                file, line = f.src.rsplit(":", 1)
                loc = f" file={file},line={line}"
            msg = f"{f.rule} {f.voice} v{f.verse} bar {f.where}: {f.message}".replace("\n", " ")
            out.append(f"::{kind}{loc},title=underlay {f.rule}::{msg}")
    return out


# ------------------------------------------------------------------ layers

def layers(res_or_analysis) -> str:
    a = getattr(res_or_analysis, "analysis", res_or_analysis)
    sc = a.score
    out = [f"Analysis of {sc.title} ({sc.slug})", ""]
    out.append("Positions are bar.minim (16.3 = third minim of bar 16).")
    out.append("")
    out.append("METRE")
    for v in sc.parts:
        out.append(f"  {v:9} mensuration {mensuration_summary(sc.voices[v])} "
                   f"({sc.config.get('mensuration_note', 'as printed')})")
    out += ["", "TEXT (words, lexicon)"]
    for row in coverage(sc, a.lines):
        flag = "" if row["known"] else "   NOT IN LEXICON"
        if row["known"] and row["lex_syllables"] and row["lex_syllables"] != row["syllables"]:
            flag = f"   lexicon has {row['lex_syllables']} syllables, sung with {row['syllables']}"
        out.append(f"  {row['word']:18} x{row['count']}{flag}")
    out += ["", f"CADENCES ({len(a.cadences)})",
            "  functions: C cantizans, T tenorizans, B bassizans, A altizans, b evaded bass, c/t prepared but not arriving"]
    for c in a.cadences:
        fs = ", ".join(f"{v} {f}" for v, f in sorted(c.functions.items()))
        out.append(f"  {c.where:7} {c.type:14} on {c.tone:3} {'(after a suspension) ' if c.prepared else ''}[{fs}]")
    out += ["", "DISSONANCE"]
    cnt = Counter(d.label for d in a.dissonances.values())
    out.append("  " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
    for (v, idx), d in sorted(a.dissonances.items(), key=lambda kv: (kv[1].onset, kv[0])):
        e = sc.voices[v][idx]
        if d.label == "suspension":
            r = sc.voices[v][d.resolution]
            out.append(f"  {e.where:7} {v:9} suspension {d.figure:5} {e.name} held against {d.agent} "
                       f"({d.interval}), resolves to {r.name} at {r.where}")
        elif d.label in ("unexplained", "cambiata", "echappee", "anticipation", "accented-passing"):
            out.append(f"  {e.where:7} {v:9} {d.label:16} {e.name} ({d.interval} against {d.against})")
    out.append("  (passing notes and neighbours are counted above, not listed)")
    out += ["", f"PHRASES ({len(a.phrases)})"]
    for ph in a.phrases:
        ln = a.line(ph.voice, ph.verse)
        cad = f"  -> {ph.cadence.type} on {ph.cadence.tone}" if ph.cadence else ""
        out.append(f"  {ph.voice:9} v{ph.verse} {ph.label(ln):13} ends at {ph.ends:11} {ph.text}{cad}")
    out += ["", f"IMITATION ({len(a.points)} points)"]
    for p in a.points:
        out.append(f"  {p.type:4} head {p.motif} (steps), led by {p.leader.voice} at {p.leader.where}")
        for e in p.entries:
            ln = a.line(e.voice, "1")
            words = ""
            if ln is not None:
                st = {s.ev: s.text for s in ln.syls}
                words = " ".join(st.get(i, "_") for i in e.head)
            out.append(f"       {e.voice:9} {e.where:7} {interval_word(e.transposition):14} "
                       f"{'exact' if e.exact else 'flexed':6} text: {words}")
    out += ["", f"HOMORHYTHM ({len(a.regions)} passages)"]
    for r in a.regions:
        out.append(f"  {r.first_where}-{r.last_where}  {r.slices} slices, voices {', '.join(r.voices)}; "
                   f"syllables together: " + ", ".join(f"v{k} {int(v * 100)}%" for k, v in r.syllable_match.items()))
    return "\n".join(out) + "\n"


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False) + "\n"
