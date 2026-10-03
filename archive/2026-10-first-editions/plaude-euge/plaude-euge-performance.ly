\version "2.24.0"
\include "common.ily"
\include "score.ily"
fl = \markup \raise #0.55 \fontsize #-3 \flat
na = \markup \raise #0.55 \fontsize #-3 \natural
sh = \markup \raise #0.55 \fontsize #-3 \sharp
\book {
\header {
  title = \markup \override #'(font-name . "EB Garamond") \fontsize #4 "Plaude euge theotocos"
  subtitle = \markup \italic "for three voices"
  composer = \markup \column { \right-align "Piotr z Grudziądza" \right-align \small "(Petrus Wilhelmi de Grudencz, 1392 – after 1452)" }
  poet = \markup \small "Leipzig, Universitätsbibliothek, Ms 1236, f. 139v"
  tagline = ##f
  footer = "Plaude euge theotocos · performance edition"
}
\bookpart {
\markup \vspace #1
\markuplist { \override #'(baseline-skip . 3.4) \column-lines { \justify { "Piotr" "z" "Grudziądza" "(1392" "–" "after" "1452)" "studied" "and" "graduated" "at" "Kraków" "and" "later" "served" "as" "a" "chaplain" "at" "the" "court" "of" "Frederick" "III." "His" "songs" "travelled" "widely" "in" "central" "Europe," "and" "he" "signed" "many" "of" "them" "with" "an" "acrostic." "Here" "the" "initials" "of" "the" "opening" "words" "spell" "PETRVS." "He" "wrote" "the" "poem" "himself." "It" "greets" "the" "Virgin" "as" \concat { \italic "theotocos" "," } "the" "Greek" "“God-bearer”" "(the" "word" "that" "Polish" \italic "Bogurodzica" "translates)," "and" "then" "asks" "her" "to" "look" "on" "her" "singers" "with" "the" "eyes" "of" "mercy," "in" "words" "close" "to" "the" \italic "Salve" \concat { \italic "Regina" "." } }
\vspace #0.3
\justify { "The" "piece" "survives" "in" "one" "manuscript," "Leipzig," "Universitätsbibliothek," "Ms" "1236," "copied" "in" "1447–9." "The" "voices" "are" "the" "source's" "own:" "Discantus," "Medius" "and" "Tenor." "At" "the" "printed" "pitch" "they" "suit" "alto," "tenor" "and" "bass." "The" "source" "writes" "no" "clefs," "so" "the" "pitch" "and" "the" "key" "signature" "are" "editorial." "Piotr's" "songs" "were" "sung" "by" "students" "and" "clerics," "often" "three" "men" "of" "similar" "range," "and" "an" "all-male" "group" "may" "transpose" "the" "piece" "down" "to" "suit." }
\vspace #0.3
\justify { "The" "Tenor" "has" "no" "text" "in" "the" "source" "and" "may" "be" "played" "(a" "fiddle" "or" "organ" "suits" "it)," "vocalised," "or" "sung." "Its" "text" "here" "is" "editorial," "printed" "in" "italics," "and" "shortened" "on" "purpose." "The" "Tenor" "keeps" "its" "long" "notes" "and" "sings" "only" "the" "words" "that" "fit," "while" "the" "upper" "voices" "carry" "the" "whole" "poem." "Dashed" "ties" "mark" "the" "places" "in" "the" "endings" "where" "a" "note" "of" "the" "source" "is" "divided." "In" "the" "first" "part" "the" "Tenor" "takes" "the" "two" "endings" "differently." "The" "first" "time" "it" "anticipates" \concat { \italic "con-fi" ";" } "the" "second" "time" "it" "moves" "with" "the" "upper" "voices." "Small" "accidentals" "above" "the" "staff" "are" "editorial." "The" "two" "sharps" "in" "the" "final" "cadence" "belong" "together," "so" "sing" "both" "or" "neither." "The" "note" "in" "square" "brackets" "at" "the" "end" "of" "each" "second" "ending" "is" "hidden" "in" "the" "binding" "of" "the" "manuscript." }
\vspace #0.3
\justify { "Note" "values" "are" "those" "of" "the" "source." "Lines" "between" "the" "staves" "mark" "each" "breve" "and" "are" "not" "bar" "lines" "in" "the" "modern" "sense." "Each" "half" "of" "the" "song" "is" "sung" "twice," "with" "the" "first" "ending" "and" "then" "the" "second." "Lines" "3–4" "of" "the" "second" "half" "are" "best" "sung" "as" "a" "block," "all" "voices" "declaiming" "together." }
\vspace #0.3 } }
\markup \vspace #1.5
\markuplist { \override #'(baseline-skip . 3.4) \column-lines { \column { \fontsize #1.5 "Text and translation" \vspace #0.4 \fill-line { \italic \column { "Plaude, euge, theotocos," "regina virginum," "salus hominum" "in te confidencium." \vspace #0.6 "Te laudantes inspice," "miseros nec despice," "sed misericordie" "oculis hos respice." } \column { "Rejoice, well done, Mother of God," "queen of virgins," "salvation of all" "who trust in you." \vspace #0.6 "Look upon those who praise you," "do not despise the wretched," "but look on them" "with the eyes of mercy." } } }
\vspace #0.6 } }
}
\bookpart { \header { title = ##f subtitle = ##f composer = ##f poet = ##f } \paper { page-count = #2 systems-per-page = #3 }
\score { \plaudeScore }
}
}
