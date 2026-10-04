%% pol-ren.ily — house engraving style for the Polish Early Music editions
%%
%% LilyPond only engraves the music. Page size, line width, running heads,
%% titles and all prose belong to the LaTeX class (house/latex/pol-ren.cls);
%% lilypond-book passes the line width in. Do not set paper margins here.
%%
%% The score is the same in the critical and the performance edition.
%% The only difference allowed is staff size (set by the edition file).

\version "2.24.0"

%% ------------------------------------------------------------ breathing room
%% Vertical clearance is set as padding: the minimum white space between the
%% actual ink of neighbouring lines (staff, lyrics, ledger-line notes,
%% accidentals, rubrics). LilyPond measures the ink, so a note far above or
%% below its staff pushes the lines apart by itself; padding is the floor
%% that is always kept. Performance editions, with fewer systems a page,
%% get more (prBreathe). A score may scale it further with
%%   prBreathe = #1.4   in music/engraving.ily (before score.ly includes this).
#(define pr-breathe
   (let ((v (ly:parser-lookup 'prBreathe)))
     (if (number? v) v
         (if (eq? (ly:parser-lookup 'prPerformance) #t) 1.3 1.0))))

%% ------------------------------------------------------------ type
%% Staff size: 17 in critical editions, 19 in performance editions.
#(set-global-staff-size
   (if (eq? (ly:parser-lookup 'prPerformance) #t) 19 17))
\paper {
  %% the pinned Junicode from tools/get-fonts.sh, if fetched; in the finished
  %% build (unless NOVELLO=0) the pressed fonts from tools/make-pressed-fonts.sh:
  %% Junicode Pressed for words, the pressed Emmentaler ("pressed-NN.otf", found
  %% on the include path that tools/build.sh passes) for the music.
  #(define pr-fonts-dir (string-append (dirname (ly:find-file "pol-ren.ily")) "/../fonts/"))
  #(define pr-pressed?
     (and (not (equal? (getenv "NOVELLO") "0"))
          (file-exists? (string-append pr-fonts-dir "pressed/JunicodePressed-Regular.otf"))
          (ly:find-file "pressed-20.otf")))
  #(for-each (lambda (d) (if (file-exists? d) (ly:font-config-add-directory d)))
     (list (string-append pr-fonts-dir "junicode")
           (string-append pr-fonts-dir "pressed")))
  #(define fonts
     (if pr-pressed?
         (set-global-fonts #:music "pressed" #:brace "emmentaler"
                           #:roman "Junicode Pressed" #:sans "Junicode Pressed"
                           #:typewriter "DejaVu Sans Mono"
                           #:factor (/ staff-height pt 20))
         (make-pango-font-tree "Junicode" "Junicode" "DejaVu Sans Mono"
                               (/ staff-height pt 20))))
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
%% sign in square brackets above it is an alteration singers may take
%% (Berger 1987).
%% Post-events: b1\optFlat (lower)  c'2\optSharp (raise)  b1\optNatural
%% The sign is worked out from the note after any transposition, so a raised
%% g' prints a sharp at written pitch and a natural over b-flat' a minor
%% third up.
#(define (pr-opt-glyph alt)
   (cond ((< alt 0) "accidentals.flat") ((> alt 0) "accidentals.sharp")
         (else "accidentals.natural")))
%% Square brackets, as all editorial matter; round brackets are kept for
%% cautionaries (see voiceSetup).
#(define (pr-opt-markup glyph)
   (markup #:fontsize -2.5
     #:override '(thickness . 1.3) #:override '(protrusion . 0.3)
     #:override '(padding . 0.12)
     #:bracket (#:musicglyph glyph)))
#(define (pr-opt-acc mode)
   (make-music 'TextScriptEvent 'direction UP 'pr-opt mode
     'text (pr-opt-markup (pr-opt-glyph (if (number? mode) mode 0)))))
optFlat = #(pr-opt-acc -1/2)
optSharp = #(pr-opt-acc 1/2)
optNatural = #(pr-opt-acc 'natural)
#(define (pr-fix-opt music)
   (music-map
     (lambda (m)
       (if (music-is-of-type? m 'note-event)
           (let ((p (ly:music-property m 'pitch)))
             (for-each
               (lambda (a)
                 (let ((mode (ly:music-property a 'pr-opt #f)))
                   (if mode
                       (ly:music-set-property! a 'text
                         (pr-opt-markup
                           (pr-opt-glyph
                             (if (number? mode) (+ (ly:pitch-alteration p) mode) 0)))))))
               (ly:music-property m 'articulations))))
       m)
     music))

%% Note supplied by the editor: small notehead, at cue size (Ross 189).
ed = \tweak font-size #-2 \etc

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
%% Cantus firmus over its whole span: \cfStart on its first note, \cfEnd on
%% its last. The label repeats at the start of every system it crosses, and
%% a light dashed line shows how far it runs.
cfStart = -\tweak direction #UP
  -\tweak style #'dashed-line
  -\tweak dash-fraction #0.2
  -\tweak dash-period #1.6
  -\tweak thickness #0.6
  -\tweak bound-details.left.text \markup \abs-fontsize #8.5 \italic "[c.f.] "
  -\tweak bound-details.left-broken.text \markup \abs-fontsize #8.5 \italic "[c.f.] "
  -\tweak bound-details.left.stencil-align-dir-y #CENTER
  -\tweak bound-details.left-broken.stencil-align-dir-y #CENTER
  -\tweak bound-details.right.text \markup \draw-line #'(0 . -0.8)
  -\tweak bound-details.right-broken.text ##f
  \startTextSpan
cfEnd = \stopTextSpan

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
%% Accidentals: a sign before a note is the source's and holds for that note
%% only ("forget"). Where an altered pitch returns unaltered later in the same
%% bar and octave, the bar rule a modern singer reads by would carry the
%% alteration on, so the note gets a cautionary sign in round brackets
%% (Caldwell 59-60, Gould 86).
voiceSetup = {
  \accidentalStyle forget
  \set Staff.autoCautionaries = #`(Staff ,(make-accidental-rule 'same-octave 0))
  \autoBeamOff
}

%% ------------------------------------------------------------ Mensurstriche
%% Drawn between the staves only, as dashed black lines: the score reads as
%% parts first and as a timed score second. No colour but black and red.
\defineBarLine "-span!" #'(#f #f "!")
%% The dashed line stops half a staff space short of each staff, and further
%% where a note, stem or accidental stands out from that staff in its way.
%% It never runs through words (syllables with their punctuation, stanza
%% numbers, text above a staff): there it breaks, a little clear of the
%% text. Where it passes between the syllables of a word, the hyphen or
%% extender line makes room for it instead (pr-lyric-hyphen, -extender).
%% A piece of dash shorter than half a dash is left out.
#(define (pr-knockout-holes grob sys cx y0)
   (let ((pad 0.4))
     (filter-map
      (lambda (g)
        (and (or (grob::has-interface g 'note-head-interface)
                 (grob::has-interface g 'stem-interface)
                 (grob::has-interface g 'accidental-interface)
                 (grob::has-interface g 'dots-interface)
                 (grob::has-interface g 'flag-interface))
             (let* ((gx (ly:grob-extent g sys X))
                    ;; a note head outside the staff carries a ledger line wider than itself
                    (px (if (grob::has-interface g 'note-head-interface) (+ pad 0.45) pad)))
               (and (interval-sane? gx)
                    (< (car gx) (+ cx px)) (> (cdr gx) (- cx px))
                    (let ((gy (ly:grob-extent g sys Y)))
                      (and (interval-sane? gy)
                           (cons (- (car gy) y0 pad) (+ (- (cdr gy) y0) pad))))))))
      (ly:grob-array->list (ly:grob-object sys 'all-elements)))))
%% Clearance (staff spaces) between the dashed line and written text.
#(define pr-text-pad 0.4)
#(define (pr-text-holes grob sys cx y0)
   (filter-map
    (lambda (g)
      (and (or (grob::has-interface g 'lyric-syllable-interface)
               (grob::has-interface g 'stanza-number-interface)
               (grob::has-interface g 'text-script-interface))
           (let ((gx (ly:grob-extent g sys X)))
             (and (interval-sane? gx)
                  (< (car gx) (+ cx pr-text-pad)) (> (cdr gx) (- cx pr-text-pad))
                  (let ((gy (ly:grob-extent g sys Y)))
                    (and (interval-sane? gy)
                         (cons (- (car gy) y0 pr-text-pad)
                               (+ (- (cdr gy) y0) pr-text-pad))))))))
    (ly:grob-array->list (ly:grob-object sys 'all-elements))))
%% [lo, hi] less the holes, as a list of intervals from the top down.
#(define (pr-interval-minus lo hi holes)
   (let loop ((segs (list (cons lo hi)))
              (hs (sort holes (lambda (a b) (< (car a) (car b))))))
     (if (null? hs)
         (sort (filter (lambda (s) (< (car s) (cdr s))) segs)
               (lambda (a b) (> (car a) (car b))))
         (let ((h (car hs)))
           (loop (append-map
                  (lambda (s)
                    (if (or (<= (cdr h) (car s)) (>= (car h) (cdr s)))
                        (list s)
                        (list (cons (car s) (car h)) (cons (cdr h) (cdr s)))))
                  segs)
                 (cdr hs))))))
%% Gap (staff spaces) between the dashed line and the staves it joins.
#(define pr-span-gap (let ((v (ly:parser-lookup 'prSpanGap))) (if (number? v) v 0.5)))
#(define (pr-span-bar grob)
   (let ((default (ly:span-bar::print grob)))
     (if (not (and (ly:stencil? default)
                   (member (ly:grob-property grob 'glyph-name "") '("!" "-span!"))))
         default
         (let* ((sys (ly:grob-system grob))
                (y0 (ly:grob-relative-coordinate grob sys Y))
                (xe (ly:stencil-extent default X))
                (cx (+ (ly:grob-relative-coordinate grob sys X) (interval-center xe)))
                (holes (pr-knockout-holes grob sys cx y0))
                (texts (pr-text-holes grob sys cx y0))
                ;; the gaps between the staves this span bar joins, in its own coordinates
                (staves (sort (filter-map
                               (lambda (b)
                                 (let ((ss (ly:grob-object b 'staff-symbol)))
                                   (and (ly:grob? ss)
                                        (let ((e (ly:grob-extent ss sys Y)))
                                          (cons (- (car e) y0) (- (cdr e) y0))))))
                               (ly:grob-array->list (ly:grob-object grob 'elements)))
                              (lambda (a b) (> (car a) (car b)))))
                (gaps (let g ((l staves) (acc '()))
                        (if (or (null? l) (null? (cdr l))) (reverse acc)
                            (g (cdr l) (cons (cons (cdr (cadr l)) (car (car l))) acc)))))
                (th (* (ly:staff-symbol-line-thickness grob)
                       (ly:grob-property grob 'hair-thickness 1.9)))
                (on 0.4) (off 0.6) (x (interval-center xe)))
           (fold
            (lambda (gap acc)
              ;; Each end stops a fixed distance from its staff, or further when a
              ;; note, stem or accidental near the line stands out from that staff;
              ;; in between, the line breaks only for text.
              (let* ((lo0 (car gap)) (hi0 (cdr gap)) (mid (/ (+ lo0 hi0) 2))
                     (hi (fold (lambda (h m) (if (> (cdr h) mid) (min m (car h)) m))
                               (- hi0 pr-span-gap) holes))
                     (lo (fold (lambda (h m) (if (< (car h) mid) (max m (cdr h)) m))
                               (+ lo0 pr-span-gap) holes)))
                (fold
                 (lambda (seg acc)
                   (let loop ((y (cdr seg)) (acc acc))
                     (let ((a (max (car seg) (- y on))))
                       (if (< (- y a) (/ on 2))   ; nothing left, or a blip
                           acc
                           (loop (- y on off)
                                 (ly:stencil-add acc (make-line-stencil th x a x y)))))))
                 acc (pr-interval-minus lo hi texts))))
            empty-stencil gaps)))))

%% Where a dashed bar line passes between the syllables of a word, the hyphen
%% steps aside (or, where it cannot, opens) and the extender line opens, a
%% little either side of the bar line.
#(define pr-lyric-gap 0.3)
%% x positions of the dashed bar lines crossing the line of this lyric grob,
%% in the grob's own coordinates. Only horizontal positions are used (the
%% vertical ones are not known yet when a lyric line is drawn): a lyric line
%% is crossed when it stands between two staves of the system.
#(define (pr-between-staves? grob)
   (let* ((vag (ly:grob-parent grob Y))
          (al (and (ly:grob? vag) (ly:grob-parent vag Y)))
          (els (if (ly:grob? al) (ly:grob-array->list (ly:grob-object al 'elements)) '()))
          (staff? (lambda (g) (not (ly:grob-property g 'staff-affinity #f))))
          (tail (member vag els)))
     (and tail
          (any staff? (cdr tail))
          (any staff? (let loop ((l els) (acc '()))
                        (if (or (null? l) (eq? (car l) vag)) acc
                            (loop (cdr l) (cons (car l) acc))))))))
#(define (pr-bars-across grob sys)
   (if (not (pr-between-staves? grob))
       '()
       (let ((gx (ly:grob-relative-coordinate grob sys X)))
         (filter-map
          (lambda (b)
            (and (grob::has-interface b 'span-bar-interface)
                 (member (ly:grob-property b 'glyph-name "") '("!" "-span!"))
                 (let ((be (ly:grob-extent b sys X)))
                   (and (interval-sane? be)
                        (- (interval-center be) gx)))))
          (ly:grob-array->list (ly:grob-object sys 'all-elements))))))
#(define (pr-box x0 x1 ye blot)
   (ly:round-filled-box (cons x0 x1) ye blot))
#(define (pr-lyric-extender grob)
   (let ((st (ly:lyric-extender::print grob)))
     (if (not (ly:stencil? st))
         st
         (let* ((sys (ly:grob-system grob))
                (xe (ly:stencil-extent st X)) (ye (ly:stencil-extent st Y))
                (blot (* 0.8 (interval-length ye)))
                (bars (filter (lambda (b) (and (> b (- (car xe) pr-lyric-gap))
                                               (< b (+ (cdr xe) pr-lyric-gap))))
                              (pr-bars-across grob sys))))
           (if (null? bars)
               st
               (let* ((segs (pr-interval-minus (car xe) (cdr xe)
                              (map (lambda (b) (cons (- b pr-lyric-gap) (+ b pr-lyric-gap))) bars)))
                      (segs (filter (lambda (s) (>= (- (cdr s) (car s)) 0.3)) segs)))
                 (apply ly:stencil-add empty-stencil
                        (map (lambda (s) (pr-box (car s) (cdr s) ye blot)) segs))))))))
#(define (pr-lyric-hyphen grob)
   (let ((st (ly:lyric-hyphen::print grob)))
     (if (not (and (ly:stencil? st) (not (ly:stencil-empty? st))))
         st
         (let* ((sys (ly:grob-system grob))
                (xe (ly:stencil-extent st X)) (ye (ly:stencil-extent st Y))
                (blot (* 0.9 (interval-length ye)))
                (len (ly:grob-property grob 'length 0.66))
                (period (ly:grob-property grob 'dash-period 10.0))
                (n (if (< (- (interval-length xe) len) 0.01) 1
                       (1+ (inexact->exact (round (/ (- (interval-length xe) len) period))))))
                (dashes (if (= n 1) (list xe)
                            (map (lambda (i) (cons (+ (car xe) (* i period))
                                                   (+ (car xe) (* i period) len)))
                                 (iota n))))
                (gx (ly:grob-relative-coordinate grob sys X))
                ;; room between the syllables, in this grob's coordinates
                (room (let ((l (ly:spanner-bound grob LEFT)) (r (ly:spanner-bound grob RIGHT)))
                        (cons (if (grob::has-interface l 'lyric-syllable-interface)
                                  (- (cdr (ly:grob-extent l sys X)) gx -0.1) (car xe))
                              (if (grob::has-interface r 'lyric-syllable-interface)
                                  (- (car (ly:grob-extent r sys X)) gx 0.1) (cdr xe)))))
                (bars (pr-bars-across grob sys))
                (hit? (lambda (d) (any (lambda (b) (and (> b (- (car d) pr-lyric-gap))
                                                        (< b (+ (cdr d) pr-lyric-gap))))
                                       bars))))
           (if (not (any hit? dashes))
               st
               (apply ly:stencil-add empty-stencil
                (append-map
                 (lambda (d)
                   (if (not (hit? d))
                       (list (pr-box (car d) (cdr d) ye blot))
                       (let* ((w (interval-length d)) (c (interval-center d))
                              (b (car (sort (filter (lambda (b) (and (> b (- (car d) pr-lyric-gap))
                                                                     (< b (+ (cdr d) pr-lyric-gap))))
                                                    bars)
                                            (lambda (p q) (< (abs (- p c)) (abs (- q c)))))))
                              ;; the free room either side of the bar line; a lone
                              ;; hyphen goes to the middle of the larger one, one of
                              ;; a row of dashes just clear of the bar line
                              (free-l (cons (car room) (- b pr-lyric-gap)))
                              (free-r (cons (+ b pr-lyric-gap) (cdr room)))
                              (place (lambda (f side)
                                       (if (= n 1)
                                           (let ((m (interval-center f)))
                                             (cons (- m (/ w 2)) (+ m (/ w 2))))
                                           (if (eq? side LEFT)
                                               (cons (- (cdr f) w) (cdr f))
                                               (cons (car f) (+ (car f) w))))))
                              (fits (lambda (s) (and (>= (car s) (car room)) (<= (cdr s) (cdr room))
                                                     (not (hit? s)))))
                              (cands (map car
                                      (sort (filter (lambda (p) (fits (car p)))
                                                    (list (cons (place free-l LEFT) (interval-length free-l))
                                                          (cons (place free-r RIGHT) (interval-length free-r))))
                                            (lambda (p q) (> (cdr p) (cdr q)))))))
                         (if (pair? cands)
                             (list (pr-box (car (car cands)) (cdr (car cands)) ye blot))
                             ;; no room to step aside: open the dash at the bar line
                             (let ((pieces (filter (lambda (s) (>= (- (cdr s) (car s)) (/ len 2)))
                                                   (pr-interval-minus (car d) (cdr d)
                                                     (list (cons (- b pr-lyric-gap) (+ b pr-lyric-gap)))))))
                               (if (null? pieces)
                                   (list (pr-box (car d) (cdr d) ye blot))
                                   (map (lambda (s) (pr-box (car s) (cdr s) ye blot)) pieces)))))))
                 dashes)))))))

%% ------------------------------------------------------------ bar lines
%% Final, repeat and double bar lines to plate proportions (Ross 147, 152):
%% the thick line half a staff space, half a space of white before it; the
%% two lines of a double bar three quarters of a space apart. LilyPond counts
%% both in line-thicknesses, so they are worked out from the staff space.
#(define (pr-per-lt grob x) (/ x (layout-line-thickness grob)))
#(define (pr-bar-thick grob) (pr-per-lt grob 0.5))
#(define (pr-bar-kern grob)
   (pr-per-lt grob (if (equal? (ly:grob-property grob 'glyph-name "") "||") 0.75 0.5)))

%% ------------------------------------------------------------ page fill
%% Spare height on a music page goes mostly to the gaps between the staves
%% of its systems, not between the systems (Ross 69). lilypond-book hands
%% LaTeX one picture per system, so this takes two passes (tools/build.sh,
%% tools/stretch_systems.py): the first build records each system's staves
%% (PR_SYSLOG) and LaTeX each page's slack; the second gives each system
%% the extra room worked out for its page (PR_STRETCH), added below the
%% lyrics of every staff but the last.
%% Systems are known by (score, system) in the order LilyPond lays them out,
%% which is the order lilypond-book numbers them; incipit staves are not
%% systems.
#(define pr-stretch-data
   (let ((f (getenv "PR_STRETCH")))
     (if (and f (file-exists? f)) (with-input-from-file f read) '())))
#(define pr-syslog
   (let ((f (getenv "PR_SYSLOG"))) (and f (not (string-null? f)) (open-file f "a"))))
#(define pr-scores '())
#(define (pr-system-key sys)
   (let* ((orig (ly:grob-original sys))
          (pieces (if (ly:grob? orig) (ly:spanner-broken-into orig) '()))
          (local (list-index (lambda (s) (eq? s sys)) pieces)))
     (and local
          (begin
            (if (not (memq orig pr-scores)) (set! pr-scores (append pr-scores (list orig))))
            (cons (list-index (lambda (o) (eq? o orig)) pr-scores) local)))))
#(define (pr-main-layout? grob)
   (not (ly:output-def-lookup (ly:grob-layout grob) 'indent-incipit-default #f)))
#(define (pr-log-staff grob)
   (let ((sys (ly:grob-system grob)))
     (if (and pr-syslog (ly:grob? sys) (pr-main-layout? grob))
         (let ((k (pr-system-key sys)))
           (if k (begin (format pr-syslog "~a ~a\n" (car k) (cdr k))
                        (force-output pr-syslog)))))))
#(define (pr-system-extra grob)
   (let ((sys (ly:grob-system grob)))
     (if (and (pair? pr-stretch-data) (ly:grob? sys) (pr-main-layout? grob))
         (let ((k (pr-system-key sys)))
           (or (and k (assoc-ref pr-stretch-data k)) 0))
         0)))
#(define (pr-lyrics-to-staff base)
   (ly:make-unpure-pure-container
    (lambda (grob) `((padding . ,(+ base (pr-system-extra grob)))))
    (lambda (grob start end) `((padding . ,base)))))

%% ------------------------------------------------------------ contexts
\layout {
  \context { \Score
    \override BarNumber.font-size = #-0.7
    \override BarNumber.font-shape = #'italic
    \override BarNumber.break-visibility = ##(#f #f #t)
    \override BarNumber.self-alignment-X = #LEFT
    %% clear of the curl of the system bracket
    \override BarNumber.X-offset = #1.2
    \override BarNumber.padding = #1.4
    \override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/4)
    \override RehearsalMark.break-align-symbols = #'(left-edge clef)
    %% Range of each voice after the clef, before the mensuration sign.
    \override BreakAlignment.break-align-orders =
      #(make-vector 3 '(left-edge cue-end-clef breathing-sign clef cue-clef
                        staff-bar key-cancellation key-signature ambitus
                        time-signature custos))
    \override VoltaBracket.font-size = #-2
    \override BarLine.thick-thickness = #pr-bar-thick
    \override BarLine.kern = #pr-bar-kern
    \override SpanBar.thick-thickness = #pr-bar-thick
    \override SpanBar.kern = #pr-bar-kern
    startRepeatBarType = ".|:"
    endRepeatBarType = ":|."
    doubleRepeatBarType = ":..:"
    sectionBarType = "||"
  }
  \context { \StaffGroup
    \override SpanBar.stencil = #pr-span-bar
    \override SystemStartBracket.collapse-height = #4
    \override StaffGrouper.staff-staff-spacing.padding = #(* pr-breathe 1.6)
    \override StaffGrouper.staffgroup-staff-spacing.padding = #(* pr-breathe 1.6)
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
    \override StaffSymbol.after-line-breaking = #pr-log-staff
  }
  %% Ties are solid; only \divTie (a divided source note) is dashed.
  \context { \Lyrics
    \override LyricText.font-size = #1.0
    %% Extender about as heavy as a full stop (Ross 183), twice LilyPond's;
    %% the hyphen to match it.
    \override LyricExtender.thickness = #2.0
    \override LyricHyphen.thickness = #1.8
    \override LyricHyphen.stencil = #pr-lyric-hyphen
    \override LyricExtender.stencil = #pr-lyric-extender
    \override LyricHyphen.minimum-distance = #1.2
    \override LyricSpace.minimum-distance = #1.2
    \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #(* pr-breathe 0.9)
    \override VerticalAxisGroup.nonstaff-nonstaff-spacing.padding = #(* pr-breathe 0.45)
    %% lyrics to the staff below: room for its ledger-line notes and accidentals
    \override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing = #(pr-lyrics-to-staff (* pr-breathe 2.0))
    \override StanzaNumber.font-size = #0.6
  }
}

%% Voice names in small capitals, abbreviated after the first system. An
%% editorial name (one the source does not give) is printed [Cantus] at its
%% first appearance in the critical edition (see \prStaff).
vname =
#(define-scheme-function (long short) (string? string?)
   #{ \with {
        instrumentName = \markup \smallCaps #long
        shortInstrumentName = \markup \smallCaps #short
      } #})
vnameEd =
#(define-scheme-function (long short) (string? string?)
   #{ \with {
        instrumentName = \markup \concat { "[" \smallCaps #long "]" }
        shortInstrumentName = \markup \smallCaps #short
      } #})

%% Editorial signs and names (critical edition only). A score whose source
%% lacks them declares, in score.ly before \prScore:
%%   prEditorialSign = ##t              mensuration sign printed [¢]
%%   prEditorialNames = ##t             every voice name editorial, or
%%   prEditorialNames = #'("altus")     only these (lower case)
#(define (pr-critical?) (not (eq? (ly:parser-lookup 'prPerformance) #t)))
#(define (pr-editorial-name? vname)
   (and (pr-critical?)
        (let ((v (ly:parser-lookup 'prEditorialNames)))
          (or (eq? v #t) (and (list? v) (member vname v) #t)))))
#(define (pr-editorial-sign?)
   (and (pr-critical?) (eq? (ly:parser-lookup 'prEditorialSign) #t)))
%% The sign in square brackets on the staff, where the sign stands.
mensSignEd =
#(define-music-function (glyph) (string?)
   #{ \override Staff.TimeSignature.stencil =
        #(lambda (grob)
           (bracketify-stencil
             (grob-interpret-markup grob (markup #:musicglyph glyph))
             Y 0.15 0.35 0.2)) #})

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

%% Rests (principles 5.8): in a performance edition every rest is cut at the
%% bar lines, so that entries can be counted by the bar. A critical edition
%% keeps the rests of a primary source as written; voices that come from a
%% modern edition can be regularised there too, by listing them in the
%% edition's music/engraving.ily:  prRegularRests = #'("cantus" "altus")
#(define (pr-regular-rests? vname)
   (or (eq? (ly:parser-lookup 'prPerformance) #t)
       (let ((l (ly:parser-lookup 'prRegularRests)))
         (and (list? l) (member vname l) #t))))

%% Whole-bar rests (performance editions; Gould 159): a rest, or the part of
%% a rest, that fills a whole bar becomes a whole-bar rest, centred in the
%% bar like any modern part's. The music is walked in time order; a change
%% of bar length (\finalis) is followed. If anything does not add up, the
%% music is left as it was.
#(define (pr-whole-bar-rests music bar)
   (let ((len bar) (anchor 0))
     (define (dur l) (ly:make-duration 0 0 l))
     (define (rest l) (make-music 'RestEvent 'duration (dur l)))
     (define (split m pos)
       ;; the rest m starting at pos, as rest / whole bars / rest
       (let* ((l (ly:moment-main (ly:music-length m)))
              (into (let ((x (- pos anchor))) (- x (* len (floor (/ x len))))))
              (head (if (zero? into) 0 (min l (- len into))))
              (n (floor (/ (- l head) len)))
              (tail (- l head (* n len))))
         (if (zero? n)
             (list m)
             (append (if (zero? head) '() (list (rest head)))
                     (map (lambda (i) (make-music 'MultiMeasureRestMusic 'duration (dur len)))
                          (iota n))
                     (if (zero? tail) '() (list (rest tail)))))))
     (define (walk m pos)
       ;; returns (new-music . end-pos)
       (cond
        ((and (music-is-of-type? m 'rest-event)
              (null? (ly:music-property m 'articulations))
              (not (ly:pitch? (ly:music-property m 'pitch #f))))
         (let ((parts (split m pos)))
           (cons (if (= 1 (length parts)) (car parts) (make-sequential-music parts))
                 (+ pos (ly:moment-main (ly:music-length m))))))
        ((music-is-of-type? m 'sequential-music)
         (let loop ((es (ly:music-property m 'elements)) (pos pos) (acc '()))
           (if (null? es)
               (begin (ly:music-set-property! m 'elements (reverse acc)) (cons m pos))
               (let ((r (walk (car es) pos)))
                 (loop (cdr es) (cdr r) (cons (car r) acc))))))
        ((music-is-of-type? m 'simultaneous-music)
         (let ((rs (map (lambda (e) (walk e pos)) (ly:music-property m 'elements))))
           (ly:music-set-property! m 'elements (map car rs))
           (cons m (apply max pos (map cdr rs)))))
        ((and (music-is-of-type? m 'layout-instruction-event) #f) (cons m pos))
        ((eq? (ly:music-property m 'name) 'PropertySet)
         (if (eq? (ly:music-property m 'symbol) 'measureLength)
             (begin (set! len (ly:moment-main (ly:music-property m 'value)))
                    (set! anchor pos)))
         (cons m pos))
        ((music-is-of-type? m 'repeated-music)
         (let* ((b (walk (ly:music-property m 'element) pos))
                (alts (let loop ((es (ly:music-property m 'elements)) (p (cdr b)) (acc '()))
                        (if (null? es) (cons (reverse acc) p)
                            (let ((r (walk (car es) p)))
                              (loop (cdr es) (cdr r) (cons (car r) acc)))))))
           (ly:music-set-property! m 'element (car b))
           (ly:music-set-property! m 'elements (car alts))
           (cons m (cdr alts))))
        ((and (ly:music? (ly:music-property m 'element #f))
              (not (music-is-of-type? m 'time-scaled-music)))
         (let ((r (walk (ly:music-property m 'element) pos)))
           (ly:music-set-property! m 'element (car r))
           (cons m (cdr r))))
        (else (cons m (+ pos (ly:moment-main (ly:music-length m)))))))
     (let* ((copy (ly:music-deep-copy music))
            (before (ly:music-length music))
            (r (walk copy 0)))
       (if (equal? before (ly:music-length (car r)))
           (car r)
           (begin (ly:warning "pr-whole-bar-rests: length changed, rests left as they were")
                  music)))))

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
          (vid (string-downcase long))
          (music (pr-fix-opt (if transposed #{ \transpose #from #to #notes #} notes)))
          (rmusic (if (pr-critical?) music
                      (pr-whole-bar-rests music
                        (ly:moment-main (pr-lookup 'prBarLength (ly:make-moment 2/1))))))
          (incipit (if (or transposed (null? (ly:music-property inc 'elements)))
                       #{ #}
                       #{ \incipit { \prMens #inc } #})))
     #{ <<
          \new Staff \with $(if (pr-editorial-name? vid) (vnameEd long short) (vname long short)) {
            $incipit
            \clef #useclef $key
            \time 2/1
            $(cond ((string-null? sign) #{ \omit Staff.TimeSignature #})
                   ((pr-editorial-sign?) #{ \mensSignEd #sign #})
                   (else #{ \mensSign #sign #}))
            \voiceSetup
            $(if (pr-regular-rests? vid)
                 #{ \new Voice = #vid \with { \remove "Rest_engraver" \consists "Completion_rest_engraver" completionUnit = #(ly:make-moment 1/1) } $rmusic #}
                 #{ \new Voice = #vid $music #})
          }
          $(make-simultaneous-music
             (map (lambda (w) #{ \new Lyrics \lyricsto #vid $w #})
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

%% Scale of reduction (Caldwell 23, 50): where the edition's values differ
%% from the source's, the critical edition states the equivalence, small,
%% above the first system, as the edition's note = the source's note.
%% score.ly declares it before the first \prScore:
%%   prValues = \prEquiv 1 2 "of the tablature"   (semibreve = minim of ...)
prEquiv =
#(define-scheme-function (ours theirs what) (ly:duration? ly:duration? markup?)
   (markup #:fontsize -1.5
     #:line (#:general-align Y DOWN #:note ours UP
             #:hspace 0.2 "=" #:hspace 0.2
             #:general-align Y DOWN #:note theirs UP
             #:italic what)))
#(define pr-values-done #f)
#(define (pr-values-mark)
   (let ((v (ly:parser-lookup 'prValues)))
     (if (and (pr-critical?) (markup? v) (not pr-values-done))
         (begin
           (set! pr-values-done #t)
           #{ \new Devnull {
                \tweak break-align-symbols #'(left-edge)
                \tweak self-alignment-X #RIGHT
                \tweak X-offset #(lambda (g) (- (self-alignment-interface::self-aligned-on-breakable g) 1.2))
                \tweak font-size #0
                \textMark #v } #})
         #{ #})))

prScore =
#(define-music-function (staves) (ly:music?)
   (let* ((perf (eq? (ly:parser-lookup 'prPerformance) #t))
          (breaks (pr-lookup (if perf 'prBreaksPerformance 'prBreaksCritical)
                             (pr-lookup 'prBreaks '())))
          (values (pr-values-mark)))
     (if (null? breaks)
         #{ \new StaffGroup << $staves $values >> #}
         #{ \new StaffGroup << $staves $values \new Devnull $(pr-break-voice breaks) >> #})))
