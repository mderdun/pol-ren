\version "2.24.0"
\include "common.ily"
\include "voices.ily"
\include "lyrics.ily"
\include "score.ily"

\header { tagline = ##f }

\book {
  \bookOutputName "vox-in-rama-critical"

  %% ===================================================== FRONT MATTER
  \bookpart {
    \paper { print-first-page-number = ##f }
    \markup \fill-line { \center-column {
      \vspace #2
      \abs-fontsize #22 "Vox in Rama"
      \vspace #0.4
      \abs-fontsize #13 \italic "Communio in festo SS. Innocentium"
      \vspace #1.2
      \abs-fontsize #12 "Mikołaj Zieleński"
      \abs-fontsize #10.5 "(fl. 1604–1611)"
      \vspace #1.2
      \abs-fontsize #10.5 \smallCaps "Critical edition"
      \abs-fontsize #10.5 \concat { "from " \italic "Communiones totius anni" " (Venice: Giacomo Vincenti, 1611), no. 36" }
      \abs-fontsize #10.5 "Tenor from the print; Cantus, Altus and Bassus from modern editions"
      \vspace #0.4
      \abs-fontsize #10.5 "edited by Mikołaj Derduń"
      \abs-fontsize #9.5 \italic "Polish Early Music"
      \vspace #1.5
    } }

    \markup \sectionHead "Introduction"
    \noPageBreak
    \markup \para {
      \italic { Vox in Rama } is the communion of the Mass of the Holy
      Innocents, 28 December. Mikołaj Zieleński set it for four voices and
      organ, and it was printed in Venice in 1611 as no. 36 of his
      \italic { Communiones totius anni. } The \italic Communiones were
      issued together with his \italic { Offertoria totius anni } as a single
      publication with continuous signatures. Between them the two books hold
      all 113 of Zieleński’s known works.
    }
    \markup \para {
      Little is known about the composer. The title pages call him
      ‘Polonus’ and ‘organarius et capellae magister’ to Wojciech Baranowski,
      archbishop of Gniezno and primate of Poland from 1608 until his death in
      1615. Documents gathered by Polish scholars add that he came from Warka
      and married Anna Feterówna. In 1604 Baranowski, then bishop of Płock,
      gave him land at Gromin near Pułtusk. He appeared in court at Łowicz,
      the primate’s seat, at the turn of February and March and again in
      April 1611. His dates of birth and death are unknown, and the
      ‘1550–1615’ printed in library catalogues and on modern scores is a
      convention, not a documented span. Szymon Starowolski wrote in 1625
      that Zieleński had studied in Rome. No document confirms it. The
      dedication of the 1611 books is dated ‘Venetijs Kalend. Martij’, on a
      day when the Łowicz records place him in Poland, so it says nothing
      about where he was.
    }
    \markup \para {
      The dedication does explain why the books were made. Baranowski, it
      says, had restored order in his dioceses and ordered that ‘this proper
      singing of the offertories and communions, each in its place and
      season’ be exactly observed \italic { (hanc ipsam certam ac propriam
      Offertoriorum, ac Communionum suis locis et temporibus decantationem
      exactè obseruari imperasti) }. He commissioned the work and paid for
      the printing. Bound with the parts is a calendar, the
      \italic { Registrum, } that assigns an offertory and a communion to each
      feast. Agnieszka Leszczyńska calls it unprecedented in prints of
      polyphony. It lists \italic { Vox in Rama } for the Innocents and again
      for their octave on 4 January. Zieleński also claims a first. These,
      he writes, are offertories and communions ‘composed for the first time
      by a Pole in the new manner’ \italic { (primùm à Polono nouo modo
      concinnata) }.
    }
    \markup \para {
      The \italic Communiones are ordered by scoring, not by the calendar.
      Pieces for one voice and organ come first, then pieces for two and
      three voices with instruments, then the pieces for four, five and six
      voices. \italic { Vox in Rama } is the fourth of eleven four-voice
      pieces. A rubric in the index governs all the pieces from four voices
      up: those that go plainly \italic (simpliciter) are to be sung with the
      organ and played on instruments; those written with ornaments
      \italic { (cum resolutione) } are sung by the singers with the organ
      played softly. \italic { Vox in Rama } is one of the plain pieces. The
      catalogue of Kurtzman and Schnoebelen, made from the Wrocław and
      Kraków books, records a further rubric for it: ‘Soli debent cantare cum
      Organo’, the singers alone with the organ.
    }
    \markup \para {
      \bold { The text. } The communion takes Matthew 2:18, where the
      evangelist quotes Jeremiah 31:15 after the slaughter of the children of
      Bethlehem. The Missal of 1570 gives it as ‘Vox in Rama audita est,
      ploratus & ululatus: Rachel plorans filios suos: & noluit consolari,
      quia non sunt’. This is the Vulgate text of Matthew without
      \italic multus (‘ploratus, et ululatus multus’). Jeremiah’s own
      Vulgate wording is different (‘Vox in excelso audita est lamentationis,
      luctus, et fletus Rachel plorantis filios suos’). The feast was kept as
      a day of mourning inside Christmastide. The general rubrics of the
      same Missal prescribe violet vestments for the Innocents unless the
      day falls on a Sunday.
    }
    \markup \para {
      \bold { The music. } The setting is 45 breves long and follows the text
      phrase by phrase. Each voice states ‘Vox in Rama’ two or three times in
      staggered entries, often adding a further ‘in Rama’, and the long
      melismas fall on the stressed ‘Ra-’. ‘Audita est’ is set almost
      syllabically. The chromatic writing is kept for ‘ploratus et
      ululatus’. In bar 15 the Cantus falls c″–b′–b♭′, and the b♭′
      sounds over the Altus f♯′ and the Tenor d′, an augmented triad on
      ‘ululatus’. In bar 18 the Cantus has g″–f♯″–f″. ‘Rachel plorans’ and
      ‘filios suos’ are short imitative points. ‘Et noluit consolari’ comes
      four times in the Altus and Tenor and three times in the Cantus and
      Bassus. ‘Quia non sunt’ is set twice, the second time over a Bassus d
      held for two breves, and the piece closes on a chord of A with a major
      third.
    }
    \markup \para {
      The text had been set often as a motet, by Clemens non Papa for four
      voices, for example, and by Giaches de Wert for five (printed 1581).
      Zieleński wrote it as the proper of the day: short, close to the words,
      and with the organ beneath the voices.
    }
    \markup \sectionHead "Sources"
    \noPageBreak
    \markup \para {
      \bold { The print. } \italic { Commvniones totivs anni quibus in
      solennioribus festis Sancta Romana Ecclesia uti consueuit ad cantum
      Organi, per Vnam, Duas, Tres, Quatuor, Quinque, & Sex voces } …
      Venetiis, Apud Iacobum Vincentium. MDCXI (RISM A/I Z 200, issued with
      Z 199). Quarto partbooks and a folio \italic { Partitura pro organo. }
      The only complete set came from the church of St Bernardine in Wrocław
      and was in the city library until 1942. Half of it was lost in the war. What
      survives:
    }
    \markup \item "PL-WRu" {
      Wrocław, Biblioteka Uniwersytecka: Cantus primi chori, Tenor primi
      chori, Altus secundi chori, Tenor secundi chori.
    }
    \markup \item "PL-Kc" {
      Kraków, Biblioteka Książąt Czartoryskich: \italic { Partitura pro
      organo. } According to the Musicare database it gives some pieces in
      full score.
    }
    \markup \item "PL-Kj" {
      Kraków, Biblioteka Jagiellońska: Cantus only.
    }
    \markup \para {
      The four voices of no. 36 were printed in the books of the first choir.
      The Tenor primi chori survives and is the source of this edition’s
      Tenor. The Cantus primi chori also survives and should hold the
      Cantus, but its facsimile was not available. The Altus and Bassus
      primi chori are lost. Before the war Zdzisław Jachimecki and Maria
      Szczepańska transcribed the complete set, and every later edition
      rests on their copies.
    }
    \markup \item "T" {
      Tenor primi chori, no. 36 (p. 76 of the scan): ‘A 4. In festo
      Sanctorum Innocentium. 36 TENOR’. Six staves; C2 clef, sign
      \musicglyph "timesig.C22"; text placed under the notes, with
      \italic ij for repeated words. Facsimile in \italic { Monumenta
      Musicae in Polonia, } ser. D, vol. 12, ed. Jerzy Morawski (Kraków:
      PWM, 1983), consulted in a scan of the Chicago Public Library copy.
      \bold { Base text for the Tenor. }
    }
    \markup \item "N" {
      \italic { Vox in Rama, } notAmos Performing Editions, full score
      100881 (PDF, 2020; CPDL). Four voices and a keyboard reduction. Final
      E, one-sharp signature, note values halved, barred in a mixture of
      3/2 and 2/2.
    }
    \markup \item "M" {
      \italic { Vox in Rama, } ed. Paul R. Marchesano (Finale PDF, 2009,
      and MusicXML, 2017; CPDL). Final F, four-flat signature, note values
      halved, barred in 4/4. \bold { Base text for Cantus, Altus and
      Bassus. }
    }
    \markup \para {
      N and M agree in every note, rest and accidental. M lies a semitone
      above N, and the two are barred differently. Their underlay differs in
      two places (bars 5–6 and 38–39). Both name the 1611 print as their
      source, but neither can have been made from the partbooks alone, since
      the Altus and Bassus are lost. Two editions that agree note for note
      across 45 breves, down to accidentals that T does not print, must share
      a parent: WDMP 12, Malinowski, or the \italic Partitura in facsimile.
      Their agreement therefore counts as one witness, not two. M was chosen
      as base text because it exists as encoded data.
    }
    \markup \para {
      \bold { Editions not seen. } Adolf Chybiński and Bronisław Rutkowski
      edited \italic { Vox in Rama } as Wydawnictwo Dawnej Muzyki Polskiej
      12 (Warsaw: TWMP, 1933; reissued by PWM in 1964, 1971 and 1980) ‘wg
      druku z r. 1611’, while the print was still complete. The library
      catalogue gives its scoring as ‘2 soprani, mezzosoprano e tenore [con
      organo]’, which matches the ranges at the printed pitch. Władysław
      Malinowski’s \italic { Opera omnia } in \italic { Monumenta Musicae in
      Polonia, } ser. A (1966–91), has the communions in vols. 4–5. The
      facsimiles of the Cantus primi chori (MMP D/11) and the
      \italic { Partitura } (MMP D/15) are the next sources to check.
    }

    \markup \sectionHead "Editorial method"
    \noPageBreak
    \markup \para {
      \bold { Status of the text. } The Tenor is edited from the 1611 print.
      The other three voices come from M, a modern edition at least two steps
      removed from the print. T shows how far such an edition can be
      trusted. Its notes and rhythms agree with M everywhere, once M’s
      transposition and halved values are undone. Its accidentals do not:
      of the thirteen chromatic notes in M’s Tenor, eight are printed in T,
      four are sharps supplied by the parent edition, and one, the e♭′ in
      bar 15, is an e♮′ in the print. Readers should assume that the
      accidentals of the Cantus, Altus and Bassus include editorial ones in
      about the same proportion. One reading of M is emended, in the Altus
      at bars 17–18 (see the notes).
    }
    \markup \para {
      \bold { Pitch, values and barring. } As in T. The Tenor’s C2 clef puts
      the piece on A with no signature, a fourth above N and a major third
      above M. Note values are those of T, twice those of N and M. The
      sign \musicglyph "timesig.C22" is T’s; the edition assumes it stood in
      every voice. A bar is one breve, the tactus. Bar lines are drawn
      between the staves only \italic (Mensurstriche). A note that runs
      across a bar line keeps its single value; the edition adds no ties.
      T’s clef is given under ‘Voices and clefs’ below; the clefs of the
      other voices are not known, and no incipits are printed. The range of
      each voice is shown at the head of its staff. The final notes are longae, as in T.
    }
    \markup \para {
      \bold { Voices and clefs. } At the printed pitch the ranges are Cantus
      g′–a″, Altus d′–f″ (after the emendation in bars 17–18), Tenor g–a′ and
      Bassus A–c′. With a Tenor in C2 they point to a high set of clefs,
      perhaps G2, G2 or C1, C2, F3, which is what the
      WDMP scoring ‘2 soprani, mezzosoprano e tenore’ describes. Cantus and
      Altus are a pair of equal voices: they enter on the same e″, share a
      range and cross often. The Cantus cannot belong an octave lower. There
      it would lie below the Altus at nine in ten note onsets and below
      the Tenor at more than half of them, while at the printed octave it
      never goes below the Tenor. The Cantus and Altus are printed in the
      treble clef, the Tenor in the octave treble clef, the Bassus in the
      bass clef.
    }
    \markup \para {
      \bold { Sounding pitch. } High clefs were a way of writing, not a pitch
      to be sung. Adriano Banchieri’s \italic { Cartella } (Venice, 1601;
      2nd edn 1610, pp. 13–15) states the rule: pieces in the G clef are sung
      a fourth lower when they have a flat and a fifth lower when they have
      none (‘quando sono per b. molle si trasportano … una Quarta bassa, &
      quando sono per b. quadro, si trasportano similmente una Quinta
      bassa’). His written-out example of the fifth-lower case has its Tenor
      in C2, the clef of T. Silverio Picerli gives the same rule in 1631. Both
      are quoted, with Banchieri’s example, by Andrew Johnstone (2006).
      \italic { Vox in Rama } has no signature, so by this rule it sounded a
      fifth lower, ending on D: Cantus c′–d″, Altus g–b♭′, Tenor c–d′, Bassus
      D–f, an ordinary four-part choir. The organ basses that Palestrina’s
      publishers printed for his high-clef works follow the same rule, a
      fifth lower without a flat and a fourth lower with one. Praetorius (1619)
      allows a fourth for some modes, and later Italian practice moved towards
      the fourth (Doni, 1640; Pasquini, 1695). The CPDL editions take it down a
      fourth, to E. A fourth down cannot be written in the notation of 1611
      without a one-sharp signature, while a fifth down gives D with one flat,
      an ordinary notation of the time. The \italic Partitura may settle the
      question, since organ parts sometimes printed the transposition. This
      edition prints the written pitch; the performance edition is a fifth
      lower.
    }
    \markup \para {
      \bold { Accidentals. } In the Tenor, accidentals before notes are those
      of T, and accidentals above the staff are editorial. In the other
      voices every accidental is M’s and stands before the note, whether the
      print had it or not. As in the sources of the period, a sign applies
      only to the note it stands against. A b after a b♭ in the same bar is
      b♮ and carries no sign.
    }
    \markup \para {
      \bold { Ligatures and coloration. } The three ligatures of T, all
      \italic { cum opposita proprietate, } are shown by brackets
      above the notes. In the second (bar 17) the second note is black;
      corner brackets mark it.
    }
    \markup \para {
      \bold { Underlay. } T places its text under the notes but loosely, and
      writes \italic ij where words repeat. Its words fall where M’s do.
      M’s underlay was then tested by script, syllable by syllable, against
      the rules of this series. It keeps every firm rule: no new syllable on
      a fusa or a dot, a syllable on the first note after every rest, no word
      divided by a rest, no elision. It departs from the sixteenth-century
      theorists in two ways, and in both the print’s Tenor does the same, so
      the edition follows the print. First, a semiminim after a dotted minim
      takes a syllable (‘fí-li-os’, ‘nó-lu-it’), which Zarlino forbids but
      which is ordinary by 1611. Second, every voice sets the unstressed
      ‘con-’ of ‘consolari’ to a melisma of five to seven notes; T’s spacing,
      ‘con … sola-’, shows the same. In bars 5–6 of the Altus N’s underlay is
      preferred, for the reason given in the notes.
    }
    \markup \para {
      \bold { Text. } Spelling follows modern Latin use (\italic et for the
      print’s ampersand, \italic ululatus for T’s \italic vlulatus ).
      Punctuation follows the Missal. The first word is capitalised; repeated
      ‘vox’ is not.
    }
  }

  %% ===================================================== SCORE
  \bookpart {
    \paper { print-first-page-number = ##t }
    \header {
      title = \markup \abs-fontsize #18 "Vox in Rama"
      subtitle = \markup \rubric "A 4. In festo Sanctorum Innocentium."
      composer = \markup \abs-fontsize #11 "Mikołaj Zieleński"
      arranger = \markup \abs-fontsize #9 \italic "ed. Mikołaj Derduń"
      tagline = ##f
    }
    \score { \theScore }
  }

  %% ===================================================== APPARATUS
  \bookpart {
    \markup \sectionHead "Critical notes"
    \noPageBreak
    \markup \para {
      Bar numbers refer to this edition, one breve to the bar. Pitches are
      given at this edition’s pitch, with c′ as middle C. Voices: C, A, T,
      B. Readings of N and M are quoted at this pitch.
    }
    \markup \note "5–6 A" {
      Underlay. M sets ‘Ra-ma’ on c″–b′ and then a melisma of eight notes on
      ‘-ma’. N sets ‘Ra-ma, in Ra-ma’: ‘in’ on a′ (bar 5), ‘Ra-’ on g♯′,
      ‘-ma’ on a′ (bar 6). N is followed. Its melisma falls on the stressed
      syllable, and the Altus then says ‘vox in Rama, in Rama’ as the Cantus
      (bars 4–7) and Tenor (bars 3–9) do.
    }
    \markup \note "8 T" {
      Fusae g♯′ f♯′: T without sharps; the minim g♯′ that follows has its
      sharp in T. N and M sharpen all three.
    }
    \markup \note "15 T" {
      e′–d′ in ligature, e′ without flat in T. N and M have e♭′. With e♮′
      the Tenor sounds a sixth below c″ and then a fifth below b′; with e♭′
      it forms a minor 6/3 and then the augmented triad e♭′–g′–b′. The flat is not
      in the print, and the counterpoint argues against it. It may come from
      the \italic Partitura or from the parent edition. The real chromatic
      moment comes two minims later, when the Cantus b♭′ meets the Altus f♯′
      over the Tenor d′.
    }
    \markup \note "17–18 A" {
      Emended. N and M have a–c′–d′–e′ an octave lower, the last four notes
      of the melisma on ‘-tus’. They take the Altus to a, a fourth below any
      other note in the part, and then make it leap e′–e″ to ‘ploratus’. In
      the high clefs of this piece an Altus would hardly go below d′. Raised
      an octave, the line runs a′–c″–d″–e″ into the repeated e″ of
      ‘ploratus’, crosses no other voice, and makes no parallels. The Altus
      partbook is lost; the \italic Partitura should settle it.
    }
    \markup \note "17 T" {
      b–a in ligature, the second note black. In imperfect time a black
      semibreve followed by short notes is worth a dotted minim, which is the
      value N and M give it.
    }
    \markup \note "25, 31 T" {
      The figure c♯′–b–c′–d′ at the cadence: T prints the sharp on the fusa
      and not on the minim. The minim’s sharp is editorial. N and M have it
      before the note.
    }
    \markup \note "38–39 T" {
      Underlay. M: ‘et no-lu-it (melisma) con- (melisma) so-la-ri’. N:
      ‘no-lu-it, no-lu-it con-so-la-ri’, filling the melisma with another
      ‘noluit’. T has ‘& no-’ at the end of its fifth staff and ‘luit conso
      la ri’ at the start of the sixth, one statement only, so N’s extra
      ‘noluit’ is not in the print. M is kept: its long ‘con-’ falls with the
      long ‘con-’ of the Cantus and Altus.
    }
    \markup \note "42 C" {
      e″ on the second minim against the Bassus f, both newly struck: a passing
      semiminim on the beat. N and M agree.
    }
    \markup \note "45" {
      T ends on a longa a′, followed by the final bar line. N and M give
      breves. The other voices are given longae to match.
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
    \markup \para {
      \vspace #0.3
      Matthew 2:18, after Jeremiah 31:15. Text of the communion for the
      feast of the Holy Innocents in the \italic { Missale Romanum }
      (Venice, 1570).
    }

    \markup \sectionHead "Sources and literature"
    \noPageBreak
    \markup \bib {
      Chemotti, Antonio. Review of \italic { Italian Music in
      Central-Eastern Europe, } ed. Jeż, Przybyszewska-Jarmińska and
      Toffetti. \italic Muzyka 62, no. 3 (2017): 130–37.
    }
    \markup \bib {
      Jeż, Tomasz, Barbara Przybyszewska-Jarmińska and Marina Toffetti, eds.
      \italic { Italian Music in Central-Eastern Europe: Around Mikołaj
      Zieleński’s Offertoria and Communiones (1611). } Venice: Fondazione
      Levi, 2015. Not seen.
    }
    \markup \bib {
      Johnstone, Andrew. ‘“High” Clefs in Composition and Performance.’
      \italic { Early Music } 34, no. 1 (2006): 29–53. Appendix 1b quotes
      Banchieri, \italic { Cartella } (2nd edn, Venice, 1610), pp. 13–15;
      appendix 1c, Picerli, \italic { Specchio secondo di musica } (Naples,
      1631), p. 192.
    }
    \markup \bib {
      Kurtzman, Jeffrey, and Anne Schnoebelen. \italic { A Catalogue of Mass,
      Office and Holy Week Music Printed in Italy, 1516–1770. } JSCM
      Instrumenta 2 (2014). Entry ‘Zielenski 1611 Z199, Z200’.
    }
    \markup \bib {
      Leszczyńska, Agnieszka. Booklet essay in \italic { Mikołaj Zieleński:
      Offertoria et Communiones totius anni. } Wrocław Baroque Ensemble,
      Andrzej Kosendiak. CD Accord ACD 272, 2019.
    }
    \markup \bib {
      \italic { Missale Romanum ex decreto sacrosancti Concilii Tridentini
      restitutum. } Venice, 1570; Rome: Typographia Vaticana, 1604.
    }
    \markup \bib {
      Musicare: A Database of Incomplete Printed Music, record 003847.
      Printed Sacred Music database, records 3388–3389 (title pages and
      dedication). RISM online, sources 990069886–7.
    }
    \markup \bib {
      Patalas, Aleksandra. ‘Zieleński, Mikołaj.’ In \italic { Encyklopedia
      muzyczna PWM, } vol. 12, 354–62. Kraków: PWM, 2012. Not seen.
    }
    \markup \bib {
      Perz, Mirosław. ‘Zieleński, Mikołaj.’ \italic { Grove Music Online. }
      Not seen.
    }
    \markup \bib {
      Schwider, Damian J. \italic { Mikołaj Zieleński: Ein polnischer
      Komponist an der Wende des 16. und 17. Jahrhunderts. } Munich: Utz,
      2008. Not seen.
    }
    \markup \bib {
      Zieleński, Mikołaj. \italic { Offertoria et communiones totius anni. }
      Facsimile, ed. Jerzy Morawski. Monumenta Musicae in Polonia, ser. D,
      vols. 11–15. Kraków: PWM, 1983–86. Vol. 12, \italic { Tenor primi
      chori } (1983), consulted; the others not seen.
    }
    \markup \bib {
      Zieleński, Mikołaj. \italic { Opera omnia. } Ed. Władysław Malinowski.
      Monumenta Musicae in Polonia, ser. A. 5 vols. Kraków: PWM, 1966–91.
      Not seen.
    }
    \markup \bib {
      Zieleński, Mikołaj. \italic { Vox in Rama. } Ed. Adolf Chybiński and
      Bronisław Rutkowski. Wydawnictwo Dawnej Muzyki Polskiej 12. Warsaw:
      TWMP, 1933; Kraków: PWM, 1964, 1971, 1980. Not seen.
    }
    \markup \bib {
      Recordings. Collegium Zieleński, Stanisław Gałoński, \italic { Opera
      omnia } vol. 5, DUX 0862 (rec. 2011). Wrocław Baroque Ensemble,
      Andrzej Kosendiak, CD Accord ACD 272 (2019): soprano, countertenor,
      tenor and bass with continuo.
    }
  }
}
