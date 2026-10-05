import re

from ..findings import Hit

IPA = re.compile(r"[ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑ]"
                 r"|\[x\]|/[a-z]{1,3}/")


def check(doc):
    code = doc.code
    for m in re.finditer(r"\\ipa\{([^}]*)\}", code):
        yield Hit(key=f"ipa:{m.group(1)}", offset=m.start(), values={"found": m.group(0)})
    prose = doc.prose
    for m in IPA.finditer(prose):
        if m.group(0).startswith("/") and doc.is_tex:
            continue          # slashes are too common in prose to call IPA
        yield Hit(key=m.group(0), offset=m.start(), values={"found": m.group(0)})
