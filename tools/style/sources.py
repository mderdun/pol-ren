"""Source files as the checks see them.

A SourceDoc is one file with its role in the series:

  critical      editions/<slug>/<slug>-critical.lytex|tex
  performance   editions/<slug>/<slug>-performance.lytex|tex
  text          editions/<slug>/text.tex (texts shared by both editions)
  music         editions/<slug>/music/*.ily|ly|gabc
  guide         guides/<name>/*.tex, and docs/editorial-principles.md, which
                tools/principles_guide.py prints as the principles guide
  house         house/latex/*.cls, house/lilypond/*.ily

Working material (notes/, build/, pdf/, generated Python) is not checked:
principles 2.4 keeps it out of the editions, so the house style does not
govern it.

TeX helpers: comments are blanked (offsets and line numbers are kept, so a
hit points at the right line), arguments of commands can be found with brace
matching, and `mask` blanks spans a check should not read (URLs, foreign text,
quotations, the literature list).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from .registry import ROOT

EXTS = {".lytex", ".tex", ".ily", ".ly", ".cls", ".gabc", ".md"}
SKIP_PARTS = {"build", "notes", "pdf", "__pycache__", "worktrees", ".claude"}
GUIDE_MD = ("docs/editorial-principles.md",)


def role_of(rel: str) -> str | None:
    p = Path(rel)
    parts = p.parts
    if any(x in SKIP_PARTS for x in parts) or p.suffix not in EXTS:
        return None
    if rel in GUIDE_MD:
        return "guide"
    if parts[0] == "house":
        return "house" if p.suffix in (".cls", ".ily") else None
    if parts[0] == "guides" and p.suffix == ".tex":
        return "guide"
    if parts[0] == "editions" and len(parts) >= 3:
        if parts[2] == "music":
            return "music" if p.suffix in (".ily", ".ly", ".gabc") else None
        if len(parts) == 3:
            stem = p.stem
            if stem == "text" or stem.endswith("-text"):
                return "text"
            if stem.endswith("-critical"):
                return "critical"
            if stem.endswith("-performance"):
                return "performance"
    return None


def slug_of(rel: str) -> str | None:
    parts = Path(rel).parts
    if parts[0] in ("editions", "guides") and len(parts) > 1:
        return parts[1]
    return None


def discover(paths: list[str] | None = None) -> list[Path]:
    """Every checkable source under the given files or directories (default:
    editions/, guides/, house/ and the principles)."""
    roots = [Path(p) for p in paths] if paths else [ROOT / "editions", ROOT / "guides", ROOT / "house",
                                                     *(ROOT / g for g in GUIDE_MD)]
    out = []
    for r in roots:
        r = r if r.is_absolute() else (Path.cwd() / r)
        files = [r] if r.is_file() else sorted(x for x in r.rglob("*") if x.is_file())
        for f in files:
            try:
                rel = f.resolve().relative_to(ROOT).as_posix()
            except ValueError:
                continue
            if role_of(rel):
                out.append(f.resolve())
    return sorted(set(out))


@dataclass
class SourceDoc:
    rel: str                      # path relative to the repository
    text: str
    role: str = ""
    slug: str | None = None
    lang: str = "la"              # the edition's text language (tools/analyser/editions.yaml)
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_path(cls, path: Path, **kw) -> "SourceDoc":
        rel = path.resolve().relative_to(ROOT).as_posix()
        return cls.make(rel, path.read_text(encoding="utf-8"), **kw)

    @classmethod
    def make(cls, rel: str, text: str, **kw) -> "SourceDoc":
        from .editions import edition
        d = cls(rel=rel, text=text, role=role_of(rel) or "", slug=slug_of(rel))
        if d.slug:
            e = edition(d.slug)
            d.lang = e.get("lang", "la")
        for k, v in kw.items():
            setattr(d, k, v)
        return d

    @property
    def suffix(self) -> str:
        return Path(self.rel).suffix

    @property
    def is_tex(self) -> bool:
        return self.suffix in (".tex", ".lytex", ".cls")

    @property
    def is_lily(self) -> bool:
        return self.suffix in (".ily", ".ly")

    @cached_property
    def line_starts(self) -> list[int]:
        out = [0]
        for m in re.finditer("\n", self.text):
            out.append(m.end())
        return out

    def line_of(self, offset: int) -> int:
        lo, hi = 0, len(self.line_starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.line_starts[mid] <= offset:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    @cached_property
    def code(self) -> str:
        """The text with comments blanked (same length, same line breaks)."""
        if self.is_tex:
            return blank_comments(self.text, "%")
        if self.is_lily:
            return blank_lily_comments(self.text)
        if self.suffix == ".md":
            return re.sub(r"<!--.*?-->", lambda m: blank(m.group(0)), self.text, flags=re.S)
        return self.text

    @cached_property
    def prose(self) -> str:
        """For TeX and Markdown: the code with what is not the editor's English
        prose blanked: URLs, foreign-language runs (\\la, \\pl, \\dipl, ...),
        quotations in ‘…’, the literature list, sigla arguments, verbatim and
        math. For LilyPond files: empty."""
        if self.is_lily or self.suffix == ".gabc":
            return blank(self.code)
        s = self.code
        if self.suffix == ".md":
            s = re.sub(r"`[^`\n]*`", lambda m: blank(m.group(0)), s)
            s = re.sub(r"\]\([^)]*\)", lambda m: blank(m.group(0)), s)
        s = mask_env(s, ("literature", "textcols", "dipltextcols", "variants", "soundtable", "latintable",
                         "pronunciation", "verbatim"))
        s = mask_args(s, ("url", "href", "la", "pl", "dipl", "textlatin", "textpolish", "sig", "siglum",
                          "lit", "ipa", "slug", "repository", "input", "lilypondfile", "includegraphics",
                          "gregorioscore", "label", "ref", "cite", "definecolor", "lnum", "voice"))
        s = mask_quotes(s)
        s = re.sub(r"\$[^$]*\$", lambda m: blank(m.group(0)), s)
        return s


def blank(s: str) -> str:
    return re.sub(r"[^\n]", " ", s)


def blank_comments(text: str, ch: str = "%") -> str:
    out = []
    for line in text.split("\n"):
        i = 0
        cut = None
        while i < len(line):
            c = line[i]
            if c == "\\":
                i += 2
                continue
            if c == ch:
                cut = i
                break
            i += 1
        out.append(line if cut is None else line[:cut] + " " * (len(line) - cut))
    return "\n".join(out)


def blank_lily_comments(text: str) -> str:
    # block comments %{ ... %}, then line comments outside strings
    text = re.sub(r"%\{.*?%\}", lambda m: blank(m.group(0)), text, flags=re.S)
    out = []
    for line in text.split("\n"):
        ins, cut = False, None
        for i, c in enumerate(line):
            if c == '"' and (i == 0 or line[i - 1] != "\\"):
                ins = not ins
            elif c == "%" and not ins:
                cut = i
                break
        out.append(line if cut is None else line[:cut] + " " * (len(line) - cut))
    return "\n".join(out)


def match_brace(s: str, i: int) -> int:
    """s[i] == '{'; return the index of the matching '}' (or len(s) - 1)."""
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    return len(s) - 1


def command_args(s: str, name: str, nargs: int = 1, optional: bool = True):
    """Yield (start, [(arg_start, arg_end), ...]) for every \\name{..}{..}.
    arg_start/arg_end exclude the braces. An optional [..] argument after the
    name is skipped."""
    for m in re.finditer(r"\\" + re.escape(name) + r"(?![A-Za-z@])", s):
        j = m.end()
        if optional:
            while j < len(s) and s[j] in " \t":
                j += 1
            if j < len(s) and s[j] == "[":
                k = s.find("]", j)
                j = k + 1 if k >= 0 else j
        args = []
        for _ in range(nargs):
            while j < len(s) and s[j] in " \t\n":
                j += 1
            if j >= len(s) or s[j] != "{":
                break
            k = match_brace(s, j)
            args.append((j + 1, k))
            j = k + 1
        if len(args) == nargs:
            yield m.start(), args


def mask_args(s: str, names) -> str:
    chars = list(s)
    for name in names:
        for _, args in command_args(s, name, 1):
            a, b = args[0]
            for k in range(a, b):
                if chars[k] != "\n":
                    chars[k] = " "
    return "".join(chars)


def mask_env(s: str, names) -> str:
    for name in names:
        s = re.sub(r"\\begin\{" + name + r"\}.*?\\end\{" + name + r"\}", lambda m: blank(m.group(0)), s,
                   flags=re.S)
    return s


def mask_quotes(s: str) -> str:
    """Blank quotations in single curly quotes ‘…’ (an apostrophe ’ inside a
    word does not close one)."""
    out = list(s)
    i = 0
    while True:
        a = s.find("‘", i)
        if a < 0:
            break
        j = a + 1
        depth = 1
        while j < len(s) and depth:
            c = s[j]
            if c == "‘":
                depth += 1
            elif c == "’":
                nxt = s[j + 1] if j + 1 < len(s) else " "
                prv = s[j - 1]
                if not (prv.isalpha() and nxt.isalpha()):
                    depth -= 1
            j += 1
        for k in range(a, j):
            if out[k] != "\n":
                out[k] = " "
        i = j
    return "".join(out)


# ------------------------------------------------------------------ sections

SECTION_RE = re.compile(r"\\(section\*?|opensection|subsection\*?|pnote)\s*\{([^{}]*)\}|^#{1,3} (.+)$", re.M)


def sections(doc: SourceDoc) -> list[tuple[int, int, str, str]]:
    """(start, end, heading_end, title) for top-level sections (\\section*,
    \\opensection, Markdown ##), end = start of the next one."""
    marks = []
    for m in SECTION_RE.finditer(doc.code):
        kind = m.group(1) or "md"
        if kind.startswith("subsection") or kind == "pnote":
            continue
        marks.append((m.start(), m.end(), (m.group(2) or m.group(3) or "").strip()))
    out = []
    for i, (a, e, t) in enumerate(marks):
        b = marks[i + 1][0] if i + 1 < len(marks) else len(doc.code)
        out.append((a, b, e, t))
    return out


def section_span(doc: SourceDoc, title_re: str):
    """(start, end) of the body of the first section whose title matches
    (after its heading, up to the next section)."""
    for a, b, e, t in sections(doc):
        if re.search(title_re, t, re.I):
            return e, b
    return None


# ------------------------------------------------------------------ sentences

ABBREV = {"fol", "fols", "pp", "p", "no", "nos", "vol", "vols", "ser", "edn", "ed", "eds", "c", "fl", "cf",
          "st", "dr", "mr", "e.g", "i.e", "ca", "trans", "repr", "op"}

def sentences(text: str, start: int = 0, end: int | None = None):
    """Yield (a, b) spans of sentences in text[start:end] (a full stop,
    question or exclamation mark followed by space and a capital or a
    command, or a blank line, ends one)."""
    end = len(text) if end is None else end
    a = start
    for m in re.finditer(r"([.!?])(?=\s+(?:[A-Z‘(\\]))|\n\s*\n", text[start:end]):
        if m.group(1) == ".":
            word = re.search(r"([A-Za-z.]+)$", text[start:start + m.start()])
            if word and (word.group(1).lower().rstrip(".") in ABBREV or len(word.group(1)) == 1):
                continue
        b = start + m.end()
        if text[a:b].strip():
            yield a, b
        a = b
    if text[a:end].strip():
        yield a, end
