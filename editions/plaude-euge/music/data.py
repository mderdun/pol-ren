from gen import *

# Discantus
D1  = parse("d':1 f':1 e':1.5 f':h g':h d':h d':h e':h c':B d':1 r:1 a':1.5 g':h f':1 bes':h a':1 g':1 f':h a':1 r:1 a':h f':h f':h g':h e':h e':h e':1 f':h d':h c':h d':h e':1 f':1 g':1.5 a':h")
D1a = parse("f':h e':h f':h g':h e':B")
D1b = parse("f':h e':h f':h d':h e':B:s")
D2  = parse("d':1 e':h f':h g':1 d':1 a':h f':h f':h g':h e':1 d':1 e':h e':h e':1 a':B bes':h g':h g':h f':h g':B f':h e':h e':h d':h f':h f':h d':1 g':h f':h e':h d':h")
D2a = parse("e':1 g':h a':h f':h e':h f':h d':h e':B")
D2b = parse("e':1 e':1 f':h e':h d':h cis':h:f d':B:s")
# Medius
M1  = parse("a:1 a:h bes:h c':1 g:h a:h bes:1 f:h g:h a:1 e:h f:h g:B e:1 r:1 r:1 bes:1 f:1 g:h f:h e:h d:h e:1 a:1 bes:h a:h a:h g:h a:1 bes:h a:h g:h f:h g:1 a:1 c':1 g:1")
M1a = parse("a:h a:h bes:h bes:h a:B")
M1b = parse("a:h a:h g:h g:h a:B")
M2  = parse("g:1 a:h b:h:f c':1 a:1 f:1 bes:1 a:h g:h g:h f:h a:B e:h e:h e:h f:h d:1 c:1 d:B a:h a:h g:h a:h bes:h a:h bes:1 c':1 b:1:f")
M2a = parse("c':1 g:h a:h bes:h a:h a:h g:h a:B")
M2b = parse("c':1 g:h a:h a:h bes:h a:h gis:h:f a:B")
# Tenor
T1  = parse("d:B a,:1 bes,:1 g,:1 bes,:1 a,:B g,:B a,:1 c:1 d:B a,:1 bes,:1 a,:B d:B c:B d:1 f:1 c:1 d:1 c:B")
T1a = parse("a,:1 d:1 a,:B")
T1b = parse("a,:1 bes,:1 a,:B")
T2  = parse("g,:1 d:1 c:1 f:1 d:B a,:1 bes,:1 a,:B c:B g,:1 a,:1 g,:B c:B d:1 f:1 e:1 g:1")
T2a = parse("c:B d:B a,:B")
T2b = parse("c:B d:1 e:1 d:B")

TXT1 = "Plau-de eu-ge the-o-to-cos re-gi-na vir-gi-num sa-lus ho-mi-num in te con-fi-den-ci-um"
TXT1e= "con-fi-den-ci-um"
TXT2D= "Te lau-dan-tes in-spi-ce mi-se-ros nec de-spi-ce sed mi-se-ri-cor-di-e o-cu-lis"
TXT2M= "Te lau-dan-tes in-spi-ce mi-se-ros nec de-spi-ce sed mi-se-ri-cor-di-e"
TXTho= "hos re-spi-ce"
TXToc= "o-cu-lis hos re-spi-ce"

for seq,st in [(D1,0),(D1a,28),(D1b,28),(D2,0),(D2a,22),(D2b,22),(M1,0),(M1a,28),(M1b,28),(M2,0),(M2a,22),(M2b,22),(T1,0),(T1a,28),(T1b,28),(T2,0),(T2a,22),(T2b,22)]:
    e=times(seq,F(st))
lens={k:sum(n['d'] for n in v) for k,v in dict(D1=D1,M1=M1,T1=T1,D2=D2,M2=M2,T2=T2,D1a=D1a,M1a=M1a,T1a=T1a,D2a=D2a,M2a=M2a,T2a=T2a,D2b=D2b,M2b=M2b,T2b=T2b).items()}
print({k:float(v) for k,v in lens.items()})

# --- D underlay
assign_by_count(D1,TXT1,[1,1,1,1,1,1,2,2, 1,1,1,2,2,1, 2,2,1,1,1, 1,1,1,1,1,1,2])
assign_by_count(D1a,TXT1e,[1]*5); assign_by_count(D1b,TXT1e,[1]*5)
pass  # part II D: see below
# --- M underlay
# Medius: 're-gi-na' kept whole after the rests (no word divided by a rest); 'sa-lus' follows a held '-num'
_OM1=[F(x) for x in (0,1,2,3,4,5,6,8, 13,14,15,16,16.5,17, 19,19.5,20,20.5,21, 22,22.5,23,23.5,24,25,26)]
assign_at(M1,_OM1,TXT1)
assign_by_count(M1a,TXT1e,[1]*5); assign_by_count(M1b,TXT1e,[1]*5)
pass  # part II M: see below

