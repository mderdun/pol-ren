%% musicxml-events.ily — event dump for tools/export_musicxml.py
%%
%% Included (through a temporary wrapper) before an edition's score.ly. It adds
%% listeners to Voice, Lyrics and Score contexts and writes one tab-separated
%% line per musical event to the file named by `prx-out`. Nothing here changes
%% the engraving; the export runs LilyPond with the null backend.
%%
%% Based on the idea of LilyPond's ly/event-listener.ly, extended with what a
%% MusicXML export needs: the voice name, exact rational moments, the bar
%% number and position, clef/key/time, ties, editorial accidentals (\fi), the
%% house editorial signs (\ed, \sup), lyric syllables with hyphens and
%% extenders, explicit bar lines, repeats and rubrics.

\version "2.24.0"

#(define prx-port #f)
#(define (prx-emit . fields)
   (if (not prx-port)
       (begin (set! prx-port (open-file prx-out "w"))
              (set-port-encoding! prx-port "UTF-8")))
   (display (string-join (map (lambda (x) (if (string? x) x (format #f "~a" x))) fields) "\t")
            prx-port)
   (newline prx-port)
   (force-output prx-port))

#(define (prx-mom m)
   (let ((g (ly:moment-grace m)))
     (if (zero? g)
         (format #f "~a" (ly:moment-main m))
         (format #f "~a~a" (ly:moment-main m) (if (negative? g) g (format #f "+~a" g))))))
#(define (prx-now ctx) (prx-mom (ly:context-current-moment ctx)))

#(define (prx-text m)
   (cond ((string? m) m)
         ((markup? m) (markup->string m))
         (else "")))
#(define (prx-clean s)
   (string-map (lambda (c) (if (memv c '(#\tab #\newline)) #\space c)) s))

#(define (prx-prop ctx sym)
   (let ((v (ly:context-property ctx sym)))
     (if (null? v) "" v)))

#(define (prx-timing ctx)
   ;; bar number, measure position, measure length, timing on/off
   (list (prx-prop ctx 'currentBarNumber)
         (prx-mom (ly:context-property ctx 'measurePosition (ly:make-moment 0)))
         (prx-mom (ly:context-property ctx 'measureLength (ly:make-moment 1)))
         (if (eq? (ly:context-property ctx 'timing) #f) "free" "timed")))

#(define (prx-dur d)
   (let ((f (ly:duration-scale d)))
     (list (ly:duration-log d) (ly:duration-dot-count d) f
           (prx-mom (ly:duration-length d)))))

#(define (prx-staff-info ctx)
   ;; clef glyph, clef position, clef transposition, key alterations, time sig
   (let* ((st (ly:context-find ctx 'Staff))
          (ka (ly:context-property st 'keyAlterations '()))
          (ts (ly:context-property st 'timeSignatureFraction #f))
          (name (ly:context-property st 'instrumentName ""))
          (short (ly:context-property st 'shortInstrumentName "")))
     (list (prx-prop st 'clefGlyph)
           (prx-prop st 'clefPosition)
           (prx-prop st 'clefTransposition)
           (string-join
            (map (lambda (e)
                   (if (pair? (car e))
                       (format #f "~a:~a" (cdar e) (cdr e))
                       (format #f "~a:~a" (car e) (cdr e))))
                 ka) ",")
           (if (pair? ts) (format #f "~a/~a" (car ts) (cdr ts)) "")
           (prx-clean (prx-text name))
           (prx-clean (prx-text short)))))

#(define (prx-grob-prop ctx grob prop)
   (let ((def (ly:context-grob-definition ctx grob)))
     (assoc-get prop def '())))

#(define (prx-note-flags ctx ev)
   (let* ((arts (ly:event-property ev 'articulations '()))
          (tweaks (ly:event-property ev 'tweaks '()))
          (flags '()))
     (define (add! f) (set! flags (cons f flags)))
     (for-each
      (lambda (a)
        (cond ((music-is-of-type? a 'tie-event) (add! "tie"))
              ((music-is-of-type? a 'articulation-event)
               (add! (format #f "art=~a" (ly:music-property a 'articulation-type))))
              ((music-is-of-type? a 'text-script-event)
               (add! (format #f "text=~a" (prx-clean (prx-text (ly:music-property a 'text))))))
              ((music-is-of-type? a 'slur-event)
               (add! (if (eqv? (ly:music-property a 'span-direction) START) "slur-start" "slur-stop")))
              ((music-is-of-type? a 'ligature-event)
               (add! (if (eqv? (ly:music-property a 'span-direction) START) "lig-start" "lig-stop")))))
      arts)
     (if (eq? (ly:context-property ctx 'suggestAccidentals #f) #t) (add! "ficta"))
     (let ((fs (assoc-get 'font-size tweaks #f)))
       (if (and (number? fs) (< fs 0)) (add! "editorial-note")))
     (if (and (defined? 'pr-bracket-head)
              (eq? (prx-grob-prop ctx 'NoteHead 'stencil) pr-bracket-head))
         (add! "supplied"))
     (if (pair? (prx-grob-prop ctx 'Tie 'dash-definition)) (add! "tie-dashed"))
     (if (number? (prx-grob-prop ctx 'NoteHead 'duration-log))
         (add! (format #f "head-log=~a" (prx-grob-prop ctx 'NoteHead 'duration-log))))
     (string-join (reverse flags) ",")))

#(define (prx-voice-ok? ctx)
   (let ((id (ly:context-id ctx)))
     (and (string? id) (not (string-null? id)))))

#(define prx-voice-engraver
   (lambda (ctx)
     (let ((seen #f))
       (define (header!)
         (if (not seen)
             (begin (set! seen #t)
                    (apply prx-emit "voice" (ly:context-id ctx) (prx-now ctx)
                           (prx-staff-info ctx)))))
       (make-engraver
        (listeners
         ((note-event engraver ev)
          (if (prx-voice-ok? ctx)
              (let ((p (ly:event-property ev 'pitch)))
                (header!)
                (apply prx-emit "note" (ly:context-id ctx) (prx-now ctx)
                       (append (prx-timing ctx)
                               (prx-dur (ly:event-property ev 'duration))
                               (list (ly:pitch-octave p) (ly:pitch-notename p)
                                     (ly:pitch-alteration p)
                                     (prx-note-flags ctx ev)
                                     (string-join (map (lambda (x) (format #f "~a" x)) (cdr (prx-staff-info ctx))) "|")))))))
         ((rest-event engraver ev)
          (if (prx-voice-ok? ctx)
              (begin
                (header!)
                (apply prx-emit "rest" (ly:context-id ctx) (prx-now ctx)
                       (append (prx-timing ctx)
                               (prx-dur (ly:event-property ev 'duration))
                               (list "" "" "" (prx-note-flags ctx ev)
                                     (string-join (map (lambda (x) (format #f "~a" x)) (cdr (prx-staff-info ctx))) "|")))))))
         ((multi-measure-rest-event engraver ev)
          (if (prx-voice-ok? ctx)
              (begin
                (header!)
                (apply prx-emit "rest" (ly:context-id ctx) (prx-now ctx)
                       (append (prx-timing ctx)
                               (prx-dur (ly:event-property ev 'duration))
                               (list "" "" "" "mmrest" ""))))))
         ((tie-event engraver ev)
          (if (prx-voice-ok? ctx) (prx-emit "tie" (ly:context-id ctx) (prx-now ctx))))
         ((slur-event engraver ev)
          (if (prx-voice-ok? ctx)
              (prx-emit "slur" (ly:context-id ctx) (prx-now ctx)
                        (if (eqv? (ly:event-property ev 'span-direction) START) "start" "stop"))))
         ((ligature-event engraver ev)
          (if (prx-voice-ok? ctx)
              (prx-emit "lig" (ly:context-id ctx) (prx-now ctx)
                        (if (eqv? (ly:event-property ev 'span-direction) START) "start" "stop"))))
         ((articulation-event engraver ev)
          (if (prx-voice-ok? ctx)
              (prx-emit "art" (ly:context-id ctx) (prx-now ctx)
                        (ly:event-property ev 'articulation-type))))
         ((text-script-event engraver ev)
          (if (prx-voice-ok? ctx)
              (prx-emit "text" (ly:context-id ctx) (prx-now ctx)
                        (prx-clean (prx-text (ly:event-property ev 'text)))))))))))

#(define (prx-assoc ctx)
   ;; \lyricsto sets associatedVoiceContext (2.24); associatedVoice may be unset
   (let ((vc (ly:context-property ctx 'associatedVoiceContext #f))
         (av (ly:context-property ctx 'associatedVoice #f)))
     (cond ((ly:context? vc) (ly:context-id vc))
           ((string? av) av)
           (else ""))))

#(define prx-lyric-engraver
   (lambda (ctx)
     (make-engraver
      (listeners
       ((lyric-event engraver ev)
        (let* ((arts (ly:event-property ev 'articulations '()))
               (hy (any (lambda (a) (music-is-of-type? a 'hyphen-event)) arts))
               (ex (any (lambda (a) (music-is-of-type? a 'extender-event)) arts))
               (shape (prx-grob-prop ctx 'LyricText 'font-shape)))
          (prx-emit "lyric" (prx-assoc ctx) (prx-now ctx)
                    (prx-clean (prx-text (ly:event-property ev 'text)))
                    (if hy "hyphen" "") (if ex "extender" "")
                    (if (eq? shape 'italic) "italic" ""))))
       ((hyphen-event engraver ev)
        (prx-emit "lyric-hyphen" (prx-assoc ctx) (prx-now ctx)))
       ((extender-event engraver ev)
        (prx-emit "lyric-extender" (prx-assoc ctx) (prx-now ctx)))))))

#(define prx-score-engraver
   (lambda (ctx)
     (make-engraver
      ((initialize engraver)
       (prx-emit "score" "" (prx-now ctx)))
      ((process-music engraver)
       (let ((wb (ly:context-property ctx 'whichBar '())))
         (if (string? wb)
             (prx-emit "bar" "" (prx-now ctx) wb))))
      (listeners
       ((ad-hoc-mark-event engraver ev)
        (prx-emit "mark" "" (prx-now ctx) (prx-clean (prx-text (ly:event-property ev 'text)))))
       ((volta-span-event engraver ev)
        (prx-emit "volta" "" (prx-now ctx)
                  (if (eqv? (ly:event-property ev 'span-direction) START) "start" "stop")
                  (ly:event-property ev 'volta-numbers '())))
       ((volta-repeat-start-event engraver ev)
        (prx-emit "repeat-start" "" (prx-now ctx)))
       ((volta-repeat-end-event engraver ev)
        (prx-emit "repeat-end" "" (prx-now ctx)))
       ((fine-event engraver ev)
        (prx-emit "fine" "" (prx-now ctx)))))))

\layout {
  \context { \Score \consists #prx-score-engraver }
  \context { \Voice \consists #prx-voice-engraver }
  \context { \Lyrics \consists #prx-lyric-engraver }
}
