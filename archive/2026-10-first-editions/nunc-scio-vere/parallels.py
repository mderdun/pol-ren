from fractions import Fraction as F
def par(voices):
    """voices: list of lists (onset, dur, midi or None). returns list of (time, i, j, kind)"""
    def at(v,t):
        for o,d,p in v:
            if o<=t<o+d: return p,o
        return None,None
    ons=sorted(set(o for v in voices for o,_,_ in v))
    out=[]; prev=None
    for t in ons:
        cur=[at(v,t) for v in voices]
        if prev:
            for i in range(len(voices)):
                for j in range(i+1,len(voices)):
                    p1,p2=prev[i][0],prev[j][0]; c1,c2=cur[i][0],cur[j][0]
                    if None in (p1,p2,c1,c2): continue
                    if p1==c1 or p2==c2: continue
                    if (c1-p1)*(c2-p2)<=0 and abs(c1-p1)!=abs(c2-p2): pass
                    i1=abs(p1-p2)%12; i2=abs(c1-c2)%12
                    if i1==i2 and i1 in (0,7) and (c1-p1)*(c2-p2)>0:
                        out.append((t,i,j,'8ve' if i1==0 else '5th'))
        prev=cur
    return out
