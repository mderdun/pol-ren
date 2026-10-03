%% pol-ren.ily — house engraving style for the Polish Early Music editions
%%
%% LilyPond only engraves the music. Page size, line width, running heads,
%% titles and all prose belong to the LaTeX class (house/latex/pol-ren.cls);
%% lilypond-book passes the line width in. Do not set paper margins here.
%%
%% The score is the same in the critical and the performance edition.
%% The only difference allowed is staff size (set by the edition file).

\version "2.24.0"

%% ------------------------------------------------------------ type
\paper {
  #(define fonts
     (make-pango-font-tree "Junicode" "Junicode" "DejaVu Sans Mono"
                           (/ staff-height pt 20)))
  indent = 27\mm
  short-indent = 7\mm
  incipit-width = 12\mm
  system-system-spacing = #'((basic-distance . 14) (minimum-distance . 10)
                              (padding . 2) (stretchability . 12))
  tagline = ##f
}

%% ------------------------------------------------------------ signs
%% Mensuration sign as printed in the source. Use the glyph name of the sign:
%% "timesig.C22" (cut C), "timesig.C44" (C), "timesig.mensural32" (O) ...
mensSign =
#(define-music-function (glyph) (string?)
   #{ \override Staff.TimeSignature.stencil =
        #(lambda (grob) (grob-interpret-markup grob
           (markup #:musicglyph glyph))) #})

%% Editorial accidental: small, above the note, valid for that note only.
fi = \once \set suggestAccidentals = ##t

%% Note supplied by the editor: small notehead.
ed = \tweak font-size #-3 \etc

%% Note supplied where the source has none legible: square brackets.
#(define (pr-bracket-head grob)
   (bracketify-stencil (ly:note-head::print grob) Y 0.12 0.25 0.12))
sup = \once \override NoteHead.stencil = #pr-bracket-head

%% Editorial suggestion outside the text of the source (performance editions
%% only): small, in round brackets. Must be explained in the notes.
sugg = {
  \once \override NoteHead.font-size = #-2
  \once \override Parentheses.font-size = #1.5
  \once \override Stem.transparent = ##t
  \once \override Flag.transparent = ##t
}

%% Coloration: corner brackets over the blackened notes.
colStart = ^\markup \raise #0.5 \abs-fontsize #9 "⌜"
colEnd   = ^\markup \raise #0.5 \abs-fontsize #9 "⌝"

%% Cantus firmus entry.
cf = ^\markup \abs-fontsize #8.5 \italic "[c.f.]"

%% Divided note (a source note split to carry text): dashed tie.
divTie = { \once \tieDashed \once \override Tie.dash-definition = #'((0 1 0.4 0.75)) }

%% Final note held to a given length in breves (scales a longa so that
%% voices whose final enters late still end together).
finalis =
#(define-music-function (breves) (rational?)
   #{ \set Timing.measureLength = #(ly:make-moment (* 2 breves)) #})

%% Liturgical rubric over the score (Antiphona, Psalmus ...): red italic.
rubric =
#(define-music-function (text) (markup?)
   #{ \tweak self-alignment-X #LEFT
      \tweak color #(rgb-color 0.604 0.118 0.118)
      \mark \markup \abs-fontsize #10.5 \italic #text #})

%% ------------------------------------------------------------ setup
%% Call at the start of every voice, after the clef.
voiceSetup = {
  \accidentalStyle forget
  \autoBeamOff
}

%% ------------------------------------------------------------ contexts
\layout {
  \context { \Score
    \override BarNumber.font-size = #-1.5
    \override BarNumber.font-shape = #'italic
    \override BarNumber.break-visibility = ##(#f #f #t)
    \override BarNumber.self-alignment-X = #LEFT
    \override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/4)
    \override RehearsalMark.break-align-symbols = #'(left-edge clef)
    %% Range of each voice after the clef, before the mensuration sign.
    \override BreakAlignment.break-align-orders =
      #(make-vector 3 '(left-edge cue-end-clef breathing-sign clef cue-clef
                        staff-bar key-cancellation key-signature ambitus
                        time-signature custos))
    \override VoltaBracket.font-size = #-2
    startRepeatBarType = ".|:"
    endRepeatBarType = ":|."
    doubleRepeatBarType = ":..:"
    sectionBarType = "||"
  }
  \context { \StaffGroup
    \override SystemStartBracket.collapse-height = #4
  }
  \context { \Staff
    %% Mensurstriche: bar lines between the staves, never through a note.
    measureBarType = "-span|"
    \consists "Ambitus_engraver"
    \override InstrumentName.self-alignment-X = #RIGHT
    \override InstrumentName.font-size = #0.6
    \override InstrumentName.padding = #1.6
    \override AccidentalSuggestion.font-size = #-1.5
    \override AccidentalSuggestion.parenthesized = ##f
    \override Ambitus.X-offset = #0.6
  }
  \context { \Voice
    \override Tie.dash-definition = #'((0 1 0.4 0.75))
  }
  \context { \Lyrics
    \override LyricText.font-size = #1.0
    \override LyricHyphen.minimum-distance = #1.2
    \override LyricSpace.minimum-distance = #1.2
    \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #0.7
    \override VerticalAxisGroup.nonstaff-nonstaff-spacing.padding = #0.3
    \override StanzaNumber.font-size = #0.6
  }
}

%% Voice names in small capitals, abbreviated after the first system.
vname =
#(define-scheme-function (long short) (string? string?)
   #{ \with {
        instrumentName = \markup \smallCaps #long
        shortInstrumentName = \markup \smallCaps #short
      } #})
