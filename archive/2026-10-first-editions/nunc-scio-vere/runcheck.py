from underlay import U
import rules
tot={}
for v in ['soprano','alto','tenor','bassus']:
    for s in 'AD':
        fl=rules.check(v,s,U[v,s])
        for x in fl: tot[x[0]]=tot.get(x[0],0)+1
print(tot)
