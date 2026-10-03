from data import *
def sect(v):
    VOICES[v][5][-1]['fl']+='F'
    b1,a1,b2,c1,c2,c3 = VOICES[v][0],VOICES[v][1],VOICES[v][2],VOICES[v][3],VOICES[v][4],VOICES[v][5]
    mus = (f"\\repeat volta 2 {{ {ly_notes(b1)} }}\n  \\alternative {{ {{ {ly_notes(a1)} }} {{ {ly_notes(b2)} }} }}\n"
           f"  {'\\break ' if v=='D' else ''}\\repeat volta 2 {{ {ly_notes(c1)} }}\n  \\alternative {{ {{ {ly_notes(c2)} }} {{ {ly_notes(c3)} \\bar \"|.\" }} }}")
    lyr = ' '.join(ly_lyrics(x) for x in (b1,a1,b2,c1,c2,c3))
    return mus,lyr
out=[]
for v,name in [('D','discantus'),('M','medius'),('T','tenor')]:
    m,l=sect(v)
    out.append(f"{name}Notes = {{\n  {m}\n}}\n{name}Text = \\lyricmode {{\n  {l}\n}}\n")
open('voices.ily','w').write('\n'.join(out))
print(open('voices.ily').read())
