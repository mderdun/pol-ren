# Test against Wacław 1553 habit: clause-final word's longest melisma falls on its stressed syllable
import build_core as bc, underlay as u
from rules import STRESS, words
tot=ok=0; bad=[]
for (v,s),und in u.U.items():
    ev=[e for e in bc.events(v,s) if e['kind']=='note']
    keys=sorted(und); n=len(ev)
    span={}
    for j,k in enumerate(keys):
        nxt=keys[j+1] if j+1<len(keys) else n+1
        span[k]=(nxt-k, sum(e['dur'] for e in ev if k<=e['idx']<nxt))
    for w,syls in words(und,n):
        last=und[syls[-1][0]]
        if not any(last.rstrip().endswith(p) for p in ',.:;') or len(syls)<2: continue
        st=STRESS.get(w, STRESS.get(w.capitalize(), None))
        if st is None: continue
        lens=[span[i][0] for i,_ in syls[:-1]]   # exclude final (cadence) syllable
        mx=max(lens); tot+=1
        if mx<=1: ok+=1; continue
        if lens[st]==mx if st<len(lens) else False: ok+=1
        else: bad.append((v,s,w,lens,st,ev[syls[0][0]-1]['bar']))
print(ok,'/',tot)
for b in bad: print(b)
