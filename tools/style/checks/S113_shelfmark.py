import re

from ..editions import edition, parse_sigla
from ..findings import Hit

SHELF = re.compile(r"\b(?:MS|MSS|Ms|Mss|Rps|Mus|Cod|Inv|sygn|Sign|Mag|Podr|Hs|Sig)\b\.?[\w. ]{0,14}?\d|"
                   r"\bshelfmark\b|\b[A-Z][A-Za-z]{1,8}[ .]\d{2,}")


def check(doc):
    over = (doc.meta.get("sigla") if "sigla" in doc.meta
            else (edition(doc.slug).get("sigla") if doc.slug else None)) or {}
    for e in parse_sigla(doc.code):
        e = {**e, **(over.get(e["siglum"]) or {})}
        if e["kind"] != "source" or e["lost"] or re.match(r"\s*As above", e["text"]):
            continue
        if SHELF.search(e["text"]):
            continue
        yield Hit(key=e["siglum"], offset=e["offset"], values={"siglum": e["siglum"]})
