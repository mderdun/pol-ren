%% pol-ren.cls — page design for the Polish Early Music editions
%%
%% One class sets every page of every edition. LilyPond (through
%% lilypond-book) and Gregorio only engrave music into it.
%%
%%   \documentclass[critical]{pol-ren}     two-sided book page, title page
%%   \documentclass[performance]{pol-ren}  one-sided, score first
%%
%% Compile with LuaLaTeX. See docs/house-style.md for the rules this encodes.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{pol-ren}[2026/10/03 Polish Early Music house style]

\newif\ifpr@critical \pr@criticaltrue
\DeclareOption{critical}{\pr@criticaltrue}
\DeclareOption{performance}{\pr@criticalfalse}
\ProcessOptions\relax

\ifpr@critical
  \LoadClass[a4paper,11pt,twoside]{article}
\else
  \LoadClass[a4paper,11pt,oneside]{article}
\fi

%% ------------------------------------------------------------ packages
\RequirePackage{iftex}
\RequireLuaTeX
\RequirePackage{fontspec}
\RequirePackage{polyglossia}
\setdefaultlanguage[variant=british]{english}
\setotherlanguages{polish,latin,german}
\RequirePackage[protrusion=true,expansion=true,tracking=true]{microtype}
\RequirePackage{geometry}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{fancyhdr}
\RequirePackage[explicit]{titlesec}
\RequirePackage{needspace}
\RequirePackage{booktabs,longtable,array,tabularx}
\RequirePackage{enumitem}
\RequirePackage{lettrine}
\RequirePackage{etoolbox}
\RequirePackage{multicol}
\RequirePackage[hidelinks]{hyperref}

