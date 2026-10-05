#!/usr/bin/env bash
# Rebuild only what changed: an edition or guide is rebuilt when any of its own
# source files is newer than its oldest PDF; everything is rebuilt when a shared
# input (house/, the build and texture tools, the pressed fonts) is newer.
#   make changed          rebuild what is out of date
#   make changed DRY=1    list it without building
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
shared=(house/latex house/lilypond house/fonts/pressed/STAMP tools/build.sh tools/novello_vector.py
        tools/stretch_systems.py tools/check_pages.py tools/principles_guide.py)
todo=()
for d in editions/*/ guides/*/; do
  d="${d%/}"; [ -d "$d/pdf" ] || { todo+=("$d"); continue; }
  oldest="$(ls -tr "$d"/pdf/*.pdf 2>/dev/null | head -1)"
  [ -n "$oldest" ] || { todo+=("$d"); continue; }
  # the principles guide is built from docs/editorial-principles.md
  extra=(); [ "$(basename "$d")" = editorial-principles ] && extra=(docs/editorial-principles.md)
  if [ -n "$(find "$d" "${shared[@]}" "${extra[@]}" -type f -newer "$oldest" \
        -not -path "*/pdf/*" -not -path "*/build/*" -not -name "*.musicxml" -not -name "*.srcmap.tsv" -not -name "tmp*" \
        -print -quit 2>/dev/null)" ]; then
    todo+=("$d")
  fi
done
if [ ${#todo[@]} -eq 0 ]; then echo "everything is up to date"; exit 0; fi
printf 'out of date: %s\n' "${todo[@]##*/}"
[ "${DRY:-0}" = 1 ] && exit 0
for d in "${todo[@]}"; do tools/build.sh "$(basename "$d")"; done
