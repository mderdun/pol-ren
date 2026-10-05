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
| against_tactus | meter | light-on-beat and stress-short count half where the voice plays against the tactus (`meter.displaced_spans`) in a span that begins a phrase for it; U210 instead accepts the displaced pulse as a beat there |
| against_tactus_mid | meter | the same, at 0.75, where the span starts in the middle of the voice's phrase: there the play is a hint (Miki, 5 Oct 2026) |
| cantus_firmus | edition | the run, repeated-note, short-melisma and clausula rules (U205–U208, U302) and imitation text (U303) count half inside a voice's cantus firmus span (`editions.yaml: cantus_firmus`; *Nunc scio*: Tenor 3–11, Cantus 13–56, Bassus 63–71), where the notes and syllable positions are the chant's; stress rules are not gated |

## The layers

Ingest (`ingest.py`). Our MusicXML, read as the old audit read it, with ties merged except the dashed ties of notes divided for text (10.13), rests kept, second endings and unmeasured chant sections marked as breaks, and the LilyPond source of every note from `<slug>.srcmap.tsv`. Durations are in semiminims. The chant part of *Nunc scio* is not analysed.

Metre (`meter.py`). The bar is a breve; the tactus is the semibreve, so the half-bar is a beat. The sign decides which value may take a syllable (10.1): a minim under cut-C or no sign, a semiminim under C. Signs come from the MusicXML, and `editions.yaml` supplies them where the edition prints none: *Plaude* is read as C, because the critical edition describes imperfect tempus and minor prolation. That is a reading to confirm.

