import json, re
from fractions import Fraction as F
d=json.load(open('events.json'))
# lyrics as actually engraved (after overrides): parse lyrics.ily
lyr={}
for l in open('lyrics.ily'):
    v,body=l.split('Words = ',1); body=body[body.index('{')+1:body.rindex('}')]
    toks=[]; raw=body.split()
    i=0
    while i<len(raw):
        t=raw[i]
        if t in ('--','__'):
            if t=='--': toks[-1]=(toks[-1][0],True)
            i+=1; continue
        toks.append((t.strip('"'),False)); i+=1
    lyr[v]=toks
STRESS={'Vox':0,'vox':0,'in':0,'Rama':0,'audita':1,'est':0,'ploratus':1,'et':0,'ululatus':2,'Rachel':0,'plorans':0,'filios':0,'suos':0,'noluit':0,'consolari':2,'quia':0,'non':0,'sunt':0}
VAL={F(16):'L',F(8):'B',F(6):'SB.',F(4):'SB',F(3):'M.',F(2):'M',F(3,2):'Sm.',F(1):'Sm',F(1,2):'F'}
issues=[]
for v,ev in d.items():
    notes=[]  # (off,dur,pitch,prev_is_rest,next_is_rest)
    for k,(o,q,p,_,_) in enumerate(ev):
        if p is None: continue
        prev_rest = k>0 and ev[k-1][2] is None
        next_rest = k+1<len(ev) and ev[k+1][2] is None or k+1==len(ev)
        notes.append((F(o),F(q),p,prev_rest,next_rest))
    L=lyr[v]; assert len(L)==len(notes),(v,len(L),len(notes))
    # build words
    words=[];cur=[]
    for i,(t,h) in enumerate(L):
        if t=='_': continue
        cur.append(i)
        if not h: words.append(cur);cur=[]
    syl_at={i for w in words for i in w}
    bar=lambda o:f"{int(o//8)+1}.{float(o%8)/2+1:g}"
    import music21 as m
    ps=lambda p:m.pitch.Pitch(p).ps
    for i,(o,q,p,pr,nr) in enumerate(notes):
        if i in syl_at and q<=F(1,2): issues.append((v,bar(o),'FIRM: syllable on fusa'))
        if pr and i not in syl_at: issues.append((v,bar(o),'FIRM: no syllable on first note after rest'))
        if i in syl_at and q==1 and i>0 and notes[i-1][1] in (F(3),F(3,2)) and False: pass
    # word divided by rest; last syllable before rest
    for w in words:
        for a,b in zip(w,w[1:]):
            for j in range(a,b):
                if notes[j][4] and j<b: issues.append((v,bar(notes[j][0]),'FIRM: word divided by rest '+''.join(L[k][0] for k in w)))
    for i,(o,q,p,pr,nr) in enumerate(notes):
        if nr:
            # the last syllable of a word must have been reached: find word containing a syllable <= i
            w=[w for w in words if w[0]<=i][-1]
            if w[-1]>i: pass
            elif L[w[-1]][0] and w[-1]!=i and any(k in syl_at for k in []): pass
    # soft: repeated note without new syllable (white notes only)
    for i in range(1,len(notes)):
        o,q,p,pr,nr=notes[i]
        if p==notes[i-1][2] and q>=2 and i not in syl_at and not pr:
            issues.append((v,bar(o),f'soft: repeated {p} without new syllable'))
    # soft: stress — in each word, the stressed syllable should not be shorter than an unstressed one immediately adjacent (syllable span length)
    def span(k):
        nxt=min([x for x in syl_at if x>k] or [len(notes)])
        return sum(notes[j][1] for j in range(k,nxt)), nxt-k
    for w in words:
        word=''.join(L[k][0] for k in w).strip(',.:;')
        if word not in STRESS or len(w)<2: continue
        s=STRESS[word]
        if s>=len(w): continue
        lens=[span(k) for k in w]
        mel=[n for _,n in lens]
        # melisma on unstressed non-final syllable longer than on stressed
        for k,(du,nn) in enumerate(lens[:-1]):
            if k!=s and nn>=3 and nn>lens[s][1]:
                issues.append((v,bar(notes[w[k]][0]),f'soft: melisma ({nn} notes) on unstressed syllable {k+1} of "{word}"'))
        # final-syllable melisma longer than stressed (allowed at cadence, report as info)
        if lens[-1][1]>=4 and lens[-1][1]>lens[s][1]:
            issues.append((v,bar(notes[w[-1]][0]),f'info: final-syllable melisma ({lens[-1][1]} notes) on "{word}"'))
        # stressed syllable on semiminim while an unstressed neighbour is longer
        if lens[s][0]<=1 and any(lens[k][0]>=3 for k in range(len(w)) if k!=s and k!=len(w)-1):
            issues.append((v,bar(notes[w[s]][0]),f'soft: stressed syllable short in "{word}"'))
for x in issues: print(*x)
print(len(issues),'items')
