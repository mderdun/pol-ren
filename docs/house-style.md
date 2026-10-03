# House style

How the Polish Early Music editions look and read. The editorial rules are in `editorial-principles.md`; this file covers design and language.

The model is the sixteenth-century partbook, read with modern eyes: black and red, one good typeface, generous margins, decoration only where a printer of 1550 would have put it, and nothing a singer has to decode. Ornament marks structure (a new part, a title, a rubric). It never carries information.

## 1. One page-maker

LaTeX (LuaLaTeX, class `house/latex/pol-ren.cls`) sets every page of every edition: titles, prose, tables, running heads, page breaks. LilyPond and Gregorio only engrave music.

- **Polyphony.** `lilypond-book` turns each `\lilypondfile` into one graphic per system. LaTeX places the systems and breaks pages between them, so headings, stanzas and notes around a score obey the same rules as the prose.
- **Chant.** `gregoriotex` sets chant directly inside the same class.
- **Shared style.** `house/lilypond/pol-ren.ily` holds every engraving decision. An edition's `score.ly` includes it and sets nothing about type or page.

This is what lets a Gregorio edition and a LilyPond edition share one design.

## 2. Page

| | Critical | Performance |
|---|---|---|
| Paper | A4, two-sided | A4, one-sided |
| Margins | inner 24, top 24, outer 36, bottom 37 mm | 18, 16, 18, 20 mm |
| Text block | 150 × 236 mm | 174 × 261 mm |
| Body | 11/14.4 pt | 11/14 pt |
| Staff size | 17 | 19 |
| Gregorio staff | 18 | 21 |

The critical page follows book proportions (inner < top < outer < bottom). The performance page gives the music room and keeps a margin to hold.

## 3. Type

**Junicode 2** throughout, music text included. It was chosen for *Bogurodzica* because it covers Old Polish and medieval Latin (ł ę ą ǫ ſ ē), and kept for the series.

| Element | Setting |
|---|---|
| Body | Junicode Regular 11 pt, old-style figures, justified, microtype |
| Italic | Translations, titles of works, foreign words in English prose, editorial text, run-in subheads |
| Small capitals | Section heads, running heads, sigla, voice names, verdicts, column heads. Letter-spaced 9% when standing alone |
| Expanded capitals | Composer's name on the title page only (Junicode Exp) |
| Bold | Not used. Emphasis is italic; labels are small capitals |
| Figures | Old-style in prose; lining tabular in apparatus columns and folios |
| Lyrics | Junicode, about 10.5 pt at staff 17 |
| Accidentals in prose | ♭ ♮ ♯ from TeX Gyre Pagella (Junicode has none) |

## 4. Colour

Black, and one red: **#9A1E1E**, a rubricator's red.

Red is used for: the series line, the fleuron that opens a part, the initial letter of the introduction, stanza numbers, liturgical rubrics in a score (*Antiphona*, *Psalmus*), the chant initial and annotation, the thin rule of the title-page frame.

Red is never used for: notes, accidentals, editorial signs, sigla, anything a reader needs. A black-and-white photocopy must lose nothing.

At most a few red marks per spread.

## 5. Ornament

| Mark | Glyph | Where |
|---|---|---|
| Fleuron | ❦ red | Opens each part of the critical edition (Text, Score, Critical notes); title page |
| Leaf | ❧ red | Centre of a blank verso |
| Middle dot | · red | Separator in running heads and edition lines |
| Thick-and-thin rule | 1.1 pt black + 0.35 pt red | Top and bottom of the critical title page |
| Initial | 3-line red drop capital | First word of the Introduction only; the rest of the word in small capitals |

Nothing else. No borders around music, no tinted boxes, no icons.

## 6. Headings and breaks

