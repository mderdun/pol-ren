\version "2.24.0"
%% Vox in Rama — the score. Content only; style is in
%% house/lilypond/pol-ren.ily. score-performance.ly sets the pitch and
%% includes this file.
\include "pol-ren.ily"
\include "engraving.ily"
\include "voices.ily"

%% The bracketed suggestion at the final belongs to the performance edition only.
#(define pr-perf (eq? (ly:parser-lookup 'prPerformance) #t))
tenorMusic  = #(if pr-perf #{ << \tenorNotes  \new Voice \tenorSugg  >> #} tenorNotes)
bassusMusic = #(if pr-perf #{ << \bassusNotes \new Voice \bassusSugg >> #} bassusNotes)

\score {
  \prScore <<
    \prStaff "Cantus" "C." {}                          "treble"   "" \cantusNotes \cantusWords
    \prStaff "Altus"  "A." {}                          "treble"   "" \altusNotes  \altusWords
    \prStaff "Tenor"  "T." { \clef "petrucci-c2" a'1. } "treble_8" "" \tenorMusic  \tenorWords
    \prStaff "Bassus" "B." {}                          "bass"     "" \bassusMusic \bassusWords
  >>
  \layout { $(pr-layout) }
}
