# Underlay analyser: survey of tools and a recommended design

Research note, 4 October 2026. Scope: what exists that could help us build a multivariate underlay analyser for the series (Latin motets and Polish songs, three and four voices), what to borrow, what to avoid, and how to build it. Our current tool is `tools/underlay_audit.py` (a single-pass rule checker over MusicXML: BREAK for principles 10.1–10.4, LOOK for six tendencies of 10.6). The rules it serves are in `docs/editorial-principles.md` §10.

**Short answer.** Nobody has published a working automatic underlay checker or generator for sixteenth-century polyphony. The musical analysis we need does exist, mostly from one lineage: Alexander Morgan's dissonance and cadence work, continued in CRIM `crim_intervals` (Python, pandas, music21) and in Craig Sapp's `humlib` (C++). Build a small core of our own on music21: our own event model, text layer and rule engine. Take CRIM's ideas and data (cadential voice functions, presentation types, the golden-file test) rather than its code. Keep humlib as an optional cross-check. Treat underlay as an alignment problem, with weighted constraints, a search for the best legal alternatives, and severity measured as the gap between what we have and the best alternative. Wrap it in linter machinery (rule IDs, levels, examples that act as tests, a baseline file, PR annotations).

---

## 0. What was tried

Everything was run in a scratch venv, outside the repo, on the MusicXML from `make musicxml` (music21 10.5.0, pandas 3.0.5 / 2.3.3, numpy 2, Python 3.13). The chant part (`Versus (chant)`) was stripped first.

