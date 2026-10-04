import re

from ..colours import from_unit, hexstr, name_of
from ..findings import Hit

DEF = re.compile(r"\\definecolor\{([^}]*)\}\{([^}]*)\}\{([^}]*)\}")
USE = re.compile(r"\\(?:textcolor|color|colorbox|pagecolor)\s*(?:\[[^\]]*\])?\{([^}]*)\}")
RGB = re.compile(r"\(rgb-color\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\)")
X11 = re.compile(r"x11-color\s+['\"]?([A-Za-z]+)")
NAMED = re.compile(r"(?:\\with-color|color\s*=?)\s*#'?([a-z][a-z-]*)\b")


def _rgb255(model: str, spec: str):
    model = model.strip()
    vals = [v.strip() for v in spec.split(",")]
    try:
        if model == "RGB":
            return tuple(int(float(v)) for v in vals[:3])
        if model == "HTML":
            return tuple(int(spec.strip()[i:i + 2], 16) for i in (0, 2, 4))
        if model in ("rgb", "gray", "cmyk"):
            return from_unit(float(v) for v in vals)
    except ValueError:
        return None
    return None


def check(doc):
    code = doc.code
    defined = {"black", "white", "rubric"}
    for m in DEF.finditer(code):
        rgb = _rgb255(m.group(2), m.group(3))
        if rgb is None or name_of(rgb) is None:
            col = hexstr(rgb) if rgb else f"{m.group(2)} {m.group(3)}"
            yield Hit(key=f"define:{m.group(1)}", offset=m.start(), values={"colour": f"{m.group(1)} = {col}"})
        else:
            defined.add(m.group(1))
    for m in USE.finditer(code):
        name = m.group(1).strip()
        if name not in defined:
            yield Hit(key=f"use:{name}", offset=m.start(), values={"colour": name})
    for m in RGB.finditer(code):
        rgb = from_unit(m.groups())
        if name_of(rgb) is None:
            yield Hit(key=f"rgb:{hexstr(rgb)}", offset=m.start(), values={"colour": hexstr(rgb)})
    for m in X11.finditer(code):
        if m.group(1).lower() not in ("black", "white"):
            yield Hit(key=f"x11:{m.group(1)}", offset=m.start(), values={"colour": m.group(1)})
    for m in NAMED.finditer(code):
        name = m.group(1)
        if name in ("rgb-color", "x11-color", "black", "white") or name.startswith("("):
            continue
        yield Hit(key=f"named:{name}", offset=m.start(), values={"colour": name})
