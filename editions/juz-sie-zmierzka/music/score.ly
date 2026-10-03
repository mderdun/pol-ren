\version "2.24.0"
%% Modlitwa gdy dziatki spać idą — the score. Content only; style is in
%% house/lilypond/pol-ren.ily. score-performance.ly sets the pitch and
%% includes this file.
\include "pol-ren.ily"
\include "voices.ily"
\include "engraving.ily"

\score {
  \prScore <<
    \prStaff "Cantus" "C." { \clef "petrucci-c1" a'\breve } "treble"   ""       \cantusNotes \cantusWords
    \prStaff "Altus"  "A." { \clef "petrucci-c3" a4 }       "treble_8" "treble" \altusNotes  \altusWords
    \prStaff "Tenor"  "T." { \clef "petrucci-c4" a\breve }  "treble_8" ""       \tenorNotes  \tenorWords
    \prStaff "Bassus" "B." { \clef "petrucci-f4" a,2. }     "bass"     ""       \bassusNotes \bassusWords
  >>
  \layout { $(pr-layout) }
}
