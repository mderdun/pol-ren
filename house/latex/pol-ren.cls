%% pol-ren.cls — page design for the Polish Early Music editions
%%
%% One class sets every page of every edition. LilyPond (through
%% lilypond-book) and Gregorio only engrave music into it.
%%
%%   \documentclass[critical]{pol-ren}     title page, preface, score, notes
%%   \documentclass[performance]{pol-ren}  masthead, score first, one page of notes
%%   \documentclass[guide]{pol-ren}        a series guide (title page, prose)
%%   add [anthology] for a bound collection: book margins, parts open on rectos
%%
%% Every design decision lives in this file and in house/lilypond/pol-ren.ily.
%% Edition files hold content only (tools/lint.sh checks this).
%%
%% Compile with LuaLaTeX. See docs/house-style.md for the rules this encodes.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{pol-ren}[2026/10/03 Polish Early Music house style]

\newif\ifpr@critical \pr@criticaltrue
\newif\ifpr@anthology \pr@anthologyfalse
\def\pr@kind{Critical edition}
\DeclareOption{critical}{\pr@criticaltrue\def\pr@kind{Critical edition}}
\DeclareOption{performance}{\pr@criticalfalse\def\pr@kind{Performance edition}}
\DeclareOption{guide}{\pr@criticaltrue\def\pr@kind{Guide}}
\DeclareOption{anthology}{\pr@anthologytrue}
\ProcessOptions\relax

%% Two-sided in every case, so running heads alternate composer / piece.
\LoadClass[a4paper,11pt,twoside]{article}

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
\RequirePackage{booktabs,longtable,array,tabularx,calc}
\RequirePackage{enumitem}
\RequirePackage{lettrine}
\RequirePackage{etoolbox}
\RequirePackage{multicol}
\RequirePackage{tikz}
\RequirePackage[hidelinks]{hyperref}

