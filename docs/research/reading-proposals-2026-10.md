# What the four books propose, October 2026

Gould, *Behind Bars* (2011); Ross, *The Art of Music Engraving and Processing* (1970); Grier, *The Critical Editing of Music* (1996); Caldwell, *Editing Early Music* (1985). Full notes with page references are in `docs/research/literature/`. Nothing here has been changed in the editions yet. Items are grouped by how much they need Miki's decision.

## Staff spacing within systems (the open question)

The evidence is now in hand, and it does not ask for equal gaps between the staves of a system. Ross distributes spare page height mostly inside systems, giving staff gaps three to six times the share of system gaps (Ross 69). Gould asks that the gap between systems be larger than the widest staff gap inside either neighbouring system (Gould 488). Our build does the opposite of Ross: lilypond-book hands LaTeX one picture per system, so all spare height goes between systems. Five performance pages and two critical pages fail Gould's test (measured in the Gould notes).

Proposal: (1) a build check for Gould's rule; (2) where a page has spare height, give it to the staff gaps (`prBreathe` per score) rather than to the system gaps. This replaces the "equalise the gaps" experiment.

## Decisions for Miki (principles)

1. **Cautionary accidentals (7.3).** All three editing books want a cautionary sign where an altered pitch returns unaltered in the same bar (Caldwell 59–60, 112–113; Grier 163–164; Gould 86). We keep "forget" and print nothing. Our bracketed sign already means "optional", so a cautionary would need another form (round brackets small above the staff, or a plain full-size natural).
2. **Latin syllable division.** Gould (445–446) and Caldwell (42) both say: one system, not a mix. *Nunc scio* has *San-cto*, *co-gno* but *om-ni*. Choose carry-over (*o-mnis*) or divide (*om-nis*) and write it into §11.
3. **Editorial signs and names in square brackets** (Caldwell 50, 52): *Nunc scio*'s editorial ¢ as [¢], editorial voice names as [Cantus] in the critical edition.
4. **A note-value equivalence above the first system of *Nunc scio*** (Caldwell 23, 50, 66), since the values are not the tablature's.
5. **Derivative editions (3.5)** reworded (Grier 63–64, 77–79, 87–88): shared errors and shared innovations are the evidence, not overall agreement, and one edition may be copied from the other. *Vox*'s argument already rests on shared errors; the rule should say so.
6. **Emendation notes say how the error arose** (Grier 72, 99–100; Caldwell 5). Most of ours do.
7. **Source descriptions**: shelfmark for every source and consulted copy; title pages transcribed with line ends (Grier 55–56, 212; Caldwell 6–7). *Vox* lacks shelfmarks for the Wrocław partbooks, the Czartoryski *Partitura* and the Kraków Cantus.
8. **Signs that mean something else to a modern singer** (Gould 494): small notes read as cues, italic text as a second language, a bracketed accidental as a cautionary. We use all three for editorial matter. NOTE or CONSIDER.
9. **Text written *ij* in the source**: Caldwell writes it out in angle brackets and keeps italics for text the source lacks entirely (63, 103). We use italics for both.
10. **Latin orthography**: Caldwell keeps the source's spelling (63). Our 11.1 normalises, which also sits uneasily with our own 11.6.
11. **Tense in critical notes**: present for extant sources, past for lost ones (Caldwell 9).

## Engraving changes (low risk; to try and show before adopting)

- Centre whole-bar rests in the performance editions (Gould 159).
- Lyric extenders about as thick as a full stop (Ross 183): about 2× LilyPond's default.
- Final and double bar lines to the plate proportions (Ross 147, 152).
- Supplied notes at cue size (Ross 189: 75–83%) instead of grace size.
- Extender lines more than one staff space below the staff (Grier 167): a check.
- Page turns at a rest or a section end in multi-page performance scores (Grier 176): a warning.
- The ligature bracket stays when the underlay breaks a ligature, with a note (Caldwell 60–61).
- Texture: cap edge wander on stems (Ross 82) and let ink fill the acute wedges where marks meet (Ross 98–99).

## Already settled, so no change

- Mensurstriche through the lyrics: Gould wants bar lines kept off the text (463, 519). Miki has decided he is not troubled by this.
- Performance edition text after the music (Gould 437, 491): deliberate.
- Caldwell's own Appendix III shows our layout (unreduced values, ¢, breve bars, Mensurstriche) as one of his models (108); Grier supports dashed Mensurstriche, one score for both editions, no notes on the music page (153–165).
- Staff sizes: our performance staff matches Gould's ideal of 6.7 mm (557); Ross's plate tables put ours in normal plate proportions.

## New leads

Grier cites Perz (1984) on text underlay in Polish sources, Bent's "Some Criteria" and "Text Setting" articles, and argues that WDMP 12 (1933), made while the 1611 *Vox* print was complete, is a real witness to its lost Altus and Bassus.