# --- T underlay (editorial): syllables placed at chosen onsets, long notes divided where needed
def onsets_of(notes):
    return [n['t'] for n in notes if n['p']!='r' and 'syl' in n]
# ---- Tenor: no note divided; it sings what fits on its own notes (text in italics, editorial).
TT1  = "Plau-de the-o-to-cos re-gi-na vir-gi-num sa-lus con-fi-den-ci"
OT1  = [F(x) for x in (0,2,4,5,6,8, 10,11,12,14,15,16, 18,20, 22,23,24,25)]
# Bar 14 (sb 26-28) moves into both endings; the Tenor varies there.
import copy
_tailT=[n for n in T1 if n['t']>=26]; T1=[n for n in T1 if n['t']<26]
assign_at(T1,OT1,TT1)
_l=[n for n in T1 if 'syl' in n][-1]; _l['syl']=(_l['syl'][0],True)
T1a=copy.deepcopy(_tailT)+T1a; T1b=copy.deepcopy(_tailT)+T1b
for n in T1a+T1b: n.pop('syl',None); n.pop('mel',None)
# first time: anticipating "con-fi" in minims, then den-ci-um on the written notes
O1a=[F(x) for x in (26,27,27.5,28,29,30)]
T1a=split_for(T1a,O1a); assign_at(T1a,O1a,"um con-fi-den-ci-um")
# second time: settles with the upper voices, four minims into the breve
O1b=[F(x) for x in (26,28,28.5,29,29.5,30)]
T1b=split_for(T1b,O1b); assign_at(T1b,O1b,"um con-fi-den-ci-um")
def _move_tail(body,e1,e2,cut=F(26)):
    tail=[n for n in body if n['t']>=cut]
    rest=[n for n in body if n['t']<cut]
    return rest, copy.deepcopy(tail)+e1, copy.deepcopy(tail)+e2
D1,D1a,D1b=_move_tail(D1,D1a,D1b)
M1,M1a,M1b=_move_tail(M1,M1a,M1b)


# ---- Part II: phrase-led underlay.
# Cadences: A at sb 8 (end of line 1), G at sb 14 (line 2), C at sb 22 (first note of the endings), final at sb 26.
# Lines 3-4 are declaimed homorhythmically by all three voices; accents fall on breve/semibreve downbeats:
# TE(0) lau-DAN(2)-tes IN(4)-spi-ce | MI-se-ros nec DE(12)-spi-ce | sed mi-se-ri-COR(18)-di-e O(20)-cu-lis hos RE(24)-spi-ce
TXT2 = "Te lau-dan-tes in-spi-ce mi-se-ros nec de-spi-ce sed mi-se-ri-cor-di-e o-cu"
TXTe = "lis hos re-spi-ce"
L34  = [16,16.5,17,17.5,18,18.5,19,20,21]
ON = {
 'D': [0,1,2,3,4,5,7,  8,8.5,9,10,12,13,14] + L34,
 'M': [0,1,2,3,4,7,8,  10,10.5,11,11.5,12,13,14] + L34,
 'T': [0,1,2,3,4,6,8,  10,10.5,11,11.5,12,13,14] + L34,
}
ONe = [22,23,24,25,26]
def setII(body,e1,e2,v):
    o=[F(x) for x in ON[v]]; oe=[F(x) for x in ONe]
    b=split_for(body,o); assign_at(b,o,TXT2)
    last=[n for n in b if 'syl' in n][-1]; last['syl']=(last['syl'][0],True)
    a=split_for(e1,oe); assign_at(a,oe,TXTe)
    c=split_for(e2,oe); assign_at(c,oe,TXTe)
    return b,a,c
D2,D2a,D2b = setII(D2,D2a,D2b,'D')
M2,M2a,M2b = setII(M2,M2a,M2b,'M')
TT2 = "Te lau-dan-tes in-spi-ce nec de-spi-ce sed hos o-cu"
OT2 = [F(x) for x in (0,1,2,3,4,6,8, 10,12,13,14, 16,18,20,21)]
TT2e= "lis re-spi-ce"; OT2e=[F(22),F(24),F(25),F(26)]
assign_at(T2,OT2,TT2)
_l=[n for n in T2 if 'syl' in n][-1]; _l['syl']=(_l['syl'][0],True)
T2a=split_for(T2a,OT2e); assign_at(T2a,OT2e,TT2e)
T2b=split_for(T2b,OT2e); assign_at(T2b,OT2e,TT2e)
last=[n for n in T2 if 'syl' in n][-1]
for nm,seq in [('D2',D2),('D2a',D2a),('D2b',D2b),('M2',M2),('M2a',M2a),('M2b',M2b)]:
    sp=[(float(n['t']),n['p']) for n in seq if n.get('split')]
    if sp: print('UNEXPECTED SPLIT',nm,sp)

VOICES=dict(D=(D1,D1a,D1b,D2,D2a,D2b),M=(M1,M1a,M1b,M2,M2a,M2b),T=(T1,T1a,T1b,T2,T2a,T2b))
