# Underlay analyser

`tools/analyser/` reads an edition's MusicXML, analyses the music and the text, and judges the underlay against the series rules (principles §10). It ranks and explains; it never changes an edition. Principles 10.6 asks for the tendencies to be weighed by ear, so every alternative it offers is something to sing, not a correction.

The design is in `docs/research/analyser-survey.md` (§3). This file says how to run it, how to read and accept a finding, how to add a rule, and what each layer does and where it is weak.

## Running it

Python 3.12 or later, with the packages in `tools/analyser/requirements.txt` (music21, PyYAML; pytest for the tests). LilyPond 2.24 is needed only to regenerate the MusicXML.

```
make musicxml                                              # editions/<slug>/pdf/<slug>.musicxml and .srcmap.tsv
python -m tools.analyser editions/*/pdf/*.musicxml         # findings, look and worse
python -m tools.analyser editions/vox-in-rama/pdf/vox-in-rama.musicxml -v --info
python -m tools.analyser analyse editions/nunc-scio-vere/pdf/nunc-scio-vere.musicxml --layers
python -m tools.analyser selfcheck editions/*/pdf/*.musicxml
python -m tools.analyser lexicon
python -m tools.analyser golden            # compare the golden snapshots; --update to accept
python -m tools.analyser legacy <musicxml> # the old audit's output, from the ported rules
python -m tools.analyser review editions/vox-in-rama/pdf/vox-in-rama.musicxml --html tools/analyser/review/vox-in-rama.html
python -m pytest tools/analyser/tests -q
```

`-v` adds, for each finding, the source line in `voices.ily`, the costs in its window and up to three alternatives. `--info` also lists the information-level findings. `--format text,json,markdown,github,sarif` and `--out DIR` choose the outputs; the CI job uses Markdown for its summary, `github` for annotations, and keeps a SARIF 2.1.0 file (`analyser.sarif`: the rules, every finding with its source line, regret and fingerprint, and `baselineState` new or unchanged) with the report.

`analyse --layers` prints the analysis the rules rely on: metre, the words and how the lexicon knows them, cadences with their voice functions, suspensions and other dissonances, phrases with their text, points of imitation with the text each entry carries, and homorhythmic passages. Read it before trusting a finding that depends on it. Positions are bar.minim: 16.3 is the third minim of bar 16.

In *Nunc scio vere* the doxology comes out as verse 2: the export numbers each voice's Lyrics contexts in order.

## Reading a finding

```
WARN  U301 Cantus    v1 39.3    cadence-syllable: the arrival carries 'la', and 'ri,' comes after it (phrygian cadence on B) regret 4.00
      at editions/vox-in-rama/music/voices.ily:12
      costs here: U401 0.50; U301 4.00
      try: 'ri,' 40.1 -> 39.3, 'qui' 40.2 -> 40.1 (-4.00; fixes U301 4.00->0.00)
```

