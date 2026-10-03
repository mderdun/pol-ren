#!/usr/bin/env python3
"""Make the body of the series guide *Editorial principles* from
docs/editorial-principles.md, so that the rules exist in one place.

    tools/principles_guide.py OUT.tex

Working notes are dropped on the way: provenance tags such as (MD, *Plaude*),
the opening note on provenance, and the decision log (section 15).
Rule numbers are kept, so editions can cite "principles 10.1".
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
md = (ROOT / "docs/editorial-principles.md").read_text(encoding="utf-8")

md = md.split("\n## 1. ", 1)
md = "## 1. " + md[1]                                   # drop title and provenance note
md = re.split(r"\n## 15\. ", md)[0]                    # drop the decision log
md = re.sub(r";\s*MD\b[^;()]*", "", md)                # mixed citations: keep the source
md = re.sub(r"\(MD\b[^;()]*;\s*", "(", md)
EDS = r"\*(?:Bogurodzica|Nunc scio|Zmierzka|Plaude|Vox)\*"
md = re.sub(r"\s*\((?:MD\b|Editor's rule|" + EDS + r")[^()]*(?:\([^()]*\)[^()]*)*\)", "", md)
md = re.sub(r' "There\'s literally no reason to baby the performer\."', "", md)
md = re.sub(r"\s*\([^()]*\b\d{1,2} Oct 2026\)", "", md)     # dated working notes
md = re.sub(r"\(\*?\s*\)", "", md)

tex = subprocess.run(["pandoc", "-f", "markdown-auto_identifiers", "-t", "latex", "--wrap=preserve", "--shift-heading-level-by=-1"],
                     input=md, capture_output=True, text=True, check=True).stdout
tex = re.sub(r"\\(sub)?section\{", lambda m: "\\" + (m.group(1) or "") + "section*{", tex)
tex = tex.replace("\\def\\labelenumi{\\arabic{enumi}.}", "").replace("\\textbf{", "\\textit{")   # house style: no bold
tex = tex.replace("``", "‘").replace("''", "’")          # house style: single quotes
tex = tex.replace("⌜", "{\\accfont ⌜}").replace("⌝", "{\\accfont ⌝}")   # Junicode lacks them
Path(sys.argv[1]).write_text("\\providecommand\\tightlist{\\setlength{\\itemsep}{0pt}\\setlength{\\parskip}{0pt}}\n" + tex,
                             encoding="utf-8")
