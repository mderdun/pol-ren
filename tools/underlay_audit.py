#!/usr/bin/env python3
"""Underlay audit: read an edition's MusicXML (make musicxml) and list what
the series rules (docs/editorial-principles.md, section 10) would question.

    tools/underlay_audit.py editions/<slug>/pdf/<slug>.musicxml [--verbose]

Firm rules (10.1-10.5) are reported as BREAK. The tendencies of 10.6 are
reported as LOOK: places to sing through and judge, not errors.

  BREAK  syllable on a note shorter than a minim, unless it follows a dotted
         minim; the note after such a semiminim without a syllable; first
         note after a rest without a syllable; a rest inside a word.
  LOOK light-on-beat   a light word (et, in, de ...) starting on the bar or
                       half-bar inside a moving figure (minims or shorter),
                       where it could sit off the beat and lead in.
  LOOK stress-short    a stressed syllable on a shorter note than the
                       unstressed syllable after it in the same word.
  LOOK after-run       a new syllable on the white note straight after a run of
                       short notes, where it could come before the run
                       (Lanfranco VI; Vicentino: the second white note).
  LOOK run-light       a run of 4+ notes on a light word.
  LOOK run-unstressed  a run of 6+ notes on an unstressed, non-final
                       syllable of a word with a known stress.
Durations are in semiminims (1 = semiminim, 2 = minim, 4 = semibreve).
Values are those printed; a bar is a breve (8) unless the score says otherwise.
"""
import sys, re, xml.etree.ElementTree as ET
from fractions import Fraction as F

LIGHT = set('et in de ad a ab cum per pro sub ex e nec sed ut qui quae quod te me se nos vos '
            'i w z na do o od u ku że by się'.split())
# Stressed syllable (0-based) of words in the series' Latin texts (principles 10.8)
STRESS = {'scio':0,'vere':0,'quia':0,'misit':0,'dominus':0,'angelum':0,'suum':0,'eripuit':1,
 'manu':0,'herodis':1,'omni':0,'exspectatione':4,'plebis':0,'iudaeorum':2,'gloria':0,'patri':0,
 'filio':0,'spiritui':0,'sancto':0,'sicut':0,'erat':0,'principio':1,'semper':0,'saecula':0,
 'saeculorum':2,'amen':0,'rama':0,'audita':1,'ploratus':1,'ululatus':2,'rachel':0,'plorans':0,
 'filios':0,'suos':0,'noluit':0,'consolari':2,'plaude':0,'euge':0,'theotocos':2,'regina':1,
 'virginum':0,'salus':0,'hominum':0,'confidencium':2,'laudantes':1,'inspice':0,'miseros':0,
 'despice':0,'misericordie':3,'oculis':0,'respice':0}
HIGH = ('cantus', 'discantus', 'superius', 'soprano')
LOW = ('bassus', 'bass')

def vowel(syl):
    s = syl.lower().replace('ae', 'e').replace('oe', 'e')
    v = [c for c in s if c in 'aeiouyąęó']
    return v[-1] if v else ''

def load(path):
    r = ET.parse(path).getroot()
    names = {p.get('id'): p.findtext('part-name') for p in r.iter('score-part')}
    parts = {}
    for p in r.findall('part'):
        div, t, beats, evs = 1, F(0), F(8), []
        for m in p.findall('measure'):
            mstart = t
            num = int(''.join(c for c in (m.get('number') or '0') if c.isdigit()) or 0)
            for el in m:
                if el.tag == 'attributes':
                    if el.findtext('divisions'): div = int(el.findtext('divisions'))
                    if el.find('time') is not None and el.findtext('time/beats'):
                        beats = F(int(el.findtext('time/beats')) * 4, int(el.findtext('time/beat-type')))
                if el.tag == 'backup': t -= F(int(el.findtext('duration')), div)
                if el.tag == 'forward': t += F(int(el.findtext('duration')), div)
                if el.tag != 'note' or el.find('chord') is not None or el.find('grace') is not None:
                    continue
                d = F(int(el.findtext('duration') or 0), div)
                rest = el.find('rest') is not None
                tie = [x.get('type') for x in el.findall('tie')]
                ly = {l.get('number'): (l.findtext('text') or '', l.findtext('syllabic'))
                      for l in el.findall('lyric')}
                pitch = None if rest else el.findtext('pitch/step') + el.findtext('pitch/octave')
                evs.append(dict(t=t, pos=t - mstart, bar=num, d=d, rest=rest, tie=tie, ly=ly, p=pitch, blen=beats))
                t += d
        merged = []
        for e in evs:
            if merged and not e['rest'] and 'stop' in e['tie'] and not merged[-1]['rest']:
                merged[-1]['d'] += e['d']
                for k, v in e['ly'].items(): merged[-1]['ly'].setdefault(k, v)
            else:
                merged.append(e)
        parts[names[p.get('id')]] = merged
    return parts

