# Style and editorial checks

`tools/style/` checks the editions against the house style (`house-style.md`) and the editorial principles (`editorial-principles.md`), with the decisions of 4 October 2026. Every check cites the rule it enforces. A rule that a program cannot judge is not checked; no check invents a house rule.

It sits beside the underlay analyser (`analyser.md`) and follows its conventions: one YAML file of metadata and one Python file of logic per check, flag and pass examples that the tests run, a baseline keyed by identity rather than line number, GitHub annotations and a Markdown job summary.

## Running it

Python 3.12 or later, with `tools/style/requirements.txt` (PyMuPDF, PyYAML; pytest for the tests). No TeX, LilyPond or poppler: the PDF checks read the committed PDFs.

```
python -m tools.style check                       # sources and committed PDFs
python -m tools.style check --sources             # sources only (under a second)
python -m tools.style check --pdfs editions/vox-in-rama
python -m tools.style check editions/nunc-scio-vere --info -v
python -m tools.style check --only S109,P208
python -m tools.style list                        # the checks, levels and rules
python -m pytest tools/style/tests -q
```

Paths may be files or directories. `--info` adds information-level findings, `-v` the rule and fingerprint of each. `--format text,markdown,github,json` and `--out DIR` choose the outputs. The exit status is 1 when there is an error not in the baseline (`--fail-on error`, the default); `--fail-on never` reports only.

`tools/build.sh` runs the PDF checks on each PDF it builds and the source checks on each edition, as warnings: a local build never fails on them. The CI job (`.github/workflows/style.yml`, on every pull request and on pushes to main) runs the tests, then every check, annotates new errors and warnings at their lines, writes the summary, and fails on a new error.

## Levels

- **error**: a rule that the source or the PDF either keeps or breaks. Fails CI unless the baseline holds it.
- **warn**: a heuristic, or a rule that needs judgement. Annotated, never failing.
- **info**: listed in the summary (the sign inventory).

## The checks

### Sources (S1xx)

Sources are the editions' `.lytex` and `.tex` files, `text.tex`, the music files (`music/*.ily`, `.ly`), the guides, the house files and `docs/editorial-principles.md` (printed as the principles guide). Comments are not read. Working material (`notes/`, `build/`) is not checked: principles 2.4 keeps it out of the editions.

| Check | Level | Rule | What it finds |
|---|---|---|---|
| S101 layout-in-content | error | house style 1 | layout commands in content files (`tools/lint.sh` in Python, with lines) |
| S102 no-bold | error | house style 3 | `\textbf`, `\bfseries`, LilyPond `\bold`, `font-series` bold |
| S103 house-colours | error | house style 5 | colour definitions and uses outside black, white and #9A1E1E (LaTeX and LilyPond) |
| S104 no-page-notes | error | house style 9 | `\pagenote`, and a `\musicnote` straight after a score |
| S105 restated-rules | warn | principles 13.4 | a method sentence that shares five words of wording with a rule, or states one with always/never/must, and cites no rule in its paragraph |
| S106 performance-names | warn | principles 13.5 | sigla, ensembles, labels, recordings and "as X does" in a performance edition |
| S107 sign-macros | error | principles 8; house style 9; decision 8 | raw markup in the music where the house has a sign: dashed ties (`\divTie`), italic lyrics (`\rep`, `\edText`), `suggestAccidentals` (`\fi`), corner brackets (`\colStart`), `[c.f.]` (`\cf`), bracketed or small noteheads (`\sup`, `\ed`), bracketed accidentals, `\parenthesize` without `\sugg` |
| S108 sign-forms | error | decisions of 4 Oct (accidentals; 9) | optional accidentals drawn in round brackets in the house file (square from now on; round brackets are for cautionaries); angle brackets other than ⟨ ⟩ for text written out from *ij* |
| S109 latin-division | error | decision 2 | Latin lyrics divided against carry-over (*om-ni* for *o-mni*, *Chris-tus*, *pat-ris*); compounds divide at the prefix (*ex-spe-cta-ti-o*) |
| S110 note-form | error | house style 10, 11 | critical notes not in the form bar \| voice \| note: hyphens in ranges, voice names written out |
| S111 emendation-cause | warn | decision 6; principles 8 | an "Emended." note that does not say how the error arose |
| S112 note-tense | warn | decision 11 | a lost source in the present tense, an extant one in the past |
| S113 shelfmark | warn | decision 7 | a source in the Sources list without a shelfmark |
| S114 british-spelling | warn | house style 11 | American spellings (-ize, -or, -er and a list) in prose |
| S115 no-em-dash | error | house style 11 | em dashes |
| S116 terms | warn | house style 11 | the "Not" column of the terms table (copy text, half note, lyrics, original pitch, Commentary as a heading ...) |
| S117 quotation-marks | warn | house style 11 | double quotation marks outside a single-quoted quotation |
| S118 names | error | principles 14.1, 14.3 | Derdun, Zielenski and other names without their diacritics; a Latin form in `\composer` |
| S119 series-rules-line | error | principles 13.4 | an Editorial method section that does not open with `\seriesrules` |
| S120 voice | warn | principles 15.4; house style 11 | editorial "we" and "our" |
| S121 range-dash | warn | house style 11 | hyphens in number ranges |
| S122 quotation-translation | warn | principles 11.7 | a foreign-language quotation without ‘…’ (‘…’) after it |
| S123 no-ipa | warn | house style 10 | IPA in pronunciation notes |
| S124 working-material | error | principles 2.4, 13.3 | TODO, FIXME, [check], ?? in printed text |
| S125 sign-inventory | info | decision 8; principles 8 | which house signs each music file uses, and how often |

