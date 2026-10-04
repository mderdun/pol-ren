#!/usr/bin/env bash
# Build editions and guides from the shared house style.
#   tools/build.sh                     everything
#   tools/build.sh juz-sie-zmierzka    one edition (both kinds)
#   tools/build.sh juz-sie-zmierzka critical
# Requires LilyPond 2.24 (lilypond-book), LuaLaTeX with gregoriotex and
# polyglossia, Junicode 2, TeX Gyre Pagella.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
"$ROOT/tools/lint.sh" || { echo "fix lint first"; exit 1; }
build_dir() {  # $1 = directory, $2 = optional kind filter
  local src="$1" out="$1/build" name
  rm -rf "$out"; mkdir -p "$out" "$src/pdf"   # lilypond-book does not track includes
  [ "$(basename "$src")" = editorial-principles ] && python3 "$ROOT/tools/principles_guide.py" "$out/principles-body.tex"
  export TEXINPUTS="$ROOT/house/latex//:$src//:"
  for f in "$src"/*.lytex "$src"/*.tex; do
    [ -e "$f" ] || continue
    name="$(basename "${f%.*}")"
    case "$name" in text|*-text) continue;; esac
    [ -n "${2:-}" ] && [[ "$name" != *"-$2" ]] && continue
    if [[ "$f" == *.lytex ]]; then
      (cd "$src" && lilypond-book --pdf --latex-program=lualatex \
         --include="$ROOT/house/lilypond" --include="$src/music" \
         --output="$out" "$name.lytex" >"$out/$name.book.log" 2>&1) \
         || { tail -20 "$out/$name.book.log"; exit 1; }
    else
      cp "$f" "$out/"
    fi
    (cd "$out" && for i in 1 2; do lualatex -interaction=nonstopmode -halt-on-error "$name.tex" >/dev/null \
       || { grep -A5 '^!' "$name.log"; exit 1; }; done)
    cp "$out/$name.pdf" "$src/pdf/"
    rm -f "$src"/tmp*.out "$src"/tmp*.pdf "$src"/tmp*.aux "$src"/tmp*.log   # lilypond-book page probes
    echo "built ${src#$ROOT/}/pdf/$name.pdf ($(pdfinfo "$src/pdf/$name.pdf" | awk '/^Pages/{print $2}') pp.)"
    python3 "$ROOT/tools/check_pages.py" "$src/pdf/$name.pdf"
    for sys in "$out"/*/lily-*.pdf; do   # a system wider than the text block (170 mm = 482 pt) runs into the margin
      [ -e "$sys" ] || continue
      w=$(pdfinfo "$sys" | awk '/Page size/{print int($3)}')
      if [ "$w" -gt 490 ]; then echo "  system $(basename "$sys"): $w pt wide, over the 482 pt text block; reset this score's breaks"; fi
    done | sort -u
  done
}
if [ $# -eq 0 ]; then
  for d in "$ROOT"/editions/*/ "$ROOT"/guides/*/; do [ -d "$d" ] && build_dir "${d%/}"; done
else
  d="$ROOT/editions/$1"; [ -d "$d" ] || d="$ROOT/guides/$1"
  build_dir "$d" "${2:-}"
fi
