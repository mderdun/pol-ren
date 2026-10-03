%% House style for the Polish Early Music editions

\paper {
  #(set-paper-size "a4")
  top-margin = 16\mm
  bottom-margin = 16\mm
  left-margin = 20\mm
  right-margin = 20\mm
  #(define fonts (make-pango-font-tree "Junicode" "Junicode" "DejaVu Sans Mono" (/ staff-height pt 20)))
  markup-system-spacing.padding = 3
  system-system-spacing.basic-distance = 18
  score-markup-spacing.padding = 4
  print-page-number = ##t
  oddHeaderMarkup = \markup \fill-line { "" \if \should-print-page-number \fromproperty #'page:page-number-string }
  evenHeaderMarkup = \markup \fill-line { \if \should-print-page-number \fromproperty #'page:page-number-string "" }
  oddFooterMarkup = ##f
  evenFooterMarkup = ##f
  tagline = ##f
}

#(define-markup-command (sectionHead layout props text) (markup?)
   (interpret-markup layout props
     #{ \markup \column { \vspace #0.9 \abs-fontsize #12.5 \bold #text \vspace #0.3 } #}))

#(define-markup-command (para layout props text) (markup-list?)
   (interpret-markup layout props
     #{ \markup \column { \abs-fontsize #10.5 \override #'(baseline-skip . 3.1) \justify { #text } \vspace #0.45 } #}))

#(define-markup-command (item layout props label text) (markup? markup-list?)
   (interpret-markup layout props
     #{ \markup \column {
          \abs-fontsize #10.5 \override #'(baseline-skip . 3.1)
          \line { \pad-to-box #'(0 . 11) #'(0 . 1) \bold #label
                  \override #'(line-width . 84) \justify { #text } }
          \vspace #0.35 } #}))

#(define-markup-command (note layout props label text) (markup? markup-list?)
   (interpret-markup layout props
     #{ \markup \column {
          \abs-fontsize #10 \override #'(baseline-skip . 2.9)
          \line { \pad-to-box #'(0 . 16) #'(0 . 1) #label
                  \override #'(line-width . 80) \justify { #text } }
          \vspace #0.3 } #}))

#(define-markup-command (bib layout props text) (markup-list?)
   (interpret-markup layout props
     #{ \markup \column {
          \abs-fontsize #10 \override #'(baseline-skip . 2.9)
          \line { \hspace #0 \override #'(line-width . 96) \justify { #text } }
          \vspace #0.3 } #}))

#(define-markup-command (rubric layout props text) (markup?)
   (interpret-markup layout props
     #{ \markup \abs-fontsize #11 \italic #text #}))

colorMark = \markup \abs-fontsize #9 \concat { "⌜" \hspace #2.2 "⌝" }
