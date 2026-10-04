%% Engraving decisions for this score only (breaks, spacing, local signs).

%% Editorial suggestion at the final (performance edition only): the house
%% \sugg, in square brackets, set in the same column as the voice's own note.
suggFinal =
#(define-music-function (note) (ly:music?)
   #{ \voiceTwo \sugg
      \once \override NoteColumn.force-hshift = #0
      \once \override Parentheses.padding = #0.3
      \parenthesize #note #})

%% Systems follow the text where the imitation allows: 'Vox in Rama' (1-10),
%% 'audita est, ploratus et ululatus' (11-20), 'Rachel plorans' (21-24),
%% 'filios suos' (25-28), 'et noluit consolari' (29-39), 'quia non sunt'
%% (40-45). The Cantus begins each new phrase at the start of a system.
prBreaksCritical = #'(5 10 15 20 24 28 34 39)
%% The performance edition sets two systems a page, the masthead page
%% included (the gap between systems stays wider than any staff gap, Gould
%% 488): eight systems on four pages. At staff size 19 a system holds six
%% bars at most (21-28, 33-39 and 7-12 overrun the line), so only the breaks
%% at 28, 34 and 39 keep to the phrases; before bar 28 the systems take five
%% or six bars each.
prBreaksPerformance = #'(6 11 17 22 28 34 39)

%% Rests: only the Tenor is a primary source (T), so its rests stand as printed
%% in the critical edition; the other voices come from M and are cut at the
%% bar lines as in the performance edition (principles 5.8).
prRegularRests = #'("cantus" "altus" "bassus")
