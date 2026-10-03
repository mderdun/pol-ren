import re
from fractions import Fraction as F
src=open('choral.ily').read()
def bars_of(name):
    body=re.search(name+r'\s*=\s*\{(.*?)\n\}',src,re.S).group(1)
    bars=[]
    for l in body.split('\n'):
        code=l.split('%')[0].strip()
        if not code: continue
        for seg in code.split('|'):
            seg=seg.strip()
            if not seg: continue
            m=re.fullmatch(r'R1\*(\d+)',seg)
            if m: bars+=['R1']*int(m.group(1)); continue
            bars.append(seg)
    return bars
STEP={'c':0,'d':2,'e':4,'f':5,'g':7,'a':9,'b':11}
def events(voice, sec):
    bars=bars_of(voice); a,b={'A':(0,56),'D':(56,88)}[sec]
    ev=[]; idx=0; tie=False
    for bi,bar in enumerate(bars[a:b]):
        pos=F(0)
        for t in re.findall(r"[a-gr](?:is|es)?[',]*\d+\.?~?|R1",bar):
            m=re.match(r"([a-grR])(is|es)?([',]*)(\d+)(\.?)(~?)",t)
            p,acc,o,d,dot,ti=m.groups()
            dur=F(1,int(d))*(F(3,2) if dot else 1)
            beat=float(pos*4+1)
            metric = 3 if pos==0 else 2 if pos==F(1,2) else 1 if pos.denominator<=4 else 0
            if p in 'rR':
                ev.append(dict(kind='rest',bar=bi+1+a,beat=beat,dur=dur)); tie=False
            else:
                midi=12*(4+o.count("'")-o.count(','))+STEP[p]+(1 if acc=='is' else -1 if acc=='es' else 0)
                if tie:
                    # extend previous
                    last=[e for e in ev if e['kind']=='note'][-1]; last['dur']+=dur
                else:
                    idx+=1; ev.append(dict(kind='note',idx=idx,bar=bi+1+a,beat=beat,dur=dur,pitch=midi,metric=metric))
                tie=bool(ti)
            pos+=dur
    return ev
