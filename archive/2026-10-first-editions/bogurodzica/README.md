# Bogurodzica: stanzas 1-2, after Kraków, Biblioteka Jagiellońska, MS 1619

Three editions in GregorioTeX.

- `bogurodzica-critical.tex`: critical edition (score, text, sources, musical and textual apparatus, notes, commentary).
- `bogurodzica-performance.tex`: performance edition (score, pronunciation, translation, performance notes).
- `bogurodzica-edition.tex`: working edition, with research notes and open questions.
- `bogurodzica.gabc`: score for the critical and working editions.
- `bogurodzica-performance.gabc`: the same melody with a shorter header.
- `pdf/`: built PDFs.

## Build

Needs LuaLaTeX, GregorioTeX 6 and the Junicode font. The `.tex` files load Junicode from
`/usr/share/fonts/opentype/junicode/`; edit the `\setmainfont` path if yours is elsewhere.

    make
