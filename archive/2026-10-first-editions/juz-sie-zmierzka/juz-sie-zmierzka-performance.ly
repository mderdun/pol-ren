\version "2.24.0"
\include "common.ily"
\include "voices.ily"
\include "text.ily"
\include "score.ily"

\book {
  \bookOutputName "juz-sie-zmierzka-performance"

  \bookpart {
    \paper { print-first-page-number = ##f }
    \markup \fill-line { \center-column {
      \abs-fontsize #22 "Modlitwa gdy dziatki spać idą"
      \vspace #0.4
      \abs-fontsize #13 \italic "Już się zmierzka"
      \vspace #1
      \abs-fontsize #12 "Wacław z Szamotuł"
      \abs-fontsize #10.5 "words by Andrzej Trzecieski"
      \vspace #1
      \abs-fontsize #10.5 \smallCaps "Performance edition"
      \abs-fontsize #10.5 "edited by Mikołaj Derduń"
      \abs-fontsize #9.5 \italic "Polish Early Music"
      \vspace #1
    } }

    \markup \sectionHead "Notes for performers" \noPageBreak
    \markup \para {
      An evening prayer for the household, printed by Łazarz Andrysowic in
      Kraków in the early 1550s. Luther’s Small Catechism taught children to
      commend themselves at bedtime into God’s hands and ask for his holy
      angel against the evil enemy. Polish Lutherans translated that prayer,
      and Trzecieski’s stanzas 3 and 4 follow it almost clause by clause; his
      first stanza recalls Compline, the old night office. Seklucjan’s hymnal
      of 1559 prints the tune among songs for ‘going to sleep’.
    }
    \markup \para {
      The Tenor carries the hymn tune, one note to each syllable; the other
      voices decorate it. All four stanzas are sung to the same music.
      Stanza 1 is set under the notes. For stanzas 2–4, give each syllable
      the notes its counterpart has in stanza 1.
    }
    \markup \para {
      \bold { The score. } It is the score of the critical edition, at the
      pitch and in the note values of the 1550s print. A bar is one breve, the
      tactus of the cut-C sign. Bar lines run between the staves only, so
      a note that crosses one is held for its full value. The small
      staff before each voice shows the original clef and first note. Sharps
      above the staff are editorial.
    }
    \markup \para {
      \bold { Pitch and voices. } Written ranges: Cantus c′–d″, Altus d–a′,
      Tenor d–e′, Bassus G–a. At written pitch the piece suits men’s voices
      with a high Cantus, or a choir of low voices. A mixed choir will usually
      sing it a minor third higher, the pitch of most modern editions. Choose
      the pitch to suit the singers; the notation does not change.
    }
    \markup \para {
      \bold { Tempo. } A minim of about 66 to 80, felt two to the semibreve
      and four to the bar. The semiminim runs should stay light.
    }
    \markup \para {
      \bold { Words. } The text keeps the forms of 1550s Polish:
      \concat { \italic zmierzka " (not " \italic zmierzcha ), }
      \concat { \italic "naszem strażem" , } \concat { \italic nawięcej , }
      \concat { \italic wszytki , } \concat { \italic swoję , }
      \concat { \italic Jesu . } Sing them as printed, with modern
      pronunciation. \italic { Ześli } in stanza 3 means ‘send’.
    }
  }

  \bookpart {
    \markup \sectionHead "Text and translation" \noPageBreak
    \markup \stanzaPair "1" \stanzaOne \transOne
    \markup \vspace #0.9
    \markup \stanzaPair "2" \stanzaTwo \transTwo
    \markup \vspace #0.9
    \markup \stanzaPair "3" \stanzaThree \transThree
    \markup \vspace #0.9
    \markup \stanzaPair "4" \stanzaFour \transFour
  }

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
}