def audit(path):
    out = []
    for voice, evs in load(path).items():
        if 'chant' in voice.lower() or 'versus' in voice.lower():
            continue
        reg = 'high' if voice.lower() in HIGH else 'low' if voice.lower() in LOW else 'mid'
        verses = sorted({k for e in evs for k in e['ly']})
        for n in verses:
            started = False
            # syllable groups: (syllable, syllabic, [notes])
            groups, cur = [], None
            prev = None
            for i, e in enumerate(evs):
                if e['rest']:
                    if cur and cur[1] in ('begin', 'middle'):
                        out.append(('BREAK', voice, n, e['bar'], f"rest inside a word ('{cur[0]}')"))
                    prev = e; continue
                if n in e['ly']:
                    started = True
                    txt, syl = e['ly'][n]
                    if e['d'] < 2 and not (prev and not prev['rest'] and prev['d'] == 3) and not (prev is None or prev['rest']):
                        out.append(('BREAK', voice, n, e['bar'], f"'{txt}' on a note shorter than a minim"))
                    if e['d'] == 1 and prev and not prev['rest'] and prev['d'] == 3:
                        nx = evs[i + 1] if i + 1 < len(evs) else None
                        if nx and not nx['rest'] and n not in nx['ly']:
                            out.append(('BREAK', voice, n, e['bar'], f"'{txt}' on the semiminim, but no syllable on the note after it"))
                    # the white note straight after a run of shorter notes (Lanfranco VI, Vicentino)
                    if i >= 3 and e['d'] >= 2 and txt[-1:] not in ',.:;' and syl in ('begin', 'middle', 'single'):
                        j = i
                        while j > 0 and not evs[j-1]['rest'] and evs[j-1]['d'] < 2 and n not in evs[j-1]['ly']:
                            j -= 1
                        run = i - j
                        before = evs[j-1] if j > 0 else None
                        if run >= 2 and before and not before['rest'] and before['d'] >= 2 and n not in before['ly'] \
                                and cur and cur[2][0] is not before:
                            out.append(('LOOK', voice, n, e['bar'], f"after-run: '{txt}' straight after {run} short notes; the white note before them is free"))
                    cur = [txt, syl, [e]]; groups.append(cur)
                else:
                    if started and prev is not None and prev['rest']:
                        # only if this voice-verse has text around here
                        if any(n in x['ly'] for x in evs[i:i + 12]):
                            out.append(('BREAK', voice, n, e['bar'], 'no syllable on the first note after a rest'))
                    if cur: cur[2].append(e)
                prev = e
            # words
            words, w = [], []
            for g in groups:
                if g[1] in ('begin', 'single') and w: words.append(w); w = []
                w.append(g)
                if g[1] in ('end', 'single'): words.append(w); w = []
            if w: words.append(w)
            for w in words:
                word = ''.join(g[0] for g in w).lower()
                word = re.sub(r"[^a-ząćęłńóśźż]", '', word)
                st = STRESS.get(word)
                for k, (txt, syl, notes) in enumerate(w):
                    first = notes[0]; nn = len(notes)
                    if nn > 30: continue   # the last syllable of a section reaching into the next one
                    on_beat = first['pos'] % 4 == 0
                    if len(w) == 1 and word in LIGHT:
                        nbr = [x for x in notes] + [first]
                        if on_beat and first['d'] <= 2 and nn <= 2:
                            out.append(('LOOK', voice, n, first['bar'], f"light-on-beat: '{txt}' on the {'bar' if first['pos'] == 0 else 'half-bar'}, {['','semiminim','minim'][int(first['d'])] if first['d'] <= 2 else ''}"))
                        if nn >= 4:
                            out.append(('LOOK', voice, n, first['bar'], f"run-light: '{txt}' over {nn} notes"))
                    v = vowel(txt)
                    if st is not None and len(w) > 1:
                        if k == st and k + 1 < len(w) - 1:   # a word-final syllable belongs on the cadence note (10.3)
                            nxt = w[k + 1][2][0]
                            if first['d'] < nxt['d'] and not on_beat:
                                out.append(('LOOK', voice, n, first['bar'], f"stress-short: '{txt}' ({word}) shorter and weaker than the syllable after it"))
                        if k != st and k != len(w) - 1 and nn >= 6:
                            out.append(('LOOK', voice, n, first['bar'], f"run-unstressed: {nn} notes on '{txt}' of {word} (stress on syllable {st + 1}; vowel {v})"))
    return out

if __name__ == '__main__':
    res = audit(sys.argv[1])
    order = {'BREAK': 0, 'LOOK': 1}
    res.sort(key=lambda r: (order[r[0]], r[1], r[2], r[3]))
    for kind, voice, n, bar, msg in res:
        print(f"{kind:5} {voice:9} v{n} bar {bar:<3} {msg}")
    print(f"-- {sum(1 for r in res if r[0]=='BREAK')} breaks, {sum(1 for r in res if r[0]=='LOOK')} places to look at")
