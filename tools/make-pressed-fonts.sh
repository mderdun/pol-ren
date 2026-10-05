#!/usr/bin/env bash
# Make the pressed fonts into house/fonts/pressed (not committed):
#   Junicode Pressed (every style the class and LilyPond use), from the pinned
#     Junicode in house/fonts/junicode. SIL Open Font License 1.1: a modified
#     version under a new name, same licence (OFL.txt copied alongside).
#   pressed-NN.otf, LilyPond's Emmentaler music font at each design size, used
#     with fonts.music = "pressed". GPL with the font exception (unchanged).
#   pressedchant.ttf, Gregorio's greciliae chant font. SIL OFL 1.1 with the
#     Reserved Font Names "Greciliae" and "Caeciliae", hence the new name.
# The outlines get the same ink-on-paper treatment as drawn marks
# (tools/texture_font.py, tools/novello_vector.py). Remade only when an input
# changes: the Junicode version, the LilyPond version or the two scripts.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
src="$ROOT/house/fonts/junicode" dest="$ROOT/house/fonts/pressed"
lily="$(lilypond --version | awk 'NR==1{print $3}')"
emm="$(dirname "$(ls /usr/share/lilypond/"$lily"/fonts/otf/emmentaler-20.otf \
  /usr/local/share/lilypond/"$lily"/fonts/otf/emmentaler-20.otf 2>/dev/null | head -1)")"
stamp="junicode $(cat "$src/VERSION") lilypond $lily gregorio $(kpsewhich greciliae.ttf 2>/dev/null | sha1sum | cut -c1-8) $(cat "$ROOT/tools/texture_font.py" "$ROOT/tools/novello_vector.py" | sha1sum | cut -c1-12)"
if [ -f "$dest/STAMP" ] && [ "$(cat "$dest/STAMP")" = "$stamp" ]; then exit 0; fi
echo "making pressed fonts (a few minutes, once)"
rm -rf "$dest"; mkdir -p "$dest"
jobs=()
for s in Regular Italic Medium MediumItalic Exp ExpItalic Bold BoldItalic; do
  jobs+=("python3 '$ROOT/tools/texture_font.py' '$src/Junicode-$s.otf' '$dest/JunicodePressed-$s.otf'")
done
chant="$(kpsewhich greciliae.ttf || true)"
if [ -n "$chant" ]; then   # Gregorio's chant font (and its hollow and hole forms); OFL with reserved names, so a new name
  for v in "" -hollow -hole; do
    jobs+=("python3 '$ROOT/tools/texture_font.py' '${chant%.ttf}$v.ttf' '$dest/pressedchant$v.ttf' --size 20 --family pressedchant --rename greciliae")
  done
fi
for n in 11 13 14 16 18 20 23 26; do
  jobs+=("python3 '$ROOT/tools/texture_font.py' '$emm/emmentaler-$n.otf' '$dest/pressed-$n.otf' --size $n --family Pressed")
done
printf '%s\n' "${jobs[@]}" | xargs -P "$(nproc)" -I{} sh -c '{} >/dev/null'
cp "$src/OFL.txt" "$dest/OFL.txt"
echo "$stamp" > "$dest/STAMP"
echo "pressed fonts in house/fonts/pressed"
