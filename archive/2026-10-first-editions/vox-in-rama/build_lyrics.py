import json
d=json.load(open('events.json'))
# Editorial underlay changes (see critical notes)
OVR={'altus':{4:('in','single'),5:('Ra','begin'),10:('ma','end')}}
def esc(t): return '"'+t+'"' if any(c in t for c in ',.;:') else t
out=[]
for v,ev in d.items():
    notes=[e for e in ev if e[2] is not None]
    syl=[(e[3],e[4]) for e in notes]
    for i,(t,s) in OVR.get(v,{}).items(): syl[i]=(t,s)
    # normalise: strip punctuation, rebuild words, punctuate phrase ends, lowercase repeated 'Vox'
    syl=[(t.strip(',.;:') if t else t,s) for t,s in syl]
    idx=[i for i,(t,s) in enumerate(syl) if t]
    words=[];cur=[]
    for i in idx:
        cur.append(i)
        if syl[i][1] in ('end','single'): words.append(cur);cur=[]
    PH={'Rama','ululatus','plorans','suos','consolari','sunt','est'}
    first=True
    for wi,w in enumerate(words):
        word=''.join(syl[i][0] for i in w)
        if word=='Vox':
            if not first: syl[w[0]]=('vox',syl[w[0]][1])
            first=False
        if wi==len(words)-1: syl[w[-1]]=(syl[w[-1]][0]+'.',syl[w[-1]][1])
        elif word in PH:
            nxt=''.join(syl[i][0] for i in words[wi+1])
            if not (word=='Rama' and nxt=='audita'):
                syl[w[-1]]=(syl[w[-1]][0]+',',syl[w[-1]][1])
    toks=[]
    for i,(t,s) in enumerate(syl):
        if t is None: toks.append('_'); continue
        tok=esc(t)
        nxt_mel = i+1<len(syl) and syl[i+1][0] is None
        if s in ('begin','middle'): tok+=' --'
        elif nxt_mel: tok+=' __'
        toks.append(tok)
    out.append(f'{v}Words = \\lyricmode {{ '+' '.join(toks)+' }')
open('lyrics.ily','w').write('\n'.join(out)+'\n')
print(open('lyrics.ily').read()[:1200])
