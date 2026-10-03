discantusNotes = {
  \repeat volta 2 { d'1 f'1 e'1. f'2 g'2 d'2 d'2 e'2 c'\breve d'1 r1 a'1. g'2 f'1 bes'2 a'1 g'1 f'2 a'1 r1 a'2 f'2 f'2 g'2 e'2 e'2 e'1 f'2 d'2 c'2 d'2 e'1 f'1 }
  \alternative { { g'1. a'2 f'2 e'2 f'2 g'2 e'\breve } { g'1. a'2 f'2 e'2 f'2 d'2 \once \override NoteHead.stencil = #bracket-head e'\breve } }
  \break \repeat volta 2 { d'1 e'2 f'2 g'1 d'1 a'2 f'2 f'2 g'2 e'1 d'1 e'2 e'2 e'1 a'\breve bes'2 g'2 g'2 f'2 g'\breve f'2 e'2 e'2 d'2 f'2 f'2 d'1 g'2 f'2 e'2 d'2 }
  \alternative { { e'1 g'2 a'2 f'2 e'2 f'2 d'2 e'\breve } { e'1 e'1 f'2 e'2 d'2 \once \set suggestAccidentals = ##t cis'2 \once \override NoteHead.stencil = #bracket-head d'\breve\fermata \bar "|." } }
}
discantusText = \lyricmode {
  Plau -- de eu -- ge the -- o -- to -- _ cos __ _ re -- gi -- na vir -- _ gi -- _ num sa -- _ lus __ _ ho -- mi -- num in te con -- fi -- den -- ci -- um __ _ con -- fi -- den -- ci -- um um __ _ con -- fi -- den -- ci -- um Te lau -- _ dan -- tes in -- _ spi -- _ _ ce mi -- se -- ros nec de -- _ spi -- _ ce sed mi -- se -- ri -- cor -- di -- e o -- _ cu -- _ lis hos __ _ re -- _ spi -- _ ce lis hos re -- _ spi -- _ ce
}

mediusNotes = {
  \repeat volta 2 { a1 a2 bes2 c'1 g2 a2 bes1 f2 g2 a1 e2 f2 g\breve e1 r1 r1 bes1 f1 g2 f2 e2 d2 e1 a1 bes2 a2 a2 g2 a1 bes2 a2 g2 f2 g1 a1 }
  \alternative { { c'1 g1 a2 a2 bes2 bes2 a\breve } { c'1 g1 a2 a2 g2 g2 a\breve } }
  \repeat volta 2 { g1 a2 \once \set suggestAccidentals = ##t b2 c'1 a1 f1 bes1 a2 g2 g2 f2 a\breve e2 e2 e2 f2 d1 c1 d\breve a2 a2 g2 a2 bes2 a2 bes1 c'1 \once \set suggestAccidentals = ##t b1 }
  \alternative { { c'1 g2 a2 bes2 a2 a2 g2 a\breve } { c'1 g2 a2 a2 bes2 a2 \once \set suggestAccidentals = ##t gis2 a\breve\fermata \bar "|." } }
}
mediusText = \lyricmode {
  Plau -- de __ _ eu -- ge __ _ the -- o -- _ to -- _ _ cos __ _ re -- gi -- na __ _ vir -- gi -- num __ _ sa -- lus ho -- mi -- num in te con -- fi -- den -- ci -- um __ _ con -- fi -- den -- ci -- um um __ _ con -- fi -- den -- ci -- um Te lau -- _ dan -- tes in -- _ _ _ spi -- _ ce mi -- se -- ros nec de -- spi -- ce sed mi -- se -- ri -- cor -- di -- e o -- cu -- lis hos __ _ re -- _ spi -- _ ce lis hos __ _ re -- _ spi -- _ ce
}

tenorNotes = {
  \repeat volta 2 { d\breve a,1 bes,1 g,1 bes,1 a,\breve g,\breve a,1 c1 d\breve a,1 bes,1 a,\breve d\breve c\breve d1 f1 c1 d1 }
  \alternative { { c1 ~ c2 ~ c2 a,1 d1 a,\breve } { c\breve a,2 ~ a,2 bes,2 ~ bes,2 a,\breve } }
  \repeat volta 2 { g,1 d1 c1 f1 d\breve a,1 bes,1 a,\breve c\breve g,1 a,1 g,\breve c\breve d1 f1 e1 g1 }
  \alternative { { c\breve d1 ~ d1 a,\breve } { c\breve d1 e1 d\breve\fermata \bar "|." } }
}
tenorText = \lyricmode {
  Plau -- de __ _ the -- o -- to -- cos re -- gi -- na vir -- gi -- num sa -- lus con -- fi -- den -- ci -- um con -- fi -- den -- ci -- um um con -- fi -- den -- ci -- um Te lau -- dan -- tes in -- spi -- _ ce nec de -- spi -- ce sed hos __ _ o -- cu -- lis re -- spi -- ce lis re -- spi -- ce
}