%% ------------------------------------------------------------ colour
%% One colour besides black. It never carries information a black-and-white
%% copy would lose: initials, ornaments, the series line, liturgical rubrics.
\definecolor{rubric}{RGB}{154,30,30}   % #9A1E1E
\newcommand\red[1]{\textcolor{rubric}{#1}}

%% ------------------------------------------------------------ type
%% The pinned release fetched by tools/get-fonts.sh, else the system copy.
%% In the finished build (tools/build.sh, unless NOVELLO=0) the type is set in
%% Junicode Pressed (tools/make-pressed-fonts.sh): the same metrics, with the
%% series' ink-on-paper texture in the outlines.
\def\pr@juniname{Junicode}
\newif\ifpr@pressed
\def\pr@junipath{../../../house/fonts/junicode/}
\IfFileExists{\pr@junipath Junicode-Regular.otf}{}{%
  \def\pr@junipath{/usr/share/fonts/opentype/junicode/}%
  \IfFileExists{\pr@junipath Junicode-Regular.otf}{}{\def\pr@junipath{}}}
\ifnum\directlua{tex.print(os.getenv('NOVELLO') == '0' and 0 or 1)}=1
  \IfFileExists{../../../house/fonts/pressed/JunicodePressed-Regular.otf}{%
    \def\pr@juniname{JunicodePressed}\pr@pressedtrue%
    \def\pr@junipath{../../../house/fonts/pressed/}}{}
\fi
\setmainfont{\pr@juniname}[
  Path=\pr@junipath, Extension=.otf,
  UprightFont=*-Regular, ItalicFont=*-Italic,
  BoldFont=*-Medium, BoldItalicFont=*-MediumItalic,
  Numbers=OldStyle, Ligatures=TeX]
%% Expanded width, for titles and spaced capitals.
\newfontfamily\expfont{\pr@juniname}[
  Path=\pr@junipath, Extension=.otf,
  UprightFont=*-Exp, ItalicFont=*-ExpItalic,
  Numbers=OldStyle, Ligatures=TeX]
\newfontfamily\ornfont{\pr@juniname}[Path=\pr@junipath, Extension=.otf, UprightFont=*-Regular]

%% Figures: old-style in prose; lining tabular in apparatus columns.
\newcommand\lnum[1]{{\addfontfeatures{Numbers={Lining,Monospaced}}#1}}

%% Spaced small capitals (running heads, section heads, labels).
\newcommand\spacedsc[1]{\textls[90]{\textsc{#1}}}
%% Siglum of a source or edition: small capitals in a thin ring (one letter)
%% or a rounded frame (several), so that A never reads as the word "a".
%% Voice abbreviations (C, A, T, B) are plain small capitals: \voice{A}.
\newcommand\pr@scap[1]{{\upshape\addfontfeatures{Letters={SmallCaps,UppercaseSmallCaps},Numbers=Lining}#1}}
\ExplSyntaxOn
\NewDocumentCommand\sig{m}{
  \int_compare:nNnTF { \tl_count:n {#1} } = { 1 }
    { \tikz[baseline=(s.base)] \node[draw, line~width=0.32pt, circle,
        inner~sep=0pt, minimum~size=1.12em, font=\small](s){\pr@scap{#1}}; }
    { \tikz[baseline=(s.base)] \node[draw, line~width=0.32pt, rounded~corners=0.5em,
        inner~xsep=0.3em, inner~ysep=0pt, minimum~height=1.12em, font=\small](s){\pr@scap{#1}}; }
}
\ExplSyntaxOff
\newcommand\voice[1]{\pr@scap{#1}}
%% Polish, Latin and German text runs.
\newcommand\pl[1]{\textpolish{\itshape #1}}
%% Polish in a source's own spelling, quoted in prose: upright.
\newcommand\dipl[1]{\textpolish{\upshape #1}}
\newcommand\la[1]{\textlatin{\itshape #1}}
%% Accidentals in prose (Junicode has no music signs).
\newfontfamily\accfont{TeX Gyre Pagella}[Scale=0.92]
\newcommand\fl{{\accfont\raisebox{0.15ex}{♭}}}
\newcommand\na{{\accfont\raisebox{0.15ex}{♮}}}
%% Opening line of every Editorial method section: the series rules are not
%% restated in an edition (principles 13.4).
\newcommand\seriesrules{\noindent This edition follows the rules of the series, set out in the guide
  \textit{Editorial principles} and cited here by number. What follows is
  particular to this piece: its choices and its departures.\par}
\newcommand\sh{{\accfont\raisebox{0.15ex}{♯}}}

%% ------------------------------------------------------------ page
\ifpr@anthology
  %% Bound collections: book margins, inner < top < outer < bottom.
  \geometry{a4paper, inner=24mm, outer=36mm, top=24mm, bottom=37mm,
            headsep=7mm, footskip=12mm}
  \linespread{1.07}
\else
  %% Single editions: one full, symmetric page for every kind.
  %% Text block 170 × 257 mm. The long measure gets extra leading.
  \geometry{a4paper, left=20mm, right=20mm, top=17mm, bottom=23mm,
            headsep=5mm, footskip=10mm}
  \ifpr@critical\linespread{1.13}\else\linespread{1.06}\fi
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
%% Running heads: composer on even pages, piece on odd; folio outside.
\fancypagestyle{pr@body}{%
  \fancyhf{}\renewcommand\headrulewidth{0pt}%
  \fancyhead[LE,RO]{\small\lnum{\thepage}}%
  \fancyhead[CE]{\small\spacedsc{\pr@shortcomposer}}%
  \fancyhead[CO]{\small\textit{\pr@shorttitle}}}
\pagestyle{pr@body}

%% Section: centred spaced small capitals; never left at the foot of a page.
\titleformat{\section}[block]
  {\Needspace{6\baselineskip}\centering\normalsize}{}{0pt}
  {\spacedsc{#1}\addcontentsline{toc}{section}{#1}}
\titlespacing*{\section}{0pt}{2.1\baselineskip}{0.9\baselineskip}
%% Subsection: italic run-in, closed by a full stop.
\titleformat{\subsection}[runin]
  {\Needspace{3\baselineskip}\normalsize\itshape}{}{0pt}{#1.}
\titlespacing*{\subsection}{\parindent}{0.5\baselineskip}{0.5em}
\setcounter{secnumdepth}{0}

%% A part opens on a new page with a red fleuron and a centred head.
%% Only anthologies open parts on a recto.
\newcommand\fleuron{\par\medskip{\centering\red{\ornfont\large ❦}\par}\medskip}
\newcommand\dinkus{\par\smallskip{\centering\red{\ornfont ·\quad·\quad·}\par}\smallskip}
\newcommand\part@open[1]{%
  \ifpr@anthology\cleardoublepage\else\clearpage\fi
  \fleuron\section*{#1}}
\let\opensection\part@open

%% Blank versos left by \cleardoublepage carry a small ornament.
\def\cleardoublepage{\clearpage\if@twoside \ifodd\c@page\else
  \hbox{}\vfill{\centering\red{\ornfont ❧}\par}\vfill\thispagestyle{pr@plain}\newpage\fi\fi}

%% Translation of a block quotation, inside the quote environment.
\newcommand\translation[1]{\par\smallskip\noindent(#1)}
%% Block quotations: a size down, indented both sides.
\renewenvironment{quote}{\par\small\list{}{\leftmargin=2em\rightmargin=2em\topsep=0.5\baselineskip}\item\relax}{\endlist}

%% ------------------------------------------------------------ initials
\renewcommand\LettrineFontHook{\color{rubric}}
\renewcommand\LettrineTextFont{\scshape}
\setlength\DefaultFindent{0.15em}
\setlength\DefaultNindent{0em}
\newcommand\initial[2]{\lettrine[lines=3,loversize=0.08]{#1}{#2}}

%% ------------------------------------------------------------ title data
\newcommand\series[1]{\gdef\pr@series{#1}}            \series{Polish Early Music}
\newcommand\seriesno[1]{\gdef\pr@seriesno{#1}}        \seriesno{}
\def\pr@composer{}\def\pr@composerdates{}
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
%% Performance editions at a pitch other than the source's say so here.
\newcommand\pitchline[1]{\gdef\pr@pitchline{#1}}      \pitchline{}
\newcommand\shortcomposer[1]{\gdef\pr@shortcomposer{#1}}

%% ------------------------------------------------------------ title page
%% Critical edition: a title page and a colophon verso.
\newcommand\maketitlepage{%
  \thispagestyle{pr@plain}%
  \begin{center}
    \pr@doublerule\par\vspace{4mm}
    {\small\red{\spacedsc{\pr@series}}\ifx\pr@seriesno\@empty\else\enspace\red{\lnum{\pr@seriesno}}\fi\par}
    \vspace{34mm}
    \ifx\pr@composer\@empty\else{\expfont\large\textls[120]{\MakeUppercase{\pr@composer}}\par}\fi
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
    {\small\spacedsc{\pr@kind}\par}
    \vspace{2mm}
    \ifx\pr@sourceline\@empty\else{\small\itshape\pr@sourceline\par}\fi
    \vspace{6mm}
    {\normalsize \ifx\pr@kind\pr@guidekind by\else edited by\fi\ \pr@editor\par}
    \vspace{22mm}
    {\small\pr@editionno\enspace\red{\ornfont ·}\enspace\lnum{\pr@editiondate}\par}
    \vspace{4mm}\pr@doublerule[flip]\par
  \end{center}
  \clearpage}
\def\pr@guidekind{Guide}
%% Thick-and-thin rule, as on the title pages of printed partbooks.
\newcommand\pr@doublerule[1][]{%
  \ifx\relax#1\relax
    \rule{\textwidth}{1.1pt}\\[-0.55\baselineskip]\textcolor{rubric}{\rule{\textwidth}{0.35pt}}%
  \else
    \textcolor{rubric}{\rule{\textwidth}{0.35pt}}\\[-0.55\baselineskip]\rule{\textwidth}{1.1pt}%
  \fi}

%% Contents, generated from the section heads (no subsections).
\setcounter{tocdepth}{1}
\renewcommand*\l@section[2]{\par\noindent\hbox to 72mm{#1\hfil\lnum{#2}}\par}
\newcommand\colophon[1][]{%
  \thispagestyle{pr@plain}%
  \vspace*{12mm}
  {\small\noindent\spacedsc{Contents}\par\vspace{2mm}\@starttoc{toc}\par}
  \vspace*{\fill}
  {\small\raggedright
   \setlength\parskip{0.6\baselineskip}%
   #1\par
   \spacedsc{\pr@series}\ifx\pr@seriesno\@empty\else\enspace\lnum{\pr@seriesno}\fi.
   \ifx\pr@composer\@empty\else\pr@composer, \fi\textit{\pr@title}. \pr@editionno, \lnum{\pr@editiondate}.
   \ifx\pr@kind\pr@guidekind By\else Edited by\fi\ \pr@editor.\par
   This \ifx\pr@kind\pr@guidekind guide\else edition\fi\ is free. The text, any music and the source
   files are released under the Creative Commons Attribution 4.0
   International licence (CC~BY~4.0): you may copy, perform, record,
   adapt and publish them, for any purpose, provided you name the editor.
   \ifx\pr@kind\pr@guidekind\else The music itself is in the public domain.\fi\par
   Source files, corrections and later editions:
   \url{https://\pr@repo}\ifx\pr@slug\@empty\else\,/\,\texttt{\small editions/\pr@slug}\fi.\par
   Set in Junicode by Peter S. Baker\def\pr@tmp{JunicodePressed}\ifx\pr@juniname\pr@tmp, in a pressed
   variant made for the series\fi\ifx\pr@kind\pr@guidekind\else; music engraved with LilyPond and Gregorio\fi.\par}
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
  \ifx\pr@pitchline\@empty\else
    \vspace{1mm}{\centering\footnotesize\itshape\pr@pitchline\par}\fi
  \vspace{4mm}}

%% Score heading inside the critical edition (title page already given).
\newcommand\scorehead[1][]{%
  \clearpage\addcontentsline{toc}{section}{Score}%
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
   \ifx\pr@composer\@empty\else\pr@composer, \fi\textit{\pr@title}. Performance edition, \pr@editionno\
   (\lnum{\pr@editiondate}), edited by \pr@editor. The score is that of the
   critical edition\ifx\pr@pitchline\@empty\else, transposed\fi. CC~BY~4.0: free to copy and perform; name the editor.
   \url{https://\pr@repo}.\par}}

%% ------------------------------------------------------------ music
%% Systems from lilypond-book arrive as separate graphics; LaTeX breaks
%% pages between them. \keepsystems{n} glues the next n systems together.
\newlength\systemskip
\ifpr@critical\setlength\systemskip{4mm plus 3mm minus 1mm}
\else\setlength\systemskip{3mm plus 4mm minus 1mm}\fi
%% Per-score page breaks, set in the edition file before \lilypondfile:
%%   \scorepagebreaks{3}      new page after system 3 (comma list allowed)
%% Elsewhere a page may break between systems where LaTeX finds room.
\ExplSyntaxOn
\clist_new:N \g_pr_pbreaks_clist
\NewDocumentCommand\scorepagebreaks{m}{\clist_gset:Nn \g_pr_pbreaks_clist {#1}}
\NewDocumentCommand\pr@sysbreak{m}{
  \clist_if_in:NnTF \g_pr_pbreaks_clist {#1} {\newpage} {}}
\ExplSyntaxOff
\def\betweenLilyPondSystem#1{\par\vspace{\systemskip}%
  \ifcsname pr@sysskip@\the\numexpr#1+1\endcsname
    \vspace{\csname pr@sysskip@\the\numexpr#1+1\endcsname}\fi
  \pr@sysbreak{#1}\noindent
  \expandafter\pr@sysmark\expandafter{\the\numexpr#1+1\relax}}
%% Extra space before system n, from the page-fill pass (see below).
\def\prsysskip#1#2{\expandafter\def\csname pr@sysskip@#1\endcsname{#2}}
\AtBeginDocument{\InputIfFileExists{\jobname.prskip}{}{}}
\def\preLilyPondExample{\pr@sysmark{1}}
%% Page fill (house-style §9, Ross 69): for tools/stretch_systems.py, record
%% in \jobname.prsys which page each system lands on (S page system) and how
%% much height each page leaves unused at natural spacing (P page slack).
%% The build then gives most of that slack to the staff gaps inside the
%% systems (pol-ren.ily, PR_STRETCH) and builds again.
\newwrite\pr@sysout
\AtBeginDocument{\immediate\openout\pr@sysout=\jobname.prsys\relax}
\def\pr@sysmark#1{\write\pr@sysout{S \thepage\space #1}}
\let\pr@makecol\@makecol
\def\@makecol{%
  \setbox\z@\vbox{\unvcopy\@cclv}%
  \immediate\write\pr@sysout{P \thepage\space\the\dimexpr\textheight-\ht\z@\relax}%
  \pr@makecol}
%% A note at the foot of a music page, for a sign on that page that singers
%% cannot read without it. Use sparingly: house-style §9.
\newcommand\pagenote[1]{{\renewcommand\thefootnote{}\renewcommand\@makefntext[1]{\noindent\itshape##1}%
  \footnotetext{#1}}}
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
\newcommand\cn[3]{\lnum{#1} & \voice{#2} & #3\\[0.25em]}

%% Variant tables for chant and texts: loc. | lemma | readings.
%%   \cl{1.4}{lemma}{readings}   \clbreak between stanzas
\newenvironment{variants}
  {\par\small\setlength\LTpre{0.4\baselineskip}\setlength\LTpost{0pt}%
   \renewcommand\arraystretch{1.18}%
   \begin{longtable}{@{}>{\raggedright\arraybackslash}p{2.6em}
                       >{\raggedright\arraybackslash}p{9em}
                       >{\raggedright\arraybackslash}p{\dimexpr\textwidth-11.6em-4\tabcolsep\relax}@{}}
   \spacedsc{loc.} & \spacedsc{lemma} & \spacedsc{readings}\\ \midrule\endhead}
  {\end{longtable}\par}
\newcommand\cl[3]{\lnum{#1} & \pl{#2} & #3\\[0.25em]}
\newcommand\clbreak{\midrule}
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
%% Verse lines inside one table cell: \lines{line\\ line\\ ...}
\newcommand\lines[1]{\begin{tabular}[t]{@{}l@{}}#1\end{tabular}}

%% Stanzas printed after a score: centred, two abreast by default; an
%% incomplete last row is centred below. Columns share the width of the
%% widest stanza. A score that needs it may ask for another count:
%%   \begin{stanzas}[3] \stanza{2}{line\\ line ...} ... \end{stanzas}
\newsavebox\pr@stbox \newsavebox\pr@strow
\newlength\pr@stmax \newcount\pr@stn \newcount\pr@sti \newcount\pr@stc \newcount\pr@stcols
\newcommand\pr@stanzabox[2]{\begin{tabular}[t]{@{}l@{}}\llap{\stanzanumber{#1}\enspace}#2\end{tabular}}
\newenvironment{stanzas}[1][2]
  {\par\nopagebreak[4]\vspace{5mm}\small\global\pr@stcols=#1\relax
   \gdef\pr@stlist{}\global\pr@stn=0
   \def\stanza##1##2{\global\advance\pr@stn by 1
     \g@addto@macro\pr@stlist{\pr@do{##1}{##2}}}}
  {\global\pr@stmax=0pt
   \def\pr@do##1##2{\sbox\pr@stbox{\pr@stanzabox{##1}{##2}}%
     \ifdim\wd\pr@stbox>\pr@stmax\global\pr@stmax=\wd\pr@stbox\fi}%
   \pr@stlist
   \global\pr@sti=0 \global\pr@stc=0
   \par\noindent\begin{minipage}{\linewidth}%   never split across pages
   \def\pr@do##1##2{\global\advance\pr@sti by 1 \global\advance\pr@stc by 1
     \ifnum\pr@stc=1 \global\sbox\pr@strow{}\fi
     \global\sbox\pr@strow{\usebox\pr@strow\ifnum\pr@stc>1 \hspace{3.5em}\fi
       \makebox[\pr@stmax][l]{\pr@stanzabox{##1}{##2}}}%
     \ifnum\pr@stc=\pr@stcols \pr@flushrow \else\ifnum\pr@sti=\pr@stn \pr@flushrow\fi\fi}%
   \def\pr@flushrow{\par{\centering\usebox\pr@strow\par}%
     \ifnum\pr@sti<\pr@stn\vspace{0.9\baselineskip}\fi\global\pr@stc=0 }%
   \pr@stlist\par\end{minipage}\par}

\newcommand\colhead[1]{{\upshape\footnotesize\spacedsc{#1}}}

%% IPA, upright in square brackets: \ipa{ˈmat.ka}
\newcommand\ipa[1]{{\upshape[#1]}}
%% Sound tables for the pronunciation guide.
%%   soundtable: spelling | sound | example
%%   latintable: spelling | Polish Latin | Roman | example
\newenvironment{soundtable}
  {\par\small\setlength\LTpre{0.5\baselineskip}\setlength\LTpost{0.5\baselineskip}%
   \renewcommand\arraystretch{1.2}%
   \begin{longtable}{@{}>{\itshape\raggedright\arraybackslash}p{34mm}
                       >{\raggedright\arraybackslash}p{62mm}
                       >{\raggedright\arraybackslash}p{\dimexpr\textwidth-96mm-4\tabcolsep\relax}@{}}
   \colhead{spelling} & \colhead{sound} & \colhead{example}\\ \midrule\endhead}
  {\end{longtable}\par}
\newenvironment{latintable}
  {\par\small\setlength\LTpre{0.5\baselineskip}\setlength\LTpost{0.5\baselineskip}%
   \renewcommand\arraystretch{1.2}%
   \begin{longtable}{@{}>{\itshape\raggedright\arraybackslash}p{30mm}
                       >{\raggedright\arraybackslash}p{24mm}
                       >{\raggedright\arraybackslash}p{30mm}
                       >{\raggedright\arraybackslash}p{\dimexpr\textwidth-84mm-6\tabcolsep\relax}@{}}
   \colhead{spelling} & \colhead{polish latin} & \colhead{roman} & \colhead{example}\\ \midrule\endhead}
  {\end{longtable}\par}
\newcommand\tablegroup[1]{\multicolumn{3}{@{}l}{\footnotesize\spacedsc{#1}}\\[0.2em]}

%% Pronunciation: spelling | sound | as in.
\newenvironment{pronunciation}
  {\par\small\noindent\begin{tabular}{@{}>{\itshape}l@{\hspace{1.5em}}l@{\hspace{1.5em}}l@{}}
   \colhead{spelling} & \colhead{sound} & \colhead{as in}\\ \midrule}
  {\end{tabular}\par}

%% Rehearsal notes: two columns on the wide performance page.
%% Kept whole with its heading: if it does not fit, it starts a new page.
\newenvironment{rehearsal}
  {\par\noindent\begin{minipage}{\linewidth}\section*{For rehearsal}%
   \setlength\columnsep{8mm}\begin{multicols}{2}\raggedcolumns}
  {\end{multicols}\end{minipage}\par}
%% Performance notes: short run-in labels in italic.
\newcommand\pnote[1]{\par\smallskip\noindent\textit{#1.}\enspace}

%% ------------------------------------------------------------ chant
%% Gregorio settings (load gregoriotex in the edition file when needed).
\AtBeginDocument{%
  \@ifpackageloaded{gregoriotex}{%
    \grechangestyle{annotation}{\small\color{rubric}}%
    \grechangestyle{initial}{\color{rubric}\fontsize{38}{38}\selectfont}%
    \ifpr@critical\grechangestaffsize{18}\else\grechangestaffsize{21}\fi
    %% the pressed copy of greciliae (tools/make-pressed-fonts.sh; TTFONTS from tools/build.sh)
    \ifpr@pressed\IfFontExistsTF{pressedchant.ttf}{\gresetgregoriofont{pressedchant}}{}\fi
  }{}}

\endinput
