"""Key words in context (Miki, second review of 4 October 2026: "it would be
easier for me to assess if they were presented in context of the verse (and
with translations), rather than alphabetically").

The text and its translation come from the edition's own paratext: the first
`textcols` (or `dipltextcols`) table found in editions/<slug>/text.tex, the
performance .lytex or the critical .lytex, with the \\newcommand macros of
text.tex expanded. In each row the last \\lines{...} is the translation and
the one before it the text; their lines (split at \\\\) are paired in order.
Nothing is invented: where no table or no translation is found the page says
so.
"""
from __future__ import annotations

import re
from pathlib import Path

from .ingest import ROOT
from .text import key_word_entries, lexicon, normalise

CMD = re.compile(r"\\newcommand\\(\w+)\{")


def _braced(s: str, i: int) -> tuple[str, int]:
    """The contents of the brace group opening at s[i] ('{'), and the index after it."""
    depth, j = 0, i
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
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def macros(tex: str) -> dict:
    out = {}
    for m in CMD.finditer(tex):
        body, _ = _braced(tex, m.end() - 1)
        out[m.group(1)] = body
    return out


def _expand(s: str, defs: dict, depth: int = 0) -> str:
    if depth > 5:
        return s
    return re.sub(r"\\(\w+)", lambda m: _expand(defs[m.group(1)], defs, depth + 1) if m.group(1) in defs
                  else m.group(0), s)


def _lines_args(row: str) -> list[str]:
    out, i = [], 0
    while True:
        k = row.find("\\lines{", i)
        if k < 0:
            return out
        body, i = _braced(row, k + len("\\lines"))
        out.append(body)


def clean(s: str) -> str:
    s = re.sub(r"\\(?:textit|la|emph|textsc)\{([^{}]*)\}", r"\1", s)
    s = s.replace("\\ ", " ").replace("~", " ")
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def split_lines(s: str) -> list[str]:
    parts = re.split(r"\\\\(?:\[[^\]]*\])?", s)
    return [clean(p) for p in parts if clean(p)]


def text_blocks(slug: str) -> dict:
    """{source, blocks: [[(text line, translation line or None)]], missing: str}."""
    d = ROOT / "editions" / slug
    tt = d / "text.tex"
    defs = macros(tt.read_text(encoding="utf-8")) if tt.exists() else {}
    cands = [tt, d / f"{slug}-performance.lytex", d / f"{slug}-critical.lytex"]
    for path in cands:
        if not path.exists():
            continue
        src = _expand(path.read_text(encoding="utf-8"), defs) if path != tt else \
            "\n".join(_expand(v, defs) for v in defs.values())
        m = re.search(r"\\begin\{(dipl)?textcols\}(.*?)\\end\{(dipl)?textcols\}", src, re.S)
        if not m:
            continue
        rows = [r for r in re.split(r"\\\\\s*(?:\[[^\]]*\])?\s*\n", m.group(2)) if "\\lines{" in r]
        blocks = []
        for r in rows:
            args = _lines_args(r)
            if len(args) < 2:
                blocks.append([(ln, None) for ln in split_lines(args[0])] if args else [])
                continue
            text, trans = split_lines(args[-2]), split_lines(args[-1])
            blocks.append([(t, trans[i] if i < len(trans) and len(trans) == len(text) else None)
                           for i, t in enumerate(text)] if len(trans) == len(text)
                          else [(t, None) for t in text] + [("", " / ".join(trans))])
        return {"source": str(path.relative_to(ROOT)), "blocks": blocks, "missing": ""}
    return {"source": "", "blocks": [], "missing": f"No text-and-translation table found in editions/{slug}/ "
            "(text.tex, the performance or the critical .lytex); the key words are listed without context."}


WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?", re.U)


def mark_line(line: str, lang: str, keys: dict) -> tuple[list, set]:
    """Tokens of a line: (text, None) for plain text, (word, info) for a key
    word, info = {confirmed, source, syls: [(text, stressed)]}."""
    lex = lexicon(lang)
    toks: list = []
    found: set = set()
    pos = 0
    ms = list(WORD.finditer(line))
    skip = False
    for n, m in enumerate(ms):
        if skip:
            skip = False
            continue
        word, end = m.group(0), m.end()
        norm = normalise(word, lang)
        if norm not in keys and n + 1 < len(ms) and line[m.end():ms[n + 1].start()].strip() == "":
            joined = normalise(word + ms[n + 1].group(0), lang)
            if joined in keys:
                norm, word, end, skip = joined, line[m.start():ms[n + 1].end()], ms[n + 1].end(), True
        toks.append((line[pos:m.start()], None))
        if norm in keys:
            k = keys[norm]
            e = lex.entries.get(norm)
            syls = _syllabify(word, e.syllables if e else [], e.stress if e else None)
            toks.append((word, {"confirmed": k["confirmed"], "source": k["source"], "syls": syls,
                                "stress_src": e.src if e else "fallback: penultimate rule"}))
            found.add(norm)
        else:
            toks.append((word, None))
        pos = end
    toks.append((line[pos:], None))
    return toks, found


def _syllabify(word: str, sylls: list, stress) -> list:
    """Cut the printed word by the lexicon's syllables (letters only)."""
    if not sylls:
        return [(word, False)]
    out, i = [], 0
    for k, s in enumerate(sylls):
        n = len(s.replace(" ", ""))
        j, got = i, 0
        while j < len(word) and got < n:
            if word[j].isalpha():
                got += 1
            j += 1
        out.append((word[i:j], k == stress))
        i = j
    if i < len(word):
        t, st = out[-1]
        out[-1] = (t + word[i:], st)
    return out


def key_entries(config: dict, lang: str) -> dict:
    return {normalise(k["word"], lang): k for k in key_word_entries(config)}
