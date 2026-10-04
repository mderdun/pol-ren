import re

from ..findings import Hit
from ..sources import command_args

CAUSE = re.compile(r"\b(errors?|erroneous|mis\w+|slips?|slipped|cop(?:y|ied|ying|yist)|scribes?|engravers?|printers?|"
                   r"compositor|typesetter|dittograph\w*|haplograph\w*|eye-skip|skipp?ed|transpos\w*|wrong\w*|"
                   r"mistak\w*|omit\w*|omission|transcri\w*|arose|arise[sn]?|confus\w*|displac\w*|shift\w*|"
                   r"duplicat\w*|read as|taken for|instead of|came from|comes from)\b", re.I)


def check(doc):
    code = doc.code
    for start, args in command_args(code, "cn", 3, optional=False):
        body = code[args[2][0]:args[2][1]]
        if not re.match(r"\s*Emended\b", body):
            continue
        if CAUSE.search(body):
            continue
        bar = code[args[0][0]:args[0][1]].strip()
        voice = code[args[1][0]:args[1][1]].strip()
        where = f"{bar} | {voice}"
        yield Hit(key=where, offset=start, values={"where": where})
