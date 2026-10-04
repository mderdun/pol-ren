import re

from ..findings import Hit

SCORE = re.compile(r"\\(lilypondfile|gregorioscore|lilypond)\b")


def check(doc):
    code = doc.code
    for m in re.finditer(r"\\pagenote\b", code):
        yield Hit(key="pagenote", offset=m.start(), values={"what": "\\pagenote"})
    for m in re.finditer(r"\\musicnote\b", code):
        before = code[max(0, m.start() - 300):m.start()]
        # the last command before the note: a score means the note sits on its page
        last = list(re.finditer(r"\\(lilypondfile|gregorioscore|includegraphics|section|opensection|scorehead)\b",
                                before))
        if last and SCORE.match(last[-1].group(0)):
            yield Hit(key="musicnote", offset=m.start(), values={"what": "\\musicnote after the score"})
