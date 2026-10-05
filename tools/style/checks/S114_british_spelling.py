import re

from ..findings import Hit

KEEP_IZE = {"size", "sizes", "sized", "prize", "prizes", "prized", "seize", "seized", "seizes", "seizing", "maize",
            "capsize", "baize", "assize", "assizes", "downsize"}
WORDS = {
    "color": "colour", "colors": "colours", "colored": "coloured",
    "honor": "honour", "favor": "favour", "favorite": "favourite", "behavior": "behaviour", "labor": "labour",
    "neighbor": "neighbour", "harbor": "harbour", "humor": "humour", "vigor": "vigour", "rumor": "rumour",
    "center": "centre", "centers": "centres", "centered": "centred", "meter": "metre", "meters": "metres",
    "theater": "theatre", "fiber": "fibre", "caliber": "calibre", "somber": "sombre",
    "catalog": "catalogue", "catalogs": "catalogues", "cataloged": "catalogued", "analog": "analogue",
    "dialog": "dialogue", "gray": "grey", "traveled": "travelled", "traveling": "travelling",
    "modeled": "modelled", "modeling": "modelling", "labeled": "labelled", "labeling": "labelling",
    "canceled": "cancelled", "signaled": "signalled", "fulfill": "fulfil", "skillful": "skilful",
    "defense": "defence", "offense": "offence", "toward": "towards", "mold": "mould", "molded": "moulded",
    "enroll": "enrol", "willful": "wilful", "aging": "ageing", "artifact": "artefact", "plow": "plough",
}


def check(doc):
    prose = doc.prose
    for m in re.finditer(r"\b[A-Za-z]+\b", prose):
        w = m.group(0)
        if m.start() and prose[m.start() - 1] in "\\@":
            continue                  # a TeX command (\normalsize)
        lw = w.lower()
        uk = None
        if lw in WORDS:
            uk = WORDS[lw]
        else:
            mm = re.fullmatch(r"([a-z]+?)iz(e|es|ed|ing|ation|ations|er|ers)", lw)
            if mm and lw not in KEEP_IZE and len(mm.group(1)) >= 2:
                uk = mm.group(1) + "is" + mm.group(2)
        if uk:
            yield Hit(key=lw, offset=m.start(), values={"word": w, "uk": uk})
