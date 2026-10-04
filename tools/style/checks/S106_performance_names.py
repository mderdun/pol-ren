import re

from ..findings import Hit

WORDS = re.compile(r"\b(recordings?|recorded|CDs?|discs?|albums?|Spotify|YouTube|CPDL|IMSLP|label)\b", re.I)
ENSEMBLE = re.compile(r"\b(?:[A-Z][\w’'-]+ )+(?:Ensemble|Consort|Singers|Scholars|Schola|Collegium|Cappella|Capella|"
                      r"Chapel|Choir|Chorus|Voices|Quartet|Orchestra|Baroque|Sixteen)\b(?: [A-Z][\w’'-]+)*")
NAMES = re.compile(r"\b(Tallis Scholars|Hilliard|Huelgas|Gothic Voices|Stile Antico|Sixteen|Tenebrae|King['’]s Singers|"
                   r"Accord|DUX|Naxos|Hyperion|Supraphon|Harmonia Mundi|notAmos|Marchesano|Perz|Spijker|Malinowski|"
                   r"Kosendiak|Gałoński|Rio)\b")
AS_DOES = re.compile(r"\bas (?:the )?([A-Z][\w’'-]+(?: [A-Z][\w’'-]+)*) (?:does|do|did|sings|sing|sang|has|have|had|"
                     r"prints|print|printed|gives|give|gave|takes|take|took|edits|edit|edited)\b")


def check(doc):
    code = doc.code
    for m in re.finditer(r"\\sig\{([^}]*)\}", code):
        yield Hit(key=f"sig:{m.group(1)}", offset=m.start(), values={"what": f"a siglum ({m.group(1)})"})
    prose = doc.prose
    seen = set()
    for pat, what in ((AS_DOES, "'as {0} does'"), (NAMES, "{0}"), (ENSEMBLE, "{0}"), (WORDS, "a {0}")):
        for m in pat.finditer(prose):
            if m.start() in seen:
                continue
            seen.add(m.start())
            txt = m.group(1) if m.groups() else m.group(0)
            yield Hit(key=txt.lower(), offset=m.start(), values={"what": what.format(txt)})
