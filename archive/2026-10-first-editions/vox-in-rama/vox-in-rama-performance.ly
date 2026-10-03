\version "2.24.0"
\include "common.ily"
\include "voices.ily"
\include "lyrics.ily"
\include "score.ily"
\include "perfscore.ily"

\header { tagline = ##f }

\book {
  \bookOutputName "vox-in-rama-performance"

  \bookpart {
    \paper { print-first-page-number = ##f top-margin = 12\mm bottom-margin = 12\mm
              markup-markup-spacing = #'((basic-distance . 1) (padding . 0.2)) }
    \markup \fill-line { \center-column {
      \abs-fontsize #22 "Vox in Rama"
      \vspace #0.3
      \abs-fontsize #13 \italic "Communio in festo SS. Innocentium"
      \vspace #0.8
      \abs-fontsize #12 "Mikołaj Zieleński (fl. 1604–1611)"
      \vspace #0.6
      \abs-fontsize #10.5 \smallCaps "Performance edition"
      \abs-fontsize #10.5 "a fifth below the printed pitch"
      \abs-fontsize #10.5 "ed. Mikołaj Derduń · Polish Early Music"
      \vspace #1
    } }

    \markup \sectionHead "About the piece"
    \noPageBreak
    \markup \para {
      The communion for the Mass of the Holy Innocents (28 December), printed
      in Venice in 1611 in Zieleński’s \italic { Communiones totius anni. }
      Zieleński was organist and chapel master to Wojciech Baranowski,
      primate of Poland, whose court was at Łowicz. The text is Matthew’s
      quotation of Jeremiah: Rachel weeping for her children. The setting
      is short, follows the words closely, and saves its chromatic writing for
      ‘ploratus et ululatus’ (bars 15–19).
    }

    \markup \sectionHead "Voices and organ"
    \noPageBreak
    \markup \para {
      The print asks for the singers alone with the organ (‘Soli debent
      cantare cum Organo’), one voice to a part. The organist played from a
      separate organ book. That book has not been consulted for this
      edition, but organ parts of this kind normally follow the voices, so
      the piece can be sung without organ, or by a choir, with nothing
      missing.
    }

    \markup \sectionHead "Pitch"
    \noPageBreak
    \markup \para {
      This score is a fifth below the print. The print uses high clefs, and
      high clefs meant transposition. Adriano Banchieri’s \italic Cartella
      (Venice, 1601 and 1610) says that pieces in these clefs are sung a
      fourth lower when they have a flat and a fifth lower when they have
      none. \italic { Vox in Rama } has none, and Banchieri’s own example of
      the fifth-lower case has its Tenor in the same C2 clef as the Tenor of
      this piece. Down a fifth, it ends on D, with one flat, and the ranges
      are Cantus c′–d″, Altus g–b♭′, Tenor c–d′, Bassus D–f: an ordinary
      four-part choir. A fourth down, ending on E (as on CPDL), also works.
      The small
      bracketed notes in the last bar are an editorial suggestion, not in the
      print: when the Altus reaches its final note, Tenor and Bassus may drop
      to the lower octave, as the organ would probably have done and as the
      Huelgas Ensemble does.
    }

    \markup \sectionHead "Reading the score"
    \noPageBreak
    \markup \para {
      The note values are those of the print; only the pitch has been
      changed, and the one-flat signature comes from the transposition. The
      beat is the semibreve
      (whole note), about 50–60 to the minute; the sign
      \musicglyph "timesig.C22" means a semibreve beat, not a fast one. A bar
      is two beats. A note that crosses a bar line is held for its full
      value. An accidental applies only to
      the note it stands before. A small accidental above the staff is the
      editor’s. Square brackets over the Tenor mark ligatures, and the corner
      brackets in bar 17 mark a blackened note in the print. The range of each
      voice is shown at the start of its staff.
    }

    \markup \sectionHead "Pronunciation"
    \noPageBreak
    \markup \para {
      Latin as sung in Poland c. 1600: \italic c before e and i as ts;
      \italic ch as in Scottish \italic loch, so \italic Rachel is
      RAH-khel; \italic qu as kv, so \italic quia is KVEE-ah;
      \italic s always voiceless. Stress: RAH-ma, ow-DEE-ta,
      plo-RAH-tus, oo-loo-LAH-tus, PLO-rans, FEE-li-os, NO-loo-it,
      kon-so-LAH-ri.
    }

    \markup \sectionHead "Text and translation"
    \noPageBreak
    \markup \fill-line {
      \hspace #1
      \override #'(baseline-skip . 3.2) \abs-fontsize #10.5 \column {
        "Vox in Rama audita est,"
        "ploratus et ululatus:"
        "Rachel plorans filios suos,"
        "et noluit consolari,"
        "quia non sunt."
      }
      \override #'(baseline-skip . 3.2) \abs-fontsize #10.5 \italic \column {
        "A voice was heard in Rama,"
        "weeping and wailing:"
        "Rachel weeping for her children,"
        "and she would not be comforted,"
        "because they are not."
      }
      \hspace #1
    }
  }

  \bookpart {
    \paper { print-first-page-number = ##t }
    \header {
      title = \markup \abs-fontsize #18 "Vox in Rama"
      subtitle = \markup \column { \rubric "A 4. In festo Sanctorum Innocentium." \abs-fontsize #9 "a fifth below the printed pitch" }
      composer = \markup \abs-fontsize #11 "Mikołaj Zieleński"
      arranger = \markup \abs-fontsize #9 \italic "ed. Mikołaj Derduń"
      tagline = ##f
    }
    \score { \perfScore }
  }
}
