%% Wacław z Szamotuł, Nunc scio vere — critical edition for voices
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

  %% ============================================================ TITLE
  \bookpart {
    \paper { print-page-number = ##f }
    \markup \column {
      \vspace #5
      \fill-line { \abs-fontsize #9.5 \override #'(word-space . 1.2) \sc "Polish Early Music" }
      \vspace #6
      \fill-line { \abs-fontsize #13 \sc "Wacław z Szamotuł" }
      \vspace #0.3
      \fill-line { \abs-fontsize #10 "c. 1520 – c. 1560" }
      \vspace #2.2
      \fill-line { \abs-fontsize #34 "Nunc scio vere" }
      \vspace #1
      \fill-line { \abs-fontsize #13 \italic "Introit for the Feast of Saints Peter and Paul" }
      \vspace #0.4
      \fill-line { \abs-fontsize #11 "Antiphon and Gloria Patri for four voices" }
      \vspace #2.5
      \fill-line { \override #'(span-factor . 1/6) \draw-hline }
      \vspace #2.5
      \fill-line { \abs-fontsize #10.5 \italic "Edited from the lost organ tablature of c. 1590" }
      \fill-line { \abs-fontsize #10.5 \italic "and the reconstruction by Mirosław Perz (1966)" }
      \vspace #1.2
      \fill-line { \abs-fontsize #11 "by Mikołaj Derdun" }
      \vspace #9
    }
    \markuplist \table-of-contents
    \markup \column {
      \vspace #6
      \fill-line { \abs-fontsize #9 "First edition · October 2026" }
    }
  }

  %% ============================================================ PREFACE
  \bookpart {
    \header { runhead = "Preface" }
    \tocItem \markup "Preface"

    \markup \head "The work" \noPageBreak
    \markup \para {
      \italic { Nunc scio vere } is the Introit for Saints Peter and Paul
      (29 June). Medieval Polish graduals also give it to Saint Peter’s Chains
      (1 August). Wacław set the antiphon and the \italic { Gloria Patri. } The
      psalm verse between them was sung to its chant tone, and the antiphon
      was then repeated.
    }
    \markup \para {
      The setting survives in one source, an eight-leaf fragment of an organ
      tablature of about 1590. Aleksander Poliński found it, and it is called
      the ‘Castle’ tablature after the State Art Collections in the Royal
      Castle, Warsaw, where it was later kept. It passed to the National
      Library and was destroyed in 1944. The fragment was probably part of the
      Łowicz tablature, which contains a cycle of introits by Marcin Leopolita
      and others. \italic { Nunc scio vere } stood on fols. 7v–8r, headed
      \italic { In die Apostolorum Petri et Pauli. Nunc scio vere W. S. } The
      monogram is usually read as Wacław’s. Tomasz Czepiel doubts the
      attribution.
    }
    \markup \para {
      Wacław studied in Poznań and Kraków. He became composer to Sigismund II
      Augustus in 1547 and later served Mikołaj Radziwiłł ‘the Black’. Two
      other Latin motets by him survive, both printed in Nuremberg:
      \italic { In te Domine speravi } (1554) and \italic { Ego sum pastor
      bonus } (1564). A Kraków inventory of 1572, made after the death of
      Jurek Jasiuczyc, lists ‘offitia Vaczlavove’. Poles used
      \italic officium for the introit, so these may have been settings like
      this one.
    }

    \markup \head "The music" \noPageBreak
    \markup \para {
      The introit chant (third mode) runs through the setting in equal
      values, lightly ornamented. It moves between voices. The Tenor has it
      for \italic { Nunc scio vere } (bars 3–12) and the Cantus from
      \italic quia to the end of the antiphon (13–56). In the \italic { Gloria
      Patri } the Bassus recites the psalm tone on c (63–71). These entries are
      marked [c.f.]. The other voices treat each clause of text as a point of
      imitation. The antiphon ends on E, the final of the mode. The
      \italic { Gloria Patri } ends on A, the last note of the psalm tone’s
      termination.
    }

    \markup \head "The reconstruction" \noPageBreak
    \markup \para {
      Mirosław Perz made a vocal version from photographs of the two pages and
      published it in 1966 (P). He set it a minor third above the tablature
      (T) and added his own underlay. His commentary records every reading of
      T that he changed. This edition starts from P, returns the music to the
      pitch of T and weighs each of Perz’s changes against T. Most stand. At
      bars 6, 9, 30 and 81–83 T’s reading is restored. The critical commentary
      lists every decision, so any of them can be reversed.
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
    \markup \vspace #0.5
    \markup \para {
      Acts 12:11; Psalm 138 (139):1–2. The verse is given as in the
      \italic { Graduale Romanum. } Medieval Polish graduals end it at
      \italic { sessionem meam; } singers who prefer that reading apply the
      termination to \italic { ses-si-ó-nem me-am. }
    }

    \markup \head "Editorial method" \noPageBreak
    \markup \subhead "Pitch and note values" \noPageBreak
    \markup \para {
      Pitch is that of T. At this pitch the antiphon ends on E with no
      signature, the normal position of the third mode, and the voices fit
      the ordinary low clefs (C1, C3, C4, F4). Cantus c′–e″, Altus f–a′, Tenor
      d–e′, Bassus E–a. A vocal original in this mode would have been notated
      this way, and nothing suggests the intabulator transposed it. P’s pitch
      would need three flats in the signature, which no source of the period
      uses. Written pitch was not sounding pitch, though (see Performance).
    }
    \markup \para {
      Note values are twice those of T and P. German organ tablatures often
      halve the values of their vocal models. As Perz transcribes it, T moves
      in semiminims and fusae, with semifusae at cadences, values a vocal
      motet of about 1550 would hardly use. Doubled, the music moves in
      semibreves and minims under ¢, like Wacław’s two printed motets. The
      bar is a breve, so bar numbers match P. The mensuration sign is
      editorial.
    }
    \markup \subhead "Score" \noPageBreak
    \markup \para {
      Bar lines run between the staves only. Voice names and clefs are
      editorial. Each voice’s range is shown at the head of its staff. Rests
      at entries follow P, since a tablature notates rests only in part.
      Final notes are printed as longs. The corona at bar 56 is P’s.
    }
    \markup \subhead "Accidentals" \noPageBreak
    \markup \para {
      A tablature spells every pitch, so accidentals before notes come from T.
      Accidentals above the staff are editorial, all of them suggested by
      Perz. Each sign applies only to the note it stands against.
    }

    \markup \head "Text underlay" \noPageBreak
    \markup \para {
      T gives only the text incipit. Every syllable below the notes is
      therefore editorial, placed by the method below.
    }
    \markup \li "1." {
      \bold Chant. Where a voice carries the cantus firmus, it takes the
      chant’s syllables. Each syllable starts on the first note of its chant
      neume, and a chant melisma stays on one syllable, subject to the rules
      that follow.
    }
    \markup \li "2." {
      \bold { Wacław’s practice. } His Kraków \italic Lamentationes (1553) set
      most of the text one syllable to a note, repeated notes included. A
      melisma comes before the cadence on the stressed syllable of the last
      word, and the final syllable takes the cadence note \concat { "(" \italic { mé–am, } }
      \italic { lú–cem, hó–minum, } \concat { \italic { su-á–rum } ")." } Short repeats are marked \italic ij,
      longer ones written out. The Nuremberg prints of his motets agree at
      clause ends but place the words too loosely to settle more. Nine in ten
      clause-final words here follow the \italic Lamentationes; the rest carry
      a short ornament or keep an imitative head-motif.
    }
    \markup \li "3." {
      \bold { The theorists. } These rules are kept without exception. A new
      syllable goes only on a minim or longer note (Lanfranco 1533; Zarlino
      1558, IV.33). None goes on a dot, or on the semiminim after a dotted
      minim (Lanfranco, Zarlino). The first note after a rest and the last
      note of a phrase each take a syllable (Zarlino). No rest divides a
      word, and there is no elision (Vicentino 1555). A repeated note takes a
      new syllable unless it is a semiminim, one of Stoquerus’s necessary rules
      (c. 1570, ch. 15).
    }
    \markup \li "" {
      Other rules are applied with the latitude Stoquerus allows the older
      generation of composers, the Netherlanders whose idiom Wacław shares.
      After a run of semiminims the syllable usually changes on the second
      white note, not the first (Vicentino), but not always. Long or stressed
      syllables go to long notes (Zarlino). A clause is repeated to keep the
      voices together or for emphasis, and repeated whole (Stoquerus).
    }
    \markup \li "4." {
      \bold Accent. Stress follows the penultimate rule as Kraków taught it in
      Wacław’s student years (Sebastian z Felsztyna 1518; Jerzy Liban c. 1539).
      Hence \italic { Dóminus, ángelum, erípuit, Heródis, exspectatióne,
      Iudaeórum, princípio, saeculórum. }
    }
    \markup \li "5." {
      \bold Imitation. Each point of imitation takes its opening motif from a
      phrase of the chant, and the words of that phrase go with it. A motif
      keeps its words wherever it recurs. Perz used the same method for
      Leopolita’s introits from this tablature (1967).
    }
    \markup \para {
      Repeated text is printed in italics, as editions print words supplied
      for a source’s \italic ij.
    }

    \markup \head "Performance" \noPageBreak
    \markup \para {
      At written pitch the setting suits an all-male chapel like Sigismund
      Augustus’s, with boys or falsettists on the Cantus (c′–e″) and a low
      Bassus (E–a). The chapel paid boy singers \concat { "(" \italic pueri, }
      \concat { \italic "adolescentes cantores" ")" } alongside its men, and Wacław’s \italic Lamentationes, in
      clefs lower still, were written for low men’s voices. Every
      voice lies two to five semitones lower than in
      Wacław’s printed motets, the Cantus most of all. A minor third higher,
      as in P, the four ranges match his printed ones almost exactly. That is
      the pitch for a mixed choir, and a sound choice for any choir, since
      written pitch fixed only the relations between the voices.
    }
    \markup \para {
      A minim pulse of about 60–72 suits the declamation. The organ may double
      the voices. The order is Antiphon, psalm verse (cantor, in chant),
      \italic { Gloria Patri, } Antiphon. The Introit was often sung in
      alternation with the organ. Perz argued in 1967 that the \italic { Gloria
      Patri } settings of Leopolita’s introits in the same tablatures were
      organ versets, and that the organ could play the repeat of an introit
      while the choir said the words quietly. This edition texts the
      \italic { Gloria Patri } because its Bassus recites the psalm tone
      syllable by syllable. An organ doxology or an organ repeat of the
      antiphon has as good a claim. Marcin Szelest has recorded the
      \italic { Gloria Patri } from T as an organ piece (Accord, 2023).
    }
    \markup \para {
      Polish Latin suits the piece. Stress follows the penultimate rule
      (rule 4 above).
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
      \italic { ti- } as [tsj] is the older usage. Polish schools now teach
      [ti]. Sources: Wikarjak 1979; Jurewicz et al. 2004.
    }
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
    \tocItem \markup "Nunc scio vere"

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

  %% ============================================================ COMMENTARY
  \bookpart {
    \header { runhead = "Critical commentary" }
    \tocItem \markup "Critical commentary"

    \markup \head "Sources" \noPageBreak
    \markup \cn \sig "T" "" {
      Organ tablature, c. 1590 (‘Castle’ or ‘Small Warsaw’ tablature; Poliński
      collection), fols. 7v–8r: \italic { In die Apostolorum Petri et Pauli. Nunc
      scio vere W. S. } Text incipit only. Destroyed 1944. Glass-plate
      photographs of three pieces from the fragment, probably of 1928, are in
      the Institute of Musicology, Jagiellonian University (IMuzUJ 014–017).
    }
    \markup \cn \sig "P" "" {
      Mirosław Perz, vocal reconstruction from photographs of T, in Hieronim
      Feicht (ed.), \italic { Muzyka staropolska / Old Polish Music } (Kraków:
      PWM, 1966), pp. 61–65; commentary pp. 380–81. Up a minor third; values as
      in T; editorial underlay. \italic { Base text, } revised against T.
    }
    \markup \cn "" "" {
      Also: Piotr Poźniak (ed.), \italic { Musica Antiqua Polonica: The
      Renaissance – Vocal Music } (PWM, 1993), not seen.
    }

    \markup \head "Readings of T altered in P" \noPageBreak
    \markup \para {
      References are to bar, voice and note; tied continuations are not
      counted. Pitches are at the pitch of this edition (c′ = middle C), and
      note values are those of this edition, twice those of T and P. Each note
      gives T’s reading, Perz’s change and his reason, then this edition’s
      decision in bold.
    }
    \markup \para {
      Perz’s changes fall into three groups. Some cure a fault of
      counterpoint, such as parallel octaves, a mishandled dissonance or an
      inner voice given to the wrong part. These are \bold { accepted, }
      because restoring T brings the fault back. Others remove a figure Perz
      thought instrumental. He judged it at the halved values of the
      tablature. At this edition’s values the figures are ordinary vocal
      ornaments, so T is \bold restored unless it creates a fault. The last
      group joins repeated notes ‘for the underlay’. T is restored where its
      repeated notes can carry syllables, as Stoquerus requires, and P stands
      where they cannot.
    }
    \markup \cn "6" "C" { T: e′ tied from bar 5, e′ (minims), f′ d′ (semiminims), e′ (minim). P: tied breve e′ and breve rest, the figure being instrumental. At doubled values it is a common cadential ornament, and makes no fault. \bold { T restored } \concat { "(" \italic { ve-re } } repeated). }
    \markup \cn "9" "T" { T: in the second half, minim c′ and semibreve c′ tied into bar 10. P: dotted semibreve, for the underlay. The repeated c′ takes \italic { -o. } \bold { T restored. } }
    \markup \cn "20" "A" { T: in the second half, minim f′ and semibreve f′ tied into bar 21. P: dotted semibreve, for the underlay. T would give five repeated f′ to the four syllables of \italic { -lum an-ge-lum. } \bold { P accepted. } }
    \markup \cn "25" "A, T" { T: A c′, T g. P exchanges them, to avoid octaves and fifths with B. T gives octaves A–B twice and fifths T–B. \bold { P accepted. } }
    \markup \cn "26" "A" { T: e′ in place of the rest. Omitted in P for octaves with B. The octave is approached, not consecutive; but the rest lets the Altus breathe before its entry at \italic { et eripuit, } and the e′ is probably the organist’s filling. \bold { P accepted. } }
    \markup \cn "30" "A" { T: first note e′. P: c′, for the cadence the text creates. T’s e′ supplies the only third of the C chord, which otherwise stands bare for a semibreve. \bold { T restored. } }
    \markup \cn "31" "A, T" { T: A c′, T a. P exchanges them, restoring the tenor’s line. \bold { P accepted. } }
    \markup \cn "34" "A" { T: second note a. P: b, for the cadence. The cadence to C has the 4–3 suspension in the Cantus, and b is its leading note. \bold { P accepted. } }
    \markup \cn "35–37" "C" { T: two separate breves f′. P ties them, for the underlay. The second f′ falls after the clause has ended, and no syllable is left for it. \bold { P accepted. } }
    \markup \cn "37" "A" { T: the first two notes are one dotted semibreve d′. P divides it (semibreve, minim) to keep the imitation exact. \bold { P accepted } (rule 5). }
    \markup \cn "49–50" "C" { T: minims g′ e′ in place of the tied semibreve g′. P: g′, for octaves with T. The octaves are real. \bold { P accepted. } }
    \markup \cn "49" "B" { T: second note without rhythm sign; read as a minim. }
    \markup \cn "52" "C" { T: in the second half, semiminims d′ c′ d′ e′. P: dotted minim d′, semiminim e′ (instrumental figure; fifths with T). The figure is vocal at these values, but the fifths are real (C–T, bar 52). \bold { P accepted. } }
    \markup \cn "53" "T" { T: first note f. P: a, for octaves with C. The octaves are real. \bold { P accepted. } }
    \markup \cn "64" "T" { T: third note d. P: f, calling d an error. d would be a dissonant semiminim left by leap. \bold { P accepted. } }
    \markup \cn "71" "A, T" { T: A c′, T a. P exchanges them (imitation in A; octaves between T and B). The octaves are real. \bold { P accepted. } }
    \markup \cn "76–77" "A" { T: one breve e′ in each bar. P: two semibreves each, for the underlay. The split gives \italic { et nunc, et semper } in the declamation the other voices have. \bold { P accepted. } }
    \markup \cn "81" "T" { T: third note b. P: g, for the cadence. T’s b sounds the resolution against the Cantus’s suspended c″. \bold { P accepted. } }
    \markup \cn "81–83" "C" { T: minims c″ a′ b′ g′ f′ a′, semibreves b′ c″, minims c″ a′. P: dotted semibreve c″, minim b′, semibreves a′ b′, dotted semibreve c″; P calls the sequence instrumental. At these values it is a vocal sequence in minims, consonant throughout, without parallels. \bold { T restored } \concat { "(" \italic { saeculorum } } twice). }
    \markup \cn "86" "C" { T: two minims in place of the semibreve a′. P joins them, for the underlay. T would put the final syllable before the cadence. \bold { P accepted. } }
    \markup \cn "86" "B" { T: second note d. P: f, for octaves with A. The octaves are real. \bold { P accepted. } }

    \markup \head "Other notes" \noPageBreak
    \markup \cn "15–16" "C, T" { Parallel fifths (b′ e′ to a′ d′, bar 16), left as in T, following P. }
    \markup \cn "44" "C" { b′ as in T, a tritone above the bass F on the third minim; P does not alter it. Singers may prefer b♭′, as in bar 45. }
    \markup \cn "44" "B" { The flat is P’s; T has B, against b♭ in the Tenor a minim later. }
    \markup \cn "54" "A, T" { Parallel fifths on the first minim, as in P. }
    \markup \cn "56" "A" { e′ (small note) is P’s addition, in square brackets in P; T presumably continued c′ from bar 55. P’s e′ makes fifths with B (a–e′, E–b); the tied c′ does not, and is a fair alternative. }
    \markup \cn "57–62" "B, T" { Bassus rests for six bars, Tenor for three; the \italic { Gloria Patri } opens in two voices, as in T. }
    \markup \cn "88" "A" { c♯′ (major final chord) is in T; at bar 87 the sharp is P’s. }

    \markup \head "Underlay" \noPageBreak
    \markup \cn "3–12" "T" { Cantus firmus. \italic { Nunc } covers the chant’s opening neume (f–d–g–f–e), \italic { sci-o } its g and a; \italic { -re } falls on the cadence note c′ of bar 9, and the clause is repeated. }
    \markup \cn "13–56" "C" { Cantus firmus. Syllables follow the chant, e.g. \italic { om- } on g′–a′ and \italic { -ni } on d′ (bars 41–42), and three syllables of \italic { exspectatione } on the repeated g′ of bars 42–43. Where the chant and rule 3 conflict, the rule decides \concat { "(" \italic { -mi- } } of \italic { Dominus, } bar 16). }
    \markup \cn "26–29" "C" { The chant’s melisma on \italic { erípuit } falls on \italic { -it, } not \italic { -pu-; } the Cantus follows it, with \italic { -it } on the c″ of bar 27. }
    \markup \cn "" "" { Elsewhere, where a free voice had a melisma of more than four semibreves, the clause is repeated instead, as in Wacław’s prints (e.g. T, \italic { exspectatione, } bars 44–48; B, \italic { eripuit me, } bars 25–30). }
    \markup \cn "44–45" "C" { The stressed \italic { -o- } of \italic { exspectatione } takes the semibreve a′; the chant’s c″ at bar 44 carries \italic { -ti-. } }
    \markup \cn "50–56" "all" { The stressed \italic { -o- } of \italic { Iudaeórum } falls on a strong minim or a high note in every voice (e.g. C, the semibreve a′ at bar 53). }
    \markup \cn "63–71" "B" { The Bassus recites the psalm tone on c; its mediant shape (d c c, c–a, c) carries \italic { -ri-tu-i San-cto } syllabically. }

    \markup \head "Bibliography" \noPageBreak
    \markup \subhead "Sources and editions" \noPageBreak
    \markup \bib { Feicht, Hieronim (ed.). \italic { Muzyka staropolska / Old Polish Music. } Kraków: PWM, 1966. (P: pp. 61–65; commentary by Mirosław Perz, pp. 380–81.) }
    \markup \bib { \italic { Tomus quartus psalmorum selectorum. } Nuremberg: Montanus & Neuber, 1554 (RISM B/I 1554/11). Wacław, \italic { In te Domine speravi, } no. 17. Munich, BSB, "4 Mus.pr. 188#Beibd.3," digitised. }
    \markup \bib { Wacław z Szamotuł. \italic { Quatuor parium vocum lamentationes Hieremiae prophetae. } Kraków: Łazarz Andrysowic, 1553. Tenor: Munich, BSB, 4 Mus.pr. 145, digitised. Altus and Bassus fragments: Gniezno, Archiwum Archidiecezjalne, PL 489, facsimile in Łukaszewski and Wydra 2016. }
    \markup \bib { \italic { Thesauri musici tomus quintus. } Nuremberg: Montanus & Neuber, 1564 (RISM B/I 1564/5). Wacław, \italic { Ego sum pastor bonus. } }
    \markup \bib { Wacław z Szamotuł. \italic { In te Domine speravi; } \italic { Ego sum pastor bonus } (1564 print and Stuttgart, WLB, Cod. mus. I fol. 8). Ed. Klaas Spijker. IMSLP and CPDL, n.d. }
    \markup \bib { \italic { Graduale Romanum. } Solesmes, 1961, p. 532. Cantus Index g00257; Cantus Planus in Polonia (cantus.ispan.pl). }
    \markup \subhead "Theory" \noPageBreak
    \markup \bib { Lanfranco, Giovanni Maria. \italic { Scintille di musica. } Brescia, 1533, pp. 68–69. }
    \markup \bib { Zarlino, Gioseffo. \italic { Le istitutioni harmoniche. } Venice, 1558, Part IV, ch. 33. }
    \markup \bib { Vicentino, Nicola. \italic { L’antica musica ridotta alla moderna prattica. } Rome, 1555, Book IV, chs. 29–30. }
    \markup \bib { Stoquerus, Gaspar. \italic { De musica verbali libri duo, } ed. and trans. Albert C. Rotola. Lincoln: University of Nebraska Press, 1988. }
    \markup \bib { Sebastian z Felsztyna. \italic { Modus regulariter accentuandi lectiones. } Kraków, 1518. }
    \markup \bib { Liban, Jerzy. \italic { De accentuum ecclesiasticorum exquisita ratione. } Kraków, c. 1539. }
    \markup \subhead "Studies" \noPageBreak
    \markup \bib { Czepiel, Tomasz M. M. \italic { Music at the Royal Court and Chapel in Poland, c. 1543–1600. } New York: Garland, 1996. }
    \markup \bib { Harrán, Don. ‘New Light on the Question of Text Underlay Prior to Zarlino’. \italic { Acta Musicologica } 45 (1973): 24–56. }
    \markup \bib { Harrán, Don. ‘Vicentino and His Rules of Text Underlay’. \italic { Musical Quarterly } 59 (1973): 620–32. }
    \markup \bib { Jurewicz, Oktawiusz, Lidia Winniczuk and Janina Żuławska. \italic { Język łaciński: podręcznik dla lektoratów szkół wyższych. } 25th ed. Warsaw: PWN, 2004, pp. 13–16. }
    \markup \bib { Łukaszewski, Jakub, and Wiesław Wydra. \italic { Fragmenty Kota ze lwem Mikołaja Reja i innych druków z XVI w. odnalezione. } Poznań: Poznańskie Studia Polonistyczne, 2016. }
    \markup \bib { Perz, Mirosław. ‘Motety Marcina Leopolity’. In \italic { Studia Hieronymo Feicht septuagenario dedicata, } ed. Zofia Lissa, 157–89. Kraków: PWM, 1967. }
    \markup \bib { Poźniak, Piotr, and Ryszard Wieczorek. ‘Wacław z Szamotuł’. \italic { Encyklopedia muzyczna PWM, } online edition (Polska Biblioteka Muzyczna), 2023. }
    \markup \bib { Schubert, Peter, and Julie E. Cumming. ‘Text and Motif c.1500: A New Approach to Text Underlay’. \italic { Early Music } 40 (2012): 3–14. }
    \markup \bib { Szelest, Marcin. ‘Nowo odkryte fragmenty \italic Lamentationes Wacława z Szamotuł: przyczynek do odczytania źródła’. \italic { Muzyka } 63, no. 1 (2018). }
    \markup \bib { Szelest, Marcin. ‘Przyczynki do działalności i twórczości muzyków związanych z dworem królewskim Rzeczypospolitej w drugiej połowie XVI wieku’. \italic { Muzyka } 67, no. 4 (2022): 81–115. }
    \markup \bib { Towne, Gary. ‘A Systematic Formulation of Sixteenth-Century Text Underlay Rules’. \italic { Musica Disciplina } 44 (1990): 255–87; 45 (1991): 143–68. }
    \markup \bib { Wieczorek, Ryszard J., and Michał Wysocki. ‘\italic Lamentationes Wacława z Szamotuł: fragmenty brakujących głosów odnalezione w Gnieźnie’. \italic { Muzyka } 62, no. 2 (2017): 4–20. }
    \markup \bib { Wikarjak, Jan. \italic { Gramatyka opisowa języka łacińskiego. } Warsaw: PWN, 1979, pp. 7–8. }
  }
}
