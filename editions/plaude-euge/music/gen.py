from fractions import Fraction as F
import re, json

def parse(spec):
    """spec tokens: pitch:dur[:flags]  dur in sb: B=2, 1, h=1/2, 1.5 ; flags: f=ficta, s=supplied ; 'r' rest"""
    out=[]
    for tok in spec.split():
        parts=tok.split(':')
        p=parts[0]; d={'B':F(2),'1':F(1),'h':F(1,2),'1.5':F(3,2),'L':F(4)}[parts[1] if len(parts)>1 else '1']
        fl=parts[2] if len(parts)>2 else ''
        out.append(dict(p=p,d=d,fl=fl))
    return out

def times(notes,start=F(0)):
    t=start
    for n in notes: n['t']=t; t+=n['d']
    return t

def sylls(text):
    """'Plau-de eu-ge' -> list of (syl, hyphen_after)"""
    out=[]
    for w in text.split():
        ps=w.split('-')
        for i,p in enumerate(ps): out.append((p,i<len(ps)-1))
    return out

def assign_by_count(notes,text,pattern):
    """pattern: list of ints, number of notes per syllable (rests excluded)."""
    S=sylls(text); assert len(S)==len(pattern),(text,len(S),len(pattern))
    ns=[n for n in notes if n['p']!='r']; assert sum(pattern)==len(ns),(text,sum(pattern),len(ns))
    k=0
    for (s,h),c in zip(S,pattern):
        ns[k]['syl']=(s,h)
        for j in range(1,c): ns[k+j]['mel']=True
        k+=c

DUR={F(2):'\\breve',F(1):'1',F(1,2):'2',F(3,2):'1.',F(4):'\\longa'}
def ly_notes(notes):
    """House notation: \\fi editorial accidental, \\sup supplied note,
    \\divTie a source note divided to carry text, flag L a long of the
    source printed as a long and scaled to the breve it fills."""
    out=[]
    for i,n in enumerate(notes):
        pre=''
        if 'f' in n['fl']: pre+='\\fi '
        if 's' in n['fl']: pre+='\\sup '
        if n.get('tie'): pre+='\\divTie '
        dur='\\longa*1/2' if 'L' in n['fl'] else DUR[n['d']]
        if 'L' in n['fl']: assert n['d']==F(2)
        tie='~' if n.get('tie') else ''
        out.append(f"{pre}{n['p']}{dur}{tie}")
    return ' '.join(out)

def ly_lyrics(notes):
    out=[]; prev_word_end=True
    for n in notes:
        if n['p']=='r': continue
        if 'syl' in n:
            s,h=n['syl']; out.append(s+(' --' if h else ''))
        else:
            out.append('_')
    # add extenders: after a word-final syllable followed by '_'
    res=[]
    for i,tok in enumerate(out):
        res.append(tok)
        if tok!='_' and not tok.endswith('--') and i+1<len(out) and out[i+1]=='_':
            res.append('__')
    return ' '.join(res)

def split_for(notes,onsets):
    """split notes so that every onset time starts a note; mark split fragments with tie."""
    out=[]
    for n in notes:
        cuts=sorted(t for t in onsets if n['t']<t<n['t']+n['d'])
        if not cuts or n['p']=='r': out.append(n); continue
        pts=[n['t']]+cuts+[n['t']+n['d']]
        for k in range(len(pts)-1):
            m=dict(n); m['t']=pts[k]; m['d']=pts[k+1]-pts[k]
            m['tie']= k<len(pts)-2
            m['split']=True
            if k>0: m['fl']=m['fl'].replace('f','')   # ficta mark only once
            out.append(m)
    return out

def assign_at(notes,onsets,text):
    S=sylls(text); assert len(S)==len(onsets),(text,len(S),len(onsets))
    m={t:s for t,s in zip(onsets,S)}
    for n in notes:
        if n['p']=='r': continue
        if n['t'] in m: n['syl']=m[n['t']]
        else: n['mel']=True
