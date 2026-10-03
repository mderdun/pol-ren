\version "2.24.0"
\include "common.ily"
\include "voices.ily"
\include "text.ily"
\include "score.ily"

\header { tagline = ##f }

\book {
  \bookOutputName "juz-sie-zmierzka-critical"

  %% ===================================================== FRONT MATTER
  \bookpart {
    \paper { print-first-page-number = ##f }
    \markup \fill-line { \center-column {
      \vspace #2
      \abs-fontsize #22 "Modlitwa gdy dziatki spać idą"
      \vspace #0.4
      \abs-fontsize #13 \italic "Już się zmierzka"
      \vspace #1.2
      \abs-fontsize #12 "Wacław z Szamotuł"
      \abs-fontsize #10.5 "words by Andrzej Trzecieski"
      \vspace #1.2
      \abs-fontsize #10.5 \smallCaps "Critical edition"
      \abs-fontsize #10.5 "from the print of Łazarz Andrysowic, Kraków [c. 1550–1556]"
      \vspace #0.4
      \abs-fontsize #10.5 "edited by Mikołaj Derduń"
      \abs-fontsize #9.5 \italic "Polish Early Music"
      \vspace #1.5
    } }

    \markup \sectionHead "Introduction" \noPageBreak
    \markup \para {
      \italic { Modlitwa gdy dziatki spać idą } (‘A prayer when the children go
      to sleep’) is an evening hymn in four six-line stanzas by Andrzej
      Trzecieski the Younger, set for four voices by Wacław z Szamotuł
      (c. 1524 – c. 1560). Łazarz Andrysowic printed it in Kraków as a small
      booklet of four leaves. The print is undated; it belongs with
      Andrysowic’s other prints of Wacław’s Polish songs, which are placed
      between 1550 and 1556.
    }
    \markup \para {
      The title page names no composer. The letters W and S stand after the
      final notes of the Tenor, Altus and Bassus, and that monogram is the
      evidence for Wacław’s authorship. Michał Wiszniewski described the print
      in 1844 as ‘4 kart. Z nutami na 4 tony W. S.’
    }
    \markup \para {
      The setting is a cantional song. The Tenor carries the hymn tune in
      breves and semibreves, one note to each syllable. The other voices move
      around it more freely, with melismas on stressed syllables and a
      clausula at the end of most lines. The tune also appears on its own,
      without an attribution, in Jan Seklucjan’s
      \italic { Pieśni chrześcijańskie dawniejsze i nowe } (Königsberg, 1559).
      Whether Wacław wrote it or arranged an existing tune is disputed:
      Mazurkiewicz takes it for his, Hławiczka for an older song.
    }
    \markup \para {
      No copy of the print is known today. In 1880 Kazimiera Przyborowska
      published a facsimile of it in Warsaw, ‘z pierwodruku’, and every later
      edition goes back to that facsimile. The usual modern editions transpose
      the piece up a minor third, halve the note values, add a three-flat
      signature and modernise the text. This edition gives the music at the
      pitch and in the note values of the print, with the barring the print
      lacks drawn between the staves only, and keeps the old forms of the text.
    }

    \markup \sectionHead "The song and its use" \noPageBreak
    \markup \para {
      The title says what the song is for. Luther’s Small Catechism (1529)
      ends with prayers that ‘ein Hausvater sein Gesinde soll lehren’, among
      them an evening blessing to be said at bedtime: ‘denn ich befehle mich,
      meinen Leib und Seele und alles in deine Hände. Dein heiliger Engel sei
      mit mir, daß der böse Feind keine Macht an mir finde.’ Polish
      Lutherans took this over directly. The second edition of Jan
      Seklucjan’s \italic Catechismus (Königsberg, 1549) closes with a
      \concat { \italic "Nauka dziecinna" , } a teaching for children, which tells them
      how to begin and end the day:
    }
    \markup \line { \hspace #8 \override #'(line-width . 104)
      \abs-fontsize #10 \override #'(baseline-skip . 3.0) \justify {
      ‘Idąc spać mają dać dobrą noc swoim starszym, a niż się układą, mają się
      naprzód przeżegnać … [i] te modlitwę mogą przydać: Wszechmogący Ojcze
      niebieski, dziękujem Tobie … iżeś nas tego dnia raczył we zdrowiu
      zachować i wszelkiej szkody uchować … a przeto my ciała swoje i dusze
      i ine wszystki rzeczy w ręce Twoje polecamy, aby Twój święty anioł był
      przy nas, aby dyjabeł żadnego prawa do nas nie miał.’ } }
    \markup \vspace #0.5
    \markup \para {
      Trzecieski’s third and fourth stanzas put this prayer into verse almost
      clause by clause. The holy angel is sent against the enemies of the
      soul; God is asked to keep the household ‘przez wszej szkody’ and from
      every sudden ‘przygoda’; and everything the household has is put into
      his care (‘Tobie wszytko poruczamy, cożkolwie w swej mocy mamy’). The
      song is the catechism’s evening prayer, made singable for the family.
    }
    \markup \para {
      Behind both stands the old night office, Compline, which the household
      prayer replaced. Its texts are close to Trzecieski’s first stanza. The
      short lesson warns that ‘adversarius vester diabolus tamquam leo rugiens
      circuit’; the hymn \italic { Te lucis } asks ‘hostemque nostrum comprime’;
      Psalm 90 promises safety ‘a negotio perambulante in tenebris’; the
      closing collect asks God to drive off ‘omnes insidias inimici’ and to let
      his holy angels dwell in the house and keep it in peace. Wacław also set
      Mikołaj Rej’s Polish version of another Compline hymn, \italic { Christe
      qui lux es et dies } \concat { ( \italic "Kryste, dniu naszej światłości" ), } and
      Trzecieski’s daily confession, \concat { \italic "Powszednia spowiedź" ; } Andrysowic
      printed both in the same years.
    }
    \markup \para {
      The hymnals show the song in this domestic use. Zaremba’s Calvinist
      \italic { Pieśni chwał boskich } (Brest, 1558), printed for Mikołaj
      Radziwiłł, Wacław’s patron, has the text, in a book that also contains
      Jakub Sylwiusz’s \concat { \italic "Pasterstwo domowe" , } an order for prayer and
      singing in the household. Seklucjan’s Lutheran hymnal of 1559 prints the
      tune among eight songs headed ‘Idąc spać’ (‘Going to sleep’), beside
      groups for rising, for grace at table and for the evening. German
      Lutherans produced the same kind of song: Nikolaus Herman’s
      ‘Hinunter ist der Sonnenschein, die finstre Nacht bricht stark herein’
      (1560) opens almost as Trzecieski does. Agnieszka Leszczyńska has
      suggested that Wacław wrote partly with young singers in mind, since the
      Tenor’s plain tune could be given to the least practised voice.
    }
    \markup \para {
      Trzecieski (c. 1525 – after 1584) was a Kraków humanist and a leader of
      the Reformation in Little Poland, a friend of Kochanowski and one of the
      translators of the Brest Bible (1563). He knew Wacław well. He wrote
      verses in praise of him for the \italic Lamentationes (1553) and, after
      the composer’s death, an elegy, \italic { De obitu Venceslai Samotulini }.
      In the twentieth century the tune found a new life in Henryk Mikołaj
      Górecki’s String Quartet no. 1, ‘Już się zmierzcha’ (1988).
    }

    \markup \sectionHead "Sources" \noPageBreak
    \markup \item "A" {
      \italic { Modlitwa gdy dźyatki śpáć idą. } W Krákowye v Łázárzá
      Andrysowicá. Undated [c. 1550–1556]. Four leaves, signed A. Title and
      woodcut of two children kneeling before their parents (A1r); Cantus
      (A1v) facing Tenor (A2r); Bassus (A2v) facing Altus (A3r); stanzas 1–3
      (A3v); stanza 4 and ‘Dokończenye’ (A4r). Clefs C1, C3, C4, F4;
      sign \fontsize #-4 \musicglyph "timesig.C22" in every voice; no signature and no
      accidentals. No copy known.
    }
    \markup \item "F" {
      Facsimile of A: ‘z Pierwodruku wznowiła Kazimiera Przyborowska.
      Warszawa. 1880 r.’ Warsaw, Biblioteka Narodowa, Podr.SD Mag.F I.6,
      digitised on Polona. A redrawn copy, not a photograph. \bold { Base text. }
    }
    \markup \item "S" {
      Jan Seklucjan, \italic { Pieśni chrześcijańskie dawniejsze i nowe }
      (Königsberg: Daubmann, 1559), p. 115: the tune only. Not consulted.
    }
    \markup \vspace #0.3
    \markup \para { Editions collated: }
    \markup \item "PWM" {
      \concat { \italic \line { Już się zmierzcha. Na chór mieszany a cappella } , } Polska
      Literatura Chóralna 208 (Kraków: PWM, 1955). ‘Opracowane na podstawie
      pierwodruku … W oryginale o małą tercję niżej.’ Tempo, dynamics and
      breath marks added.
    }
    \markup \item "K" {
      \concat { \italic \line { Modlitwa, gdy dziatki spać idą (Już się zmierzka) } , }
      Towarzystwo Muzyczne im. Edwina Kowalika (Sibelius, 2015). Stanzas 1–2
      underlaid.
    }
    \markup \item "M" {
      Maia McCormick, \concat { \italic \line { Modlitwa, gdy dziatki spać idą } , } Sibelius and
      MusicXML (2024).
    }
    \markup \para {
      Z. M. Szweykowski’s edition of the songs, Wydawnictwo Dawnej Muzyki
      Polskiej 28 (Kraków: PWM, 1956), was not available. PWM, K and M agree
      in every note with F, apart from the places listed in the critical notes.
    }
    \markup \sectionHead "Editorial method" \noPageBreak
    \markup \para {
      \bold { Pitch, values and barring. } As in A: final D, no signature, no
      reduction of note values. A bar is one breve, the tactus of
      \fontsize #-4 \musicglyph "timesig.C22". Bar lines are drawn between the staves only
      \concat { ( \italic Mensurstriche ). } A note that runs across a bar line keeps its
      single value; the edition adds no ties. The incipit before each staff
      gives the clef, sign and first note of A. The range of each voice
      follows the incipit. The final notes are longae, as in A; the Bassus has
      a maxima (see the notes).
    }
    \markup \para {
      \bold { Clefs and voices. } The voice names are those of A. The Altus
      and Tenor are given in the octave-transposing treble clef. At written
      pitch the ranges are Cantus c′–d″, Altus d–a′, Tenor d–e′, Bassus G–a.
    }
    \markup \para {
      \bold { Accidentals. } A prints none, so every accidental here is
      editorial. Accidentals stand above the note and apply to that note only.
      They are limited to the five places where a major sixth opens to an
      octave at a cadence and the upper note must be raised (bars 2, 4, 9, 19
      and 29). Two further places where other editions alter a note are
      discussed in the notes (bars 4 and 29).
    }
    \markup \para {
      \bold { Underlay. } A prints each voice’s text as a block under the
      staff, not placed note by note, so the underlay is editorial. Three
      things in A guide it. The Tenor’s text fits its notes exactly, one
      syllable to one note, staff by staff. Where A spaces the words apart, it
      is leaving room for a melisma: Cantus ‘Bo … gá’ and ‘Vżywá … yą’,
      Bassus ‘Yuż … sye’ and ‘Bo … gá o … po’. The line breaks of the other
      voices give only a rough guide, since the text runs ahead of the music
      or behind it by several syllables. Elsewhere the underlay follows the
      rules used throughout this series. No new syllable falls on a
      semiminim, except straight after a dotted minim, or on a fusa. A
      repeated note takes a new syllable where the text allows. The last
      syllable of a line falls on its cadence note. Where these leave a
      choice, the syllable goes where the Tenor has the same word.
    }
    \markup \para {
      \bold { Text. } A prints four stanzas, ending with ‘Dokończenye’ and no
      Amen. All four are sung to the same music. Stanza 1 is underlaid and
      stanzas 2–4 follow the score. Each line has eight syllables with a break
      after the fourth, and Old Polish verse counts syllables, not stresses,
      so the later stanzas take the notes of stanza 1 syllable for syllable.
      A melisma may then fall on an unstressed syllable; this is inherent in
      the strophic form. The
      transcription uses modern spelling and punctuation but keeps the old
      sounds and forms: \italic { zmierzka, naszem, strażem, nawięcej,
      wszytki, swoję, Jesu, raczysz, wszej, } \concat { \italic jenż . } The music pages of A read
      \concat { \italic nássem , } the stanza page \concat { \italic náſſym ; } the edition
      follows the music. The diplomatic text keeps the spelling and line
      division of A; ſ is kept and \italic ē is left unexpanded.
    }

  }

  \bookpart {
    \markup \sectionHead "Text" \noPageBreak
    \markup \override #'(baseline-skip . 2.9) \abs-fontsize #9 \line {
      \pad-to-box #'(0 . 3) #'(0 . 1) " "
      \pad-to-box #'(0 . 31) #'(0 . 1) \italic "A, fols. A3v–A4r"
      \pad-to-box #'(0 . 30) #'(0 . 1) \italic "Transcription"
      \italic "Translation" }
    \markup \vspace #0.5
    \markup \stanzaRow "1" \diplOne \stanzaOne \transOne
    \markup \vspace #0.9
    \markup \stanzaRow "2" \diplTwo \stanzaTwo \transTwo
    \markup \vspace #0.9
    \markup \stanzaRow "3" \diplThree \stanzaThree \transThree
    \markup \vspace #0.9
    \markup \stanzaRow "4" \diplFour \stanzaFour \transFour
  }

  %% ============================================================= SCORE
  \bookpart {
    \header {
      title = \markup \abs-fontsize #18 "Modlitwa gdy dziatki spać idą"
      subtitle = \markup \abs-fontsize #11 \italic "Już się zmierzka"
      poet = \markup \abs-fontsize #10 "Andrzej Trzecieski"
      composer = \markup \abs-fontsize #10 "Wacław z Szamotuł"
    }
    \paper { system-system-spacing.basic-distance = 12 system-system-spacing.padding = 2.5 }
    \theScore
    \markup \fill-line { \hspace #1 \column {
      \vspace #1
      \abs-fontsize #10 \line { \bold "2." \stanzaTwo }
    } \hspace #4 \column {
      \vspace #1
      \abs-fontsize #10 \line { \bold "3." \stanzaThree }
    } \hspace #4 \column {
      \vspace #1
      \abs-fontsize #10 \line { \bold "4." \stanzaFour }
    } \hspace #1 }
  }

  %% ==================================================== CRITICAL NOTES
  \bookpart {
    \markup \sectionHead "Critical notes" \noPageBreak
    \markup \para {
      PWM, K and M transpose up a minor third, halve the values, bar in 4/4
      and use a signature of three flats. The notes below give their readings
      at the pitch and in the values of this edition. Bar numbers are the
      same in all four editions. Pitch names: c′ = middle C.
    }
    \markup \note "1–2 A" {
      PWM splits the dotted minim f′ into two notes so that ‘się’ has a note
      of its own. A has one dotted minim; ‘się’ falls on the following e′.
    }
    \markup \note "4 C, note 2" {
      PWM raises the semiminim g′ as well as the cadential minim. Only the
      minim is raised here, as in K and M.
    }
    \markup \note "8–10 A, T" {
      M exchanges the two parts here, ‘for tessitura’ in its own words. A
      has the semiminims c′ b a g and the descent f e d in the Altus.
    }
    \markup \note "8–9 A, text" {
      PWM, K: ‘ga’ on the semiminim c′, ‘o’ on f. (M has the Tenor’s notes
      here.) Here ‘ga’ on f and ‘o’ on e, so that ‘pomoc’ falls with the
      Cantus and Tenor.
    }
    \markup \note "12–13 C, B" {
      Parallel fifths d′–g′ over g–c. They stand in A.
    }
    \markup \note "15–17 C, text" {
      PWM, K, M: ‘złych’ on the semiminim g′, bar 17. Here on a′, bar 16,
      which puts the word in step with the Altus and keeps the run of
      semiminims under one syllable.
    }
    \markup \note "23 A, text" {
      K, M: ‘-cej’ on the second semiminim a. Here on b, directly after
      the dotted minim.
    }
    \markup \note "27–29 C, text" {
      PWM, K, M put ‘ją’ on the e′ of bar 27 and fit ‘swej chytrości’ to
      the minims that follow. Here ‘ją’ c′, ‘swej’ d′, ‘chy-’ e′, ‘-tro-’ d′.
      A leaves a gap after ‘Vżywá’, which keeps the e′ of bar 27 within the
      melisma; the line then moves with the Tenor and Bassus.
    }
    \markup \note "28 A, text" {
      M: ‘ją’ on the second semiminim c′. Here on d′, directly after the
      dotted minim.
    }
    \markup \note "29 A" {
      PWM, K and M flatten b, following the rule \concat { \italic \line { una nota super la } . }
      Here it is left as in A. B♭ would sound a tritone against e′ in the
      Cantus on the first minim of the bar, and b is the proper sixth degree
      of the D mode. Singers who prefer the flat may take it.
    }
    \markup \note "30 B" {
      A has a maxima; given as a longa to match the other voices.
    }
    \markup \note "Text" {
      PWM: ‘zmierzcha’, ‘naszym stróżem’. K, M: ‘naszym strażem’,
      ‘nawięcej’; M ‘zmierzcha’. All three print ‘On’ with a capital.
      A: ‘zmyerzka’, ‘nássem strażem’, ‘nawyęcey’, ‘on’.
    }

    \markup \sectionHead "Literature" \noPageBreak
    \markup \lit "Leszczyńska 2018" {
      Agnieszka Leszczyńska, ‘Piosnka nadobna dla dziatek. Z myślą o
      młodocianych użytkownikach polskich kancjonałów’, \italic { Odrodzenie
      i Reformacja w Polsce } 62 (2018), 91–122.
    }
    \markup \lit "Luther 1529" {
      Martin Luther, \italic { Der kleine Catechismus } (Wittenberg, 1529),
      ‘Der Abendsegen’. Cited from \italic { Concordia Triglotta } (St Louis,
      1921), p. 558.
    }
    \markup \lit "Seklucjan 1549" {
      Jan Seklucjan, \italic { Catechismus, to iest krotka a prosta starey
      wiary chrzescianskiey nauka, powtore wydana } (Königsberg, 1549),
      ‘Nauka dziecinna’ (final gathering). Warsaw, BN, SD XVI.O.6247 adl.,
      digitised on Polona.
    }
    \markup \lit "Seklucjan 1559" {
      Jan Seklucjan, \italic { Pieśni chrześcijańskie dawniejsze i nowe }
      (Königsberg, 1559); ed. A. Kalisz (Kraków, 2007), pp. 60–62, 166–194.
    }
    \markup \lit "Wiszniewski 1844" {
      Michał Wiszniewski, \concat { \italic "Historya literatury polskiej" , } vol. 6
      (Kraków, 1844), p. 466.
    }
    \markup \lit "Zaremba 1558" {
      \italic { Pieśni chwał boskich } (Brest, 1558), no. 33; facsimile, Monumenta Musicae in Polonia, ser. B
      (1989).
    }
  }
}
