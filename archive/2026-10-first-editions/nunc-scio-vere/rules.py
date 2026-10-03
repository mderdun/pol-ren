"""Underlay rule checker. Works in vocal values = 2 x tablature/Perz values
(Perz quarter = minim, eighth = semiminim, sixteenth = fusa). Tactus on the semibreve (= Perz half)."""
import re, sys
from fractions import Fraction as F
import importlib, build_core as bc

STRESS = {  # word -> index of stressed syllable (0-based)
 'Nunc':0,'scio':0,'vere':0,'quia':0,'misit':0,'Dominus':0,'angelum':0,'suum':0,'et':0,'eripuit':1,
 'me':0,'de':0,'manu':0,'Herodis':1,'omni':0,'exspectatione':4,'plebis':0,'Iudaeorum':2,
 'Gloria':0,'Patri':0,'Filio':0,'Spiritui':0,'Sancto':0,'Sicut':0,'erat':0,'in':0,'principio':1,
 'nunc':0,'semper':0,'saecula':0,'saeculorum':2,'Amen':0,'amen':0,'a':0,'sicut':0}

def words(und, n):
    """group syllables into words: returns list of (word, [(onset_idx, syl)])"""
    out=[]; cur=[]
    for i in sorted(und):
        s=und[i]; cur.append((i,s.rstrip('-').strip(',.:;')))
        if not s.endswith('-'):
            out.append((''.join(x[1] for x in cur), cur)); cur=[]
    return out

def check(voice, sec, und, verbose=True):
    ev = bc.events(voice, sec)          # list of dicts: kind note/rest, onset idx, pos, dur, pitch, bar
    notes=[e for e in ev if e['kind']=='note']
    flags=[]
    def f(sev, e, msg): flags.append((sev, e['bar'], e['beat'], msg))
    syl_on = {i:und.get(i) for i in range(1,len(notes)+1)}
    # word membership: which syllable is 'current' at each note
    cur=None; curword_open=False
    for k,e in enumerate(ev):
        if e['kind']=='rest':
            if curword_open: f('STRONG', e, 'rest interrupts a word')
            e['after_rest']=True; continue
        i=e['idx']; s=syl_on.get(i)
        prev_note = notes[i-2] if i>1 else None
        # R5: new syllable on semiminim or shorter (vocal) = Perz < quarter
        if s and e['dur']<F(1,4): f('STRONG', e, f'syllable "{s}" on black note (semiminim or shorter)')
        # R6: first white note after a run of >=2 black notes takes a new syllable
        if s and e['dur']>=F(1,4) and i>=3:
            a,b=notes[i-2],notes[i-3]
            if a['dur']<F(1,4) and b['dur']<F(1,4) and not a.get('tiedfrom'):
                f('SOFT', e, f'new syllable "{s}" on first white note after black run (Vicentino/Stoquerus)')
        # R7: dotted minim + semiminim + next note
        if s and i>=3 and notes[i-2]['dur']<F(1,4) and notes[i-3]['dur']==F(3,8):
            f('SOFT', e, f'new syllable "{s}" on note after dotted-minim figure (Lanfranco V/Zarlino 5)')
        # R8: repeated pitch without new syllable
        if not s and prev_note and prev_note['pitch']==e['pitch'] and not k==0 and ev[k-1]['kind']=='note':
            f('SOFT', e, 'repeated note without syllable')
        # R9: first note after rest takes a syllable
        if not s and (k==0 or ev[k-1]['kind']=='rest'):
            f('STRONG', e, 'first note after rest without syllable')
        if s: curword_open = s.endswith('-')
    # R10 last note
    if len(notes) not in und: f('STRONG', notes[-1], 'last note without syllable')
    # accent: stressed syllable should not sit on a weaker metrical position AND shorter note than the next syllable of the word
    for w,syls in words(und, len(notes)):
        if len(syls)<2: continue
        key=w.strip(',.:;')
        st=STRESS.get(key)
        if st is None: f('INFO', notes[syls[0][0]-1], f'no stress entry for {key}'); continue
        sidx=syls[st][0]; e=notes[sidx-1]
        for j,(oi,sy) in enumerate(syls):
            if j==st: continue
            o=notes[oi-1]
            # weight: duration of syllable span
            def span(ix):
                pos=[jj for jj,(a,_) in enumerate(syls) if a==ix][0]
                end = syls[pos+1][0] if pos+1<len(syls) else None
                return e2 if False else None
            if (o['metric']>e['metric']) and (o['dur']>e['dur']) and abs(j-st)==1 and j!=len(syls)-1:
                f('SOFT', e, f'false accent? "{w}": stressed "{syls[st][1]}" ({e["dur"]}, m{e["metric"]}) weaker than "{sy}" ({o["dur"]}, m{o["metric"]})')
    if verbose:
        for x in flags: print(f'  {voice:7s} {sec} bar {x[1]:>2} beat {x[2]:<4} {x[0]:6s} {x[3]}')
    return flags
