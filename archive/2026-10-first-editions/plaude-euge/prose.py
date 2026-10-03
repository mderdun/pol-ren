import re
def esc(s): return s.replace('\\','\\\\').replace('"','\\"')
SPECIAL={'{fl}':'\\fl','{na}':'\\na','{sh}':'\\sh'}
def word(w, it):
    # returns (markup, italic_state_after)
    parts=re.split(r'(\{fl\}|\{na\}|\{sh\}|\*)',w)
    segs=[]; 
    for p in parts:
        if p=='': continue
        if p=='*': it=not it; continue
        if p in SPECIAL: segs.append(SPECIAL[p]); continue
        q=f'"{esc(p)}"'
        segs.append(f'\\italic {q}' if it else q)
    if not segs: return None,it
    if len(segs)==1: return segs[0],it
    return '\\concat { '+' '.join(segs)+' }',it
def para(text, cmd='\\justify'):
    it=False; out=[]
    for w in text.split():
        m,it=word(w,it)
        if m: out.append(m)
    return f'{cmd} {{ {" ".join(out)} }}'
def heading(t, size=2):
    return f'\\fontsize #{size} "{esc(t)}"'
def block(head, paras, size=1):
    items=[]
    if head: items.append(heading(head,size))
    items.append('\\vspace #0.3' if head else '')
    first=para(paras[0])
    col=f"\\column {{ {heading(head,size) if head else ''} \\vspace #0.2 {first} }}"
    rest=[para(p) for p in paras[1:]]
    return [col]+rest
