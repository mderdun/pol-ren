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
%% Staff size: 17 in critical editions, 19 in performance editions.
#(set-global-staff-size
   (if (eq? (ly:parser-lookup 'prPerformance) #t) 19 17))
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

%% Optional editorial accidental: the note keeps the edition's reading; the
%% bracketed sign above it is an alteration singers may take (Berger 1987).
%% Post-events: b1\optFlat  c'2\optSharp  b1\optNatural
#(define (pr-opt-acc glyph)
   (make-music 'TextScriptEvent 'direction UP
     'text (markup #:fontsize -2.5
             #:concat (#:musicglyph "accidentals.leftparen"
                       #:musicglyph glyph
                       #:musicglyph "accidentals.rightparen"))))
optFlat = #(pr-opt-acc "accidentals.flat")
optSharp = #(pr-opt-acc "accidentals.sharp")
optNatural = #(pr-opt-acc "accidentals.natural")

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

%% Text supplied by the editor: italic underlay. \edText for a whole
%% lyric line (put it first in the \lyricmode block), \rep for one syllable
%% (repeated text standing for a source's ij).
edText = \override LyricText.font-shape = #'italic
rep = \once \override LyricText.font-shape = #'italic

%% Coloration of a single note: both corners over it.
colNote = ^\markup \raise #0.5 \abs-fontsize #9 \concat { "⌜" \hspace #2.2 "⌝" }

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

%% ------------------------------------------------------------ Mensurstriche
%% Drawn between the staves only, as dashed black lines: the score reads as
%% parts first and as a timed score second. No colour but black and red.
\defineBarLine "-span!" #'(#f #f "!")

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
    measureBarType = "-span!"
    \consists "Ambitus_engraver"
    \override InstrumentName.self-alignment-X = #RIGHT
    \override InstrumentName.font-size = #0.6
    \override InstrumentName.padding = #2.4
    \override AccidentalSuggestion.font-size = #-1.5
    \override AccidentalSuggestion.parenthesized = ##f
    \override Ambitus.X-offset = #0.6
  }
  %% Ties are solid; only \divTie (a divided source note) is dashed.
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

%% ------------------------------------------------------------ the score
%% An edition's score.ly calls \prScore with one \prStaff per voice. The same
%% file serves both editions. A performance edition at another pitch sets,
%% before including score.ly:
%%   prPerformance = ##t
%%   prTranspose = { d f }        % from, to
%%   prKey = { \key f \dorian }
%% and gives per-voice performance clefs in \prStaff. Incipits are dropped in
%% a transposed edition (they would show the source's pitch).

#(define (pr-lookup sym default)
   (let ((v (ly:parser-lookup sym))) (if (null? v) default v)))
#(define (pr-transposed?) (not (null? (ly:parser-lookup 'prTranspose))))

prMens = {
  \override Staff.TimeSignature.style = #'mensural
  \override NoteHead.style = #'petrucci
  \time 2/2
}

%% \prStaff long short incipit clef perf-clef notes words
%%   words: one \lyricmode block, or << \stanzaOne \stanzaTwo >> for several
%%   incipit: music for the incipit staff (clef, sign, first note), or {} for none
%%   perf-clef: clef in a transposed performance edition ("" = same as clef)
prStaff =
#(define-music-function (long short inc clef pclef notes words)
   (string? string? ly:music? string? string? ly:music? ly:music?)
   (let* ((transposed (pr-transposed?))
          (tr (and transposed (ly:music-property (ly:parser-lookup 'prTranspose) 'elements)))
          (from (and tr (ly:music-property (car tr) 'pitch)))
          (to (and tr (ly:music-property (cadr tr) 'pitch)))
          (useclef (if (and transposed (not (string-null? pclef))) pclef clef))
          (key (pr-lookup 'prKey #{ #}))
          (sign (pr-lookup 'prSign "timesig.C22"))
          (vname (string-downcase long))
          (music (if transposed #{ \transpose #from #to #notes #} notes))
          (incipit (if (or transposed (null? (ly:music-property inc 'elements)))
                       #{ #}
                       #{ \incipit { \prMens #inc } #})))
     #{ <<
          \new Staff \with \vname #long #short {
            $incipit
            \clef #useclef $key
            \time 2/1
            $(if (string-null? sign) #{ \omit Staff.TimeSignature #} #{ \mensSign #sign #})
            \voiceSetup
            \new Voice = #vname $music
          }
          $(make-simultaneous-music
             (map (lambda (w) #{ \new Lyrics \lyricsto #vname $w #})
                  (if (music-is-of-type? words 'simultaneous-music)
                      (ly:music-property words 'elements)
                      (list words))))
        >> #}))

%% Per-score layout: music/engraving.ily may define
%%   prLayoutCritical = \layout { ... }   and/or   prLayoutPerformance = \layout { ... }
%% for spacing that only this score needs; score.ly ends with \layout { $(pr-layout) }.
#(define (pr-layout)
   (let ((v (ly:parser-lookup
             (if (eq? (ly:parser-lookup 'prPerformance) #t)
                 'prLayoutPerformance 'prLayoutCritical))))
     (if (null? v) (ly:parser-lookup '$defaultlayout) v)))

%% Per-score engraving: an edition's music/engraving.ily may set
%%   prBreaksCritical = #'(5 10 15 20 25)     ; system breaks after these bars
%%   prBreaksPerformance = #'(5 10 15 20 25)
%%   prBarLength = #(ly:make-moment 2/1)       ; length of a bar (default breve)
%% and spacing for this score only. Style stays in this file.
#(define (pr-break-voice breaks)
   (let* ((len (pr-lookup 'prBarLength (ly:make-moment 2/1)))
          (last (apply max breaks)))
     (make-sequential-music
      (append-map
       (lambda (bar)
         (list (make-music 'SkipEvent 'duration
                 (ly:make-duration 0 0 (ly:moment-main len)))
               (if (memv bar breaks)
                   (make-music 'LineBreakEvent 'break-permission 'force)
                   (make-music 'LineBreakEvent 'break-permission '()))))
       (iota last 1)))))

prScore =
#(define-music-function (staves) (ly:music?)
   (let* ((perf (eq? (ly:parser-lookup 'prPerformance) #t))
          (breaks (pr-lookup (if perf 'prBreaksPerformance 'prBreaksCritical)
                             (pr-lookup 'prBreaks '()))))
     (if (null? breaks)
         #{ \new StaffGroup $staves #}
         #{ \new StaffGroup << $staves \new Devnull $(pr-break-voice breaks) >> #})))
