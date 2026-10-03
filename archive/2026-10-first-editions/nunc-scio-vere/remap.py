import importlib, re
from fractions import Fraction as F
import build_core as bc
from underlay import U
old=open('choral_P.ily').read(); new=open('choral.ily').read()
def onsets(src,v,s):
    bc.src=src
    return [(e['idx'],F(e['bar'])*0+e['t']) for e in []]
def times(src,v,s):
    bc.src=src; ev=bc.events(v,s); t=F(0); out={}
    for e in ev:
        if e['kind']=='note': out[e['idx']]=(t,e['bar'],e['pitch'])
        t+=e['dur']
    return out
NU={}
for v in ['soprano','alto','tenor','bassus']:
  for s in 'AD':
    to=times(old,v,s); tn=times(new,v,s)
    t2n={t:i for i,(t,b,p) in tn.items()}
    und={}
    for i,syl in U[v,s].items():
        t=to[i][0]
        if t in t2n: und[t2n[t]]=syl
        else: print('LOST',v,s,'bar',to[i][1],syl)
    NU[v,s]=und
    # report new onsets near changes that lack syllable and are repeated pitch
    for i,(t,b,p) in tn.items():
        if t not in {x[0] for x in to.values()}: print('NEW onset',v,s,'bar',b,'idx',i,'syl?',und.get(i))
# write
txt=open('underlay.py').read()
for (v,s),und in NU.items():
    body=' '.join(f'{k}:{und[k]}' for k in sorted(und))
    txt=re.sub(r"(U\['%s','%s'\]=L\(\"\"\")(.*?)(\"\"\"\))"%(v,s), lambda m: m.group(1)+body+m.group(3), txt, flags=re.S)
open('underlay.py','w').write(txt)
