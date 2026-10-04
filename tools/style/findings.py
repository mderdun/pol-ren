"""Run the checks and collect findings.

A check yields Hits: where (an offset in a source file, or a page of a PDF),
the values its message needs, and a key. The key is what the baseline
remembers (with the check, the file and an occurrence count): the offending
word, siglum, font or page, never a line number, so editing elsewhere in a
file reopens nothing.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .registry import ROOT, Check, load
from .sources import SourceDoc, discover

LEVEL_ORDER = {"error": 0, "warn": 1, "info": 2}


@dataclass
class Hit:
    key: str
    offset: int | None = None      # source checks: offset in doc.text
    page: int | None = None        # PDF checks: 1-based page
    values: dict = field(default_factory=dict)
    line: int | None = None        # set directly when there is no offset


@dataclass
class Finding:
    check: str
    name: str
    level: str
    kind: str
    file: str
    line: int | None
    page: int | None
    message: str
    rule: str
    key: str
    fingerprint: str = ""
    baseline: str | None = None

    def to_json(self) -> dict:
        return asdict(self)

    @property
    def where(self) -> str:
        if self.line is not None:
            return f"{self.file}:{self.line}"
        if self.page is not None:
            return f"{self.file} p.{self.page}"
        return self.file


def _finding(c: Check, rel: str, h: Hit, line: int | None) -> Finding:
    vals = dict(h.values)
    vals.setdefault("key", h.key)
    return Finding(check=c.id, name=c.name, level=c.level, kind=c.kind, file=rel, line=line, page=h.page,
                   message=c.format(vals), rule=c.rule, key=h.key)


def _fingerprints(findings: list[Finding]) -> None:
    occ: Counter = Counter()
    for f in findings:
        k = (f.check, f.file, f.key)
        occ[k] += 1
        f.fingerprint = f"{f.check}|{f.file}|{f.key}|{occ[k]}"


def check_source(doc: SourceDoc, checks: list[Check]) -> list[Finding]:
    out = []
    for c in checks:
        if c.kind != "source" or (c.applies and doc.role not in c.applies):
            continue
        for h in c.fn(doc) or ():
            line = h.line if h.line is not None else (doc.line_of(h.offset) if h.offset is not None else None)
            out.append(_finding(c, doc.rel, h, line))
    return out


def check_pdf_file(path: Path, checks: list[Check]) -> list[Finding]:
    from .pdf import PdfDoc
    pdf = PdfDoc.open(path)
    out = []
    for c in checks:
        if c.kind != "pdf" or (c.applies and pdf.kind not in c.applies):
            continue
        for h in c.fn(pdf) or ():
            out.append(_finding(c, pdf.rel, h, None))
    return out


def pdf_paths(paths: list[str] | None) -> list[Path]:
    if not paths:
        return sorted(list(ROOT.glob("editions/*/pdf/*.pdf")) + list(ROOT.glob("guides/*/pdf/*.pdf")))
    out = []
    for p in paths:
        p = Path(p)
        p = p if p.is_absolute() else Path.cwd() / p
        if p.is_file() and p.suffix == ".pdf":
            out.append(p.resolve())
        elif p.is_dir():
            out += sorted(x.resolve() for x in p.rglob("*.pdf")
                          if x.parent.name == "pdf" and "build" not in x.parts)
    return sorted(set(out))


def run(paths: list[str] | None = None, *, sources: bool = True, pdfs: bool = True,
        only: set[str] | None = None) -> list[Finding]:
    checks = [c for c in load().values() if not only or c.id in only]
    findings: list[Finding] = []
    if sources:
        for p in discover(paths):
            findings += check_source(SourceDoc.from_path(p), checks)
    if pdfs:
        for p in pdf_paths(paths):
            findings += check_pdf_file(p, checks)
    findings.sort(key=lambda f: (f.file, LEVEL_ORDER[f.level], f.line or 0, f.page or 0, f.check))
    _fingerprints(findings)
    return findings
