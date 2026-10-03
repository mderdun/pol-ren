%% The score (identical in the critical and performance editions)

cutC = \with { \consists "Ambitus_engraver" }
mens = {
  \override Staff.TimeSignature.style = #'mensural
  \override NoteHead.style = #'petrucci
  \time 2/2
}
setup = {
  \time 2/1
  \override Staff.TimeSignature.stencil =
    #(lambda (grob) (grob-interpret-markup grob #{ \markup \musicglyph "timesig.C22" #}))
  \accidentalStyle forget
  \autoBeamOff
}

theScore = \score {
  \new StaffGroup <<
    \new Staff \with { \cutC instrumentName = "Cantus" shortInstrumentName = "C" } {
      \incipit { \clef "petrucci-c1" \mens a'\breve }
      \clef treble \setup
      \new Voice = "c" \cantusNotes
    }
    \new Lyrics \lyricsto "c" \cantusWords

    \new Staff \with { \cutC instrumentName = "Altus" shortInstrumentName = "A" } {
      \incipit { \clef "petrucci-c3" \mens a4 }
      \clef "treble_8" \setup
      \new Voice = "a" \altusNotes
    }
    \new Lyrics \lyricsto "a" \altusWords

    \new Staff \with { \cutC instrumentName = "Tenor" shortInstrumentName = "T" } {
      \incipit { \clef "petrucci-c4" \mens a\breve }
      \clef "treble_8" \setup
      \new Voice = "t" \tenorNotes
    }
    \new Lyrics \lyricsto "t" \tenorWords

    \new Staff \with { \cutC instrumentName = "Bassus" shortInstrumentName = "B" } {
      \incipit { \clef "petrucci-f4" \mens a,2. }
      \clef bass \setup
      \new Voice = "b" \bassusNotes
    }
    \new Lyrics \lyricsto "b" \bassusWords
  >>
  \layout {
    indent = 30\mm
    short-indent = 6\mm
    incipit-width = 13\mm

    \context { \Staff
      measureBarType = "-span|"
      \override InstrumentName.self-alignment-X = #RIGHT
      \override InstrumentName.font-size = #0.5
      \override AccidentalSuggestion.font-size = #-1.5
    }
    \context { \Lyrics
      \override LyricText.font-size = #0.8
      \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #0.6
      \override VerticalAxisGroup.nonstaff-nonstaff-spacing.padding = #0.3
      \override StanzaNumber.font-size = #0.5
    }
    \context { \Score
      \override BarNumber.font-size = #-0.5
      \override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/4)
    }
  }
}
