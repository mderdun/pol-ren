%% Engraving decisions for this score only (breaks, spacing).
%% One verse line per system: the Tenor's lines cadence on bars 5, 10, 15,
%% 20, 25 and 30, so each system closes a line of the poem (the other voices
%% begin the next line inside the cadence bar).
prBreaksCritical = #'(5 10 15 20 25)
prBreaksPerformance = #'(5 10 15 20 25)

%% Performance: six systems at staff size 19 must go three to a page, so the
%% space between a lyric line and the next staff is tightened.
prLayoutPerformance = \layout {
  \context { \Lyrics
    \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #0.3
    \override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing.padding = #0.4
  }
  \context { \StaffGroup
    \override StaffGrouper.staff-staff-spacing.padding = #0.6
  }
}