### Committed PDFs (P2xx)

| Check | Level | Rule | What it finds |
|---|---|---|---|
| P201 pdf-colours | error | house style 5, 5a | text or drawing colours outside black, white and #9A1E1E (raster facsimiles are not judged) |
| P202 red-music | error | house style 5 | music-font glyphs in red |
| P203 fonts-embedded | error | house style 3, 5a | a font that is not embedded |
| P204 pressed-fonts | error | house style 3, 5a | a font other than Junicode Pressed, the pressed Emmentaler (`Pressed-NN`) and pressed chant, apart from the two the house style names as not yet pressed (TeX Gyre Pagella, LM Mono) |
| P205 bold-fonts | error | house style 3 | bold fonts; Junicode Medium counts, as the class maps bold to it |
| P206 page-fill | warn | house style 7 | `tools/check_pages.py` on the committed PDF: a short music page before another, ink in the bottom margin, a last page with only the foot line |
| P207 system-width | error | house style 2 | staff lines outside the 170 mm text block |
| P208 system-gap | error | decision of 4 Oct (Gould 488) | a gap between systems not larger than the widest staff gap in either neighbouring system |
| P209 extender-clearance | error | decision of 4 Oct (Grier 167) | a lyric extender one staff space or less below its staff |
| P210 page-turns | warn | decision of 4 Oct (Grier 176) | a turn (odd page to the next) in a performance score where a voice sings on |
| P211 searchable-text | error | house style 5a | a page with marks but no text layer; text that does not map to Unicode |
| P212 page-size | error | house style 2 | a page that is not A4 |

### How the PDF checks measure

The house finish merges every drawn mark of a page into one path, so the staff lines are read from a 200 dpi greyscale rendering (`tools/style/pdf.py`): five equally spaced long dark rows make a staff, and the staff space is their spacing. Two staves belong to one system when a solid vertical line joins them (the systemic bar line, the bracket, or a section bar line; the dashed Mensurstriche are too broken to count). Gaps are measured line to line, in staff spaces, as in the Gould reading notes. An extender is a thin dark run at least 2.5 spaces long under a staff, carrying no notehead and not stacked one space from a run of the same length (a ledger line). Chant staves have four lines and are not measured.

Page turns: the polyphonic systems on each page are counted and mapped to bars through the edition's `prBreaksPerformance` lists (`music/engraving.ily`) and the end of each score block; the MusicXML says whether each voice rests or a section ends there. If the counts do not agree, P210 says nothing rather than guess.

## Per-edition facts

`tools/style/editions.py` reads each critical edition's Sources: a siglum is a source unless its list is introduced as collated editions or recordings, and it is lost when its entry says lost, destroyed or "no copy known". `tools/style/editions.yaml` corrects what that reading gets wrong (Vox's N and M, Nunc's P are modern editions). The language of each edition comes from `tools/analyser/editions.yaml`, shared with the analyser.

## Accepting a finding

The baseline, `tools/style/baseline.json`, lists findings by fingerprint: check, file, key and occurrence. The key is the offending word, siglum, font, critical-note position or page, never a line number, so editing elsewhere in a file reopens nothing. (PDF findings are keyed by page; a rebuild that moves the music reopens them, which is what a rebuild should do.) Each entry has a status and a reason:

- `accepted`: the editor keeps it, for the reason given.
- `pending`: present when the checks were introduced (4 October 2026) and not yet decided. Pending findings are listed in the summary but do not fail CI.

To accept a finding, find its fingerprint (`-v`, or `--format json`), set `status` to `accepted` and write the reason. `python -m tools.style check --update-baseline` adds every current error and warning not yet listed as pending, keeps the reasons already written, and drops entries whose finding has gone (the summary lists those). Review its diff like code. Findings that are being fixed are better left out of the baseline, so that CI shows them until the fix lands.

## Adding a check

1. Choose an ID: S1xx for sources, P2xx for PDFs.
2. Write `tools/style/checks/<ID>-<name>.yaml`: `id`, `name`, `kind` (source or pdf), `level`, `rule` (the principle, house-style section or decision), `authority` (its wording, with the book and page where there is one), `message` (a format string over the values the check returns), `applies` (roles: critical, performance, text, music, guide, house; or PDF kinds), `heuristic: true` where it guesses, and `examples` with at least one `flag` and one `pass`. Source examples give `path` and `text` (and `meta` where the check needs per-edition facts); PDF examples name a builder in `tools/style/pdf_fixtures.py`.
3. Write `tools/style/checks/<ID>_<name>.py` with `check(doc)` or `check(pdf)`, yielding `Hit(key=..., offset=... | page=..., values=...)`. Choose a key that survives unrelated edits.
4. Run `python -m pytest tools/style/tests -q`, then the check on the repository, and add the current findings to the baseline only if they are not about to be fixed.
