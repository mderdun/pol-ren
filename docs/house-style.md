# House style

How the Polish Early Music editions look and read. The editorial rules are in `editorial-principles.md`; this file covers design and language.

The model is the sixteenth-century partbook, read with modern eyes: black and red, one good typeface, clear margins, decoration only where a printer of 1550 would have put it, and nothing a singer has to decode. Ornament marks structure (a new part, a title, a rubric). It never carries information.

## 1. One place for design

Every design decision lives in two files:

- `house/latex/pol-ren.cls`: pages, type, colour, headings, title pages, tables, stanza layout, sigla, running heads.
- `house/lilypond/pol-ren.ily`: engraving, staff size, Mensurstriche, editorial signs, the score builder (`\prScore`, `\prStaff`) and performance transposition.

LaTeX (LuaLaTeX) sets every page. LilyPond, through `lilypond-book`, and Gregorio only engrave music into it. `lilypond-book` hands LaTeX one graphic per system, so LaTeX breaks pages between systems and headings, stanzas and notes around a score obey the same rules as the prose. A chant edition and a polyphonic one share one design.

**Style is central; engraving is per score.** Type, colour, sizes, signs, page design and every visual default are set once in the house files. How a particular score falls on the page cannot be automated well, so each edition makes those decisions itself, in two places:

- `music/engraving.ily`: system breaks for each kind of edition (`prBreaksCritical`, `prBreaksPerformance`, as bar numbers after which a system ends), and spacing that only this score needs (`prLayoutCritical`, `prLayoutPerformance`). Break at the ends of verse lines or sections where the music allows.
- the edition file: page breaks between systems (`\scorepagebreaks{3}`), and the number of stanza columns where the default two would push the stanzas off the last page of music (`\begin{stanzas}[3]`).

Everything else in an edition is content: text, sigla, notes, the music data, and the choice of pitch for a transposed performance edition. `tools/lint.sh` rejects layout commands elsewhere; `engraving.ily` may adjust breaks and spacing but not type, colour or staff size. To change the style, edit the two house files and run `make`; every edition and guide is rebuilt, and each keeps its own breaks. Check the page breaks by eye after any style change that alters sizes.

## 2. Page

One page for every single edition and guide, critical or performance: A4, symmetric margins (20 mm sides, 17 mm top, 23 mm bottom), text block 170 × 257 mm. Running heads alternate: composer on even pages, piece on odd, folio outside. These documents are short and printed loose, so they do not get book margins.

| | Critical, guide | Performance |
|---|---|---|
| Body | 11 pt, leading 1.13 (the long measure needs it) | 11 pt, leading 1.06 |
| Staff size | 17 | 19 |
| Gregorio staff | 18 | 21 |

**Anthologies** (option `anthology`) get book margins (inner 24, top 24, outer 36, bottom 37 mm) and open each part on a recto, with an ornament on any blank verso.

## 3. Type

**Junicode 2** throughout, music text included. Accidentals in prose (♭ ♮ ♯) come from TeX Gyre Pagella, since Junicode has none.

| Element | Setting |
|---|---|
| Body | Junicode Regular 11 pt, old-style figures, justified, microtype |
| Italic | Translations, titles of works, foreign words in English prose, editorial text, run-in subheads |
| Small capitals | Section heads, running heads (composer), voice names and abbreviations, verdicts, column heads. Letter-spaced when standing alone |
| Expanded capitals | Composer's name on a title page only (Junicode Exp) |
| Bold | Not used. Emphasis is italic; labels are small capitals |
| Figures | Old-style in prose; lining in apparatus columns and folios |

## 4. Sigla

A siglum of a source or edition is set in small capitals inside a thin ring (one letter) or a rounded frame (several letters). The frame says "this is a source", so a source A never reads as the word "a" or as the Altus. Voice abbreviations (C, A, T, B) stay plain small capitals.

## 5. Colour

Black, white and one red; no other colour, grey included: **#9A1E1E**, a rubricator's red.

Red is used for: the series line, the fleuron that opens a part, the drop initial of the first section, stanza numbers, liturgical rubrics over a score, the chant initial and annotation, the thin rule of the title-page frame.

