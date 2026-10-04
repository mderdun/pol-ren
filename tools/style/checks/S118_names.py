import re

from ..findings import Hit
from ..sources import command_args, mask_quotes

ASCII_FORMS = {"Derdun": "Derduń", "Zielenski": "Zieleński", "Waclaw": "Wacław", "Szamotul": "Szamotuł",
               "Grudziadza": "Grudziądza", "Mikolaj": "Mikołaj"}
LATIN = re.compile(r"\b(Venceslaus|Wenceslaus|Wenceslai|Vences\w*|Nicolaus|Nicolai|Petrus|Samotul\w*|Grudenc\w*|"
                   r"Wilhelmi|Zielenscius|Polonus)\b")


def check(doc):
    code = doc.code
    quoted = mask_quotes(code)
    for m in re.finditer(r"\b(" + "|".join(ASCII_FORMS) + r")\b", code):
        if quoted[m.start()] == " ":
            continue      # a source's own spelling, quoted
        yield Hit(key=m.group(1), offset=m.start(),
                  values={"what": f"'{m.group(1)}' without its diacritics; write '{ASCII_FORMS[m.group(1)]}'"})
    for cmd in ("composer", "shortcomposer"):
        for start, args in command_args(code, cmd, 1):
            name = code[args[0][0]:args[0][1]]
            mm = LATIN.search(name)
            if mm:
                yield Hit(key=f"{cmd}:{name}", offset=start,
                          values={"what": f"Latin form '{name}' in \\{cmd}; composers by their vernacular names (14.1)"})
