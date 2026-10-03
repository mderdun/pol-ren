%% Wacław z Szamotuł, Nunc scio vere — performance edition (score identical to the critical edition)
%% Build:  python3 build.py && lilypond nunc-scio-vere-choral.ly
%%         (LilyPond 2.24; font: EB Garamond)
%% Music:  choral.ily (notes, tablature pitch and Perz's values)
%% Text:   underlay.py (syllable placement)  ->  build.py  ->  parts.ily

\version "2.24.0"

%% ---------------------------------------------------------------- music helpers
ficta  = \once \set suggestAccidentals = ##t
ed     = \tweak font-size #-3 \etc
fin    = \once \override NoteHead.duration-log = #-2
cf     = ^\markup \abs-fontsize #8.5 \italic "[c.f.]"

\include "parts.ily"

global = {
  \key c \major
  \time 4/2
  \override Staff.TimeSignature.stencil = #(lambda (grob)
     (grob-interpret-markup grob #{ \markup \musicglyph "timesig.mensural22" #}))
  \accidentalStyle forget
  \autoBeamOff
  \override Score.BreakAlignment.break-align-orders =
    #(make-vector 3 '(left-edge cue-end-clef clef cue-clef key-cancellation
                      key-signature ambitus time-signature staff-bar custos breathing-sign))
}
vocal = #(define-music-function (m) (ly:music?) #{ \shiftDurations #-1 #0 { #m } #})

%% ---------------------------------------------------------------- page
sc = #(define-markup-command (sc layout props txt) (markup?)
  (interpret-markup layout props
    #{ \markup \override #'(font-features . ("smcp" "c2sc" "onum")) #txt #}))
#(set-global-staff-size 17)
\paper {
  #(set-paper-size "a4")
  #(define fonts (set-global-fonts #:roman "Junicode" #:sans "TeX Gyre Heros"
                                   #:factor (/ staff-height pt 20)))
  top-margin = 14\mm
  bottom-margin = 14\mm
  inner-margin = 20\mm
  outer-margin = 16\mm
  two-sided = ##t
  indent = 18\mm
  short-indent = 8\mm
  ragged-last-bottom = ##t
  system-system-spacing = #'((basic-distance . 13) (minimum-distance . 9) (padding . 3) (stretchability . 18))
  score-markup-spacing = #'((basic-distance . 9) (padding . 2.5))
  markup-system-spacing = #'((basic-distance . 7) (padding . 2.5))
  markup-markup-spacing = #'((basic-distance . 1) (padding . 0.5))
  print-first-page-number = ##f
  oddHeaderMarkup = \markup \fill-line {
    \null
    \if \should-print-page-number \abs-fontsize #8.5 \sc \fromproperty #'header:runhead
    \if \should-print-page-number \abs-fontsize #9 \fromproperty #'page:page-number-string
  }
  evenHeaderMarkup = \markup \fill-line {
    \if \should-print-page-number \abs-fontsize #9 \fromproperty #'page:page-number-string
    \if \should-print-page-number \abs-fontsize #8.5 \sc "Wacław z Szamotuł · Nunc scio vere"
    \null
  }
  oddFooterMarkup = ##f
  evenFooterMarkup = ##f
  tocTitleMarkup = \markup \null
  tocItemMarkup = \markup \abs-fontsize #10 \fill-line {
    \null
    \override #'(line-width . 70) \fill-with-pattern #1.2 #CENTER . \fromproperty #'toc:text \fromproperty #'toc:page
    \null
  }
  tagline = ##f
}

%% ---------------------------------------------------------------- prose helpers

