%% Engraving decisions for this score only (breaks, spacing, local signs).

%% Editorial suggestion at the final (performance edition only): the house
%% \sugg, in round brackets, set in the same column as the voice's own note.
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
prBreaksPerformance = #'(5 10 15 20 24 28 34 39)
