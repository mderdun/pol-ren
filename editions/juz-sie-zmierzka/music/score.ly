\version "2.24.0"
%% Modlitwa gdy dziatki spać idą — the score, identical in both editions.
%% Staff size is given by the edition file (lilypondfile option).
\include "pol-ren.ily"
\include "voices.ily"

incipitMens = {
  \override Staff.TimeSignature.style = #'mensural
  \override NoteHead.style = #'petrucci
  \time 2/2
}
setup = {
  \time 2/1
  \mensSign "timesig.C22"
  \voiceSetup
}

\score {
  \new StaffGroup <<
    \new Staff \with \vname "Cantus" "C." {
      \incipit { \clef "petrucci-c1" \incipitMens a'\breve }
      \clef treble \setup
      \new Voice = "c" \cantusNotes
    }
    \new Lyrics \lyricsto "c" \cantusWords

    \new Staff \with \vname "Altus" "A." {
      \incipit { \clef "petrucci-c3" \incipitMens a4 }
      \clef "treble_8" \setup
      \new Voice = "a" \altusNotes
    }
    \new Lyrics \lyricsto "a" \altusWords

    \new Staff \with \vname "Tenor" "T." {
      \incipit { \clef "petrucci-c4" \incipitMens a\breve }
      \clef "treble_8" \setup
      \new Voice = "t" \tenorNotes
    }
    \new Lyrics \lyricsto "t" \tenorWords

    \new Staff \with \vname "Bassus" "B." {
      \incipit { \clef "petrucci-f4" \incipitMens a,2. }
      \clef bass \setup
      \new Voice = "b" \bassusNotes
    }
    \new Lyrics \lyricsto "b" \bassusWords
  >>
  \layout { }
}
