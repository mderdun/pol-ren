%% Performance score: the critical score transposed down a fifth (Banchieri's rule for high clefs without signature)

mens = {
  \override Staff.TimeSignature.style = #'mensural
  \override NoteHead.style = #'petrucci
  \time 2/2
}
setupP = {
  \key d \minor
  \time 4/2
  \override Staff.TimeSignature.stencil =
    #(lambda (grob) (grob-interpret-markup grob #{ \markup \musicglyph "timesig.C22" #}))
  \accidentalStyle forget
  \autoBeamOff
}

breaksP = { \repeat unfold 8 { s\breve*5 \break } s\breve*5 }

%% Editorial suggestion (performance edition only): lower octave at the final,
%% where the Altus reaches its final note. Not in the source.
dropNote = #(define-music-function (n) (ly:music?)
  #{ \once \override NoteHead.font-size = #-1.5
     \once \override NoteColumn.force-hshift = #0
     \once \override Stem.transparent = ##t
     \once \override Parentheses.font-size = #1.5
     \once \override Parentheses.padding = #0.3
     \parenthesize #n #})
dropT = { \voiceTwo s\breve*44 s1 \dropNote a1 }
dropB = { \voiceTwo s\breve*44 s1 \dropNote a,1 }

perfScore = \score {
  \new StaffGroup <<
    \new Devnull \breaksP
    \new Staff \with { \withAmbitus instrumentName = "Cantus" shortInstrumentName = "C" } {
      \clef treble \setupP
      \new Voice = "c" \transpose a d \cantusNotes
    }
    \new Lyrics \lyricsto "c" \cantusWords

    \new Staff \with { \withAmbitus instrumentName = "Altus" shortInstrumentName = "A" } {
      \clef treble \setupP
      \new Voice = "a" \transpose a d \altusNotes
    }
    \new Lyrics \lyricsto "a" \altusWords

    \new Staff \with { \withAmbitus instrumentName = "Tenor" shortInstrumentName = "T" } {
      \clef "treble_8" \setupP
      << \new Voice = "t" \transpose a d \tenorNotes \new Voice \transpose a d \dropT >>
    }
    \new Lyrics \lyricsto "t" \tenorWords

    \new Staff \with { \withAmbitus instrumentName = "Bassus" shortInstrumentName = "B" } {
      \clef bass \setupP
      << \new Voice = "b" \transpose a d \bassusNotes \new Voice \transpose a d \dropB >>
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
