# Polish Early Music

Critical and performance editions of early Polish music, edited by Mikołaj Derduń. Free to copy, perform, record and adapt under CC BY 4.0.

| No. | Piece | Composer | Status |
|---|---|---|---|
| 1 | *Bogurodzica* | anonymous, 13th–14th c. | first edition (2026), awaiting reset |
| 2 | *Nunc scio vere* | Wacław z Szamotuł | first edition (2026), awaiting reset |
| 3 | *Modlitwa gdy dziatki spać idą* (*Już się zmierzka*) | Wacław z Szamotuł | house-style mock |

**Guide**: *Singing Polish and Polish Latin*, a pronunciation guide for the whole series (`guides/pronunciation`).
| 4 | *Plaude euge theotocos* | Piotr z Grudziądza | first edition (2026), awaiting reset |
| 5 | *Vox in Rama* | Mikołaj Zieleński | first edition (2026), awaiting reset |

Each piece is published twice. The **critical edition** gives the sources, the editorial method, the text with a diplomatic transcription and translation, the score and the critical notes. The **performance edition** has the same score with only what singers need around it.

## Layout

```
docs/editorial-principles.md   the editorial rules
docs/house-style.md            design and language
house/latex/pol-ren.cls        all page design (LuaLaTeX)
house/lilypond/pol-ren.ily     all engraving style and the score builder (LilyPond 2.24)
editions/<piece>/              content only: text, music data, built PDFs (pdf/)
guides/<guide>/                series guides
archive/2026-10-first-editions the first editions as delivered, before the reset
tracker/issues.json            source gaps and work items (synced to Issues)
tools/build.sh                 build script
```

## Building

Needs LilyPond 2.24 (with `lilypond-book`), TeX Live with LuaLaTeX, `gregoriotex` and `polyglossia`, Junicode 2 and TeX Gyre Pagella.

```
make                                       # every edition and guide
make juz-sie-zmierzka                      # one
tools/build.sh juz-sie-zmierzka critical   # one kind
make lint                                  # check content files hold no layout
```

Design lives only in `house/`. Edition files hold content; `tools/lint.sh` rejects layout commands in them, and every build runs it. Change the house files, run `make`, and every edition is reset to the new design. LaTeX sets every page; LilyPond and Gregorio only engrave the music, and `lilypond-book` hands LaTeX one graphic per system so page breaks fall between systems.

## Corrections and gaps

Known gaps in the sources are open issues labelled *source gap*. `tracker/issues.json` is the source of truth for the tracker: a GitHub Action creates, updates and closes issues to match it. Corrections are welcome as issues. A correction that changes a reading makes a new edition; typographic fixes do not.

## Licence

Editions, scores and their sources: [CC BY 4.0](LICENSE). Credit "ed. Mikołaj Derduń, Polish Early Music". Build code: [MIT](LICENSE-CODE). The music is in the public domain.
