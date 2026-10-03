%% Text of all four stanzas: diplomatic (A, fols. A3v–A4r), transcription, translation

diplOne = \markup \column {
  "Iuż ſye zmyerzka nádchodźi noc/"
  "Poprośmy Bogá o pomoc/"
  "Aby on náſſym ſtrażem był/"
  "Od złych czártow nas obronił/"
  "Ktorzy nawyęcey wćyemnośći/"
  "Vżywáyą ſwey chytrośći."
}
diplTwo = \markup \column {
  "Yeſu Kryſte Pánye miły/"
  "Tyś wſſytki pyekyelne śiły/"
  "Przez męke ſwoyę poráźił/"
  "A nam wyeczny pokoy ſpráwił/"
  "Ráczyſz miłośyerny Pánye/"
  "Wyſłyſſeć náſſe wołánye."
}
diplThree = \markup \column {
  "Ześli Anyołá ſwyętego/"
  "Aby mocą boſtwá twego/"
  "Przed duſſnemi przećiwniki/"
  "Bronił nas twe ſłużebniki/"
  "Y záchował przez wſſey ſzkody/"
  "Od káżdey nagłey przygody."
}
diplFour = \markup \column {
  "Tobyeć wſſycko poruczamy/"
  "Coż kolwye w ſwey mocy mamy/"
  "Coś nam vżyczył złáſki ſwey/"
  "Nyech to będźye wopyece twey/"
  "Yenż z Oycem y zduchē ſwyętym"
  "Yeſteś Krolem wyekuiſtym."
  \vspace #0.2
  "Dokończenye."
}

stanzaOne = \markup \column {
  "Już się zmierzka, nadchodzi noc,"
  "poprośmy Boga o pomoc,"
  "aby on naszem strażem był,"
  "od złych czartów nas obronił,"
  "którzy nawięcej w ciemności"
  "używają swej chytrości."
}
stanzaTwo = \markup \column {
  "Jesu Kryste, Panie miły,"
  "tyś wszytki piekielne siły"
  "przez mękę swoję poraził,"
  "a nam wieczny pokój sprawił."
  "Raczysz, miłosierny Panie,"
  "wysłyszeć nasze wołanie."
}
stanzaThree = \markup \column {
  "Ześli anioła świętego,"
  "aby mocą bóstwa twego"
  "przed dusznemi przeciwniki"
  "bronił nas, twe służebniki,"
  "i zachował przez wszej szkody"
  "od każdej nagłej przygody."
}
stanzaFour = \markup \column {
  "Tobieć wszytko poruczamy,"
  "cożkolwie w swej mocy mamy;"
  "coś nam użyczył z łaski swej,"
  "niech to będzie w opiece twej,"
  "jenż z Ojcem i z Duchem Świętym"
  "jesteś Królem wiekuistym."
}

transOne = \markup \column {
  "Dusk is falling, night is coming;"
  "let us ask God for help,"
  "that he may be our guard"
  "and defend us from the evil devils,"
  "who most of all in the dark"
  "put their cunning to use."
}
transTwo = \markup \column {
  "Jesus Christ, dear Lord,"
  "by your passion you struck down"
  "all the powers of hell"
  "and won us eternal peace."
  "Deign, merciful Lord,"
  "to hear our cry."
}
transThree = \markup \column {
  "Send a holy angel,"
  "that by the might of your godhead"
  "he may defend us, your servants,"
  "from the enemies of the soul,"
  "and keep us without any harm"
  "from every sudden mishap."
}
transFour = \markup \column {
  "To you we commend"
  "whatever we hold in our power;"
  "what you have lent us of your grace,"
  "let it be in your care,"
  "who with the Father and the Holy Spirit"
  "are King everlasting."
}

stanzaRow = #(define-scheme-function (num dip pl en) (markup? markup? markup? markup?)
  #{ \markup \override #'(baseline-skip . 2.9) \abs-fontsize #9.6 \line {
       \pad-to-box #'(0 . 3) #'(0 . 1) \bold #num
       \pad-to-box #'(0 . 31) #'(0 . 1) #dip
       \pad-to-box #'(0 . 30) #'(0 . 1) #pl
       \italic #en } #})

stanzaPair = #(define-scheme-function (num pl en) (markup? markup? markup?)
  #{ \markup \override #'(baseline-skip . 3.0) \abs-fontsize #10.5 \line {
       \hspace #12
       \pad-to-box #'(0 . 4) #'(0 . 1) \bold #num
       \pad-to-box #'(0 . 52) #'(0 . 1) #pl
       \italic #en } #})
