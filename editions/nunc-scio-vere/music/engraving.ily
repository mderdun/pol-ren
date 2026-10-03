%% Engraving decisions for this score only (breaks, spacing, local helpers).
%% The score has three parts, each its own \score: antiphon (bars 1-56),
%% psalm verse in chant, Gloria Patri (bars 57-88). \prSection, called in
%% score.ly before each part, selects that part's breaks and layout below.

%% System breaks, as absolute bar numbers after which a system ends.
prBreaksCriticalAnt = #'(6 12 19 25 31 38 44 50)
prBreaksPerformanceAnt = #'(8 16 24 32 40 48)
prBreaksCriticalDox = #'(62 67 72 77 82)
prBreaksPerformanceDox = #'(64 72 80)

%% ------------------------------------------------------------ helpers
%% Proposed for the house: a score in several parts.
%% \prSection #'Name #first-bar sets prBreaksCritical/Performance from
%% prBreaks<Kind><Name> (shifted so that first-bar counts as 1) and
%% prLayoutCritical/Performance from prLayout<Kind><Name> (house default
%% layout if undefined).
prSection =
#(define-void-function (name first) (symbol? integer?)
   (for-each
    (lambda (kind)
      (let ((br (ly:parser-lookup (symbol-append 'prBreaks kind name)))
            (lo (ly:parser-lookup (symbol-append 'prLayout kind name))))
        (ly:parser-define! (symbol-append 'prBreaks kind)
          (if (null? br) '() (map (lambda (b) (- b (- first 1))) br)))
        (ly:parser-define! (symbol-append 'prLayout kind) lo)))
    '(Critical Performance)))

%% A final printed as a long that lasts one bar (the source's breve tied
%% into a long-shaped head, as in the archive edition).
fin = \once \override NoteHead.duration-log = #-2

%% Closing rubric over the last bar line, right-aligned. \rubric aligns its
%% text left; this moves it left by its own width.
rubricEnd =
#(define-music-function (text) (markup?)
   #{ \once \override Score.RehearsalMark.break-visibility = #begin-of-line-invisible
      \once \override Score.RehearsalMark.X-offset =
        #(lambda (g) (- (self-alignment-interface::self-aligned-on-breakable g)
                        (interval-length (ly:stencil-extent (ly:grob-property g 'stencil) X))))
      \rubric #text #})

%% Psalm verse in chant: stemless notes on one staff, no time or range.
prChantStaff = \with {
  \remove Time_signature_engraver
  \remove Ambitus_engraver
  \override Stem.stencil = ##f
  \override Flag.stencil = ##f
  \override Slur.thickness = #1.4
}
prChantLyrics = \with {
  \override LyricSpace.minimum-distance = #2.2
  \override LyricHyphen.minimum-distance = #1.6
}
prLayoutCriticalPsalm = \layout { indent = 10\mm }
prLayoutPerformancePsalm = \layout { indent = 10\mm }