Note values (`shortnote.py`; rules U101, U102, U106, U203). Principles 10.1 was rewritten on 4 October 2026 after the literature review (`docs/research/rule-10-1-review.md`), and the analyser follows it in three parts. *Firm*, a break (U101): a new syllable on a note smaller than the dot it follows, on a fusa (under C, anything shorter than a semiminim), on a middle or last note of a run of short notes outside (c), or on a semiminim that no licence covers; and (U102) a lone semiminim with a syllable whose next note has none (the semiminim after a dotted minim counts as lone). *Licences*, legal at a small cost so that the search can propose them and the minim still wins where it is about as good (`settings.yaml: licences_10_1`; U106 reports them, with the clause): (a) the first semiminim of a run on a minim beat, 0.5; (b) a semiminim straight after a dotted minim, 0.25, or a lone semiminim on a pitch repeated next to it after a longer note, 0.25; (c) a later note of a run where every sounding voice strikes a short note at the same moment, or which the line reaches by a leap of a third or more, 0.5. (d), the white note straight after a run, is U203: at a phrase end (the phrase's last syllable or the one before it) it costs only the licence, 0.25; elsewhere the old 0.75. A run's own syllable (a) counts as the run for U203, so the white note after a run that began with a syllable is priced too. (e), what the period source shows, the analyser cannot see: accept the break beside the note with `underlay: ok U101 -- 10.1(e) ...`; so too an older licence used with a reason (10.1, last sentence), or an editorial departure with its ground named in the critical note, as in the *Vox* Altus at bar 12 (Miki, 5 October 2026: singability). Towne's split dotted figure (19f) is covered by (a) where the split falls on the beat; elsewhere it is not tested. On the pre-review *Vox in Rama* the new rule leaves one of the review's eight breaks, Altus 12 (Marchesano's *-di-*, *-ta* on lone semiminims), and licenses the rest: Altus 11 (b), Altus 32, Bassus 27, Tenor 6, 37 and 40 (a).

Playing against the tactus (`meter.displaced_spans`). Miki's second review (Vox Altus 10.4: "the 3 top parts are clearly playing against the tactus here"; Altus 15: "the note values suggesting hemiola") showed passages where the accent moves off the tactus on purpose. A displaced note starts a minim off the tactus, is a dotted minim or longer and sounds across the next tactus. A span is either syncopation shared by two or more voices (displaced notes starting within a semiminim of each other, at least two of them taking a new syllable, extended by any displaced note within a tactus) or a hemiola-like chain in one voice (two or more displaced semibreves in a row, the first texted). It lasts until a tactus after its last displaced note, and applies to the voices that take part. There U210 counts the displaced pulse as a beat as well as the tactus, and U201 and U202 count half (gate `against_tactus`) where the span begins a phrase for the voice, and three quarters (`against_tactus_mid`) where it starts mid-phrase (`meter.mark_phrase_starts`: the voice's first displaced note, or the note up to a minim before it, begins new text). Miki, third review: the play "is most obvious when it begins a phrase (and its doubly obvious when these phrases are in homorhythm)"; mid-phrase, as in the *Vox* Altus at bar 12, Zieleński only hints at it. The homorhythm gate already multiplies the stress rules there. A suspension held in one voice is not a span. *Vox* has nine (bar 10 among them, Cantus, Altus and Tenor; Altus 15.4 as a hemiola), *Nunc scio* eight; both are listed in the review page's layer tables. The test is a count of note shapes, not a reading of the counterpoint: read the list before trusting a stress finding near one.

Key words (`editions.yaml: key_words`). *Vox in Rama*'s are confirmed (Miki, 5 October 2026): *vox*, *audita*; *ploratus*, *ululatus*; *plorans* (the main one of the piece), *suos*; *noluit*, with *consolari* as `rank: secondary` (it travels with *noluit*: listed and shown, no rule weight); *non*. *Rama* is not one. Each edition lists the words that carry the sense of each clause (*Dominus*, *angelum*, *Herodis*; *Rachel*, *plorans*, *filios*, *consolari* ...), each with a `source`. The analyser proposed these lists on 4 October 2026 from the texts, marked `source: "proposed, not confirmed"`, and a proposal has no effect. To confirm a word, change its source to `"MD, <date>"`; to reject it, delete the line. A confirmed key word is no longer a light word (U201, U205), and its stressed syllable weighs more when short (gate `key_word`). `analyse --layers` and the review page list both kinds.

Text (`text.py`, `lexicon/la.yaml`, `lexicon/pl.yaml`). Words grouped by `syllabic`, as the old audit grouped them. Each syllable's coda has a class (`coda_class`: open, sonorant, obstruent) and, for U208, a kind (`coda_kind`): a stop if a stop is anywhere in the coda (*it*, *et*, *est*, *nec*: Latin c is /k/), a fricative if fricatives only (*x*, *f*), and a sibilant for an s alone (*-tus*, *os*), the mildest. Each word has its syllables, stress and class (light, function, content, fragment; key words per edition) and the source of the decision. Latin stress follows the quantity rule (10.8), cross-checked against the old audit's table. Polish stress is the penult, checked by the loader, with exceptions listed as they arise. The editor has not yet confirmed the entries; `lexicon` lists how many. An unknown word gets the penultimate rule and an information finding (U501), never a silent guess.

Sonorities (`layers/sonority.py`). Vertical slices from music21's timespan tree, with attacks and sustains per voice. A fourth counts as dissonant only against the lowest sounding voice.

Dissonance (`layers/dissonance.py`). Suspension (with preparation, agent, resolution and figure such as 7-6 or 4-3), passing, accented passing, neighbour, cambiata, anticipation, échappée, and unexplained, after Morgan's taxonomy as described in the survey (§1.2), written from its definitions. Limits: no ornamental or fake suspensions, no chanson idiom, no dissonant third quarter, no separate ternary suspensions; those notes come out as unexplained or as passing notes. A held note against a moving voice on the tactus is tested as a suspension first.

Cadences (`layers/cadence.py`, `layers/cadence_tables.yaml`). Two voices moving by contrary step from a major sixth to the octave (or a minor third to the unison), arriving on the tactus with notes of a minim or more, give the cantizans and tenorizans. The other voices are labelled bassizans, altizans or evaded bass, and the type (authentic, phrygian, clausula vera, evaded, abandoned) comes from our own table, not CRIM's; an evaded bass does not override a bassizans in another voice. A 7-6 suspension into a major sixth that does not open to the octave gives an evaded or abandoned cadence. At the end of a section, a lowest voice rising a fifth or falling a fourth onto a held final under the tone gives a plagal ending (functions P and H; the final of *Vox in Rama*).

Each cadence has a closure score, a point each for: arrival notes of a semibreve or more (a minim under C), a rest after the arrival in a voice of the clausula, a suspension leading in, a bass (bassizans or plagal), and the end of a clause in the text on or just after the arrival. A complete clausula with fewer than two points (`full_closure`) is a weak figure: it is listed and drawn but not counted as a cadence, and U301 counts half there. Every cadence therefore has a kind (full, weak, evaded or abandoned), reported separately. CRIM's `cadences()` counts evaded and abandoned cadences with the full ones. *Vox in Rama*: 8 full and 4 evaded, 12 (CRIM 12), and 8 weak figures. *Nunc scio*: 20 full and 5 evaded, 25 (CRIM 24), and 5 weak figures. The totals agree; the places do not always: in *Vox* the two lists share 6 of their 12. CRIM has three the contrary-step test does not find (bars 13, 19, 35) and three the analyser finds weak (bars 23, 26, 34); the analyser has the plagal final and five figures CRIM does not list. Cadences without a contrary-step pair are not found. Read the cadence list before trusting a 10.3 finding.

Phrases (`layers/phrase.py`). From rest to rest (music21's `segmentByRests`), cut at section breaks, at cadence arrivals where a word ends, and after punctuation. Each phrase has a landing note, its temporal centre, where it has one: its longest note, at least a semibreve (a minim under C) and strictly longer than every other (Miki, 5 October 2026: "the 'landing' semibreve in a phrase of minims or shorter"). The stressed syllable of the key or last word belongs on it. U301 reads it: where the arrival is the landing note and carries its word's stressed syllable, and the last syllable takes the phrase's last note alone, a minim or longer, the late last syllable is right and is not flagged (*Vox* Cantus 39.3, *-la-* then *-ri*; *Nunc scio* Cantus and Tenor 55.3, *iudae-O-rum*). `analyse --layers` prints it as `[lands 39.3]`.

Contour accents (`meter.contour_accents`; information only, under investigation). After a run of short notes, the longer notes that the melody leans on: the run's goal (the first longer note), a turning point (a local high or low) and the centre (the pitch the run circles, its most frequent, counting the note before it). Such a note can carry an agogic or contour accent against the tactus. Miki on *Vox* Altus 33.3 (his "34.4"): "something about the melodic shape that makes the G the centre of gravity that side of the run, which also when sung actually encourages a strong beat against the tactus there. I don't know enough about the theory to articulate that further but it's something to investigate." No rule reads it yet; `analyse --layers` lists them (*Vox*: 56, too many to weigh without a better test).

Motifs (`layers/imitation.py: motifs`). A head with a dotted value and a leap, from an entry after a rest, sought at every note in every voice: the same values, repeated notes in the same places, other intervals within a step, the same direction throughout or inverted throughout (an inversion counts only inside the span of the direct occurrences). Occurrences within four breves of each other chain; three or more in two voices make a motif. U306 compares each occurrence's syllables with the text most occurrences carry.

Imitation (`layers/imitation.py`). Entries are first notes after a rest; the head motif is four notes. Two heads match when they are close in both intervals and rhythm: at most one interval differs, by a step (a flexed entry; this also admits a tonal answer, a fifth answered by a fourth), and flexed intervals plus differing values (all notes but the last) number at most two. Intervals alone can match by chance: in *Vox in Rama* the old test joined *ploratus et* (Bassus 16) to *Rachel plorans* (Tenor 19); the rhythm now keeps them apart, and the opening becomes one point of four voices. Where the evidence is strong an entry need not follow a rest: the note after a cadence arrival in its voice, or the first note of a new clause of the text, counts when six notes agree exactly in intervals and rhythm with another entry (*et noluit*, Tenor 28 in *Vox*). Entries within four breves of the previous one form a point: FUGA, PEN (equal time distances) or DUO. The three fugas the survey found with CRIM in *Nunc scio* (bars 1–3, 35–36, 61–64) are found, the last as 57–63.

Stanzas (rule U305, principles 10.14). In a strophic piece (`editions.yaml: strophic`; *Już się zmierzka*), a later stanza follows stanza 1 where its words fall alike. Each voice is cut at the notes where both stanzas start a word; in a segment where the later stanza has as many syllables as stanza 1, with the stresses and word breaks in the same places, each syllable it places differently costs 1. Where the words fall differently, the stanza may take its own underlay and nothing is flagged. *Zmierzka* has 28 such segments in its two stanzas and agrees in all of them.

Texture (`layers/texture.py`). A slice where every sounding voice attacks scores 1, all but one 0.5; four points in a row make a homorhythmic passage. A passage reaches back to the tutti entry that starts it (every voice attacks, two or more with new text after a rest or punctuation, on the tactus or off it) within a breve and a semibreve, with every voice sounding in between; and two passages with no rest between them and a gap of a semibreve or less are one. Miki, third review: the *Rachel plorans* section "runs from 23.2 (with the offbeat tutti entry) through to the end of 27"; the slice score alone gave 24.3–25.3 and 26.1–27.1, and now gives 23.2–27.1. In *Plaude* the same merging joins five passages into two (10.3–22.1, 27.1–36.1). For each passage the report gives how often the voices change syllable together. Principles 10.6 says the voices need not, so the related rule (U304) is information only.

Upper-voice duos (`layers/texture.py: duos`). Miki on *Vox*: the Altus and Cantus start together and "come in and out of each others rhythms". The two highest voices begin new text within a semiminim of each other; over the next three breves (or to a rest) they share between 30 and 85 per cent of their note onsets, and the page lists where they part and meet again. Information only; no rule reads it. *Vox* has seven, *Nunc scio* two.

The underlay model (`underlay.py`, `findings.py`). Syllables are aligned to the notes between rests; the first syllable after a rest is pinned (10.2) and no syllable crosses a rest. Firm rules decide legality; the rest are priced. A k-best dynamic programme over (syllable, start note) finds the best legal alternatives; rules that compare voices (imitation, homorhythm) are added afterwards and the candidates re-ranked.

The self-check (`selfcheck.py`). For every voice and verse it counts the syllables in `voices.ily`, in the MusicXML (read independently with music21), in the analyser's model and in the old audit's. All editions agree. The October review's export bug in the *Plaude* Tenor is not in the export: the MusicXML has all 53 syllables, and it was the old audit's tie merging that dropped five, on notes divided with a dashed tie (bars 14, 18 and 32).

## The review page

```
python -m tools.analyser review editions/vox-in-rama/pdf/vox-in-rama.musicxml --html tools/analyser/review/vox-in-rama.html
```

writes one self-contained HTML page for one piece (`review.py`, with `review_assets/app.css` and `app.js` inlined). The pages for *Vox in Rama* and *Nunc scio vere* are committed in `tools/analyser/review/`, and CI keeps fresh ones with its report. Regenerate them after a change to an edition or to the analyser.

Version 3 (5 October 2026) follows Miki's verdict on version 2: "things are out of reach, require a lot of page maneuvering, there's so much text on the pages that it all reads as noise, and the interface is broadly clunky (including the inline editor which would ideally be more Sibelius-like)". The page is now one screen with no document scroll:

- Top bar: the piece's title (click it for *About this piece*), progress (`14 / 39 decided`, with a thin line: the findings pending review or new), ‹ › to the previous and next finding, zoom (− Fit +), *Layers*, `?` for the keyboard shortcuts, the save state (Saved, Saving, Local only, with a tooltip) and ⋯ with *Copy edits as JSON*.
- The score canvas: the critical score as notation, filling the rest of the screen and scrolling inside itself. LilyPond 2.24 renders a small file that `\include`s the edition's `music/score.ly` with the SVG backend and point-and-click links, on one tall page, without the ambitus. Every note's link names its line and column in `voices.ily`; the source map gives the analyser's notes the same, so each drawn note carries its analyser id. The score stays on a white paper panel in dark mode. When a finding is active the canvas scrolls its passage to the centre, its notes get a soft red halo, the voice's lyrics in the span a soft band, and the other systems are dimmed.
- The findings rail (left, `[` or the ☰ button; a drawer on a phone): one compact row per finding, `bar.beat · voice · word`, a level mark (colour and shape: ◆ break, ▲ warn, ● look, ○ info), a tick when decided and Claude's suggested reading as a chip. Groups: *To review*, *Decided*, *Accepted earlier* (folded). Chips filter by voice and level (info off by default). Rows run in score order. Claude's custom recommendations (edits not tied to a finding) are rows of their own, marked *edit*.
- The inspector dock (under the score; a bottom sheet on a phone) shows one finding: a plain line in a singer's words (`review.plain`: "‘bis’ comes after the cadence on C"), with bar, voice, verse and word as a small label; the readings as tabs, *Current · A · B · C*, each with a small better/worse mark (▲, ▲▲ for a large gain, ▼) and *Suggested* on Claude's; and *Keep current* (K), *Take A* (Enter) and *Edit* (E). Choosing a tab redraws the lyrics in the score at once: the printed syllables that move are hidden, with the hyphens and extenders across them, and the reading's are drawn in the house red under the notes it gives them, with their own hyphens and extenders. After a decision the dock moves on to the next undecided finding in score order and offers *Undo* for a few seconds; a reason can be added afterwards (*Add a reason*). *Why* (W) opens the rule's name and principle, the analyser's message, Claude's recommendation if there is one, each alternative's moves and what it fixes and costs, the gates, cost and regret, the authority, the earlier review status and the text of the principle. None of these numbers is shown until asked for.
- Layers (L): cadences (on by default), dissonance, phrases, imitation, homorhythm, against the tactus (a line over each displaced note) and key words (a line under their syllables, dashed if proposed). They are drawn thin and without labels; hover a mark for its detail. Their legends are the tooltips on the toggles.
- *About this piece*: the counts by level and earlier review, the analysis numbers, the key words in context and, folded, the layers as tables and the words with their stress. Key words in context (Miki, second review: "presented in context of the verse (and with translations), rather than alphabetically"): the text line by line, as the edition prints it, with the edition's translation beside each line; confirmed key words filled, proposed ones dashed, the stressed syllable underlined (`keytext.py`).

Keyboard: → or J next finding, ← or Shift+J previous (K is *Keep*, so J/K could not be the pair); 1–4 show a reading; Enter takes it; K keeps the current; E edits; W why; U undo; `[` the rail; L layers; Z, X, F zoom out, in, fit; ? the list. Without LilyPond the page is written without the score.

### Editing the lyrics, Sibelius-style

E, or a double-click on a note, enters edit mode (a single click selects a note). From a finding, the caret starts on its first note, from the reading on show. The caret is a box under the note on the lyric line; the word being placed is shown small above it, its placed syllables faint and the next one red.

- Type the syllable: it appears under the note in red as you type. Typed without its printed punctuation or capital, it takes the text's own (*dis* is set as *dis,*).
- Space ends the word and moves to the next note; `-` hyphenates and moves on; `_` or Shift+Space holds the syllable over the next note (a melisma) and moves on; on an empty caret it makes this note part of the previous syllable.
- Backspace on an empty caret clears the note's syllable and moves back; Delete clears it without moving. ← → move between notes without changing anything; ↑ ↓ move to the voice above or below at the same moment; Tab changes verse (*Nunc*: antiphon and doxology; *Zmierzka*: the stanzas).
- A syllable on a note too short for one (a fusa; under ¢ a semiminim, which needs a licence of 10.1) is ringed in amber with the reason; nothing is blocked.
- Esc (or Enter, or *Done*) leaves edit mode. Edits are saved on leaving and after 1.5 s without typing: the voice's changed notes (changes up to four notes apart count as one passage) become one `custom` document each. Editing from a finding also records the finding as decided (`edited: true`).

The voice's text is fixed: typing re-places it. A typed syllable that the voice sings on another note nearby (the same word or about two words either side; punctuation and capitals ignored) moves here: its old copy is cleared, and when it came from a later note the notes in between become a melisma of the syllable before, so the word re-lays from the caret. The saved document covers the whole span (the new note set, the old one cleared), so `edits apply --dry-run` takes a typical move without `--allow-text` (tests: `test_review_editor.py`, *Nunc* Altus *He-ro-dis* with *ro* drawn back to 33.1, and a *Vox* Bassus syllable drawn back over a melisma). Only a syllable that is not in the voice's text nearby is a text change: it is kept, ringed in amber ("text differs from the source text"), and `apply` still asks for `--allow-text`.

Progress counts the findings pending review or new; where there are none (*Vox*, all accepted earlier) it reads "Nothing to review · 10 accepted earlier", and "All findings decided" once every one is.

### Saving

The page is published with `capabilities: {db: {}, user: {}}`. It asks for the db with `claude.use("db")` once rendered; until it answers, and where it never does (a local copy, a signed-out viewer), decisions and edits stay in the page and in the browser's storage, and the save dot says *Local only*. With a db, each is one document in the collection `edits`, written on every change, and a snapshot listener shows what is saved and the edits made in another view. A document:

```
edits/<slug>__<fingerprint without slug, or voice-v<verse>-b<bar>>
{ slug, kind: "alternative" | "custom", finding: <fingerprint> | null, rule, voice, verse,
  alternative: <k, 0 = keep the current> | null, edited?: true,
  notes: [{id: "Altus:37", bar: "12", pos: "2", pitch: "D5", where: "12.2", syllable: "di" | null, syllabic}],
  reason, status: "proposed" | "declined", recommendation?: <Claude's reason>, recAlternative?: <k>,
  updatedAt: <ISO>, by: <viewer id> | null }
```

An alternative's `notes` are every note of the finding's span (null: no syllable starts there); a custom edit's are the notes of one edited passage of a voice and verse (version 2's documents, one per bar, are read the same way). Only ids are stored, never names.

Claude's recommendations are documents whose reason begins `Claude's recommendation:` (seeded into the db, and committed beside the page as `review/<slug>.recommendations.json`, which the page embeds so they show without a db too). They show as *Suggested* until the editor decides: taking or keeping replaces the document with his decision and keeps Claude's reason in `recommendation`; keeping a custom recommendation marks it `status: "declined"`, which `edits apply` skips. Claude reads the documents with the artifact's db (`ArtifactData`, collection `edits`), or the editor pastes the copied JSON into the chat.

Applying.

```
python -m tools.analyser edits apply edits.json --dry-run
```

takes the documents (a JSON list, or `{"edits": [...]}`), groups them by piece, voice and verse, and for each prints the syllables as they stand and as the edit asks (`bar pitch:syllable`, `-` where the word goes on, `·` for none), then the diff of `voices.ily`. Without `--dry-run` it writes the file. It refuses, saying why, an edit whose notes are not in the score, one that changes the words (a dropped or added syllable: `--allow-text` when that is meant, 10.13), one that leaves the first note without its syllable, and a voice whose lyrics do not tie or do not rebuild. *Nunc*'s `voices.ily` is generated by `music/build.py` from `music/underlay.py`, so for *Nunc* it prints what to change and leaves the file alone. The analyser still never changes an edition by itself: `apply` writes only what the editor decided on the page.

## Tests

`tools/analyser/tests/`: the rule examples; the port against `tools/underlay_audit.py` on every edition and on the *Vox in Rama* of commit bb75083, before the review fixed its eight breaks (one under the rewritten 10.1); unit tests for each layer; the model (legality, regret, anchors, gates); the review cases (on the pre-review *Vox in Rama* the rewritten 10.1 licenses six of the review's eight breaks and leaves Altus 12, where the model still finds no move-only fix; and Miki's verdicts of 4 October 2026, below); the self-check; the baseline; the gaps closed on 4 October 2026 (`test_gaps.py`: text edits, stanzas, key words, inline acceptance, attributable regret, cadence closure and plagal endings, stricter imitation, SARIF); the review page (`test_review.py`; the score test is skipped without LilyPond); and golden snapshots of every edition's findings and layers (`tests/golden/`). A change to a snapshot is a fix or a regression: look at the diff before `golden --update`.

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

Miki's second review (4 October 2026; `books/MIKI-VOX-REVIEW-2-2026-10-04.txt`), on the *Vox* of commit ee0dcc9 (`tests/fixtures/vox-in-rama-ee0dcc9.musicxml`; cases in `tests/test_review_cases.py`, `test_miki2_*`):

| Pattern | Rule |
|---|---|
| "Penalise fricatives far less than stops ... particularly s"; Polish is "a much more fricative language", so "limit to latin only" | U208 applies to Latin only; its amount is multiplied by the coda's kind (`params.kinds`: stop 1, fricative 0.2, s 0.1) |
| Polish clusters cannot be solved, but can be removed "in particularly tricky spots like short note changes" | U209: Polish clusters count twice (`pl_factor`), and a Polish cluster of three or more also counts at a change after a minim under cut-C (`pl_short`) |
| Altus 41.4 *quia*: QUI-a (the lexicon agrees); *qui* has nowhere better to go, and "there's no reason to force 'a' off a strong beat" | U210 is the stressed syllable's alone: it is flagged only if a note on the beat that may take a syllable lies within its reach, and an unstressed syllable on the bar no longer counts, so moving it answers nothing |
| Altus 10.4 *Ra*: "the 3 top parts are clearly playing against the tactus here"; Altus 15 *la* off the tactus, "the note values suggesting hemiola" | metre layer `displaced_spans`; U210 accepts the displaced pulse as a beat there; gate `against_tactus` halves U201 and U202 |
| The Altus and Cantus "starting together", then "coming in and out of each others rhythms" | `texture.duos`, information on the review page |
| Key words in the verse, with translations | review page, *Key words in context* |

On the pre-review *Vox* (bb75083) the first alternative at Altus 11 is no longer *Ra* drawn back to 10.3 but the review's own drop of *est*: Ra on 10.4 is right. On the current *Vox* the U210 findings at Altus 10.4, 11.4, 12.3 and 41.4 are gone, and the one at Altus 36.4 (Miki's approved alternative 1) stays. The accepted U301 at Cantus 39.3 now shows a regret of 1.5: inside the displaced span from 38.4, *la* on 39.2 is on the displaced pulse, so the alternative that ends the phrase on the arrival costs nothing under U210.

What the analyser could not yet do with his verdicts (the third review settled the last): it never restores a dropped word, so the *et noluit* findings at Altus 31.4 and Tenor 37.4 have no lawful alternative and stay information (an xfail case); his Tenor *la* at 40.1 falls on a semiminim, which 10.1 (U101) forbids under cut-C; and his Cantus 39.3 (*la*, the stressed syllable, on a weak cadence) is not a rule.

Miki's third review (5 October 2026; `books/MIKI-VOX-REVIEW-3-2026-10-05.txt`), on the *Vox* of commit 9227043 (`tests/fixtures/vox-in-rama-9227043.musicxml`; `test_miki3_*`). It finished *Vox in Rama*: no finding is left open.

| Pattern | Rule |
|---|---|
| Cantus 39.3, a false flag: "Stress syllable 'la' arrives on cadence and strong beat (and the temporal centre of the phrase, that being the 'landing' semibreve in a phrase of minims or shorter), and the final syllable 'ri' occurs on the last minim of the phrase" | phrase layer `landing`; U301 does not flag a late last syllable when the stressed syllable is on the landing note at the arrival and the last syllable alone on the phrase's last minim. *Qui* on 40.2, the next landing, is not flagged either |
| The homorhythm of *Rachel plorans* begins at the offbeat tutti entry, 23.2, not 24.3 | texture: a passage reaches back to a tutti entry and joins its neighbour across a short gap |
| Altus 33.3 (his "34.4"): the G is the melodic centre of gravity after the run and invites a strong beat against the tactus | `meter.contour_accents`, information only, under investigation; the U210 at 33.4 is accepted beside the note |
| The play against the tactus is meant to be heard when it begins a phrase, doubly in homorhythm; mid-phrase it is a hint (Altus 12) | gate `against_tactus` at a phrase start, `against_tactus_mid` (0.75) mid-phrase |
| Altus 12: his own reading kept outside 10.1 for singability ("double break the rules") | accepted beside the note (U101, U102), the ground named in the critical note |
| Bassus 27.3, alternative 1 approved: inter-part unity in the homorhythm, and no s–s across a fusa | applied: *su-* on 27.1 under 10.1(a) |
| Tenor 6: bring back *in* | restored: *Ra-* on the first semiminim of the run, 10.1(a) |
| Key words line by line | confirmed in `editions.yaml`, *consolari* secondary |

## Known limits

- Weights are hand-set. They have not been calibrated against texted sources (survey §3.3, step 7 of the build order).
- Text edits are limited to dropping a droppable or doubled word and repeating one word; the analyser does not propose repeating a clause or changing the text otherwise. The edit costs are judgements (`settings.yaml`).
- The key words of every edition but *Vox in Rama* are proposals until the editor confirms them (`editions.yaml`); until then the key-word class has no effect.
- Contour accents are counted, not weighed: no rule reads them yet, and the phrase-start test for playing against the tactus follows the current underlay.
- The displaced-pulse spans are found from note shapes and texted syncopations only; the reach U210 uses for "a beat it could take" follows the current underlay's neighbours, not every reading the search may try.
- Stanza consistency compares later stanzas with stanza 1 only.
- Cadence closure is a count of five signs, not a calibrated measure; the threshold of two puts the totals of full and evaded cadences near CRIM's.
- The Latin and Polish lexicons await the editor's confirmation.
