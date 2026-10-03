#!/usr/bin/env bash
# Edition and guide files hold content only; all design lives in house/.
# Flags layout primitives in editions/ and guides/. Exit 1 if any are found.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
pat='\\(v|h)space|\\fontsize|\\setlength|\\geometry|\\linespread|\\(small|large|Large|footnotesize|normalsize)\b|\\color|\\textcolor|staffsize=|\\override|\\paper|set-global-staff-size|\\layout *\{ *[^} ]|#\(set-'
hits=$(grep -rnE "$pat" "$ROOT/editions" "$ROOT/guides" --include='*.lytex' --include='*.tex' --include='*.ly' --include='*.ily' 2>/dev/null | grep -v '/build/')
if [ -n "$hits" ]; then
  echo "Layout in content files (move it to house/):"; echo "$hits"; exit 1
fi
echo "lint: content files clean"
