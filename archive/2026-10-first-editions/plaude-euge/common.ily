\version "2.24.0"
#(set-default-paper-size "a4")
#(set-global-staff-size 19)
#(define (bracket-head grob)
   (bracketify-stencil (ly:note-head::print grob) Y 0.12 0.25 0.12))
\paper {
  #(define fonts (make-pango-font-tree "EB Garamond" "EB Garamond" "DejaVu Sans Mono" (/ staff-height pt 20)))
  top-margin = 16\mm bottom-margin = 16\mm
  left-margin = 18\mm right-margin = 18\mm
  indent = 22\mm short-indent = 8\mm
  system-system-spacing = #'((basic-distance . 18) (minimum-distance . 14) (padding . 4) (stretchability . 20))
  markup-system-spacing.padding = #4
  ragged-last-bottom = ##t
  print-first-page-number = ##f
  oddHeaderMarkup = \markup \fill-line { \null \fromproperty #'page:page-number-string }
  evenHeaderMarkup = \markup \fill-line { \fromproperty #'page:page-number-string \null }
  oddFooterMarkup = \markup \fill-line { \abs-fontsize #8 \italic \fromproperty #'header:footer }
  evenFooterMarkup = \oddFooterMarkup
}
\layout {
  \context { \Score
    \remove Bar_number_engraver
    measureBarType = "-span|"
    startRepeatBarType = ".|:"
    endRepeatBarType = ":|."
    doubleRepeatBarType = ":..:"
    sectionBarType = "||"
    \override VoltaBracket.font-size = #-2
    \override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/4)
  }
  \context { \Staff
    \remove Time_signature_engraver
    \consists Bar_number_engraver
    \override BarNumber.break-visibility = ##(#f #f #t)
    \override BarNumber.font-size = #-2
    \override BarNumber.self-alignment-X = #LEFT
  }
  \context { \Voice
    melismaBusyProperties = #'()
    \tieDashed
    \override Tie.dash-definition = #'((0 1 0.4 0.75))
  }
  \context { \Lyrics
    \override LyricText.font-size = #0.5
    \override LyricText.whiteout = #0.6
    \override LyricText.layer = #3
    \override LyricHyphen.whiteout = #0.4
    \override LyricHyphen.layer = #3
    \override LyricSpace.minimum-distance = #1.2
    \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #0.6
  }
}
