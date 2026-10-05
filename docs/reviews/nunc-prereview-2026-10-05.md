# Nunc scio vere: pre-review of the underlay findings (5 October 2026)

Prepared by Claude for Miki's underlay review on the interactive page (`tools/analyser/review/nunc-scio-vere.html`). Nothing in the edition has changed: `music/underlay.py` and `voices.ily` are as on `october-decisions` (752bb2c). The recommended changes are in `tools/analyser/review/nunc-scio-vere.recommendations.json`, one db `edits` document each (status `proposed`, reason beginning "Claude's recommendation: "), ready to seed into the page so that each shows as a firmed reading or a custom edit to accept, change or withdraw.

Positions are bar.minim (16.3 = third minim of bar 16). Verse 2 is the doxology.

## Summary

- The analyser (before the new c.f. gate) reported 0 break, 12 warn, 27 look: **39 findings triaged**, plus the suspicious information-level ones below.
- **Change: 14 findings, in 13 documents**: 7 clear, 6 judgement calls. Altus 32.4 and 33.2 are one change, and Altus 49.4 is answered by the change at 49.1. The Altus long *Nunc* (judgement call 1) would also answer the U303s at Bassus 1.3, Cantus 2.1 and Tenor 3.3, which are kept in those voices.
- **Keep: 25 findings**: 14 clear, 8 judgement calls, 3 false flags (the analyser is wrong, not the underlay). Five more kept findings are partly false because they sit in c.f. spans; they are now gated.
- The analyser now knows the cantus firmus spans (gate `cantus_firmus`, below). With it the counts are 10 warn, 28 look.
- Key words: cut from fifteen to a modest proposal, line by line (below). Still unconfirmed.

Agreed decisions this triage honours: long flowing *Nunc* in all voices; change syllable before a run rather than after it; *et* before the strong beat in moving figures; c.f. spans marked. From the *Vox* reviews: melisma length in time; short syllables are those closed by a stop; the last syllable on the voice's own resolution; a stressed syllable on the landing note at the arrival with the last syllable after it is right (Vox Cantus 39.3); imitation pins the text; dropping a word is the last resort.

## Clear cases (recommended)

| Finding | Recommendation | Why |
|---|---|---|
| U301 Altus 49.1 *plebis* | alternative 1 | The Altus is the cantizans of the full cadence on C; *bis* lands on the arrival instead of the next *PLE-*. Every repeated C keeps its own syllable and the third *PLE-bis* gets the long A. |
| U303 Tenor v2 77.1 *et in saecula* | alternative 1 (as a custom edit, bar 78) | The Tenor answers the Cantus an octave lower; *sae* on the A sets the motif note for note like the Cantus (10.10). |
| U301 Tenor v2 81.3 *saeculorum* | alternative 3 | Each repeated G still takes a syllable, but *cu* now leads off the beat into *LO* on the downbeat and *rum* arrives with the cadence. The method's departure "Tenor *-rum* in bar 81" goes. |
| U302 Altus 32.4 *Herodis* (and U210 Altus 33.2) | alternative 1 | *He* on the minim after the rest leads into *RO* on the downbeat, which takes the run and the long notes to the cadence. Your *Vox* Altus 32.4 *con-* pattern: licence 10.1(a), to be named in the critical note; the departure "Altus *He-* in bar 32" goes. |
| U210 Altus 53.2 *Iudaeorum* | alternative 1 | The other three voices all sing *-o-* on the downbeat of 53 (the Tenor in exactly this rhythm). *dae* leads in off the beat. |
| U210 Altus v2 72.4 *principio* | alternative 2 | *prin* off the beat into *CI* on the downbeat and the leap to G; the stressed syllable takes the run to the cadence (10.7). |
| U210 Tenor 10.2 *vere* | alternative 1 | The Tenor has the chant here: the chant's *ve-* is the c′ at 10.3, as in the first statement (critical note 3–12), and it is on the beat. The B before it is an ornament. |

## Judgement calls (most important first)

