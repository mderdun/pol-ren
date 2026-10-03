import json
from fractions import Fraction as F
import music21 as m
d=json.load(open('events.json'))
V={}
for v,ev in d.items():
    V[v]=[(F(o),F(o)+F(q),m.pitch.Pitch(p) if p else None) for o,q,p,_,_ in ev]
names=list(V)
times=sorted({e[0] for v in V for e in V[v]})
def snd(v,t):
    for a,b,p in V[v]:
        if a<=t<b: return p
def bar(t): return f"{int(t//8)+1}.{float(t%8)/2+1:g}"
print('-- vertical dissonances on strong minims (pos even) involving a fresh attack; tritones/aug any time')
for t in times:
    so={v:snd(v,t) for v in names}
    att={v:any(e[0]==t for e in V[v]) for v in names}
    for i in range(4):
        for j in range(i+1,4):
            a,b=so[names[i]],so[names[j]]
            if not a or not b: continue
            iv=abs(int(a.ps-b.ps))%12
            if iv==6 and (att[names[i]] or att[names[j]]): print('TT',bar(t),names[i],a.nameWithOctave,names[j],b.nameWithOctave)
            if iv in (1,11) and (att[names[i]] and att[names[j]]): print('2nd/7th both attack',bar(t),names[i],a.nameWithOctave,names[j],b.nameWithOctave)
print('-- parallels')
prev=None
for t in times:
    so={v:snd(v,t) for v in names}
    if prev:
        for i in range(4):
            for j in range(i+1,4):
                a0,b0=prev[names[i]],prev[names[j]]; a1,b1=so[names[i]],so[names[j]]
                if all([a0,b0,a1,b1]) and a0.ps!=a1.ps and b0.ps!=b1.ps:
                    i0=abs(int(a0.ps-b0.ps))%12; i1=abs(int(a1.ps-b1.ps))%12
                    if i0==i1 and i0 in (0,7): print('P'+('8' if i0==0 else '5'),bar(t),names[i],a0.nameWithOctave,a1.nameWithOctave,names[j],b0.nameWithOctave,b1.nameWithOctave)
    prev=so
print('-- cross relations (same letter, different alteration within one minim across voices)')
for t in times:
    for i in names:
        for j in names:
            if i>=j: continue
            a=snd(i,t)
            for dt in (F(1,2),F(1),F(2)):
                b=snd(j,t+dt) if t+dt<360 else None
                if a and b and a.step==b.step and a.alter!=b.alter: print('XR',bar(t),i,a.name,j,b.name,'+',float(dt))
print('-- ranges')
for v in names:
    ps=[p for a,b,p in V[v] if p]; lo=min(ps,key=lambda x:x.ps); hi=max(ps,key=lambda x:x.ps)
    print(v,lo.nameWithOctave,hi.nameWithOctave)
