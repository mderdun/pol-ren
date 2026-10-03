import json
from fractions import Fraction as F
d=json.load(open('events.json'))
for v,ev in d.items():
    print('=====',v)
    line=[];cur=None
    for off,ql,p,ly,syl in ev:
        off=F(off); bar=int(off//8)+1; pos=(off%8)
        if bar!=cur:
            if line: print(' '.join(line))
            line=[f'[{bar}]']; cur=bar
        if p is None: line.append(f'r{float(F(ql)):g}'); continue
        txt = (ly+('-' if syl in('begin','middle') else '')) if ly else '_'
        line.append(f'{p}:{float(F(ql)):g}:{txt}')
    print(' '.join(line))
