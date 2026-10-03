\include "voices.ily"
global = { \key f \major \time 2/1 }
plaudeScore = \score {
  \new StaffGroup \with { \override SystemStartBracket.collapse-height = #1 } <<
    \new Staff \with { instrumentName = "Discantus" shortInstrumentName = "D." \consists Bar_number_engraver } {
      \new Voice = "D" { \global \clef treble \discantusNotes } }
    \new Lyrics \lyricsto "D" \discantusText
    \new Staff \with { instrumentName = "Medius" shortInstrumentName = "M." \remove Bar_number_engraver } {
      \new Voice = "M" { \global \clef "treble_8" \mediusNotes } }
    \new Lyrics \lyricsto "M" \mediusText
    \new Staff \with { instrumentName = "Tenor" shortInstrumentName = "T." \remove Bar_number_engraver } {
      \new Voice = "T" { \global \clef bass \tenorNotes } }
    \new Lyrics \with { \override LyricText.font-shape = #'italic } \lyricsto "T" \tenorText
  >>
  \layout { }
}
