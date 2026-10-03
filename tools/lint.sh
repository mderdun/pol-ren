#!/usr/bin/env bash
# Edition and guide files hold content only; all design lives in house/.
# Flags layout primitives in editions/ and guides/. Exit 1 if any are found.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
pat='\\(v|h)space|\\fontsize|\\setlength|\\geometry|\\linespread|\\(small|large|Large|footnotesize|normalsize)\b|\\color|\\textcolor|staffsize=|\\override|\\paper|set-global-staff-size|\\layout *\{ *[^} ]|#\(set-'
# music/engraving.ily may adjust breaks and spacing for its own score, but
# not type, colour or staff size.
eng='\\fontsize|\\color|\\textcolor|staffsize=|set-global-staff-size|font-(name|family|size)|color'
hits=$( { grep -rnE "$pat" "$ROOT/editions" "$ROOT/guides" --include='*.lytex' --include='*.tex' --include='*.ly' --include='*.ily' 2>/dev/null | grep -v '/build/' | grep -v '/music/engraving.ily:' | grep -v 'layout { $(pr-layout) }';
          grep -rnE "$eng" "$ROOT"/editions/*/music/engraving.ily 2>/dev/null; } )
if [ -n "$hits" ]; then
  echo "Layout in content files (move it to house/):"; echo "$hits"; exit 1
fi
echo "lint: content files clean"
