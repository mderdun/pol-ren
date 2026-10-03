\version "2.24.0"
%% Plaude euge theotocos: the score. Content only; style is in
%% house/lilypond/pol-ren.ily. score-performance.ly includes this file.
%% The source has no clefs, signature or mensuration sign: clefs and the
%% one-flat signature are editorial, and no sign or incipit is printed.
\include "pol-ren.ily"
\include "engraving.ily"
\include "voices.ily"

prKey = { \key f \major }
prSign = ""

\score {
  \prScore <<
    \prStaff "Discantus" "D." {} "treble"   "" \discantusNotes \discantusWords
    \prStaff "Medius"    "M." {} "treble_8" "" \mediusNotes    \mediusWords
    \prStaff "Tenor"     "T." {} "bass"     "" \tenorNotes     \tenorWords
  >>
  \layout { $(pr-layout) }
}