head = #(define-markup-command (head layout props txt) (markup?)
  (interpret-markup layout props
    #{ \markup \column { \vspace #0.9 \abs-fontsize #12 \sc #txt \vspace #0.15 } #}))
subhead = #(define-markup-command (subhead layout props txt) (markup?)
  (interpret-markup layout props
    #{ \markup \column { \vspace #0.35 \abs-fontsize #10.5 \italic #txt } #}))
para = #(define-markup-command (para layout props args) (markup-list?)
  (interpret-markup layout props
    #{ \markup \column { \abs-fontsize #10.5 \override #'(font-features . ("onum")) \override #'(baseline-skip . 3.05)
         \override #'(line-width . 112) \justify { #args } \vspace #0.3 } #}))
rule = #(define-markup-command (rule layout props txt) (markup? markup-list?)
  (interpret-markup layout props #{ \markup \null #}))
%% numbered list item with hanging indent
li = #(define-markup-command (li layout props num args) (markup? markup-list?)
  (interpret-markup layout props
    #{ \markup \column { \abs-fontsize #10.5 \override #'(font-features . ("onum")) \override #'(baseline-skip . 3.05) \line {
         \pad-to-box #'(0 . 5) #'(0 . 0) #num
         \override #'(line-width . 107) \justify { #args } } \vspace #0.2 } #}))
%% critical note: bar | voice | text
cn = #(define-markup-command (cn layout props bar voice args) (markup? markup? markup-list?)
  (interpret-markup layout props
    #{ \markup \column { \abs-fontsize #10 \override #'(font-features . ("onum")) \override #'(baseline-skip . 2.9) \line {
         \pad-to-box #'(0 . 13) #'(0 . 0) #bar
         \pad-to-box #'(0 . 10) #'(0 . 0) #voice
         \override #'(line-width . 89) \wordwrap { #args } } \vspace #0.12 } #}))
%% bibliography entry with hanging indent
bib = #(define-markup-command (bib layout props args) (markup-list?)
  ;; hanging indent: first line flush, turnovers indented by `hang'
  (let* ((hang 4)
         (width 112)
         (props (cons (list (cons 'font-features '("onum"))
                            (cons 'baseline-skip 2.9)
                            (cons 'line-width (- width hang)))
                      props))
         (tfs (ly:output-def-lookup layout 'text-font-size 11))
         (lines (interpret-markup-list layout
                  (cons (list (cons 'font-size (magnification->font-size (/ 10 tfs)))) props)
                  (make-wordwrap-lines-markup-list args)))
         (indented (cons (car lines)
                         (map (lambda (st) (ly:stencil-translate-axis st hang X)) (cdr lines))))
         (col (stack-lines DOWN 0 2.9 indented)))
    (ly:stencil-combine-at-edge col Y DOWN (ly:make-stencil "" '(0 . 0) '(0 . 1.1)) 0)))
pron = #(define-markup-command (pron layout props spell ipa ex) (markup? markup? markup?)
  (interpret-markup layout props
    #{ \markup \abs-fontsize #10.5 \line {
         \hspace #4 \pad-to-box #'(0 . 26) #'(0 . 0) \italic #spell
         \pad-to-box #'(0 . 12) #'(0 . 0) #ipa
         #ex } #}))
rubric = #(define-markup-command (rubric layout props txt) (markup?)
  (interpret-markup layout props
    #{ \markup \with-color "#9a1e1e" \abs-fontsize #11 \italic #txt #}))
sig = #(define-markup-command (sig layout props txt) (markup?)
  (interpret-markup layout props #{ \markup \bold #txt #}))

%% ---------------------------------------------------------------- polyphony layout
polyLayout = \layout {
  \context {
    \Staff
    measureBarType = "-span|"
    \consists "Ambitus_engraver"
    \override Ambitus.space-alist.time-signature = #'(extra-space . 1.2)
    \override InstrumentName.self-alignment-X = #RIGHT
    \override InstrumentName.padding = #1.4
    \override InstrumentName.font-size = #0.5
  }
  \context {
    \Voice
    \override AccidentalSuggestion.font-size = #-2
    \override AccidentalSuggestion.parenthesized = ##f
    \override TextScript.padding = #0.8
  }
  \context {
    \Lyrics
    \override LyricText.font-size = #0.9
    \override LyricHyphen.minimum-distance = #1.4
    \override LyricHyphen.thickness = #1.1
    \override LyricSpace.minimum-distance = #1.3
    \override LyricExtender.left-padding = #0.3
    \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #1.2
    \override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing.padding = #1.6
  }
  \context {
    \Score
    \override BarNumber.font-size = #-0.5
    \override BarNumber.font-shape = #'italic
    \override BarNumber.break-visibility = ##(#f #f #t)
    \override SpacingSpanner.common-shortest-duration = #(ly:make-moment 1/4)
    \override SpacingSpanner.spacing-increment = #1.25
    \override TimeSignature.break-visibility = ##(#f #f #t)
    \override Fermata.font-size = #-1
  }
}

voiceStaff =
#(define-music-function (name short clef music words) (markup? markup? string? ly:music? ly:music?)
  #{
    <<
      \new Staff \with { instrumentName = #name shortInstrumentName = #short }
      { \global \clef #clef \vocal #music }
      \addlyrics { #words }
    >>
  #})

\book {
  \header { tagline = ##f runhead = "Nunc scio vere" }

  %% ============================================================ TITLE AND NOTES
  \bookpart {
    \paper { print-page-number = ##f }
    \markup \column {
      \vspace #1
      \fill-line { \abs-fontsize #12 \sc "Wacław z Szamotuł" }
      \fill-line { \abs-fontsize #9.5 "c. 1520 – c. 1560" }
      \vspace #1.2
      \fill-line { \abs-fontsize #28 "Nunc scio vere" }
      \vspace #0.6
      \fill-line { \abs-fontsize #12 \italic "Introit for the Feast of Saints Peter and Paul" }
      \fill-line { \abs-fontsize #10.5 "Antiphon and Gloria Patri for four voices" }
      \vspace #0.8
      \fill-line { \abs-fontsize #9.5 \sc "performance edition" }
      \fill-line { \abs-fontsize #9.5 \italic "ed. Mikołaj Derdun · score as in the critical edition (2026)" }
      \vspace #0.4
    }

    \markup \head "The work" \noPageBreak
    \markup \para {
      The setting survives only in a textless organ tablature of about 1590.
      It is built on the Introit chant, which passes between the voices
      (marked [c.f.]). The words are editorial. The critical edition gives
      the sources and the reasons for each reading.
    }

    \markup \head "Order" \noPageBreak
    \markup \para {
      Antiphon (choir). Psalm verse (cantor, in chant; the choir may join at
      the asterisk). \italic { Gloria Patri } (choir). Antiphon repeated. The
      organ may take the \italic { Gloria Patri } or the repeat, as it often did
      in Wacław’s time, while the choir says the words quietly.
    }

    \markup \head "Pitch and tempo" \noPageBreak
    \markup \para {
      The score is at written pitch, for men’s voices with boys or falsettists
      on the Cantus. A mixed choir should sing a minor third higher, where the
      ranges match Wacław’s other motets. Minim pulse about 60–72. The organ
      may double the voices.
    }

    \markup \head "Signs" \noPageBreak
    \markup \para {
      Accidentals before notes come from the source and apply to their own
      note only. Accidentals above the staff are editorial. Italic words are
      repetitions of text. The small note in the Altus at bar 56 is editorial;
      the tied c′ before it may be held instead.
    }

    \markup \head "Pronunciation" \noPageBreak
    \markup \para {
      Polish Latin, as Wacław’s singers spoke it. Vowels are pure.
    }
    \markup \column {
      \pron "c (before e, i, ae)" "[ts]" \line { \italic principio [prinˈtsipjɔ] }
      \pron "sc (before e, i)" "[sts]" \line { \italic scio [ˈstsiɔ] }
      \pron "ti (before a vowel)" "[tsj]" \line { \italic exspectatione [ɛkspɛktaˈtsjɔnɛ] }
      \pron "g" "[g]" \line { always hard: \italic angelum [ˈaŋgɛlum] }
      \pron "h, ch" "[x]" \line { \italic Herodis [xɛˈrɔdis] }
      \pron "ae" "[ɛ]" \line { \italic saecula [ˈsɛkula] }
      \pron "s (between vowels)" "[z]" \line { \italic misit [ˈmizit] }
      \vspace #0.3
    }
    \markup \para {
      Stress: \italic { Dóminus, ángelum, erípuit, Heródis, exspectatióne,
      Iudaeórum, princípio, saeculórum. }
    }

    \markup \head "Text and translation" \noPageBreak
    \markup \fill-line {
      \pad-to-box #'(0 . 54) #'(0 . 0) \abs-fontsize #10.5 \override #'(baseline-skip . 3.0) \column {
        \line { \italic "Ant." Nunc scio vere, }
        \line { quia misit Dominus angelum suum: }
        \line { et eripuit me de manu Herodis, }
        \line { et de omni exspectatione plebis Iudaeorum. }
        \vspace #0.3
        \line { \italic "Ps." Domine, probasti me, et cognovisti me: }
        \line { tu cognovisti sessionem meam, }
        \line { et resurrectionem meam. }
        \vspace #0.3
        \line { Gloria Patri, et Filio, et Spiritui Sancto. }
        \line { Sicut erat in principio, et nunc, et semper, }
        \line { et in saecula saeculorum. Amen. }
      }
      \pad-to-box #'(0 . 54) #'(0 . 0) \abs-fontsize #10.5 \override #'(baseline-skip . 3.0) \italic \column {
        \line { Now I know for certain }
        \line { that the Lord has sent his angel }
        \line { and has rescued me from the hand of Herod }
        \line { and from all the people of the Jews expected. }
        \vspace #0.3
        \line { Lord, you have searched me and known me; }
        \line { you know my sitting down }
        \line { and my rising up. }
        \vspace #0.3
        \line { Glory be to the Father, and to the Son, }
        \line { and to the Holy Spirit. As it was in the beginning, }
        \line { is now, and ever shall be, world without end. Amen. }
      }
    }
    \markup \fill-line { \abs-fontsize #9.5 \italic "Acts 12:11; Psalm 138 (139):1–2." }
  }

  %% ============================================================ SCORE
  \bookpart {
    \header {
      runhead = "Nunc scio vere"
      title = \markup \column {
        \fill-line { \abs-fontsize #20 "Nunc scio vere" }
        \vspace #0.2
        \fill-line { \rubric "In die Apostolorum Petri et Pauli" }
      }
      composer = \markup \abs-fontsize #11 \sc "Wacław z Szamotuł"
    }

    \markup \rubric "Antiphona" \noPageBreak
    \score {
      \new StaffGroup <<
        \voiceStaff "Cantus" "C." "treble"   \cantusAnt \cantusAntText
        \voiceStaff "Altus"  "A." "treble"   \altusAnt  \altusAntText
        \voiceStaff "Tenor"  "T." "treble_8" \tenorAnt  \tenorAntText
        \voiceStaff "Bassus" "B." "bass"     { \bassusAnt \bar "||" } \bassusAntText
      >>
      \layout { \polyLayout }
    }

    \pageBreak
    \markup \rubric "Psalmus. Tonus iii." \noPageBreak
    \score {
      \new Staff \with {
        \remove Time_signature_engraver
        \override Stem.stencil = ##f
        \override Flag.stencil = ##f
        \override Slur.thickness = #1.4
        instrumentName = \markup \abs-fontsize #10 "℣."
      } {
        \clef "treble_8" \cadenzaOn \key c \major
        g4 a( c') c' c' c' c' c' \bar "'"
        c' d' c' c' b( a) c'( c' c') \bar "|"
        b( g) a( c') c' c' c' c' c' c' c' c' c'2 \bar "'"
        c'4 c' c' c' c'( c' b) a( g) a b g( a2) \bar "||"
      }
      \addlyrics {
        Dó -- mi -- ne pro -- bá -- sti me,
        et co -- gno -- ví -- sti "me: *"
        tu co -- gno -- ví -- sti ses -- si -- ó -- nem me -- am,
        et re -- sur -- re -- cti -- ó -- nem me -- am.
      }
      \layout {
        indent = 10\mm
        \context { \Lyrics \override LyricText.font-size = #0.9 \override LyricSpace.minimum-distance = #2.2 \override LyricHyphen.minimum-distance = #1.6 }
      }
    }

    \markup \column { \vspace #0.6 \rubric "Gloria Patri" } \noPageBreak
    \score {
      \new StaffGroup <<
        \voiceStaff "Cantus" "C." "treble"   \cantusDox \cantusDoxText
        \voiceStaff "Altus"  "A." "treble"   \altusDox  \altusDoxText
        \voiceStaff "Tenor"  "T." "treble_8" \tenorDox  \tenorDoxText
        \voiceStaff "Bassus" "B." "bass"     { \bassusDox \bar "|." } \bassusDoxText
      >>
      \layout {
        \polyLayout
        \context { \Score currentBarNumber = #57 }
      }
    }
    \markup \fill-line { \null \rubric "Repetitur antiphona Nunc scio vere." }
  }

}