- The rule (U301) and the principle it serves are in `tools/analyser/rules/U301-cadence-syllable.yaml`, with the authority it rests on.
- Cost: the rule's weight times how much it is broken, times the gates that apply (below).
- Regret: how much the best legal underlay nearby that solves this finding scores better than the underlay as it stands, and only this finding's part of it. An alternative often solves several findings at once (a U301 and a U302 on the same clausula); its gain is split among them in proportion to how much each one's cost falls, so the regrets of the findings it solves add up to its gain, and one change is not counted several times at the top of the list. Only syllables within two of the finding may move, and only between the same rests. A syllable with punctuation stays where the editor put it, except for a 10.3 finding: 10.6 places each line's last syllable on its cadence first.
- Level: `break` for a firm rule (10.1, 10.2, 10.4, 10.5). 10.3 is firm too, but the analyser can only check it against the cadences it detects, so it prices it (U301, the highest weight) instead of failing on it. Otherwise `warn` (regret 2 or more), `look` (0.75 or more) or `info`. A finding with no better legal alternative is information, however often it occurs: a run on *et* that nothing lawful can avoid is not a problem to solve.
- `try:` lists the alternatives, each with its change in cost and the rules it fixes or costs (over the whole span between the rests).
- An alternative may change the text (`settings.yaml: text_edits`). In a voice below the top one, principles 10.13 lets a word be skipped to keep long notes if the text still makes sense alone: the analyser offers dropping a conjunction or auxiliary on the `droppable` list (*et*, *est* ...) or one of a word sung twice in a row (*plebis, plebis*), never a preposition or a content word from a single statement. For a long melisma (U205, U206, U302) it offers singing the word again (10.9). Such an alternative starts with `drop 'est' at 12.1 (10.13)` or `repeat 'Rama'`, lists `edit 1.00` among its costs, and is marked `edit: drop` or `edit: repeat` in JSON and SARIF. Dropping costs 1.0 (1.5 for a doubled content word) and repeating 1.0, so a reading that keeps the text wins when it is about as good. On the pre-review *Vox in Rama* the analyser proposes the review's drop of *est* in the Altus at bar 12; it no longer proposes the review's *et* in the Tenor at bar 37, which heads the *et noluit* motif (Miki, 4 October 2026). A word on a motif's head notes is never dropped, and a finding that only a text edit improves is reported at look, not warn.

## Accepting a finding

The baseline, `tools/analyser/baseline.json`, lists findings by fingerprint: edition, voice, verse, rule, word, syllable within the word, and occurrence. Bar numbers are not part of it, so renumbering does not reopen anything. Each entry has a status and a reason:

- `accepted`: the editor keeps the underlay. Give the reason, normally a source reading kept under 10.12 or a choice the method section records. Example: the long *con-* in every voice of *Vox in Rama*, which is the print's own.
- `pending`: present when the analyser was introduced (4 October 2026) and not yet reviewed. Pending findings stay in the job summary's list of open findings but do not count as new.

To accept a finding, find its fingerprint (in `-v` output or `--format json`), set `status` to `accepted` and write the reason.

Or accept it in the source, beside the note (`inline.py`):

```
% underlay: ok U206 bar 34 'consolari' -- the print's long con-, kept under 10.12
cantusNotes = { ... }
altusNotes = { ... }   % underlay: ok U301 -- source reading
```

A trailing comment covers findings on its own line; a comment line covers the next line of code. One line of `voices.ily` often holds a whole voice, so narrow the comment with `bar N` and a quoted word (as the lexicon spells it, or the syllable as printed). Several rules may be listed. The reason after `--` is required; a comment without one is ignored and `check` reports it. Inline acceptances count as accepted in every output; the baseline file stays the place for decisions that should outlive edits to the music. `--update-baseline` adds every current finding that is not yet listed as pending, keeps the reasons already written, and drops entries whose finding has gone; review its diff like code.

CI fails only on a new break. New warnings and looks appear as annotations at the `voices.ily` line and in the summary.

## Adding a rule

