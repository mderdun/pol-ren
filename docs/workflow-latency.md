# Why sessions wait, and what to change (note, 4 October 2026)

Miki asked why sessions have long silent waits. These are the causes measured in the session of 4 October 2026, and the fixes to discuss. Nothing here is changed yet.

## Causes, largest first

1. **Parallel agents block the whole turn until the slowest one finishes.** Four agents were launched together. Their run times were 15, 36, 38 and 82 minutes. The main session could not report, check or merge anything until all four returned, so the 82-minute engraving agent set the wait for everything. The same happened earlier with the four book readers and the survey: 13 to 44 minutes each, and the wait was the longest of them.
2. **The engraving agent was given eleven items in one go.** Each item needed a build and a visual check, so a large batch meant a long serial loop. Smaller agents finish sooner and can be reviewed one at a time.
3. **The machine has two CPU cores.** Agents running in parallel share them with LilyPond, LuaLaTeX, the texture pass and the font generator. A full `make` takes about 4 minutes on an idle machine and much longer when four agents are building at once. The engraving agent's full build ran past its 10-minute limit.
4. **Builds always rebuild everything.** `tools/build.sh` deletes each edition's build folder, so lilypond-book re-engraves every system even when one lyric changed. The texture pass then re-treats every page. The texture is now about 60% slower per page than before, since straight lines keep one weight and the wedges between marks fill in.
5. **One-off slow steps.** OCR of two scanned books ran for about 20 minutes. The first run of the pressed-font generator takes about 4 minutes, and so does any change to `texture_font.py` or `novello_vector.py`, which forces a remake. Push timeouts needed `git gc` first.

## Fixes to discuss

- **Launch agents in the background, or in waves.** Background launches would let the main session merge and review each agent's result as it arrives; waves of two would keep each wait short. Either way, give each agent one coherent job with a time budget.
- **Check in while agents run.** Post a short status line whenever an agent returns, rather than one report at the end.
- **Build incrementally.** Keep lilypond-book's build folder and its snippet cache between builds; rebuild only the editions whose sources changed (a make dependency on `music/`, `notes/` and `house/`).
- **Make the texture opt-in while iterating.** Agents use `NOVELLO=0` for development builds and add the texture only for the final check, on one edition.
- **Cache the texture per page.** Hash each page's drawn marks and reuse the treated page when the hash is unchanged.
- **Keep the pressed-font stamp narrow.** The stamp should depend on `treat()` and its parameters, not on the whole of `novello_vector.py`, so page-level changes don't remake the fonts.
- **Move full builds to CI.** Run full builds in GitHub Actions and keep local sessions to the editions being changed.
- **Get a larger session machine** if the plan allows it. Two cores are the hard limit on everything above.
