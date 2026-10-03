%% The score (identical in the critical and performance editions)

withAmbitus = \with { \consists "Ambitus_engraver" }
mens = {
  \override Staff.TimeSignature.style = #'mensural
  \override NoteHead.style = #'petrucci
  \time 2/2
}
setup = {
  \time 4/2
  \override Staff.TimeSignature.stencil =
    #(lambda (grob) (grob-interpret-markup grob #{ \markup \musicglyph "timesig.C22" #}))
  \accidentalStyle forget
  \autoBeamOff
}

breaks = { \repeat unfold 8 { s\breve*5 \break } s\breve*5 }

theScore = \score {
  \new StaffGroup <<
    \new Devnull \breaks
    \new Staff \with { \withAmbitus instrumentName = "Cantus" shortInstrumentName = "C" } {
      \clef treble \setup
      \new Voice = "c" \cantusNotes
    }
    \new Lyrics \lyricsto "c" \cantusWords

    \new Staff \with { \withAmbitus instrumentName = "Altus" shortInstrumentName = "A" } {
      \clef treble \setup
      \new Voice = "a" \altusNotes
    }
    \new Lyrics \lyricsto "a" \altusWords

    \new Staff \with { \withAmbitus instrumentName = "Tenor" shortInstrumentName = "T" } {
      \clef "treble_8" \setup
      \new Voice = "t" \tenorNotes
    }
    \new Lyrics \lyricsto "t" \tenorWords

    \new Staff \with { \withAmbitus instrumentName = "Bassus" shortInstrumentName = "B" } {
      \clef bass \setup
      \new Voice = "b" \bassusNotes
    }
    \new Lyrics \lyricsto "b" \bassusWords
  >>
  \layout {
    indent = 22\mm
    short-indent = 6\mm
    #(layout-set-staff-size 17.5)
    #(define fonts (make-pango-font-tree "Junicode" "Junicode" "DejaVu Sans Mono" (/ 17.5 20)))
    \context { \Staff
      measureBarType = "-span|"
      \override InstrumentName.self-alignment-X = #RIGHT
      \override InstrumentName.font-size = #0.5
      \override AccidentalSuggestion.font-size = #-1.5
    }
    \context { \Voice
      melismaBusyProperties = #'()
    }
    \context { \Lyrics
      \override LyricText.font-size = #0.8
      \override VerticalAxisGroup.staff-affinity = #UP
      \override LyricSpace.minimum-distance = #1.3
      \override LyricHyphen.minimum-distance = #0.8
      \override VerticalAxisGroup.nonstaff-relatedstaff-spacing = #'((basic-distance . 3) (padding . 0.6) (stretchability . 0))
    }
    \context { \Score
      \override BarNumber.font-size = #-0.5
      \override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/8)
    }
  }
}
