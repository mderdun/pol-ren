import re

from ..findings import Hit
from ..sources import command_args

RANGE = r"\d+[a-z]?(?:(?:–|--)\d+[a-z]?)?"
BAR = re.compile(rf"^(?:text|{RANGE}(?:, {RANGE})*)?$")
VOICE1 = rf"[A-Z][a-z]?(?: {RANGE})?"
VOICE = re.compile(rf"^(?:all|{VOICE1}(?:, {VOICE1})*)?$")
NAMES = re.compile(r"\b(Cantus|Altus|Tenor|Bassus|Discantus|Medius|Superius|Quintus|Sextus|Vox)\b")


def check(doc):
    code = doc.code
    for start, args in command_args(code, "cn", 3, optional=False):
        bar = code[args[0][0]:args[0][1]].strip()
        voice = code[args[1][0]:args[1][1]].strip()
        where = f"{bar or '-'} | {voice or '-'}"
        if re.search(r"\d-\d", bar):
            yield Hit(key=f"{where}:hyphen", offset=start, values={"where": where, "what": "en dash in a range, not a hyphen"})
        elif not BAR.match(bar):
            yield Hit(key=f"{where}:bar", offset=start,
                      values={"where": where, "what": "the bar column takes bar numbers only (17, 17–18, 25, 31)"})
        if NAMES.search(voice):
            yield Hit(key=f"{where}:name", offset=start,
                      values={"where": where, "what": "voices are abbreviated in the voice column (C, A, T, B)"})
        elif re.search(r"\d-\d", voice):
            yield Hit(key=f"{where}:vhyphen", offset=start, values={"where": where, "what": "en dash in a range, not a hyphen"})
        elif not VOICE.match(voice):
            yield Hit(key=f"{where}:voice", offset=start,
                      values={"where": where, "what": "the voice column takes voice abbreviations (A, T; M 3; all)"})