1. **Altus 1–4, long *Nunc*** (custom; answers U303 at Bassus 1.3, Cantus 2.1, Tenor 3.3). The agreed long *Nunc* is in Cantus, Tenor and Bassus, and the method says "every voice", but the Altus sings *sci-* on the third note of the motif (2.1). The custom gives the Altus *Nunc* over C–A–D–C–B–A–B, *sci* on the C at 3.2, *o* on the long A, *ve* on the D before the run. For: the point of imitation is set alike, and Cantus and Bassus already have *sci* on a weak minim with *o* on the strong one. Against: the Altus loses *SCI* on the dotted high D, the best-declaimed *scio* in the piece. If you keep the Altus, the method sentence needs "except the Altus".
2. **Bassus 17, *Dominus*** (custom; U301 17.3). Move the first *Dominus*'s *nus* from the E to the low A at 17.3, the bass's arrival: *mi* holds D–E by step, the final move gets the last syllable (your *Vox* Bassus 18). *Do* of the repeat stays on the top of the octave, which 10.6 allows where the lower note carries a phrase's last syllable. The analyser's own alternative (*Do* down onto the A) makes the arrival begin the repeat, an elided cadence; I'd not take it. Keep the U210 at 17.4.
3. **Tenor 28, *eripuit*** (U302, alternative 2). *e-RI-pu-it*: *ri* takes the high C and the run before the cadence (Wacław's one melisma, 10.7) instead of *pu*. Against: *pu* then changes on the white A straight after the run, and the Tenor no longer moves to *pu* with the Cantus's chant at 28.2.
4. **Tenor 19–21, *angelum suum*** (U206, alternative 3). *SU-* on the high syncopated D at 20.4, together with the Bassus's *su* on the same syncopation (a span against the tactus); *lum* takes the run from its first semiminim on the beat (10.1(a)) and is sung through on the m. Against: the Tenor leaves the Cantus's *su* at 21.3.
5. **Cantus v2 81, *saeculorum*** (U210, alternative 2). *sae* keeps the high e″ (the method's choice), and *LO* moves from the off-beat A to the B on the beat. The method's "*-ló-* takes the three minims" becomes two.
6. **Altus v2 85, *Amen*** (U210, alternative 1). *A-* on the beat, *men* off it; *saeculorum.* gets its full stop before *Amen* begins. Small.

Judgement calls I would keep (no document):

- **Cantus 5.3 *vere*** (U301, warn). *VE-* on the landing E at the arrival and *-re* on the next minim, carried through the turn to the voice's own resolution at 6.4: your *Vox* Cantus 39.3 pattern. The analyser's landing exemption misses it only because *-re* carries the closing turn. Alternative 2 (a second *vere* after the cadence) is the one to sing if you disagree.
- **Cantus 28.4 *-it*** (U208, warn; c.f.). *-it* is two notes, the chant's G and the cadential F♯: a held note, not a run. Every alternative takes *me* off the arrival (10.3) or moves the chant's syllables off its notes. Your *Vox* objection was to a melismatic *it*; this is a long one.
- **Cantus 9.3 / 10.2 *scio vere*** (U207, U210). *VE-* is on the high dotted D: the high point and a long note (10.6), against the tactus. The repeated A at 9.3 is the first semiminim of a run.
- **Bassus 54.1 *Iudaeorum*** (U302). *dae* already falls off the beat leading into *-O-* on the downbeat (10.6), and *-o-* has the cadential melisma. Three minims on *Iu* are not a run.
- **Bassus 23.4 *et*** (U208, look). *et* on its dotted minim before the strong beat, then three quick notes: short in time. The only fix drops *et*, the head of the clause (last resort).
- **Bassus 15.2 *misit*** (U210). The analyser offers only drops of *Dominus*. If you want *MI* on the beat, try *mi* on the A at 15.1 in the page's edit mode; I could not confirm it is better.
- **Bassus v2 78.2 *saecula*** (U206). The run on *cu* follows the agreed "change before the run"; *la* after the run would break it.

## Kept (clear)

| Finding | Why |
|---|---|
| U302 Cantus 51.4 *Iu-* | The dotted head motif carries *Iu-* in Cantus and Bassus (imitation; critical method). |
| U302 Cantus 16.4 *-mi-* | Agreed: *-mi-* on the a′ before the run (commit 93f026d); *Do-* has the run. |
| U206 Bassus 26.4 *e-* | Agreed and in the method: the Bassus's long *e-* of *eripuit* on an open vowel. |
| U302 Tenor 16.2 *-mi-* | *Do-* has the run; *-mi-* changes before the semiminims, as agreed. |
| U210 Bassus 3.2, U303 Bassus 1.3, Cantus 2.1, Tenor 3.3, U207 Tenor 7.1 | The agreed long *Nunc*. Every alternative shortens it. (See judgement call 1 for the Altus.) |
| U210 Bassus 17.4 *Do-* | See judgement call 2: *Do* on the top of the octave after the cadence note. |
| U210 Bassus 9.2 *scio* | *SCI* on the syncopated F semibreve, a leap up; the alternatives drop *vere*. |
| U210 Cantus v2 69.2, U301 Cantus v2 68.3 *Sancto. Sicut* | The method's one *Sancto* with a single run (65–68); *-cto.* on the repeated F after an evaded arrival; *Si-* picks up off the beat after the full stop. |
| U207 Tenor 32.3 *Herodis* | *RO* on the downbeat semibreve; the repeated F is the first semiminim of a run (10.9: "may", not "must"). |

## False flags

| Finding | Why the analyser is wrong |
|---|---|
| U301 Bassus 11.1 *vere* (warn) | The Bassus is tenorizans of a passing clausula on G at 11.1, but its own cadence is the authentic one on C at 11.3 (closure 5), where *-re* lands. When a voice belongs to two cadences a minim apart, U301 should judge it at the later, stronger one. |
| U204 Bassus 14.1 *quia* | The low F at 13.3 carries *-re,* (the end of *scio vere*); 10.6 lets the next syllable start on the top of the octave there. The cadence layer finds no cadence at 13.3, so gate `cadence_lower_note` never applies. |
| U210 Tenor v2 67.2 *Sancto* | *SAN-* is on the syncopated high A semibreve: long note and high point (10.6). U210 reads only the tactus, not the agogic accent of a syncopation. |
| U210 Altus 49.4 *plebis* | Answered by the U301 at 49.1 (alternative 1 moves *ple* to the A breve); its own alternatives only drop words. |
| U208 Cantus 28.4, U302 Cantus 16.4, 51.4, U207/U303 Tenor 7.1, 3.3 | Partly false: these are in c.f. spans, where the notes and syllable positions are the chant's. Now gated (below). |

Information level, worth knowing:

- U303 Bassus v2 63.1 and Tenor v2 60.1 (*Gloria*): the Bassus "entry" at 63 is the psalm tone recited syllabically (c.f.); it cannot be texted like the free voices' long *Glo-*. Now halved by the gate; it was regret 0 anyway.
- `analyse --layers` prints the doxology's points of imitation with text `_ _ _ _`: the layer shows verse 1's text only, so the doxology entries look untexted. A display fault, not an underlay one.
- U201 Tenor v2 63.1 *et* on the bar, in the homorhythm 62.2–63.1: the voices declaim together there; keep.
- The critical note on 13–56 says "*-mi-* takes the g♯′ before the cadence (bar 17)", but since 93f026d *-mi-* is on the a′ at 16.4. The note needs updating whatever else changes.

## Key words (proposed, in `editions.yaml`)

Line by line, with the translation the page shows beside them. Modest: the words that carry each line's sense; secondary where a word travels with another (as *consolari* in *Vox*).

| Line | Key words | Translation |
|---|---|---|
| *Nunc scio vere,* | **scio**, *vere* (secondary) | Now I know for certain |
| *quia misit Dominus angelum suum:* | **angelum**, *Dominus* (secondary) | that the Lord has sent his angel |
| *et eripuit me de manu Herodis,* | **eripuit**, *Herodis* (secondary) | and has rescued me from the hand of Herod |
| *et de omni exspectatione plebis Iudaeorum.* | **exspectatione** | and from all the expectation of the people of the Jews |
| *Gloria Patri, et Filio, et Spiritui Sancto.* | **Gloria** | Glory be to the Father, and to the Son, and to the Holy Spirit |
| *Sicut erat in principio, et nunc, et semper,* | **semper** | As it was in the beginning, is now, and ever shall be |
| *et in saecula saeculorum. Amen.* | none | world without end. Amen. |

Dropped from the old list: *Iudaeorum, Patri, Filio, Spiritui, Sancto, principio, saeculorum*. The three names of the doxology are formula, and *saecula saeculorum* is one idea. Open questions for you: is *Nunc* itself a key word (the moment of recognition, and the chant gives it the long neume)? Does the doxology's *et nunc* answer it?

## Cantus firmus

The c.f. spans (`\cfStart`/`\cfEnd`) were invisible to the analyser: the MusicXML does not carry them. They are now in `editions.yaml` (`cantus_firmus`: Tenor 3–11, Cantus 13–56, Bassus 63–71), with a new gate, `cantus_firmus` (`gates.py`, `gates.yaml`; tests in `tests/test_model.py`).

- What it does: in a c.f. span the run, repeated-note, short-melisma and clausula rules (U205–U208, U302) and the imitation rule (U303) count half. The chant fixes the notes, the edition puts the syllables on the chant's notes (critical note 13–56), and the short notes between them are its ornaments, not editorial melismas.
- What it does not do: stress rules (U202, U210) are not gated, because the method says "within a word, the stresses above place the syllables, not the chant's neumes". The Tenor 10.2 finding above is a stress finding that the chant itself answers.
- Effect: Cantus 28.4 (U208) and Cantus 16.4, 51.4 (U302) are halved; the Tenor's U207 at 7.1 and U303 at 3.3 too. Two warns become looks.
- Not done, worth considering: when an alternative moves a c.f. syllable onto an ornament note (a note shorter than the chant's unit), it could be priced or refused. That needs the chant's own notes marked, which the source does not give us directly.

## Process notes

- `voices.ily` is generated from `music/underlay.py`, so `edits apply` prints the change for *Nunc* and leaves the file alone. The documents pass `edits apply --dry-run` with nothing refused. Tenor v2 77.1 is seeded as a custom edit (bar 78) because its span overlaps the 81.3 alternative, and an alternative's document lists every note of its span.
- Critical notes to update if the recommendations stand: the departures for Altus *He-* (bar 32) and Tenor *-rum* (bar 81) go; licence 10.1(a) is named for Altus 33.1 and Tenor 20.1; the 13–56 note on *-mi-* is corrected; the *Words and music* paragraph on bar 80 changes if judgement call 5 is taken.
