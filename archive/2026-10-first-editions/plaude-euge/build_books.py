from prose import *
import text as T

PRE = r'''\version "2.24.0"
\include "common.ily"
\include "score.ily"
fl = \markup \raise #0.55 \fontsize #-3 \flat
na = \markup \raise #0.55 \fontsize #-3 \natural
sh = \markup \raise #0.55 \fontsize #-3 \sharp
'''
def mlist(items, gap=1.0):
    out=[]
    for it in items:
        out.append(it)
        if gap>0.2: out.append(f'\\vspace #{gap*0.6}')
    return '\\markuplist { \\override #\'(baseline-skip . 3.4) \\column-lines { '+'\n'.join(out)+' } }'

def sections(secs, hsize=1.5):
    items=[]
    for head,paras in secs:
        items += block(head,paras,hsize)
        items.append('\\vspace #0.4')
    return items

def commentary():
    items=[]
    items += block(T.COMMENTARY_HEAD,[T.COMMENTARY_INTRO],1.5)
    for loc,txt in T.COMMENTARY:
        it=False
        m=para(txt,'\\justify')
        # prepend bold location
        m=m.replace('\\justify {', f'\\justify {{ \\bold "{loc}."',1)
        items.append(m)
    return items

def text_trans():
    lat='\\column { '+' '.join(f'"{l}"' if l else '\\vspace #0.6' for l in T.TEXT_LAT)+' }'
    eng='\\column { '+' '.join(f'"{l}"' if l else '\\vspace #0.6' for l in T.TEXT_ENG)+' }'
    col=f"\\column {{ {heading('Text and translation',1.5)} \\vspace #0.4 \\fill-line {{ \\italic {lat} {eng} }} }}"
    return [col]

def sources():
    items=[f"\\column {{ {heading('Sources and literature',1.5)} \\vspace #0.2 {para(T.SOURCES[0])} }}"]
    items += [para(s) for s in T.SOURCES[1:]]
    return items

TITLE = r'''\header {
  title = \markup \override #'(font-name . "EB Garamond") \fontsize #4 "Plaude euge theotocos"
  subtitle = \markup \italic "for three voices"
  composer = \markup \column { \right-align "Piotr z Grudziądza" \right-align \small "(Petrus Wilhelmi de Grudencz, 1392 – after 1452)" }
  poet = \markup \small "Leipzig, Universitätsbibliothek, Ms 1236, f. 139v"
  tagline = ##f
  footer = "%s"
}'''

def facs():
    return r'''\markup \column {
  \fill-line { \epsfile #X #100 "facs.eps" }
  \vspace #0.6
  \fill-line { \justify { Leipzig, Universitätsbibliothek, Ms 1236, f. 139v (upper part). Discantus (staves 1–2), Medius (staves 3–4), Tenor (stave 5). Leipzig University Library, Public Domain Mark. } }
}'''

def critical():
    s=PRE+'\\book {\n'+TITLE%"Plaude euge theotocos · critical edition"+'\n'
    s+='\\bookpart {\n\\markup \\vspace #1\n'
    s+=mlist([heading('Introduction',2.5),'\\vspace #0.5']+sections(T.INTRO))+'\n'
    s+='\\markup \\vspace #1\n'+mlist(sections(T.METHOD))+'\n'
    s+='\\pageBreak\n'+facs()+'\n'
    s+='\\markup \\vspace #2\n'+mlist(text_trans())+'\n'
    s+='}\n\\bookpart { \\header { title = ##f subtitle = ##f composer = ##f poet = ##f } \\paper { page-count = #2 systems-per-page = #3 }\n\\score { \\plaudeScore \\header { piece = \\markup \\fontsize #2 "Plaude euge theotocos" } }\n}\n'
    s+='\\bookpart { \\header { title = ##f subtitle = ##f composer = ##f poet = ##f } \\paper { markup-markup-spacing = #\'((basic-distance . 1) (padding . 0.6)) }\n'+mlist(commentary(),0.25)+'\n'
    s+='\\markup \\vspace #1.5\n'+mlist(sources(),0.5)+'\n'
    s+='}\n}\n'
    open('plaude-euge-critical.ly','w').write(s)

def performance():
    s=PRE+'\\book {\n'+TITLE%"Plaude euge theotocos · performance edition"+'\n'
    s+='\\bookpart {\n\\markup \\vspace #1\n'+mlist([para(p) for p in T.PERF_NOTE],0.5)+'\n'
    s+='\\markup \\vspace #1.5\n'+mlist(text_trans())+'\n}\n'
    s+='\\bookpart { \\header { title = ##f subtitle = ##f composer = ##f poet = ##f } \\paper { page-count = #2 systems-per-page = #3 }\n\\score { \\plaudeScore }\n}\n'
    s+='}\n'
    open('plaude-euge-performance.ly','w').write(s)
critical(); performance()