Red is never used for notes, accidentals, editorial signs, sigla, or anything a reader needs. A black-and-white photocopy must lose nothing.

## 5a. Finish

Every PDF is printed through a plate-and-paper finish at strength 1.5 on a white page: each mark gains a little ink, its corners round, its edge wanders with a fine paper-fibre field, and solid heads get the odd pore. It stays vector, in black and the one red. The texture is generated from a fixed seed, so a rebuild prints the same page. It is the series' look; it carries no information.

Type and music glyphs carry the finish in their own outlines: the build sets words in Junicode Pressed, the music in a pressed Emmentaler and chant in a pressed greciliae (`tools/make-pressed-fonts.sh`, made once into `house/fonts/pressed` and remade when Junicode, LilyPond, Gregorio or the treatment changes). The text stays live and searchable. Drawn marks (staff lines, stems, beams, bar lines, slurs, rules) are treated on the page by `tools/novello_vector.py`. Licences: Junicode and greciliae are under the SIL Open Font License, so the pressed copies take new names (greciliae's name is reserved) and keep the licence; Emmentaler is GPL with the font-embedding exception. The colophon credits Junicode. Not yet pressed: the prose accidentals (TeX Gyre Pagella) and the monospaced repository address. `NOVELLO=0 make` gives the plain PDF, in the original fonts, for proofing.

## 6. Ornament

| Mark | Glyph | Where |
|---|---|---|
| Fleuron | ❦ red | Opens each part of a critical edition (Text, Critical notes); title page |
| Leaf | ❧ red | Centre of a blank verso (anthologies) |
| Middle dot | · red | Separator in the series line |
| Thick-and-thin rule | 1.1 pt black and 0.35 pt red | Top and bottom of a title page |
| Initial | 3-line red drop capital | First word of the first section only; the rest of the word in small capitals |

Nothing else. No borders around music, no tinted boxes, no icons.

## 7. Headings and breaks

- **Section head**: centred spaced small capitals. **Subhead**: italic, run into the paragraph, closed with a full stop.
- **A heading never ends a page.** Every head reserves room for several lines after it, or moves to the next page. (Editor's rule.)
- No widows or orphans. Paragraphs indent 1.2 em, except after a heading. No space between paragraphs.
- **Critical edition**: the title page stands alone; its verso carries the contents (generated from the section heads) and the colophon. Text, Score and Critical notes each start a new page.
- **Performance edition**: no blank pages, and no short or crowded music pages. Aim for the music and its stanzas to fill whole pages, with the stanzas on the last page of music; set system and page breaks per score to get there. Blocks that should not split (the stanzas after a score, the rehearsal notes with their heading) are kept whole.
- A repeated section starts and ends on its own system.

## 8. The two editions

**Critical.** Title page between thick-and-thin rules: series and number, composer, title, subtitle, fleuron, forces, poet, "Critical edition", source line, editor, edition and year. Verso: contents and colophon with licence. Then the preface sections, text, score with its own heading, critical notes and literature.

**Performance.** No title page. A masthead at the top of page 1: series and "Performance edition", title, subtitle, poet left and composer right, and one italic line if the score is transposed. No context before the music: setting the scene belongs to the director and to the rehearsal notes. The score starts on page 1, with the stanzas after it. Then Text and translation and the For rehearsal notes in two columns, with a one-line colophon at the foot.

**Guide.** As a critical edition without music: title page, contents and colophon, then prose and tables.

**Titles and subtitles** follow the rule in `editorial-principles.md` §14: title from the source; subtitle the incipit, or the liturgical designation if the title is the incipit; scoring in the forces line.

## 9. Score

- Voice names in small capitals, abbreviated after the first system (C. A. T. B.).
- Incipit with original clef, sign and first note (omitted in a transposed performance edition); then the modern clef and the ambitus; then the mensuration sign.
- **Mensurstriche** as dashed lines between the staves, so the parts read first and the bar lines are there for whoever wants them. Section, repeat and final bar lines are solid.
- Bar numbers in small italic at the start of each system only.
- **No notes on the music page.** Tried in *Vox in Rama* (Oct 2026) and dropped: a sign the score already marks as editorial (small, in brackets) needs no gloss on the page, and anything more belongs in the rehearsal notes. (Editor's rule.)
- Editorial accidentals small, above the note; optional ones in brackets (`\optFlat` lowers, `\optSharp` raises, `\optNatural` cancels). The printed sign is worked out after transposition, so a raised b♭ in a performance edition shows a natural.
- Ties are solid. A dashed tie means a source note divided to carry text (`\divTie`) and nothing else.
- Editorial underlay in italics: `\edText` for a whole line, `\rep` for one syllable.
- Rubrics red italic, left-aligned over the system.
- In the critical edition the score has its own heading: title, subtitle, poet left, composer right.
- **Stanzas after the score**: centred, two abreast, the widest stanza setting both column widths. An odd last stanza is centred below. Red stanza numbers hang in the left margin of each stanza.

## 10. Tables and lists

- No vertical rules. One rule under the column heads. Column heads in spaced small capitals.
- **Variants** (chant and texts): three columns, loc. | lemma | readings (`variants`, `\cl`).
- **Critical notes**: three columns, bar | voice | note. Bar numbers in lining figures; voices as plain small capitals; sigla framed. Pitches in Helmholtz notation, c′ = middle C, roman. A note ends with its verdict in small capitals where a reading is weighed.
- **Sources**: siglum in a hanging column; base text marked *Base text*.
- **Literature**: author first, hanging indent; grouped only when the list is long.
- **Text and translation**: two columns (text, italic translation) or, in the critical edition, three (diplomatic, transcription, translation). Red stanza numbers.
- **Pronunciation**: in the series guide, as tables (spelling | sound | example; for Latin, spelling | Polish Latin | Roman | example). Sounds are described by comparison with familiar words, stress by capitals (po-PROŚ-my). No IPA.

## 11. Language

The prose is academic in what it claims and plain in how it says it. Argue from first principles, the sources and the counterpoint; for performers, from what happens in rehearsal.

**Voice and register**

- Short declarative sentences. One idea per sentence. Active voice; name who did it ("Perz joins the notes", not "the notes are joined").
- "I" for the editor's judgements and readings ("I take b natural here"; "the parallel is my own reading"). Impersonal wording for method ("Bar lines run between the staves").
- State a reading, then the reason. No hedging stacks. "Probably" once, where it is true.
- No puffery or mood words: not "beautiful", "haunting", "pivotal". Describe the music: its range, its cadences, what the Tenor does.
- No em dashes. Commas and full stops; parentheses only for references and glosses. Colons only before a list or a quotation.
- Every claim verified or cut. Unverified material goes to the issue tracker, not into the edition.
- The performance edition speaks to singers and directors: what to sing, how fast, what the signs mean, what the words say, and enough about the piece to rehearse it with understanding. Nothing about how the edition was made beyond one line. Reasons are given in general terms ("as an organ would have done"), never by naming an ensemble, a recording or another edition; those citations belong in the critical edition.

**Terms** (use these, not their synonyms)

| Use | Not |
|---|---|
| source, witness | original, document |
| base text | copy text |
| critical notes | commentary, apparatus (in headings) |
| editorial | ed., added |
| semibreve, minim, semiminim, fusa, breve, long | whole note, half note |
| Mensurstriche | bar lines (when the distinction matters) |
| cadence, clausula | resolution |
| underlay | text setting, lyrics |
| written pitch | original pitch |
| Cantus, Altus, Tenor, Bassus | soprano, alto (except about modern choirs) |

**Conventions**

- British spelling (-ise). Dates "c. 1550–1556", "fl. 1604–1611", "after 1452". En dash in ranges.
- Single curly quotation marks, double inside. Quotations in their own language, roman, in quotation marks, always followed by an English translation in parentheses: ‘dziękujem Tobie’ (‘we thank you’). Block quotations: the translation follows inside the block (`\translation{...}`).
- Titles of works in italic; Polish and Latin titles in the source's form.
- References in prose: "bar 29, Altus". In critical notes: "29 | A".
- Polish names with their diacritics, always.
- Every edition's prose gets an unslop pass before release. (Editor's rule.)
- Never restate a series rule in an edition. Cite it by number ("as the series rules require (principles 10.1)") and spend the words on what is particular to the piece. The rules are in the series guide *Editorial principles*. (Editor's rule.)