%% ------------------------------------------------------------ colour
%% One colour besides black. It never carries information a black-and-white
%% copy would lose: initials, ornaments, the series line, liturgical rubrics.
\definecolor{rubric}{RGB}{154,30,30}   % #9A1E1E
\newcommand\red[1]{\textcolor{rubric}{#1}}

%% ------------------------------------------------------------ type
\def\pr@junipath{/usr/share/fonts/opentype/junicode/}
\IfFileExists{\pr@junipath Junicode-Regular.otf}{}{\def\pr@junipath{}}
\setmainfont{Junicode}[
  Path=\pr@junipath, Extension=.otf,
  UprightFont=*-Regular, ItalicFont=*-Italic,
  BoldFont=*-Medium, BoldItalicFont=*-MediumItalic,
  Numbers=OldStyle, Ligatures=TeX]
%% Expanded width, for titles and spaced capitals.
\newfontfamily\expfont{Junicode}[
  Path=\pr@junipath, Extension=.otf,
  UprightFont=*-Exp, ItalicFont=*-ExpItalic,
  Numbers=OldStyle, Ligatures=TeX]
\newfontfamily\ornfont{Junicode}[Path=\pr@junipath, Extension=.otf, UprightFont=*-Regular]

%% Figures: old-style in prose; lining tabular in apparatus columns.
\newcommand\lnum[1]{{\addfontfeatures{Numbers={Lining,Monospaced}}#1}}

%% Spaced small capitals (running heads, section heads, labels).
\newcommand\spacedsc[1]{\textls[90]{\textsc{#1}}}
%% Siglum: capitals set as small capitals, upright.
\newcommand\sig[1]{{\upshape\addfontfeatures{Letters={SmallCaps,UppercaseSmallCaps}}#1}}
%% Polish, Latin and German text runs.
\newcommand\pl[1]{\textpolish{\itshape #1}}
\newcommand\la[1]{\textlatin{\itshape #1}}
%% Pitch: c′ = middle c. \p{c'} → c′
%% Accidentals in prose (Junicode has no music signs).
\newfontfamily\accfont{TeX Gyre Pagella}[Scale=0.92]
\newcommand\fl{{\accfont\raisebox{0.15ex}{♭}}}
\newcommand\na{{\accfont\raisebox{0.15ex}{♮}}}
\newcommand\sh{{\accfont\raisebox{0.15ex}{♯}}}

%% ------------------------------------------------------------ page
\ifpr@critical
  %% Text block 150 × 236 mm; margins inner < top < outer < bottom.
  \geometry{a4paper, inner=24mm, outer=36mm, top=24mm, bottom=37mm,
            headsep=7mm, footskip=12mm, marginparwidth=24mm}
  \linespread{1.07}           % 11/14.4
\else
  %% Wider block for larger music; still a margin to hold.
  \geometry{a4paper, left=18mm, right=18mm, top=16mm, bottom=20mm,
            headsep=5mm, footskip=9mm}
  \linespread{1.04}
\fi

\setlength\parindent{1.2em}
\setlength\parskip{0pt}
\clubpenalty=10000 \widowpenalty=10000 \displaywidowpenalty=10000
\brokenpenalty=10000
\raggedbottom
\frenchspacing

%% ------------------------------------------------------------ heads
\fancypagestyle{pr@plain}{\fancyhf{}\renewcommand\headrulewidth{0pt}}
\newcommand\pr@shorttitle{}
\newcommand\pr@shortcomposer{}
\newcommand\pr@section{}
\newcommand\runninghead[1]{\gdef\pr@section{#1}}
\ifpr@critical
  \fancypagestyle{pr@body}{%
    \fancyhf{}\renewcommand\headrulewidth{0pt}%
    \fancyhead[LE]{\small\lnum{\thepage}}%
    \fancyhead[RO]{\small\lnum{\thepage}}%
    \fancyhead[CE]{\small\spacedsc{\pr@shortcomposer}\enspace\red{\ornfont ·}\enspace\textit{\pr@shorttitle}}%
    \fancyhead[CO]{\small\spacedsc{\pr@section}}}
\else
  \fancypagestyle{pr@body}{%
    \fancyhf{}\renewcommand\headrulewidth{0pt}%
    \fancyhead[R]{\small\lnum{\thepage}}%
    \fancyhead[L]{\small\spacedsc{\pr@shortcomposer}\enspace\red{\ornfont ·}\enspace\textit{\pr@shorttitle}}}
\fi
\pagestyle{pr@body}

%% Section: centred spaced small capitals; never left at the foot of a page.
\titleformat{\section}[block]
  {\Needspace{6\baselineskip}\centering\normalsize}{}{0pt}
  {\spacedsc{#1}\gdef\pr@section{#1}}
\titlespacing*{\section}{0pt}{2.1\baselineskip}{0.9\baselineskip}
%% Subsection: italic run-in, closed by a full stop.
\titleformat{\subsection}[runin]
  {\Needspace{3\baselineskip}\normalsize\itshape}{}{0pt}{#1.}
\titlespacing*{\subsection}{\parindent}{0.5\baselineskip}{0.5em}
\setcounter{secnumdepth}{0}

%% A part opens with a red fleuron and a centred head (critical edition only).
\newcommand\fleuron{\par\medskip{\centering\red{\ornfont\large ❦}\par}\medskip}
\newcommand\dinkus{\par\smallskip{\centering\red{\ornfont ·\quad·\quad·}\par}\smallskip}
\newcommand\part@open[1]{%
  \ifpr@critical\cleardoublepage\else\clearpage\fi
  \fleuron\section*{#1}}
\let\opensection\part@open

%% Blank versos left by \cleardoublepage carry a small ornament.
\def\cleardoublepage{\clearpage\if@twoside \ifodd\c@page\else
  \hbox{}\vfill{\centering\red{\ornfont ❧}\par}\vfill\thispagestyle{pr@plain}\newpage\fi\fi}

%% ------------------------------------------------------------ initials
\renewcommand\LettrineFontHook{\color{rubric}}
\renewcommand\LettrineTextFont{\scshape}
\setlength\DefaultFindent{0.15em}
\setlength\DefaultNindent{0em}
\newcommand\initial[2]{\lettrine[lines=3,loversize=0.08]{#1}{#2}}

%% ------------------------------------------------------------ title data
\newcommand\series[1]{\gdef\pr@series{#1}}            \series{Polish Early Music}
\newcommand\seriesno[1]{\gdef\pr@seriesno{#1}}        \seriesno{}
\newcommand\composer[2][]{\gdef\pr@composer{#2}\gdef\pr@shortcomposer{#2}\gdef\pr@composerdates{#1}}
\newcommand\composeralt[1]{\gdef\pr@composeralt{#1}}  \composeralt{}
\newcommand\poet[1]{\gdef\pr@poet{#1}}                \poet{}
\renewcommand\title[2][]{\gdef\pr@title{#2}\gdef\pr@shorttitle{#2}\ifx\relax#1\relax\else\gdef\pr@shorttitle{#1}\fi}
\newcommand\subtitle[1]{\gdef\pr@subtitle{#1}}        \subtitle{}
\newcommand\forces[1]{\gdef\pr@forces{#1}}            \forces{}
\newcommand\sourceline[1]{\gdef\pr@sourceline{#1}}    \sourceline{}
\newcommand\editor[1]{\gdef\pr@editor{#1}}            \editor{Mikołaj Derduń}
\newcommand\edition[2]{\gdef\pr@editionno{#1}\gdef\pr@editiondate{#2}}
\edition{First edition}{2026}
\newcommand\repository[1]{\gdef\pr@repo{#1}}          \repository{github.com/mderdun/pol-ren}
\newcommand\slug[1]{\gdef\pr@slug{#1}}                \slug{}
\newcommand\headnote[1]{\gdef\pr@headnote{#1}}        \headnote{}

%% ------------------------------------------------------------ title page
%% Critical edition: a title page and a colophon verso.
\newcommand\maketitlepage{%
  \thispagestyle{pr@plain}%
  \begin{center}
    \pr@doublerule\par\vspace{4mm}
    {\small\red{\spacedsc{\pr@series}}\ifx\pr@seriesno\@empty\else\enspace\red{\lnum{\pr@seriesno}}\fi\par}
    \vspace{34mm}
    {\expfont\large\textls[120]{\MakeUppercase{\pr@composer}}\par}
    \ifx\pr@composerdates\@empty\else\vspace{1.5mm}{\small\pr@composerdates\par}\fi
    \ifx\pr@composeralt\@empty\else\vspace{1mm}{\small\itshape\pr@composeralt\par}\fi
    \vspace{12mm}
    {\fontsize{30}{34}\selectfont\pr@title\par}
    \ifx\pr@subtitle\@empty\else\vspace{4mm}{\Large\itshape\pr@subtitle\par}\fi
    \vspace{6mm}
    {\red{\ornfont\Large ❦}\par}
    \vspace{6mm}
    {\normalsize\pr@forces\par}
    \ifx\pr@poet\@empty\else{\normalsize words by \pr@poet\par}\fi
    \vfill
    {\small\spacedsc{Critical edition}\par}
    \vspace{2mm}
    \ifx\pr@sourceline\@empty\else{\small\itshape\pr@sourceline\par}\fi
    \vspace{6mm}
    {\normalsize edited by \pr@editor\par}
    \vspace{22mm}
    {\small\pr@editionno\enspace\red{\ornfont ·}\enspace\lnum{\pr@editiondate}\par}
    \vspace{4mm}\pr@doublerule[flip]\par
  \end{center}
  \clearpage}
%% Thick-and-thin rule, as on the title pages of printed partbooks.
\newcommand\pr@doublerule[1][]{%
  \ifx\relax#1\relax
    \rule{\textwidth}{1.1pt}\\[-0.55\baselineskip]\textcolor{rubric}{\rule{\textwidth}{0.35pt}}%
  \else
    \textcolor{rubric}{\rule{\textwidth}{0.35pt}}\\[-0.55\baselineskip]\rule{\textwidth}{1.1pt}%
  \fi}

\newcommand\colophon[1][]{%
  \thispagestyle{pr@plain}%
  \vspace*{\fill}
  {\small\raggedright
   \setlength\parskip{0.6\baselineskip}%
   #1\par
   \spacedsc{\pr@series}\ifx\pr@seriesno\@empty\else\enspace\lnum{\pr@seriesno}\fi.
   \pr@composer, \textit{\pr@title}. \pr@editionno, \lnum{\pr@editiondate}.
   Edited by \pr@editor.\par
   This edition is free. The editorial text, the score and its source
   files are released under the Creative Commons Attribution 4.0
   International licence (CC~BY~4.0): you may copy, perform, record,
   adapt and publish them, for any purpose, provided you name the editor.
   The music itself is in the public domain.\par
   Source files, corrections and later editions:
   \url{https://\pr@repo}\ifx\pr@slug\@empty\else\,/\,\texttt{\small editions/\pr@slug}\fi.\par
   Set in Junicode. Music engraved with LilyPond; chant with Gregorio.\par}
  \clearpage}

%% Performance edition: a masthead at the top of the first page; the
%% music follows on the same page.
\newcommand\makemasthead{%
  \thispagestyle{pr@plain}%
  \begin{center}
    {\footnotesize\red{\spacedsc{\pr@series}}\enspace\red{\ornfont ·}\enspace\footnotesize\spacedsc{Performance edition}\par}
    \vspace{5mm}
    {\fontsize{24}{28}\selectfont\pr@title\par}
    \ifx\pr@subtitle\@empty\else\vspace{1.5mm}{\large\itshape\pr@subtitle\par}\fi
    \vspace{3mm}
  \end{center}
  {\small\noindent
   \begin{tabularx}{\textwidth}{@{}X r@{}}
   \ifx\pr@poet\@empty\else\pr@poet\fi &
   \spacedsc{\pr@composer}\ifx\pr@composerdates\@empty\else\ \pr@composerdates\fi
   \end{tabularx}\par}
  \ifx\pr@headnote\@empty\else
    \vspace{2mm}
    {\centering\begin{minipage}{0.86\textwidth}\centering\small\itshape
       \pr@headnote\end{minipage}\par}
  \fi
  \vspace{4mm}}

%% Score heading inside the critical edition (title page already given).
\newcommand\scorehead[1][]{%
  \begin{center}
    \ifx\relax#1\relax\else{\small\red{\itshape #1}\par}\vspace{2mm}\fi
    {\Large\pr@title\par}
    \ifx\pr@subtitle\@empty\else\vspace{1mm}{\itshape\pr@subtitle\par}\fi
  \end{center}
  {\small\noindent\begin{tabularx}{\textwidth}{@{}X r@{}}
   \ifx\pr@poet\@empty\else\pr@poet\fi & \spacedsc{\pr@composer}\end{tabularx}\par}
  \vspace{3mm}}

%% Colophon line at the foot of the last page of a performance edition.
\newcommand\footcolophon{%
  \par\vfill
  {\footnotesize\noindent\rule{\textwidth}{0.3pt}\par\vspace{1mm}\noindent
   \pr@composer, \textit{\pr@title}. Performance edition, \pr@editionno\
   (\lnum{\pr@editiondate}), edited by \pr@editor. The score is that of the
   critical edition. CC~BY~4.0: free to copy and perform; name the editor.
   \url{https://\pr@repo}.\par}}

%% ------------------------------------------------------------ music
%% Systems from lilypond-book arrive as separate graphics; LaTeX breaks
%% pages between them. \keepsystems{n} glues the next n systems together.
\newlength\systemskip
\ifpr@critical\setlength\systemskip{4mm plus 3mm minus 1mm}
\else\setlength\systemskip{3mm plus 4mm minus 1mm}\fi
\def\betweenLilyPondSystem#1{\par\vspace{\systemskip}\pr@sysbreak\noindent}
\def\pr@sysbreak{}
\newcommand\musicnote[1]{\par{\small\itshape\centering #1\par}}

%% ------------------------------------------------------------ apparatus
%% Sources: siglum in a hanging column of small capitals.
\newenvironment{sigla}
  {\begin{description}[leftmargin=4.2em,labelwidth=3.6em,labelsep=0.6em,
     align=left,font=\normalfont,itemsep=0.35\baselineskip,parsep=0pt,topsep=0.4\baselineskip]}
  {\end{description}}
\newcommand\siglum[1]{\item[\sig{#1}]}

%% Critical notes: Bar | Voice | Note. Three columns, no vertical rules.
\newenvironment{apparatus}
  {\par\small\setlength\LTpre{0.4\baselineskip}\setlength\LTpost{0pt}%
   \renewcommand\arraystretch{1.18}%
   \begin{longtable}{@{}>{\raggedright\arraybackslash}p{2.6em}
                       >{\raggedright\arraybackslash}p{3.4em}
                       >{\raggedright\arraybackslash}p{\dimexpr\textwidth-6em-4\tabcolsep\relax}@{}}
   \spacedsc{bar} & \spacedsc{voice} & \spacedsc{note}\\ \midrule\endhead}
  {\end{longtable}\par}
\newcommand\cn[3]{\lnum{#1} & \sig{#2} & #3\\[0.25em]}
%% Verdict at the end of a note: small capitals, not bold.
\newcommand\verdict[1]{\textsc{#1}}

%% Literature: hanging indent, short title first.
\newenvironment{literature}
  {\par\small\begin{list}{}{\leftmargin=1.6em\itemindent=-1.6em\itemsep=0.3\baselineskip
     \parsep=0pt\topsep=0.4\baselineskip}}
  {\end{list}\par}
\newcommand\lit{\item}
\newcommand\litgroup[1]{\par\medskip\noindent{\itshape #1}\par\smallskip}

%% Text and translation side by side: textcols (text | translation) and
%% dipltextcols (diplomatic | transcription | translation).
\newenvironment{textcols}
  {\par\small\noindent\setlength\tabcolsep{0pt}\setlength\LTpre{0.3\baselineskip}%
   \begin{longtable}{@{}p{1.8em}p{0.46\textwidth}@{\hspace{0.04\textwidth}}>{\itshape}p{\dimexpr0.5\textwidth-1.8em\relax}@{}}}
  {\end{longtable}\par}
\newenvironment{dipltextcols}
  {\par\small\noindent\setlength\tabcolsep{0pt}\setlength\LTpre{0.3\baselineskip}%
   \begin{longtable}{@{}p{1.8em}p{0.315\textwidth}@{\hspace{0.025\textwidth}}p{0.295\textwidth}@{\hspace{0.025\textwidth}}>{\itshape}p{\dimexpr0.34\textwidth-1.8em\relax}@{}}}
  {\end{longtable}\par}
\newcommand\stanzanumber[1]{\red{\lnum{#1}}}
\newcommand\colhead[1]{{\upshape\footnotesize\spacedsc{#1}}}

%% Pronunciation: spelling | sound | as in.
\newenvironment{pronunciation}
  {\par\small\noindent\begin{tabular}{@{}>{\itshape}l@{\hspace{1.5em}}l@{\hspace{1.5em}}l@{}}
   \colhead{spelling} & \colhead{sound} & \colhead{as in}\\ \midrule}
  {\end{tabular}\par}

%% Rehearsal notes: two columns on the wide performance page.
\newenvironment{rehearsal}{\par\setlength\columnsep{8mm}\begin{multicols}{2}\raggedcolumns}{\end{multicols}}
%% Performance notes: short run-in labels in italic.
\newcommand\pnote[1]{\par\smallskip\noindent\textit{#1.}\enspace}

%% ------------------------------------------------------------ chant
%% Gregorio settings (load gregoriotex in the edition file when needed).
\AtBeginDocument{%
  \@ifpackageloaded{gregoriotex}{%
    \grechangestyle{annotation}{\small\color{rubric}}%
    \grechangestyle{initial}{\color{rubric}\fontsize{38}{38}\selectfont}%
    \ifpr@critical\grechangestaffsize{18}\else\grechangestaffsize{21}\fi
  }{}}

\endinput
