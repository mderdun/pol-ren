# Polish Early Music

Critical and performance editions of early Polish music, edited by Mikołaj Derduń. Free to copy, perform, record and adapt under CC BY 4.0.

| No. | Piece | Composer | Status |
|---|---|---|---|
| 1 | *Bogurodzica* | anonymous, 13th–14th c. | first edition (2026), awaiting reset |
| 2 | *Nunc scio vere* | Wacław z Szamotuł | first edition (2026), awaiting reset |
| 3 | *Modlitwa gdy dziatki spać idą* (*Już się zmierzka*) | Wacław z Szamotuł | house-style mock |
| 4 | *Plaude euge theotocos* | Piotr z Grudziądza | first edition (2026), awaiting reset |
| 5 | *Vox in Rama* | Mikołaj Zieleński | first edition (2026), awaiting reset |

Each piece is published twice. The **critical edition** gives the sources, the editorial method, the text with a diplomatic transcription and translation, the score and the critical notes. The **performance edition** has the same score with only what singers need around it.

## Layout

```
docs/editorial-principles.md   the editorial rules
docs/house-style.md            design and language
house/latex/pol-ren.cls        page design (LuaLaTeX)
house/lilypond/pol-ren.ily     engraving style (LilyPond 2.24)
editions/<piece>/              sources, music, built PDFs (pdf/)
archive/2026-10-first-editions the first editions as delivered, before the reset
tracker/issues.json            source gaps and work items (synced to Issues)
tools/build.sh                 build script
```

## Building

Needs LilyPond 2.24 (with `lilypond-book`), TeX Live with LuaLaTeX, `gregoriotex` and `polyglossia`, Junicode 2 and TeX Gyre Pagella.

```
tools/build.sh juz-sie-zmierzka            # both editions
tools/build.sh juz-sie-zmierzka critical   # one
```

LaTeX sets every page. LilyPond and Gregorio only engrave the music; `lilypond-book` hands LaTeX one graphic per system so page breaks fall between systems.

## Corrections and gaps

Known gaps in the sources are open issues labelled *source gap*. Corrections are welcome as issues. A correction that changes a reading makes a new edition; typographic fixes do not.

## Licence

Editions, scores and their sources: [CC BY 4.0](LICENSE). Credit "ed. Mikołaj Derduń, Polish Early Music". Build code: [MIT](LICENSE-CODE). The music is in the public domain.