- **Section head**: centred spaced small capitals, 2.1 lines above, 0.9 below.
- **Subhead**: italic, run into the paragraph, closed with a full stop.
- **Part opening** (critical only): new recto, red fleuron, section head.
- **A heading never ends a page.** Every head reserves room for at least three lines after it; otherwise it moves to the next page. (Editor's rule.)
- No widows or orphans. Paragraphs indent 1.2 em, except after a heading. No space between paragraphs.
- **Critical edition** may break generously: the title page stands alone, and Text, Score and Critical notes each begin on a recto. A blank verso carries the leaf ornament.
- **Performance edition** has no blank pages. Page turns fall at the end of a section or stanza, or in a rest of at least a breve in every voice. A piece of four pages or fewer should need no turn in the middle of a phrase.
- A repeated section starts and ends on its own system.

## 7. The two editions

**Critical.** Title page (series and number, composer, title, subtitle, forces, poet, "Critical edition", source line, editor, edition and year) between thick-and-thin rules. Verso: contents and colophon with licence. Then preface sections, text, score with its own heading, critical notes and literature. Running heads: verso composer · title; recto section.

**Performance.** No title page. A masthead at the top of page 1 (series · Performance edition, title, subtitle, poet left, composer right) and a headnote of one or two italic lines that set the scene. The score starts on page 1. After the score, one page: text and translation, pronunciation, "For rehearsal" notes in two columns, and a one-line colophon at the foot. Running head: composer · title, folio right.

## 8. Score

- Voice names in small capitals, abbreviated after the first system (C. A. T. B.).
- Incipit with original clef, sign and first note; then the modern clef and the ambitus; then the mensuration sign.
- Mensurstriche between the staves. Bar numbers in small italic at the start of each system only.
- Editorial accidentals small, above the note.
- Rubrics red italic, left-aligned over the system.
- The score heading in the critical edition repeats title and subtitle, with poet left and composer right.
- Stanzas after the score: up to three abreast, red stanza numbers.

## 9. Tables and lists

- No vertical rules. One rule under the column heads (booktabs `\midrule`). Column heads in spaced small capitals.
- **Critical notes**: three columns, bar | voice | note. Bar numbers in lining figures. Pitches in Helmholtz notation, c′ = middle C, roman. A note ends with its verdict in small capitals where a reading is weighed.
- **Sources**: siglum in a hanging column of small capitals; base text marked *Base text*.
- **Literature**: author-first, hanging indent, short; grouped (Sources and editions / Theory / Studies) only when the list is long.
- **Text and translation**: two columns (text, italic translation) or, in the critical edition, three (diplomatic, transcription, translation). Stanza numbers red.
- **Pronunciation**: spelling (italic) | sound | as in.

## 10. Language

The prose is academic in what it claims and plain in how it says it. Argue from first principles, the sources and the counterpoint; for performers, from what happens in rehearsal.

**Voice and register**

- Short declarative sentences. One idea per sentence. Active voice; name who did it ("Perz joins the notes", not "the notes are joined").
- "I" for the editor's judgements and readings ("I take b natural here"; "the parallel is my own reading"). Impersonal for method ("Bar lines run between the staves").
- State a reading, then the reason. No hedging stacks. "Probably" once, where it is true.
- No puffery or mood words: not "beautiful", "haunting", "pivotal", "rich tapestry". Describe the music: its range, its cadences, what the Tenor does.
- No em dashes. Commas and full stops; parentheses only for references and glosses.
- Colons only before a list or a quotation.
- Every claim verified or cut. Unverified material does not go in to be flagged; it goes to the issue tracker.
- The performance edition speaks to singers: what to sing, how fast, what the signs mean, what the words say. Nothing about how the edition was made beyond one line.

**Terms** (use these, not their synonyms)

| Use | Not |
|---|---|
| source, witness | original, document |
| base text | copy text |
| critical notes | commentary, apparatus (in headings) |
| editorial | ed., added |
| semibreve, minim, semiminim, fusa, breve, longa | whole note, half note |
| Mensurstriche | bar lines (when the distinction matters) |
| cadence, clausula | resolution |
| underlay | text setting, lyrics |
| written pitch | original pitch |
| Cantus, Altus, Tenor, Bassus | soprano, alto (except when talking about modern choirs) |

**Conventions**

- British spelling (-ise). Dates "c.\,1550–1556", "fl. 1604–1611", "after 1452". En dash in ranges.
- Single curly quotation marks, double inside. Quotations in their own language, roman, in quotation marks; a translation follows in parentheses when needed.
- Titles of works in italic; Polish and Latin titles in the source's form.
- References in prose: "bar 29, Altus". In critical notes: "29 | A".
- Polish names with their diacritics, always.
- Every edition's prose gets an unslop pass before release. (Editor's rule.)
