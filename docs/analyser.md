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
python -m pytest tools/analyser/tests -q
```

`-v` adds, for each finding, the source line in `voices.ily`, the costs in its window and up to three alternatives. `--info` also lists the information-level findings. `--format text,json,markdown,github` and `--out DIR` choose the outputs; the CI job uses Markdown for its summary and `github` for annotations.

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
- Regret: how much the best legal underlay nearby that solves this finding scores better than the underlay as it stands. Only syllables within two of the finding may move, and only between the same rests. A syllable with punctuation stays where the editor put it, except for a 10.3 finding: 10.6 places each line's last syllable on its cadence first.
- Level: `break` for a firm rule (10.1, 10.2, 10.4, 10.5). 10.3 is firm too, but the analyser can only check it against the cadences it detects, so it prices it (U301, the highest weight) instead of failing on it. Otherwise `warn` (regret 2 or more), `look` (0.75 or more) or `info`. A finding with no better legal alternative is information, however often it occurs: a run on *et* that nothing lawful can avoid is not a problem to solve.
- `try:` lists the alternatives, each with its change in cost and the rules it fixes or costs.

## Accepting a finding

The baseline, `tools/analyser/baseline.json`, lists findings by fingerprint: edition, voice, verse, rule, word, syllable within the word, and occurrence. Bar numbers are not part of it, so renumbering does not reopen anything. Each entry has a status and a reason:

- `accepted`: the editor keeps the underlay. Give the reason, normally a source reading kept under 10.12 or a choice the method section records. Example: the long *con-* in every voice of *Vox in Rama*, which is the print's own.
- `pending`: present when the analyser was introduced (4 October 2026) and not yet reviewed. Pending findings stay in the job summary's list of open findings but do not count as new.

To accept a finding, find its fingerprint (in `-v` output or `--format json`), set `status` to `accepted` and write the reason. `--update-baseline` adds every current finding that is not yet listed as pending, keeps the reasons already written, and drops entries whose finding has gone; review its diff like code.

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
| suspension | dissonance | a syllable on a suspension counts a quarter (Vicentino's exception) |
| full_point | imitation | imitation text counts half again in a point of three or more entries (10.10) |
| homorhythm | texture | stress-short and light-on-beat count half again where the voices declaim together (10.6) |
| older_practice | edition | stress and light-word rules count half in an older piece (Towne 1990, 285); set for *Plaude* |

## The layers

Ingest (`ingest.py`). Our MusicXML, read as the old audit read it, with ties merged except the dashed ties of notes divided for text (10.13), rests kept, second endings and unmeasured chant sections marked as breaks, and the LilyPond source of every note from `<slug>.srcmap.tsv`. Durations are in semiminims. The chant part of *Nunc scio* is not analysed.

Metre (`meter.py`). The bar is a breve; the tactus is the semibreve, so the half-bar is a beat. The sign decides which value may take a syllable (10.1): a minim under cut-C or no sign, a semiminim under C. Signs come from the MusicXML, and `editions.yaml` supplies them where the edition prints none: *Plaude* is read as C, because the critical edition describes imperfect tempus and minor prolation. That is a reading to confirm.

Text (`text.py`, `lexicon/la.yaml`, `lexicon/pl.yaml`). Words grouped by `syllabic`, as the old audit grouped them. Each word has its syllables, stress and class (light, function, content, fragment; key words per edition) and the source of the decision. Latin stress follows the quantity rule (10.8), cross-checked against the old audit's table. Polish stress is the penult, checked by the loader, with exceptions listed as they arise. The editor has not yet confirmed the entries; `lexicon` lists how many. An unknown word gets the penultimate rule and an information finding (U501), never a silent guess.

Sonorities (`layers/sonority.py`). Vertical slices from music21's timespan tree, with attacks and sustains per voice. A fourth counts as dissonant only against the lowest sounding voice.

Dissonance (`layers/dissonance.py`). Suspension (with preparation, agent, resolution and figure such as 7-6 or 4-3), passing, accented passing, neighbour, cambiata, anticipation, échappée, and unexplained, after Morgan's taxonomy as described in the survey (§1.2), written from its definitions. Limits: no ornamental or fake suspensions, no chanson idiom, no dissonant third quarter, no separate ternary suspensions; those notes come out as unexplained or as passing notes. A held note against a moving voice on the tactus is tested as a suspension first.

Cadences (`layers/cadence.py`, `layers/cadence_tables.yaml`). Two voices moving by contrary step from a major sixth to the octave (or a minor third to the unison), arriving on the tactus with notes of a minim or more, give the cantizans and tenorizans. The other voices are labelled bassizans, altizans or evaded bass, and the type (authentic, phrygian, clausula vera, evaded, abandoned) comes from our own table, not CRIM's. A 7-6 suspension into a major sixth that does not open to the octave gives an evaded or abandoned cadence. Limits: the detector finds more cadences than CRIM did in the survey (30 against 24 in *Nunc scio*, 19 against 12 in *Vox*), because it does not weigh how strongly a clausula closes; plagal endings and cadences without a contrary-step pair are not found. Read the cadence list before trusting a 10.3 finding.

Phrases (`layers/phrase.py`). From rest to rest (music21's `segmentByRests`), cut at section breaks, at cadence arrivals where a word ends, and after punctuation.

Imitation (`layers/imitation.py`). Entries are first notes after a rest; the head motif is four notes. Entries match on their intervals, allowing one interval to differ by a step, within four breves of the previous entry. Points are FUGA, PEN (equal time distances) or DUO. The three fugas the survey found with CRIM in *Nunc scio* (bars 1–3, 35–36, 61–64) are found, the last as 57–63. Limits: entries after a cadence without a rest are missed; a four-note head can match by chance.

Texture (`layers/texture.py`). A slice where every sounding voice attacks scores 1, all but one 0.5; four points in a row make a homorhythmic passage. For each passage the report gives how often the voices change syllable together. Principles 10.6 says the voices need not, so the related rule (U304) is information only.

The underlay model (`underlay.py`, `findings.py`). Syllables are aligned to the notes between rests; the first syllable after a rest is pinned (10.2) and no syllable crosses a rest. Firm rules decide legality; the rest are priced. A k-best dynamic programme over (syllable, start note) finds the best legal alternatives; rules that compare voices (imitation, homorhythm) are added afterwards and the candidates re-ranked.

The self-check (`selfcheck.py`). For every voice and verse it counts the syllables in `voices.ily`, in the MusicXML (read independently with music21), in the analyser's model and in the old audit's. All editions agree. The October review's export bug in the *Plaude* Tenor is not in the export: the MusicXML has all 53 syllables, and it was the old audit's tie merging that dropped five, on notes divided with a dashed tie (bars 14, 18 and 32).

## Tests

`tools/analyser/tests/`: the rule examples; the port against `tools/underlay_audit.py` on every edition and on the *Vox in Rama* of commit bb75083, before the review fixed its eight breaks; unit tests for each layer; the model (legality, regret, anchors, gates); the self-check; the baseline; and golden snapshots of every edition's findings and layers (`tests/golden/`). A change to a snapshot is a fix or a regression: look at the diff before `golden --update`.

## Known limits

- Weights are hand-set. They have not been calibrated against texted sources (survey §3.3, step 7 of the build order).
- The search moves syllables only. It does not propose dropping or repeating words (10.13), or changing the text.
- Key words are not marked in any edition yet (`editions.yaml`), so the key-word class has no effect.
- Strophic consistency (10.14) is not a rule: each stanza is judged on its own.
- The Latin and Polish lexicons await the editor's confirmation.
