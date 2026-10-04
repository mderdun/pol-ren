#!/usr/bin/env bash
# Fetch the pinned release of Junicode into house/fonts/junicode (not committed).
# The class and the LilyPond setup use these files when present, so every build
# sets type with the same version. Bump JUNICODE to update.
set -euo pipefail
JUNICODE=2.226
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
dest="$ROOT/house/fonts/junicode"
if [ -f "$dest/VERSION" ] && [ "$(cat "$dest/VERSION")" = "$JUNICODE" ]; then exit 0; fi
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
curl -sSL -o "$tmp/j.zip" "https://github.com/psb1558/junicode-font/releases/download/v$JUNICODE/Junicode_$JUNICODE.zip"
unzip -q "$tmp/j.zip" -d "$tmp"
mkdir -p "$dest"
for s in Regular Italic Medium MediumItalic Bold BoldItalic Exp ExpItalic; do cp "$tmp/Junicode/OTF/Junicode-$s.otf" "$dest/"; done
cp "$tmp/Junicode/OFL.txt" "$dest/"
echo "$JUNICODE" > "$dest/VERSION"
echo "Junicode $JUNICODE in house/fonts/junicode"
