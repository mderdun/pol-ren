import re

from ..editions import sigla
from ..findings import Hit

PRESENT = set("""has have reads gives give prints print shows show lacks lack omits omit sets places writes is are
contains contain puts put agrees agree differs differ ends begins keeps keep adds add notes names calls marks mark
sharpens sharpen spells spell transmits preserves preserve survives survive""".split())
PAST = set("""had gave showed lacked omitted wrote was were contained agreed differed ended began kept added
named called marked sharpened spelled transmitted preserved survived""".split())
SUBJ = re.compile(r"\\sig\{([^}]*)\}((?:\s*(?:,|and|or)\s*\\sig\{[^}]*\})*)\s+(?:also\s+|still\s+|only\s+|alone\s+|"
                  r"itself\s+|too\s+)?([a-z]+)\b(\s+[a-z]+)?")
PARTICIPLE = re.compile(r"\s+(\w+ed|chosen|made|given|written|taken|known|seen|done|set|read|sung|shown|drawn|kept|left|"
                        r"put|found|held|brought|thought|meant|lost|destroyed|described|collated)$")


def check(doc):
    known = doc.meta.get("sigla") or (sigla(doc.slug) if doc.slug else {})
    if not known:
        return
    for m in SUBJ.finditer(doc.code):
        names = [m.group(1)] + re.findall(r"\\sig\{([^}]*)\}", m.group(2) or "")
        verb = m.group(3)
        if verb in ("is", "are", "was", "were") and m.group(4) and PARTICIPLE.match(m.group(4)):
            continue          # a passive: what the edition does with the source ('M was chosen')
        states = {bool((known.get(s) or {}).get("lost")) for s in names if s in known}
        if len(states) > 1:
            continue          # a list of lost and extant sources
        for sig in names:
            e = known.get(sig)
            if e is None:
                continue
            lost = bool(e.get("lost"))
            if lost and verb in PRESENT:
                tense, state = "past", "lost"
            elif not lost and verb in PAST:
                tense, state = "present", "extant"
            else:
                continue
            phrase = " ".join(re.sub(r"\\sig\{([^}]*)\}", r"\1", m.group(0)[:m.end(3) - m.start()]).split())
            yield Hit(key=f"{sig}:{verb}", offset=m.start(),
                      values={"phrase": phrase, "siglum": sig, "state": state, "tense": tense})
            break
