import sys, build_core as bc
from underlay import U
NM='C D E F G A B'.split()
def nm(m):
    pc=m%12; o=m//12-1
    names={0:'c',1:'cis',2:'d',3:'es',4:'e',5:'f',6:'fis',7:'g',8:'gis',9:'a',10:'bes',11:'b'}
    return names[pc]+("'"*(o-3) if o>=4 else ','*(3-o) if o<3 else '')
v,s=sys.argv[1],sys.argv[2]
ev=bc.events(v,s); und=U[v,s]
bar=None; line=[]
for e in ev:
    if e['bar']!=bar:
        if line: print(f'{bar:>2}: '+'  '.join(line))
        bar=e['bar']; line=[]
    if e['kind']=='rest': line.append('r'+str(e['dur'])); continue
    d=e['dur']; ds={1:'1',F(1,2) if False else 0:''}
    syl=und.get(e['idx'],'')
    line.append(f"{e['idx']}:{nm(e['pitch'])}/{e['dur']}"+(f"[{syl}]" if syl else ''))
print(f'{bar:>2}: '+'  '.join(line))