1. Choose an ID in the right band: U1xx firm rules, U2xx tendencies of 10.6 and 10.9, U3xx phrase and imitation rules, U4xx dissonance, U5xx text and lexicon.
2. Write `rules/U2nn-name.yaml`: `id`, `name`, `level` (break, look or info), `weight`, `tier`, `principle`, `authority` (the theorist or the editor's decision, with page), `message` (a format string over the values the check returns), `gates`, and `examples`. `hard: true` makes it a firm rule that decides legality. `scope` is `syllable` (the default), `line` or `piece`.
3. Write `rules/U2nn_name.py` with `check(ctx)` (or `check_line`, `check_piece`). A syllable check sees one syllable under one candidate underlay (`rules/base.py`): its notes, its word, the note before and after, the next syllable's first note, and `ctx.analysis` for the music layers. Yield `ctx.hit(...)` with the values the message needs and an `amount`.
4. Give it at least one `flag` and one `pass` example. Fixtures use the compact notation in `fixtures.py` (`notes: "f2 g1 a2"`, `text: "Do- mi- nus"`; `voices:` for several parts); `ref: slug/Voice/verse/bar` points at a passage of an edition. `tests/test_rule_examples.py` runs them all, and a rule without both kinds fails.
5. Run the tests, then `python -m tools.analyser golden` to see what the rule changes in the editions, and `--update` once the diff is right.

Weights and thresholds live in the YAML files and `settings.yaml`, not in code. They are judgements, set from the order of the principles. A reviewer who disagrees with one should change the number and look at the golden diff.

## Gates

A gate is a named multiplier that a music layer applies to a rule's weight (`gates.yaml`; predicates in `gates.py`). Each finding lists the gates that applied.

| Gate | Layer | Effect |
|---|---|---|
| cadence_approach | cadence | stress-short and run-unstressed count half in the last word before a cadence (Lanfranco VIII) |
| cadence_lower_note | cadence | the octave rule does not apply where the lower note is a cadence arrival (10.6) |
| evaded_cadence | cadence | the cadence-syllable rule counts half at an evaded or abandoned cadence |
| weak_cadence | cadence | the cadence-syllable rule counts half at a weak figure (a complete clausula that closes weakly) |
| key_word | text | stress-short counts 1.5 times on a key word the editor has confirmed (10.6) |
| suspension | dissonance | a syllable on a suspension counts a quarter (Vicentino's exception) |
| full_point | imitation | imitation text counts half again in a point of three or more entries (10.10) |
| homorhythm | texture | stress-short and light-on-beat count half again where the voices declaim together (10.6) |
| older_practice | edition | stress and light-word rules count half in an older piece (Towne 1990, 285); set for *Plaude* |
| sung_through | text | the run rules (U205, U206) count half on a syllable that is open or closed by a sonorant (*con*, *in*) |
| melodic_resolution | cadence | the cadence-syllable rule counts half where the last syllable falls on the voice's own resolution after the arrival |
| tail_voice | cadence | the cadence-syllable rule counts half where other voices have begun new text during the last syllable |

## The layers

Ingest (`ingest.py`). Our MusicXML, read as the old audit read it, with ties merged except the dashed ties of notes divided for text (10.13), rests kept, second endings and unmeasured chant sections marked as breaks, and the LilyPond source of every note from `<slug>.srcmap.tsv`. Durations are in semiminims. The chant part of *Nunc scio* is not analysed.

Metre (`meter.py`). The bar is a breve; the tactus is the semibreve, so the half-bar is a beat. The sign decides which value may take a syllable (10.1): a minim under cut-C or no sign, a semiminim under C. Signs come from the MusicXML, and `editions.yaml` supplies them where the edition prints none: *Plaude* is read as C, because the critical edition describes imperfect tempus and minor prolation. That is a reading to confirm.

Key words (`editions.yaml: key_words`). Each edition lists the words that carry the sense of each clause (*Dominus*, *angelum*, *Herodis*; *Rachel*, *plorans*, *filios*, *consolari* ...), each with a `source`. The analyser proposed these lists on 4 October 2026 from the texts, marked `source: "proposed, not confirmed"`, and a proposal has no effect. To confirm a word, change its source to `"MD, <date>"`; to reject it, delete the line. A confirmed key word is no longer a light word (U201, U205), and its stressed syllable weighs more when short (gate `key_word`). `analyse --layers` and the review page list both kinds.

Text (`text.py`, `lexicon/la.yaml`, `lexicon/pl.yaml`). Words grouped by `syllabic`, as the old audit grouped them. Each word has its syllables, stress and class (light, function, content, fragment; key words per edition) and the source of the decision. Latin stress follows the quantity rule (10.8), cross-checked against the old audit's table. Polish stress is the penult, checked by the loader, with exceptions listed as they arise. The editor has not yet confirmed the entries; `lexicon` lists how many. An unknown word gets the penultimate rule and an information finding (U501), never a silent guess.

Sonorities (`layers/sonority.py`). Vertical slices from music21's timespan tree, with attacks and sustains per voice. A fourth counts as dissonant only against the lowest sounding voice.

Dissonance (`layers/dissonance.py`). Suspension (with preparation, agent, resolution and figure such as 7-6 or 4-3), passing, accented passing, neighbour, cambiata, anticipation, échappée, and unexplained, after Morgan's taxonomy as described in the survey (§1.2), written from its definitions. Limits: no ornamental or fake suspensions, no chanson idiom, no dissonant third quarter, no separate ternary suspensions; those notes come out as unexplained or as passing notes. A held note against a moving voice on the tactus is tested as a suspension first.

Cadences (`layers/cadence.py`, `layers/cadence_tables.yaml`). Two voices moving by contrary step from a major sixth to the octave (or a minor third to the unison), arriving on the tactus with notes of a minim or more, give the cantizans and tenorizans. The other voices are labelled bassizans, altizans or evaded bass, and the type (authentic, phrygian, clausula vera, evaded, abandoned) comes from our own table, not CRIM's; an evaded bass does not override a bassizans in another voice. A 7-6 suspension into a major sixth that does not open to the octave gives an evaded or abandoned cadence. At the end of a section, a lowest voice rising a fifth or falling a fourth onto a held final under the tone gives a plagal ending (functions P and H; the final of *Vox in Rama*).

Each cadence has a closure score, a point each for: arrival notes of a semibreve or more (a minim under C), a rest after the arrival in a voice of the clausula, a suspension leading in, a bass (bassizans or plagal), and the end of a clause in the text on or just after the arrival. A complete clausula with fewer than two points (`full_closure`) is a weak figure: it is listed and drawn but not counted as a cadence, and U301 counts half there. Every cadence therefore has a kind (full, weak, evaded or abandoned), reported separately. CRIM's `cadences()` counts evaded and abandoned cadences with the full ones. *Vox in Rama*: 8 full and 4 evaded, 12 (CRIM 12), and 8 weak figures. *Nunc scio*: 20 full and 5 evaded, 25 (CRIM 24), and 5 weak figures. The totals agree; the places do not always: in *Vox* the two lists share 6 of their 12. CRIM has three the contrary-step test does not find (bars 13, 19, 35) and three the analyser finds weak (bars 23, 26, 34); the analyser has the plagal final and five figures CRIM does not list. Cadences without a contrary-step pair are not found. Read the cadence list before trusting a 10.3 finding.

Phrases (`layers/phrase.py`). From rest to rest (music21's `segmentByRests`), cut at section breaks, at cadence arrivals where a word ends, and after punctuation.

Motifs (`layers/imitation.py: motifs`). A head with a dotted value and a leap, from an entry after a rest, sought at every note in every voice: the same values, repeated notes in the same places, other intervals within a step, the same direction throughout or inverted throughout (an inversion counts only inside the span of the direct occurrences). Occurrences within four breves of each other chain; three or more in two voices make a motif. U306 compares each occurrence's syllables with the text most occurrences carry.

Imitation (`layers/imitation.py`). Entries are first notes after a rest; the head motif is four notes. Two heads match when they are close in both intervals and rhythm: at most one interval differs, by a step (a flexed entry; this also admits a tonal answer, a fifth answered by a fourth), and flexed intervals plus differing values (all notes but the last) number at most two. Intervals alone can match by chance: in *Vox in Rama* the old test joined *ploratus et* (Bassus 16) to *Rachel plorans* (Tenor 19); the rhythm now keeps them apart, and the opening becomes one point of four voices. Where the evidence is strong an entry need not follow a rest: the note after a cadence arrival in its voice, or the first note of a new clause of the text, counts when six notes agree exactly in intervals and rhythm with another entry (*et noluit*, Tenor 28 in *Vox*). Entries within four breves of the previous one form a point: FUGA, PEN (equal time distances) or DUO. The three fugas the survey found with CRIM in *Nunc scio* (bars 1–3, 35–36, 61–64) are found, the last as 57–63.

Stanzas (rule U305, principles 10.14). In a strophic piece (`editions.yaml: strophic`; *Już się zmierzka*), a later stanza follows stanza 1 where its words fall alike. Each voice is cut at the notes where both stanzas start a word; in a segment where the later stanza has as many syllables as stanza 1, with the stresses and word breaks in the same places, each syllable it places differently costs 1. Where the words fall differently, the stanza may take its own underlay and nothing is flagged. *Zmierzka* has 28 such segments in its two stanzas and agrees in all of them.

Texture (`layers/texture.py`). A slice where every sounding voice attacks scores 1, all but one 0.5; four points in a row make a homorhythmic passage. For each passage the report gives how often the voices change syllable together. Principles 10.6 says the voices need not, so the related rule (U304) is information only.

The underlay model (`underlay.py`, `findings.py`). Syllables are aligned to the notes between rests; the first syllable after a rest is pinned (10.2) and no syllable crosses a rest. Firm rules decide legality; the rest are priced. A k-best dynamic programme over (syllable, start note) finds the best legal alternatives; rules that compare voices (imitation, homorhythm) are added afterwards and the candidates re-ranked.

The self-check (`selfcheck.py`). For every voice and verse it counts the syllables in `voices.ily`, in the MusicXML (read independently with music21), in the analyser's model and in the old audit's. All editions agree. The October review's export bug in the *Plaude* Tenor is not in the export: the MusicXML has all 53 syllables, and it was the old audit's tie merging that dropped five, on notes divided with a dashed tie (bars 14, 18 and 32).

## The review page

```
python -m tools.analyser review editions/vox-in-rama/pdf/vox-in-rama.musicxml --html tools/analyser/review/vox-in-rama.html
```

writes one self-contained HTML page for one piece (`review.py`, with `review_assets/page.css` and `page.js` inlined). The pages for *Vox in Rama* and *Nunc scio vere* are committed in `tools/analyser/review/`, and CI keeps fresh ones with its report. Regenerate them after a change to an edition or to the analyser.

- The score is the critical score as notation. LilyPond 2.24 renders a small file that `\include`s the edition's `music/score.ly` with the SVG backend and point-and-click links, on one tall page with room under each system for the analysis bands, and without the ambitus (whose heads carry the same links as the notes they show). Every note's link names its line and column in `voices.ily`; the source map gives the analyser's notes the same, so each drawn note carries its analyser id. The page says how many notes could not be tied (none in either piece). The score stays on a white paper panel in dark mode and scrolls sideways when it is wider than the screen; − and + change its size.
- The findings are ranked by level and regret and filtered by level, rule and voice. Choosing one lights up its notes in the score and scrolls to them, and shows the rule, its principle (the text of §10) and authority, how the cost is made (weight, tier, the gates that applied, the costs around it) and how the regret is shared, the baseline status, and a note-by-note grid: the notes (bar, pitch, value) with the syllables as they stand and under each of up to three alternatives, changes in red. Each alternative lists its change in cost, what it fixes and costs, and whether it drops or repeats a word.
- The layers are overlays on the score, each switchable: cadences (rings at the arrival notes with each voice's function, and a band under the system with type, tone and kind; weak figures grey and dashed), dissonance (labels above the notes; a suspension with its figure, an arc to its resolution and a dot on its preparation), phrases (brackets under each staff), points of imitation (each entry's head marked and numbered, and a band entry), and homorhythmic passages (a tint over the system and a bar in the band). Hover a mark for its detail. Tables below list the same layers; a row finds its notes.
- The summary at the top gives the counts by level, the baseline status, the biggest open regrets, the analysis counts and the key words (confirmed and proposed). At the foot, every word the piece sings, with its syllables, the stressed one in capitals, its class and the source of the stress, so that a wrong stress shows.

Without LilyPond the page is written without the score.

## Tests

`tools/analyser/tests/`: the rule examples; the port against `tools/underlay_audit.py` on every edition and on the *Vox in Rama* of commit bb75083, before the review fixed its eight breaks; unit tests for each layer; the model (legality, regret, anchors, gates); the review cases (on the pre-review *Vox in Rama* the model finds a move-only fix where the review did, Bassus 27 and Tenor 40, and none where the review dropped a word, Altus 12 and Tenor 37; at Altus 11 it finds a lawful reading the review did not consider; and Miki's verdicts of 4 October 2026, below); the self-check; the baseline; the gaps closed on 4 October 2026 (`test_gaps.py`: text edits, stanzas, key words, inline acceptance, attributable regret, cadence closure and plagal endings, stricter imitation, SARIF); the review page (`test_review.py`; the score test is skipped without LilyPond); and golden snapshots of every edition's findings and layers (`tests/golden/`). A change to a snapshot is a fix or a regression: look at the diff before `golden --update`.

## What Miki's review taught

Miki's review of the *Vox in Rama* findings (4 October 2026; `books/MIKI-VOX-REVIEW-2026-10-04.txt`) is a singer's, and it is read here for patterns, not only verdicts. Each is a rule or a change to one, citing the review; the verdicts are regression cases in `tests/test_review_cases.py`, on the *Vox* of commit c157d86 (`tests/fixtures/vox-in-rama-c157d86.musicxml`).

| Pattern | Rule |
|---|---|
| A melisma is long in time, not in notes: six fast quavers are short | U205, U206 measure the syllable's length in semiminims (`params` in their YAML); the note count stays in the message |
| A short syllable is one whose vowel a plosive or fricative stops (*it*, *et*, *-tus*); an open one or one closed by m, n, l, r (*con*, *in*) can be sung through | `text.coda_class` (Latin and Polish; Polish *rz* is a fricative); U208 short-melisma, weight 3; gate sung_through halves U205/U206 |
| A syllable change through a consonant cluster (*con-so*: o-n-s) needs time: not on a fusa or the end of a fast figure | U209 cluster-short |
| A stressed syllable belongs on the tactus when the line allows it (*-la-* at Cantus 35.3) | U210 stress-weak-beat; with no better lawful place it stays information |
| The last syllable goes on the voice's own resolution, which may come after the harmonic arrival; a voice carrying the old phrase across the join keeps the tail's momentum; a vowel on the final move is a full stop, so a held syllable is the one before it | cadence layer `melodic_resolutions`; U301 gates melodic_resolution and tail_voice; U301 prices a last syllable carried back across the final move (Bassus 18: *la* over 18.2–18.3, not *tus* over 18.3–19.1) |
| Imitation pins the underlay: a motif passed round the voices is texted alike, syllabic where the others are | imitation layer `motifs` (entries anywhere, not only after rests; a voice may recur; flexed, at any interval, or inverted inside the chain); U306 motif-text, weight 4. *Et noluit* is found in 13 places, Altus 31.4 and Tenor 37.4 included |
| A dropped word must never break a motif's text | `edits.py` offers no drop on a motif's head notes; the review's drop of *et* at Tenor 37 is no longer proposed |
| Dropping a word is the last resort (10.13) | a finding that only a text edit improves is reported at look, never warn |
| Key words | unchanged: still proposals; the review page's summary lists the confirmed and proposed ones together for confirmation |

What the analyser cannot yet do with his verdicts: it never restores a dropped word, so the *et noluit* findings at Altus 31.4 and Tenor 37.4 have no lawful alternative and stay information (an xfail case); his Tenor *la* at 40.1 falls on a semiminim, which 10.1 (U101) forbids under cut-C; and his Cantus 39.3 (*la*, the stressed syllable, on a weak cadence) is not a rule.

## Known limits

- Weights are hand-set. They have not been calibrated against texted sources (survey §3.3, step 7 of the build order).
- Text edits are limited to dropping a droppable or doubled word and repeating one word; the analyser does not propose repeating a clause or changing the text otherwise. The edit costs are judgements (`settings.yaml`).
- The key words are proposals until the editor confirms them (`editions.yaml`); until then the key-word class has no effect.
- Stanza consistency compares later stanzas with stanza 1 only.
- Cadence closure is a count of five signs, not a calibrated measure; the threshold of two puts the totals of full and evaded cadences near CRIM's.
- The Latin and Polish lexicons await the editor's confirmation.
