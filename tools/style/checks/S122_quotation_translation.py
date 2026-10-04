import re

from ..findings import Hit
from ..sources import mask_env

FOREIGN = {
    "Latin": set("et est sunt cum ad per non quod qui quae quia ut sed ac atque enim de ex pro sub hanc hoc haec "
                 "suis suos nos vos ego tu sicut erat ipsam eius debent quando".split()),
    "Polish": set("się nie jest na do że jak od przez za ku dla gdy tak już nas was mnie wg".split()),
    "Italian": set("sono una della delle che di del si trasportano quando".split()),
    "German": set("und der die das ist mit von zu nicht ein eine auf für".split()),
}
ENGLISH = set("the of and to a is are was were for with that this it by on as be his her their from at an".split())


def _quotes(code: str):
    i = 0
    while True:
        a = code.find("‘", i)
        if a < 0:
            return
        j, depth = a + 1, 1
        while j < len(code) and depth:
            c = code[j]
            if c == "‘":
                depth += 1
            elif c == "’" and not (code[j - 1].isalpha() and j + 1 < len(code) and code[j + 1].isalpha()):
                depth -= 1
            j += 1
        yield a, j
        i = j


def check(doc):
    # titles in the literature and source lists are not translated (11.7)
    code = mask_env(doc.code, ("literature", "sigla", "textcols", "dipltextcols", "variants"))
    for a, b in _quotes(code):
        inner = code[a + 1:b - 1]
        if "‘" in inner or not inner.strip():
            continue
        if re.search(r"\w-\w", inner):
            continue          # underlay quoted syllable by syllable (au-di-ta est)
        ws = re.findall(r"[^\W\d_]+", re.sub(r"\\[A-Za-z]+", " ", inner).lower())
        if len(ws) < 4 or any(w in ENGLISH for w in ws):
            continue
        caps = sum(1 for w in re.findall(r"[^\W\d_]+", inner) if w[0].isupper())
        if caps >= 0.6 * len(ws):
            continue          # a name or a title in the source's form
        lang = next((n for n, fw in FOREIGN.items() if any(w in fw for w in ws)), None)
        if lang is None:
            continue
        after = code[b:b + 12]
        if re.match(r"[\s,.;:]*\(\s*‘", after) or re.match(r"[\s,.;:]*\\translation", after):
            continue
        # a translation before the quotation: (‘…’) just before, or 'that is' constructions are left alone
        if re.search(r"\(\s*$", code[max(0, a - 3):a]):
            continue
        quote = " ".join(inner.split())
        what = ("has its translation after a comma, not in parentheses" if re.match(r"[\s]*,\s*‘", after)
                else "has no translation after it")
        yield Hit(key=quote[:40], offset=a, values={"quote": quote[:60] + ("…" if len(quote) > 60 else ""),
                                                     "lang": lang, "what": what})
