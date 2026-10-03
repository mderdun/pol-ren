#!/usr/bin/env bash
# Build one or more editions:  tools/build.sh juz-sie-zmierzka [critical|performance]
# Requires: LilyPond 2.24 (with lilypond-book), LuaLaTeX, Gregorio 6, Junicode 2.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
slug="$1"; kinds="${2:-critical performance}"
src="$ROOT/editions/$slug"
out="$src/build"
mkdir -p "$out" "$src/pdf"
export TEXINPUTS="$ROOT/house/latex//:$src//:"
for kind in $kinds; do
  f="$slug-$kind"
  if [ -f "$src/$f.lytex" ]; then
    (cd "$src" && lilypond-book --pdf --latex-program=lualatex \
        --include="$ROOT/house/lilypond" --include="$src/music" \
        --output="$out" "$f.lytex" >/dev/null)
    (cd "$out" && lualatex -interaction=nonstopmode -halt-on-error "$f.tex" >/dev/null \
               && lualatex -interaction=nonstopmode -halt-on-error "$f.tex" >/dev/null)
  else  # chant-only editions: plain .tex with gregoriotex
    (cd "$src" && lualatex -interaction=nonstopmode -halt-on-error \
        -output-directory="$out" "$f.tex" >/dev/null \
        && lualatex -interaction=nonstopmode -halt-on-error -output-directory="$out" "$f.tex" >/dev/null)
  fi
  cp "$out/$f.pdf" "$src/pdf/"
  echo "built editions/$slug/pdf/$f.pdf ($(pdfinfo "$src/pdf/$f.pdf" | awk '/^Pages/{print $2}') pp.)"
done
