from ..findings import Hit
from ..lyrics import division_problem, letters, words


def check(doc):
    if doc.lang != "la" or not doc.is_lily:
        return
    for w in words(doc.code):
        for i, expected in division_problem([s.text for s in w]):
            a, b = w[i - 1], w[i]
            found = f"{letters(a.text)}-{letters(b.text)}"
            word = "".join(letters(s.text) for s in w)
            yield Hit(key=f"{word}:{found}", offset=a.offset,
                      values={"found": found, "word": word, "expected": expected})
