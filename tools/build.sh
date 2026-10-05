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
"$ROOT/tools/get-fonts.sh"
if [ "${NOVELLO:-1}" != 0 ]; then "$ROOT/tools/make-pressed-fonts.sh"; fi
lily_book() {  # $1 = source dir, $2 = name, $3 = system log, $4 = stretch data
  (cd "$1" && PR_SYSLOG="$3" PR_STRETCH="$4" lilypond-book --pdf --latex-program=lualatex \
     --include="$ROOT/house/lilypond" --include="$1/music" --include="$ROOT/house/fonts/pressed" \
     --output="$1/build" "$2.lytex" >"$1/build/$2.book.log" 2>&1) \
     || { tail -20 "$1/build/$2.book.log"; exit 1; }
}
latex_twice() {  # $1 = build dir, $2 = name
  (cd "$1" && for i in 1 2; do lualatex -interaction=nonstopmode -halt-on-error "$2.tex" >/dev/null \
     || { grep -A5 '^!' "$2.log"; exit 1; }; done) || exit 1
}
build_dir() {  # $1 = directory, $2 = optional kind filter
  local src="$1" out="$1/build" name
  rm -rf "$out"; mkdir -p "$out" "$src/pdf"   # lilypond-book does not track includes
  [ "$(basename "$src")" = editorial-principles ] && python3 "$ROOT/tools/principles_guide.py" "$out/principles-body.tex"
  export TEXINPUTS="$ROOT/house/latex//:$src//:"
  export TTFONTS="$ROOT/house/fonts/pressed//:"   # the pressed chant font, then the usual places
  for f in "$src"/*.lytex "$src"/*.tex; do
    [ -e "$f" ] || continue
    name="$(basename "${f%.*}")"
    case "$name" in text|*-text) continue;; esac
    [ -n "${2:-}" ] && [[ "$name" != *"-$2" ]] && continue
    if [[ "$f" == *.lytex ]]; then
      rm -f "$out/$name.syslog" "$out/$name.syslog2" "$out/$name.stretch.scm" "$out/$name.prskip"
      lily_book "$src" "$name" "$out/$name.syslog" ""
    else
      cp "$f" "$out/"
    fi
    latex_twice "$out" "$name"
    # Page fill (house-style §9): give each music page's spare height to the
    # staff gaps inside its systems, then build again. STRETCH=0 skips it.
    if [[ "$f" == *.lytex ]] && [ "${STRETCH:-1}" != 0 ] && \
       python3 "$ROOT/tools/stretch_systems.py" "$out/$name.prsys" "$out/$name.syslog" \
         "$( [[ "$name" == *-performance ]] && echo 19 || echo 17 )" "$out/$name.stretch.scm" "$out/$name.prskip"; then
      pages1=$(pdfinfo "$out/$name.pdf" | awk '/^Pages/{print $2}')
      cp "$out/$name.pdf" "$out/$name.pass1.pdf"
      snip=$(sed -n 's/.*\\input{\(.*\)-systems\.tex}.*/\1/p' "$out/$name.tex" | head -1)
      [ -n "$snip" ] && rm -f "$out/$snip"*      # else lilypond-book reuses the first pass
      lily_book "$src" "$name" "$out/$name.syslog2" "$out/$name.stretch.scm"
      latex_twice "$out" "$name"
      pages2=$(pdfinfo "$out/$name.pdf" | awk '/^Pages/{print $2}')
      if ! cmp -s <(sort "$out/$name.syslog") <(sort "$out/$name.syslog2"); then
        echo "  stretch: systems differ between passes; keeping the first pass"
        cp "$out/$name.pass1.pdf" "$out/$name.pdf"
      elif [ "$pages1" != "$pages2" ]; then
        echo "  stretch: $pages1 pages became $pages2; keeping the first pass"
        cp "$out/$name.pass1.pdf" "$out/$name.pdf"
      fi
    fi
    cp "$out/$name.pdf" "$src/pdf/"
    rm -f "$src"/tmp*.out "$src"/tmp*.pdf "$src"/tmp*.aux "$src"/tmp*.log "$src"/tmp*.prsys   # lilypond-book page probes
    echo "built ${src#$ROOT/}/pdf/$name.pdf ($(pdfinfo "$src/pdf/$name.pdf" | awk '/^Pages/{print $2}') pp.)"
    python3 "$ROOT/tools/check_pages.py" "$src/pdf/$name.pdf"
    # house finish: plate-and-paper texture, vector, text kept searchable
    # (tools/novello_vector.py). NOVELLO=0 tools/build.sh ... skips it for a quick look.
    if [ "${NOVELLO:-1}" != 0 ]; then
      cp "$src/pdf/$name.pdf" "$out/$name.plain.pdf"
      python3 "$ROOT/tools/novello_vector.py" "$out/$name.plain.pdf" "$src/pdf/$name.pdf" \
        || { echo "texture failed for $name"; exit 1; }
    fi
    for sys in "$out"/*/lily-*.pdf; do   # a system wider than the text block (170 mm = 482 pt) runs into the margin
      [ -e "$sys" ] || continue
      w=$(pdfinfo "$sys" | awk '/Page size/{print int($3)}')
      if [ "$w" -gt 490 ]; then echo "  system $(basename "$sys"): $w pt wide, over the 482 pt text block; reset this score's breaks"; fi
    done | sort -u
    style_check --pdfs "$src/pdf/$name.pdf"
  done
  style_check --sources "$src"
}
# Style and editorial checks (docs/style-checks.md) as warnings: a local build
# never fails on them; CI (.github/workflows/style.yml) gates on new errors.
style_check() {
  if python3 -c 'import pymupdf, yaml' 2>/dev/null; then
    (cd "$ROOT" && python3 -m tools.style check "$@" --fail-on never) | sed -n '/^== /,$p' | grep -v '^-- 0 error, 0 warn' || true
  fi
}
if [ $# -eq 0 ]; then
  for d in "$ROOT"/editions/*/ "$ROOT"/guides/*/; do [ -d "$d" ] && build_dir "${d%/}"; done
else
  d="$ROOT/editions/$1"; [ -d "$d" ] || d="$ROOT/guides/$1"
  build_dir "$d" "${2:-}"
fi
