# Underlay review, October 2026

Every edition was checked against the firm rules (principles 10.1–10.5) and the new rule 10.6 (text first). Method: export each score to MusicXML (one lyric line per stanza since this review), then run a script that flags (a) a new syllable on a semiminim that does not follow a dotted minim, (b) a note after a rest with no syllable, (c) a word split by a rest, and (d) melismas of three or more notes on an unstressed syllable or a light word. Every flag was then read against the score. Cadential tails on a final syllable are not counted as faults.

*Już się zmierzka* was reworked before this review (PR #32). *Bogurodzica* takes its underlay from the chant sources and is out of scope.

## Plaude euge theotocos

Clean. No firm-rule breaks. Melismas sit on stressed syllables (*the-o-TO-cos*, *VIR-gi-num*, *IN-spi-ce*, *RE-spi-ce*). In bar 22, Discantus, *-spi-* has one more note than *in-*. That is because the repeated f′ takes the new syllable (rule 10.9), so it stays.

## Vox in Rama

**The critical edition says the underlay "keeps every firm rule". It doesn't.** There are eight places where a new syllable falls on a semiminim after a plain minim. All of them come from Marchesano's underlay (**M**), and none is the dotted-minim case the method already defends. Proposed fixes:

| Bar | Voice | Now | Proposal |
|---|---|---|---|
| 6 | T | *in* e′ (minim), *Ra-* a (semiminim), then the run | Drop the repeated *in*. *Ra-* takes the e′ minim and the whole run, so the run sits on the stressed syllable. Check **T** first: if the print clearly puts *in* under the e′, keep it and record a departure instead. |
| 11–12 | A | *au-di-ta est* twice, with *au* on c″, *di* on d″ and *ta* on b′, all semiminims | Neither statement has enough white notes for four syllables. Drop *est* in both. Bar 11: *-ma* takes e″ and the semiminim c″; *au-* c″ (minim) with the fusae; *-di-* b′; *-ta* c″ on the cadence. Bar 12: *au-* e″ d″, *-di-* c″ b′, *-ta* c″. |
| 32 | A | *con-* on the semiminim g′ after *-it* f♯′ | Drop this *et*. *no-* d′, *-lu-* g′ (dotted minim), *-it* the semiminim g′ after it, *con-* f♯′ with the run. This keeps the long *con-* that the critical note for bars 38–39 defends. |
| 37 | T | *-la-* d′ (semiminim) after *-so-* e′ | *-so-* takes e′ d′ c′, *-la-* b, *-ri* the following c′. The *et* that follows drops, so *no-* moves to the dotted minim a. |
| 40 | T | *-la-* on the repeated e′ semiminim | *con-* g a, *-so-* b, *-la-* e′ (minim) with the run, *-ri* a. The run moves onto the stressed syllable *con-so-LA-ri*. No word is lost. |
| 27 | B | *su-* d (semiminim) after *-os* c♯ | *su-* on the semibreve a, under the Tenor's *su-*. The run goes to *-os* of *filios*. This is the weakest fix, but no other one is lawful. |

The critical edition's Underlay paragraph then lists the omitted words (two *est* in the Altus, two *et*, and possibly one *in*) under rule 10.13.

Text-led observations, no change proposed. The long *con-* in every voice is the print's own (bars 29–39). *Altus 9*: *in* has six notes. It is the head of the imitation and **N**'s reading (critical note on bars 5–6). *Tenor 16*: *u-LU-la-tus*, where the run on *-lu-* comes from the print's Tenor.

## Nunc scio vere

The underlay is entirely editorial, because the source is a tablature. It keeps every firm rule. On the text, though, about forty melismas fall on unstressed syllables in the middle of a phrase. Examples: Cantus 16 *Do-MI-nus* (7 notes on *-mi-*), Cantus 27 *e-ri-pu-IT* (8), Cantus 44–46 *ex-spe-cta-TI-o-NE*, Altus 59 *Glo-ri-A*, Bassus 31 *ma-NU* (7), and *et* with three to five notes in all four voices. The method claims Wacław's own rule from the *Lamentationes*: one melisma before each cadence, on the stressed syllable of the last word. The clause ends mostly follow it; the middles of phrases often don't.

**Proposal**: a text-led re-underlay of *Nunc scio*, as its own task. It means four voices and 87 bars, re-placing syllables so that each run falls on the stressed syllable or the key word, and the light words (*et*, *de*, *in*) take one or two notes. The firm rules and the imitation rule (10.10) stay as they are.

Also fixed in this review: the method cited Lanfranco as forbidding a syllable on the semiminim after a dotted minim. He allows it; Zarlino is the stricter one.

## Tools

- MusicXML now carries one lyric line per stanza. Before this, both stanzas of *Zmierzka* were merged into one line.
- Export bug, not fixed: in *Plaude*, the Tenor loses some syllables of *confidencium* inside the repeat. The PDF is correct.