| Test | Result |
|---|---|
| `pip install crim_intervals` (2.0.78) | Hangs. It pins `music21==8.3.0`, `numpy<2.0` and about 25 other exact versions, and there is no numpy 1.x wheel for Python 3.13. Installing with `--no-deps` on top of our stack works. |
| CRIM `cadences()` on *Nunc scio*, *Vox in Rama* | Works, about 2 s per piece. *Nunc scio*: 24 cadences (Authentic, Clausula Vera, Phrygian, Evaded…), each with bar, beat, tone and the voice functions (e.g. `CuTB`). *Vox*: 12. Plausible on inspection. Three evaded cadences in *Vox* have no tone (`NaN`, LeadingTones −1). |
| CRIM `homorhythm()` | Works. It also reports whether the homorhythmic voices carry the same syllables (`voice_match`), which bears directly on 10.10. |
| CRIM `presentationTypes()` | Crashes under pandas 3. A `stack()` now keeps NaN, and the code casts the result to `int`. Under pandas 2.3 it works: *Nunc scio* has 3 fugas (bars 1–3, 35–36, 61–64), *Vox* has 4, *Zmierzka* none (it is homophonic, so that is correct). |
| verovio 6.3 Python (embeds humlib) | Segfault or floating-point exception on loading our MusicXML, so humlib filters can't be run through verovio. |
| humlib built from source (HEAD of 20 Sept 2026, BSD-2) | The library takes about 25 minutes to build on 2 cores. `dissonant` works on Humdrum input: in a hand-written test it labelled a 7–6 upper-voice suspension and a 2–3 bass suspension, each with its agent, correctly. But `musicxml2hum` segfaults on *every* MusicXML file, ours and a trivial one written by music21. So for now the humlib tools can't be run on our scores without a working converter. |
| music21 10.5 | Parsing, lyrics with `syllabic`, `stripTies`, timespan-tree verticalities and `search.lyrics.LyricSearcher` all work on our files. `figuredBass.checker` crashes on rests. `beatStrength` under 2/1 is the modern hierarchy, not a tactus. |
| CLTK | 2.5.1 has dropped its prosody modules (it is now an LLM-centred pipeline, Python ≥3.13). The 1.0.25 Latin syllabifier (MIT) gets *e-ri-pu-it* wrong (`er-i-pu-it`), rewrites *Iudaeorum* as `ju-dae-o-rum`, and assigns no stress. |
| Pyphen `pl_PL` with `left=1, right=1` | Good Polish syllables for our test words (*i-dą*, *Ma-ry-ja*, *zmierz-ka*, *na-szem*, *swo-ję*, *zro-bi-li-śmy*). It has no Latin dictionary. |
| Morfeusz 2 (`pip install morfeusz2`) | Tags modern function words correctly (*w* prep, *się*/*już* part, *by* comp/part). Old forms come back `ign` (*zmierzka*, *naszem*, *jenż*, *wszytki*) or wrong (*swoję* → verb *swoić*). |
| Current audit, all editions | 0 BREAK; 23/9/4/11 LOOK (*Nunc*, *Vox*, *Plaude*, *Zmierzka*). |

---

## 1. Tools and projects

Verdicts: **Use** (as a dependency), **Borrow** (ideas, data or algorithms; reimplement), **Reference** (read it; don't depend on it), **Avoid**.

### 1.1 CRIM `crim_intervals` — Borrow (ideas and tables), optional dependency for cross-checks

- **What**: the analysis library of *Citations: The Renaissance Imitation Mass* (Richard Freedman, Haverford; with Alexander Morgan, Daniel Russo-Batterham and others). Repo: <https://github.com/HCDigitalScholarship/intervals>; PyPI `crim_intervals`; docs in the repo's `tutorial/`. It loads MEI, MusicXML or MIDI into an `ImportedPiece`, and every analysis is a pandas DataFrame indexed by offset, with one column per voice.
- **Relevant methods** (all in `crim_intervals/main_objs.py`):
  - `notes`, `durations`, `melodic`, `harmonic`, `lyrics`, `beatStrengths`, `detailIndex` give the voice × offset grids.
  - `ngrams(how='modules')` builds contrapuntal modules: harmonic interval plus both voices' melodic motion, e.g. `7_1:-2, 6_-2:2, 8`. This is the representation everything else rests on.
  - `cvfs()` assigns **cadential voice functions** per voice. It matches regexes over module n-grams against `data/cadences/CVFLabels.csv` (133 patterns) to give C cantizans, T tenorizans, B bassizans, A altizans, Q quintizans, S sestizans, L, P, plus evaded (c, t, b, u, s) and abandoned (x, y, z) forms. `cadences()` then maps the combination of CVFs to a cadence type through `cadenceLabels.csv` (58 regex rows: Authentic, Clausula Vera, Phrygian, Evaded…, with leading-tone count and the cadential tone).
  - `presentationTypes()` classifies imitative entries into FUGA, PEN (periodic entry), ID (imitative duo), NIM (non-imitative duo) and HR, from melodic n-gram entries (`entries()`: n-grams that start after a rest or a section break) and their time and pitch intervals. `flexed_distance` allows inexact imitation.
  - `homorhythm()` finds regions where at least two voices share durational n-grams. It also reports syllable n-grams and whether they match.
  - `markFourths()` and `ic()` (invertible counterpoint).
- **Quality and maintenance**: active (74 commits in 2026; release 2.0.78, July 2026). There is a golden-file regression test (`test_cadences.py`, which compares two hand-checked pieces against stored tables). CI on push runs flake8 and tests on Python 3.10–3.12. The weak points: one 5,700-line class; `from music21 import *`; `verovio`, `plotly`, `seaborn`, `altair` and `IPython` imported at module level; exact pins three years old; tests fetch MEI over HTTP; and the pandas 3 break above. It is notebook-first research code, competent and in daily use, but not built as a library to depend on.
- **Licence**: the README says CC BY-SA 4.0, and `pyproject` says "creative commons". That is a content licence, and ShareAlike. We can depend on it unmodified. If we copy `CVFLabels.csv` or `cadenceLabels.csv` into our MIT code, those files (and arguably their adaptations) must stay CC BY-SA with attribution. Keep any copied table as a separate data file with its own licence header, or write our own table from the published definitions.
- **Borrow**: (1) the CVF model: label each voice's cadential role, then classify the cadence from the set of roles. This gives cadence type, arrival offset and *which voice carries the clausula*, which is what rule 10.3 needs. (2) Rules as data tables of regexes over interval-module strings: easy to read, test and extend. (3) The presentation-type vocabulary, so 10.10 can name what it found. (4) `homorhythm`'s syllable match as a measure for 10.10. (5) The golden-file test.
- **Avoid**: using it as the core runtime dependency. It would freeze us at pandas < 3 and drag in a plotting stack. Its index (offset in quarter notes, "beat" from the modern meter) also doesn't match our semiminim/tactus units.

### 1.2 humlib and the Humdrum tools — Reference, optional cross-check

- **What**: Craig Sapp's C++ library and command-line tools for Humdrum (<https://github.com/craigsapp/humlib>). It is the engine behind the Verovio Humdrum Viewer and the Josquin Research Project's analyses. BSD-2-Clause. Very active (commits in September 2026, mostly by Morgan on `autocadence`).
- **Relevant tools** (`src/tool-*.cpp`):
  - `dissonant`: Morgan's Renaissance dissonance taxonomy, 48 labels. It covers passing and neighbour notes up and down, échappée, short and long cambiata, anticipation, dissonant third quarter, accented passing tones, binary and ternary suspensions with their **agents**, fake suspensions, the chanson idiom, ornamental suspensions, and labels for unexplained dissonances. This is the most serious open dissonance classifier for this repertory. The older Python version lived in VIS (§1.4).
  - `autocadence` (2025–26): cadence formulas as regexes over interval strings, with CVF labels, the same idea as CRIM's in newer code.
  - `imitation`: pairwise imitation by interval matching, with a threshold and maximum distance.
  - `homorhythm`: a sonority score (1.0 for three or more attacks, 0.5 between, threshold 4.0). The weighting is simple and easy to port.
  - `melisma`, `textdur`: notes and durations per syllable.
  - `cint`: contrapuntal interval modules and lattices.
  - Also `synco`, `metlev` and `musicxml2hum` (the converter).
- **How to use**: as a CLI over Humdrum. **Blocker (tested)**: the MusicXML-to-Humdrum step fails. `musicxml2hum` at the current HEAD segfaults on any MusicXML, and verovio 6.3's embedded converter crashes on ours. The way round is to write `**kern` ourselves. This is easy from our own event table (`tools/musicxml-events.ily` already gives exact moments) and is a good independent export check. Alternatively, pin an older humlib release. Building the library takes about 25 minutes on 2 cores, so cache it in CI or keep it for local and nightly runs. `dissonant` itself works (checked on a hand-written two-voice passage).
- **Borrow**: the dissonance label set and its decision logic (port the subset we need: suspension with preparation, dissonance and resolution; passing; neighbour; cambiata; anticipation; chanson idiom). Use the label names so our output can be checked against `dissonant`.

### 1.3 music21 — Use (foundation)

- <https://github.com/cuthbertLab/music21>, BSD-3-Clause, v10.5, actively maintained, with a large test suite. It is the safe base.
- **Use**: `converter.parse` for MusicXML; `Note.lyrics[].syllabic`; `stripTies`; `tree.fromStream.asTimespans(...).iterateVerticalities()` for fast sonority slices with start, sustain and stop per voice (the right structure for dissonance analysis); `interval.Interval`; `voiceLeading.VoiceLeadingQuartet` (parallel and hidden perfect intervals, motion types); `search.lyrics.LyricSearcher` (finds text across notes; handy for 10.10); `analysis.segmentByRests` (first-cut phrase units).
- **Don't rely on**: `beatStrength` and `TimeSignature` hierarchies (modern metre; we need a tactus model by mensuration, since 10.1 depends on C vs ¢); `roman`, `key` and `analysis.discrete` (tonal; *Nunc scio* comes out "F major"); `figuredBass.checker` (a chorale teaching checker that crashes on rests); `features.jSymbolic` (corpus classification, not passage diagnosis). `alpha.theoryAnalysis` no longer exists.

### 1.4 VIS-framework (ELVIS, McGill) — Avoid

<https://github.com/ELVIS-Project/vis-framework>, AGPL-3.0. It pins `music21==2.1.2` and `pandas==0.17.1`, and was last pushed in 2022. It holds historical value: the interval n-gram indexers and Morgan's first `dissonance.py` indexer. Both live on in CRIM and humlib. Don't install it, and don't copy it (the licence is AGPL).

### 1.5 Josquin Research Project — Reference

<https://josquin.stanford.edu>. A web interface over a Humdrum corpus, with analyses supplied by humlib tools. It offers no separate library to depend on. Useful as a model of how analyses are shown (colour-coded dissonance and cadence overlays on the score) and as a source of comparison data. Check the data licence before using its scores for calibration.

### 1.6 DCML standards, ms3, dimcat — Avoid (the wrong repertory and input)

`ms3` (GPL-3.0) and `dimcat` (GPL-3.0) parse MuseScore files and the DCML harmonic annotation standard (Roman numerals, tonal). One idea is worth taking: analyses as plain TSV tables in the repo, with a documented column standard, so that diffs are reviewable.

### 1.7 partitura — Reference only

<https://github.com/CPJKU/partitura>, Apache-2.0, well maintained. Built for performance research (score–performance alignment, note arrays). Its structured `note_array` (onset and duration in beats and quarters, voice, id) is a good model for our event table. We don't need the dependency.

### 1.8 musif — Avoid

`musif` (MIT, DIDONE project): bulk feature extraction for opera arias, including syllabic and melismatic ratios. It is a corpus statistics tool, not a passage checker.

### 1.9 Counterpoint checkers — none worth depending on

Open species-counterpoint checkers (many GitHub projects, often built on music21) apply first- to fifth-species rules to two-voice cantus-firmus exercises. They are pedagogical, and free sixteenth-century counterpoint with ties, cadences and syncopations defeats them. The serious work is the Morgan taxonomy (humlib `dissonant`). Build on that.

### 1.10 Texture recognition (SEILS, ISMIR 2021) — Reference

Parada-Cabaleiro et al., 'Automatic Recognition of Texture in Renaissance Music', ISMIR 2021 (<https://archives.ismir.net/ismir2021/paper/000063.pdf>; code at github.com/SEILSdataset/Texture_Recognition). It classifies antiphonal, contrapuntal and homorhythmic texture in 30 madrigals with SVM, MLP, CNN and BLSTM; the best is about 51 % unweighted average recall over the three classes. Too weak to use. Rule-based homorhythm (CRIM, humlib) is better here.

### 1.11 Text-underlay research

- **No open software** for checking or generating underlay in sixteenth-century polyphony turned up in this survey. (Search terms: computational underlay, automatic text underlay, Renaissance, Josquin, Humdrum, music21.) Lyrics-to-audio alignment (ISMIR) is a different problem: it aligns audio, not notation.
- **Musicological rule systems** (already in `docs/research/literature/`): Towne 1990/91 is the closest thing to a specification, with rules formalised from Lanfranco, Zarlino, Vicentino and Stoquerus. Harrán 1973a/b and 1997. Stoquerus (Rotola ed.).
- **Linguistic textsetting** (the strongest design precedent):
  - Halle & Lerdahl, 'A Generative Textsetting Model', *Current Musicology* 55 (1993).
  - Hayes & Kaun, 'The Role of Phonological Phrasing in Sung and Chanted Verse', *The Linguistic Review* 13 (1996).
  - Hayes, 'Textsetting as Constraint Conflict', in *Towards a Typology of Poetic Forms* (Benjamins, 2009; <https://brucehayes.org/Textsetting>). Four violable constraints: stressed syllables to strong positions, avoid long gaps without a syllable onset, avoid compression, align phrase boundaries with line ends. They are ranked, and the best setting is the one that sacrifices the lowest-ranked goal. That is our 10.6 ("tendencies to weigh") in formal dress.
  - Girardi & Plag (2019) on metrical mapping in textsetting.
- **`prosodic`** (Apache-2.0, <https://pypi.org/project/prosodic/>): a maintained Python metrical parser for English and Finnish verse. It scores all parses of a line against weighted, violable constraints and returns them ranked. The architecture we want, applied to verse rather than music. Read its constraint and parse code; don't depend on it.

### 1.12 Latin

- **CLTK** (<https://github.com/cltk/cltk>): 2.x (current) has no prosody. 1.0.25 (MIT) has a rule syllabifier and a POS-based macronizer that needs model downloads. In our test it was unreliable on our words, and it has no stress. **Avoid** as a runtime dependency.
- **Collatinus** 11.2 (Biblissima; GPL-3.0; C++/Qt; <https://github.com/biblissima/collatinus>): a lemmatiser with a lexicon of vowel quantities. It marks accents and hyphenation, scans text, and has a console client and a server mode. **Use offline** to propose stresses for new words, which a human then confirms into our lexicon. Don't link it (GPL, Qt).
- **Liturgical accents**: Vatican and Solesmes books print the accent on every word of three or more syllables. Chant transcriptions (GregoBase gabc) usually keep those accents. Divinum Officium's Latin texts were not checked here. These are good seed sources, but each needs checking against Kraków practice (10.8).
- **Recommendation**: a reviewed series lexicon file (word → syllables, stressed syllable, word class, source of the decision), seeded from `STRESS` in `underlay_audit.py`. Our texts are short; a few hundred entries cover the series. A regular penultimate-rule fallback, with a WARN whenever a word is not in the lexicon, is better than a silent wrong stress.

### 1.13 Polish

- **Syllables**: Pyphen (<https://github.com/Kozea/Pyphen>; tri-licensed GPL/LGPL/MPL; bundles LibreOffice `hyph_pl_PL`) with `left=1, right=1`. Hyphenation patterns are not phonological syllables, so keep an override list.
- **Stress**: modern Polish is fixed on the penult. The exceptions (*-yka* loans, *-liśmy/-liście*, a few clitic groups) are lexical, and so is any Old Polish exception. Syllabic verse also has a paroxytonic cadence at the caesura and the line end. That is a phrase-level constraint we can encode, and it drives 10.14 (stanzas with different stress patterns).
- **Word class**: Morfeusz 2 (IPI PAN; BSD-2; `pip install morfeusz2`) for the modern-identical function words. It does not know Old Polish forms (tested), so the lexicon overrides it. The KORBA historical-corpus work at IPI PAN has adapted analysers for 17th–18th-century Polish; that is worth a follow-up if the Polish corpus grows, but too late a period to rely on.
- spaCy and Stanza Polish models are overkill here; check their licences before any use.

---

## 2. Lessons from adjacent fields

| Field | Lesson | Where we use it |
|---|---|---|
| **Vale** (prose linter, MIT) | Rules are YAML files, each with `extends` (a rule template: existence, substitution, occurrence, sequence…), `message`, `level` (suggestion, warning, error) and a `link`. Styles are folders, so a project can turn a rule off or change its level without touching code. | Rule metadata in YAML: ID, level, weight, principle reference, message template. The logic stays in Python. |
| **LanguageTool** (LGPL) | Each XML rule carries `<example correction="…" type="incorrect">` and correct examples. The test suite runs every rule over its own examples, so a rule without examples doesn't pass review. | Every rule ships with must-flag and must-not-flag passages, run by pytest. |
| **proselint** (BSD) | Few rules, high precision, each with a citation to the authority it follows. | Each rule cites its principle (§10.x) and theorist. A low-precision rule stays at LOOK. |
| **ruff, ESLint** | Stable rule codes. Severity is configured, not hard-coded. Inline suppression (`# noqa: E501`) with a reason. Fixes are labelled safe or unsafe, and ESLint separates fixes from *suggestions*. | Codes like `U101`. A suppression comment in the LilyPond source (`% underlay: ok U205 source reading`) maps naturally to principle 10.12 (departures the source shows). Alternatives are always *suggestions*, never auto-applied. |
| **Baselines** (PHPStan, detekt, Psalm; Semgrep `--baseline-commit`) | Record the accepted violations once; CI fails only on new ones. Fingerprints must survive unrelated edits. | Baseline keyed on (edition, voice, verse, rule, word, syllable index within the word, occurrence), not bar number. |
| **SARIF, GitHub annotations, reviewdog** | SARIF 2.1.0 is the interchange format for code scanning: rules, results, locations, fingerprints. Code-scanning upload is free on public repos and needs GitHub Advanced Security on private ones. Workflow-command annotations are capped per step and per job. reviewdog (MIT) turns any linter output into PR review comments, filtered to changed lines. | Output to a job summary (Markdown) plus annotations on new findings only, at `music/*.ly` file:line. SARIF if the repo is public. |
| **Chess engines** (Stockfish; Lichess game reports) | A move is judged by how much worse it is than the engine's best move (centipawn or win-chance loss). Labels (inaccuracy, mistake, blunder) are thresholds on that loss. The engine shows the better line. | Severity = the *regret* of the current underlay against the best legal alternative in the same window, not an absolute penalty. Show the better line ("move *-mi-* back two notes: cost 3.0 → 0.5"). |
| **Sequence alignment** (Needleman–Wunsch; Viterbi; speech forced alignment) | Monotone alignment with a scoring matrix and gap penalties, solved by dynamic programming. *k*-best paths enumerate alternatives. | Syllables are aligned to note onsets: a monotone map in which each syllable starts on one onset and a melisma is a run of unassigned onsets. DP over (syllable, onset) with segment costs. |
| **Optimality Theory / Harmonic Grammar / MaxEnt** (Goldwater & Johnson 2003; Hayes & Wilson 2008) | Violable constraints with weights. Weights can be fitted from observed choices among candidate sets (conditional logit). | Hand-set weights first; later calibrate against texted sources (the 1611 *Vox* print, Wacław's 1553 *Lamentationes*). |
| **Golden-file tests** (CRIM `test_cadences.py`) | Freeze the analysis of hand-checked pieces; any change is either a fix or a regression and must be looked at. | Snapshot the analyser's JSON for every edition; the PR diff shows what changed. |

---

## 3. Recommended architecture

A Python package `tools/analyser/` (stdlib plus music21 plus PyYAML; optional Pyphen and morfeusz2). No pandas in the core. The pieces are small, and dataclasses give typed, testable code. Pandas can come in for corpus statistics.

### 3.1 Data flow

```
LilyPond score.ly ──(musicxml-events.ily, extended with source locations)──► events.tsv + .musicxml
                                                                                 │
           underlay.py / lexicon.yaml ─────────────┐                             ▼
                                                    ▼                     ingest ─► Score model
                                              text layer ◄─────────────────────────┘ (voices, notes, syllables,
                                                    │                                     mensuration, sections)
               music layers: meter · sonority · dissonance · cadence · phrase · imitation · texture
                                                    │
                                     underlay model (alignment + constraints)
                                                    │
                     check (current underlay) ─── search (best legal / k-best alternatives)
                                                    │
                                   findings (rule, level, regret, explanation, alternatives)
                                                    │
                          baseline filter ──► text · JSON · Markdown summary · annotations · SARIF
```

### 3.2 Modules

1. **`ingest`**: MusicXML to a `Score`: voices → notes (onset and duration as `Fraction` in semiminims, as now; ties merged; rests kept), syllables (text, `syllabic`, verse, the note index they start on), sections and mensuration, bar and half-bar positions. Reuse the parser in `underlay_audit.py`, which is already correct for our export, and keep music21 for pitch and interval objects. **Source map**: extend `tools/musicxml-events.ily` to emit each event's `origin` (`ly:event-property ev 'origin` → `ly:input-file-line-char-column`), so every finding can point at `editions/<slug>/music/voices.ily:123`. *Borrows*: partitura's note array (the shape of the table).
2. **`meter`**: a tactus model by mensuration: ¢ (tactus on the semibreve; the half-bar of a breve bar is a beat) against C (semiminims count as minims for 10.1, per Stoquerus). Output: a strength for every onset (bar > half-bar > minim > semiminim), syncopation flags (a note that crosses the tactus). This must not use music21 `beatStrength`.
3. **`text`**: words, syllables, the stressed syllable, the word class (light, function, content, and `key`, marked per edition), whether the vowel is open, and punctuation, giving phrase and line ends. Lexicons in `tools/analyser/lexicon/{la,pl}.yaml`, each entry with `source:` (Kraków rule, Collatinus, the liturgical book, MD). Pyphen and Morfeusz only propose entries. *Borrows*: Hayes's constraint inputs; Collatinus offline.
4. **`sonority`**: vertical slices from the music21 timespan tree: per slice, the sounding pitches, which voices attack, sustain or rest, and the interval to the lowest voice (fourths against the bass count as dissonant, as in CRIM `markFourths`).
5. **`dissonance`**: a port of the subset of Morgan's taxonomy we need: suspension (preparation, dissonance, resolution, agent), passing, neighbour, cambiata, anticipation, chanson idiom, plus "unexplained". *Borrows*: humlib `dissonant` (labels and decision order). Cross-check against `dissonant` in an optional test.
6. **`cadence`**: CVF labelling by pattern tables over two-voice modules (harmonic interval, plus each voice's melodic step), and cadence types from the combination of CVFs. Output: arrival onset, the cadential tone, the type, its strength (full, evaded, abandoned, Phrygian) and the voice functions. *Borrows*: the CRIM CVF and cadence-label model and the humlib `autocadence` approach. Write our own tables, or vendor CRIM's as a separately licensed CC BY-SA data file. Validate against CRIM `cadences()` on our editions (done once by hand above: 24 in *Nunc*, 12 in *Vox*).
7. **`phrase`**: phrase units per voice: from rest to rest, cut at cadence arrivals in that voice and at text punctuation. Each phrase records its text span (the words it carries) and its cadence note, which is what 10.3 needs.
8. **`imitation`**: melodic n-grams (diatonic intervals plus duration ratios) at entries (after a rest or a cadence), matched across voices with a time window and flexed distance. The output is *points of imitation*: head motif, leading voice, the order of entries, and the transposition interval. Each entry is a note-index range in its voice. *Borrows*: CRIM `entries` and `presentationTypes` (FUGA, PEN, ID); humlib `imitation`.
9. **`texture`**: a homorhythm score per window (humlib's 1.0/0.5 weights over attack counts). The output marks homorhythmic regions and their voices. CRIM `homorhythm`'s syllable match becomes the 10.10 and 10.14 measure.
10. **`model`**: the underlay as an alignment. For each (voice, verse, phrase): the syllable sequence *s₁…sₘ* and the onset sequence *o₁…oₙ*; an underlay is a strictly increasing map *a(i)* from syllables to onsets with *a(1)* = the first onset after a rest (10.2). A candidate is **legal** if it passes the hard constraints (10.1–10.5, 10.9 with its exception) and scores the sum of its weighted soft-constraint violations.
11. **`rules`**: one Python function per constraint, plus YAML metadata (§3.4). Each returns violations with a location, a cost and an explanation.
12. **`search`**: for each phrase, DP (Viterbi) over syllable × onset finds the minimum-cost legal underlay. The step cost covers this syllable's notes (its melisma), so constraints whose span is a whole syllable stay local. Constraints with longer reach (imitation consistency, stanza consistency) are added as pairwise terms in a second pass, with candidate entries re-ranked. *k*-best Viterbi or local edits (move one boundary ±1–3 onsets; drop a repeated word per 10.13) enumerate the legal alternatives. This is our "move generation".
13. **`report`**: findings carry `rule`, `level`, `cost`, `regret`, `location` (bar, voice, verse, LilyPond file:line), `explanation` (the constraints violated, with their weights) and up to three `alternatives` (each with its cost and the constraints it fixes and breaks). Output as text (our current format), JSON (the golden snapshots), Markdown (the job summary, the review notes in the Project) and SARIF. *Borrows*: ruff and ESLint output conventions, SARIF 2.1.0.

### 3.3 Scoring

- **Hard constraints** decide legality. A BREAK is the current underlay failing one, and is always reported.
- **Soft constraints** carry weights in a few tiers, first hand-set from the order in the principles:
  1. phrase structure (10.3: last syllable on the cadence note; 10.10: imitation texted alike; Wacław's practice 10.7: one melisma before the cadence, on the stressed syllable of the last word)
  2. stress and key words (a stressed syllable on a weak or short note against a long or strong one later in the word; a run on an unstressed syllable in mid-phrase)
  3. light words (on the beat inside moving figures; a run on a light word)
  4. local idioms (after-run; octave-up; the repeated-note exception)
  5. vowel (information only: 10.6 says vowel difficulty alone is not a reason).
- **Severity** = regret = cost(current) − cost(best legal alternative in the same phrase). Levels are thresholds on regret, not on absolute cost. A melisma on *et* that no legal alternative can avoid is then *information*, not a problem. That answers the main complaint about the current LOOKs (the review read every flag by hand).
- **Context gating from the music layers**: a cadence arrival raises the weight of 10.3. A suspension's preparation–dissonance–resolution is a unit, so a syllable change on the dissonance costs more than one on the preparation. The head motif of an imitation pins 10.10. Homorhythm raises the weight of aligned syllables across voices. Each gate is a named multiplier in the YAML, so it can be inspected.
- **Calibration later**: generate candidate sets for passages from texted sources (the 1611 *Vox* Tenor, Wacław's *Lamentationes*, where the edition agrees in 72 of 80 clause-final words). Fit the weights by conditional logit (MaxEnt OT), with strong regularisation toward the hand-set values. With so few data, use it to check the *ordering* of the tiers, not to fit fine weights.

### 3.4 Rule definition format

```yaml
# tools/analyser/rules/U210-stress-short.yaml
id: U210
name: stress-short
level: look            # break | warn | look | info
weight: 2.0
tier: stress
principle: "10.6"
authority: "Zarlino rule II; Towne 1990, rule 7"
message: "'{syl}' ({word}) is stressed but shorter and weaker than '{next}'"
applies: { lang: [la, pl] }
gates: { cadence_phrase_end: 0.5 }   # weaker near the clausula, where 10.3 rules
examples:
  flag:
    - { notes: "f2 g1 a2",  text: "Do- mi- nus", stress: 0, at: 0 }
  pass:
    - { notes: "f1 g2 a2",  text: "Do- mi- nus" }
    - { ref: "plaude-euge/Discantus/22", why: "repeated note takes the syllable, 10.9" }
```

- The logic lives in `rules/U210_stress_short.py`, a function `check(ctx) -> Iterable[Violation]`; the YAML holds everything a reviewer tunes.
- **Examples** are pytest fixtures in a compact one-voice notation (pitch and duration in semiminims, text with `-` for continuation; parsed by a 40-line helper). music21's tinyNotation takes lyrics (`a2_Do`) but has no `syllabic`, so it is too weak. Multi-voice examples (cadence, imitation) are short LilyPond files in `tools/analyser/tests/fixtures/` that go through the real export.
- `ref:` examples point at real passages in our editions. The October underlay review supplies the first set: the *Vox* Altus bars 11–12 and Tenor bars 6, 37 and 40 must flag; *Plaude* Discantus bar 22 must not.
- Each rule needs at least one `flag` and one `pass` example, or CI fails (the LanguageTool discipline).
- The theorists' own examples (Lanfranco, Zarlino, Stoquerus, from the literature notes) become fixtures with their citations.

### 3.5 Tests

1. **Rule examples** (above): fast, with no LilyPond.
2. **Analysis layers**: unit tests per layer on fixtures (a 4–3 suspension, a Phrygian clausula, an evaded cadence, a two-voice fuga at the fifth).
3. **Golden snapshots**: `tests/golden/<slug>.json` with the full findings and analysis layers for each edition. A PR that changes them shows the diff, and the reviewer accepts it with `--update-golden`.
4. **Cross-checks** (optional, nightly): cadences against CRIM (pinned in a separate venv) and dissonance against humlib `dissonant`. Report the disagreements; don't fail.
5. **Export self-check**: compare the syllable counts per voice in the MusicXML against `underlay.py`/`voices.ily`. Known bug: *Plaude* Tenor loses syllables of *confidencium* inside the repeat (October review). Otherwise the analyser judges a broken export.

### 3.6 CI (GitHub Actions)

```yaml
on: pull_request
jobs:
  underlay:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get install -y lilypond          # pin 2.24 (export needs it)
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r tools/analyser/requirements.txt   # music21==10.5.*, pyyaml, pyphen
      - run: pytest tools/analyser/tests -q
      - run: make musicxml
      - run: python -m tools.analyser editions/*/pdf/*.musicxml
               --baseline tools/analyser/baseline.json
               --format github,markdown,sarif --out analyser.sarif
               --fail-on new-break
      - run: cat analyser.md >> "$GITHUB_STEP_SUMMARY"
```

- **New BREAKs** fail the job and appear as error annotations at the LilyPond file:line. New LOOKs are warning annotations, filtered to changed files (reviewdog-style) and kept under the annotation caps. Everything else goes in the summary table, sorted by regret.
- **Baseline**: `baseline.json` lists the accepted findings by fingerprint, each with a reason (`source reading, 10.12`) and the principle. `--update-baseline` rewrites it; the diff is reviewed like code. Fingerprints use word and syllable identity, not bars, so renumbering bars doesn't reopen anything.
- **Inline acceptance**: `% underlay: ok U210 -- the print's Tenor` beside the note in `voices.ily`. The source map gives the line.
- **SARIF upload** (`github/codeql-action/upload-sarif`) only if the repo is public; otherwise annotations and the summary are enough.
- **Runtime**: CRIM took about 2 s per piece for cadences and presentation types. Our own layers should be well under 10 s for the whole series. LilyPond export dominates.

### 3.7 Build order

1. Port the current audit into the rule framework (same results, golden snapshot). Add the source map and the export self-check.
2. Text layer and lexicons; mensuration-aware meter.
3. The alignment model and DP search; regret-based severity. *The LOOK list gets ranked and explained here, the biggest win for the review work.*
4. Cadence and phrase layers (10.3 and Wacław's clausula rule).
5. Imitation and texture (10.10, homorhythmic consistency).
6. Dissonance (suspension-aware costs).
7. Calibration against texted sources.

---

## 4. Risks

1. **The tool replacing the ear.** 10.6 says "tendencies to weigh by ear… sing every line before settling it". The analyser must rank and explain, never decide or auto-apply. Alternatives are suggestions; only firm rules fail CI.
2. **False confidence from good-looking numbers.** Weights are judgements. Show each finding's constraint breakdown, so a reviewer can disagree with a weight rather than with a black box.
3. **Export fidelity.** Every finding is only as good as `make musicxml` (see the *Plaude* repeat bug). The self-check (§3.5) is a precondition, not an extra.
4. **Mensuration.** 10.1 changes between C and ¢, and modern beat strength gets the tactus wrong. If the meter layer is wrong, the stress and light-word rules are wrong too.
5. **Repertory mismatch.** CRIM and humlib cadence and imitation logic were tuned on Franco-Flemish masses and chansons, mostly in four to six voices. Ours includes three-voice pieces, a motet that survives only in tablature (*Nunc scio*) and homophonic Polish songs. The NaN-tone evaded cadences in *Vox* show the edges. Validate on our own pieces before trusting any label.
6. **Dependency rot.** CRIM pins (music21 8.3, numpy < 2) and its pandas-3 break; verovio and humlib's `musicxml2hum` crashing on MusicXML; CLTK dropping its prosody between major versions. Keep the core on music21 plus stdlib, pin it, and isolate the cross-check tools in their own optional environment.
7. **Licences.** CRIM is CC BY-SA 4.0: don't copy its tables into MIT files. VIS is AGPL: don't copy. Collatinus is GPL: use it offline only. humlib (BSD-2), music21 (BSD-3), Pyphen (GPL/LGPL/MPL, pick LGPL or MPL), Morfeusz 2 (BSD-2), prosodic (Apache-2.0) and partitura (Apache-2.0) are all fine.
8. **Small data.** Four polyphonic editions and a handful of texted sources are too few to learn weights. Calibration can confirm the order of the tiers at best.
9. **Lexicon gaps.** Silent wrong stress is worse than none: unknown words must be reported, and Old Polish forms are not covered by Morfeusz.
10. **Scope creep.** This is a one-person series. Build order §3.7 delivers value at step 3. Steps 4–7 are worth doing only as the editions need them.
