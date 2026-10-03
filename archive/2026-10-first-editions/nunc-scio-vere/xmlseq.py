import zipfile, re, sys
import xml.etree.ElementTree as ET
from fractions import Fraction as F
STEP={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
def parts(path):
    z=zipfile.ZipFile(path); name=[n for n in z.namelist() if (n.endswith('.xml') or n.endswith('.musicxml')) and 'META' not in n and 'container' not in n][0]
    root=ET.fromstring(z.read(name))
    out={}
    for p in root.findall('part'):
        div=None; ev=[]; backups=0
        for m in p.findall('measure'):
            a=m.find('attributes/divisions')
            if a is not None: div=int(a.text)
            for el in m:
                if el.tag=='backup': backups+=1
                if el.tag!='note': continue
                if el.find('chord') is not None: continue
                v=el.find('voice'); 
                if v is not None and v.text!='1': continue
                d=F(int(el.find('duration').text),div)
                if el.find('rest') is not None: ev.append((m.get('number'),d,None,None,None)); continue
                st=el.find('pitch/step').text; oc=int(el.find('pitch/octave').text)
                alt=el.find('pitch/alter'); alt=int(float(alt.text)) if alt is not None else 0
                midi=12*(oc+1)+STEP[st]+alt
                ly=[(l.get('number','1'),l.findtext('text'),l.findtext('syllabic')) for l in el.findall('lyric')]
                ties=[t.get('type') for t in el.findall('tie')]
                ev.append((m.get('number'),d,midi,ly,ties))
        out[p.get('id')]=(ev,backups)
    return out
if __name__=='__main__':
    for pid,(ev,b) in parts(sys.argv[1]).items():
        print(pid,'events',len(ev),'backups',b)
