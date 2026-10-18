"""Render code / terminal 'screenshots' that look like they were taken on a PC."""
from PIL import Image, ImageDraw, ImageFont
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.token import Token

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
S = 2  # supersampling for crisp output

# VS Code "Dark+" like palette
EDITOR = {
    "bg": (30, 30, 30), "gutter": (30, 30, 30), "ln": (110, 118, 129),
    "title": (50, 50, 52), "tab": (30, 30, 30), "tabbar": (37, 37, 38),
    "status": (0, 122, 204), "fg": (212, 212, 212),
}
TOK = [
    (Token.Comment, (106, 153, 85)),
    (Token.Literal.String.Doc, (106, 153, 85)),
    (Token.Literal.String, (206, 145, 120)),
    (Token.Literal.Number, (181, 206, 168)),
    (Token.Keyword, (86, 156, 214)),
    (Token.Name.Builtin, (78, 201, 176)),
    (Token.Name.Function, (220, 220, 170)),
    (Token.Name.Class, (78, 201, 176)),
    (Token.Name.Namespace, (78, 201, 176)),
    (Token.Operator.Word, (86, 156, 214)),
    (Token.Name, (156, 220, 254)),
]


def color_for(ttype):
    for t, c in TOK:
        if ttype in t:
            return c
    return EDITOR["fg"]


def _font(path, size):
    return ImageFont.truetype(path, size * S)


def editor_shot(code, filename, out, first_line=1, size=13, width_chars=None,
                highlight=()):
    f = _font(MONO, size)
    ui = _font(SANS, 11)
    lines = code.rstrip("\n").split("\n")
    cw = f.getlength("M")
    lh = int(size * 1.55 * S)
    width_chars = width_chars or max(len(l) for l in lines) + 2
    gutter = int(cw * (len(str(first_line + len(lines))) + 3))
    W = int(gutter + cw * width_chars + 20 * S)
    title_h, tab_h, stat_h = 30 * S, 30 * S, 22 * S
    H = title_h + tab_h + lh * len(lines) + 16 * S + stat_h
    img = Image.new("RGB", (W, H), EDITOR["bg"])
    d = ImageDraw.Draw(img)
    # title bar
    d.rectangle([0, 0, W, title_h], fill=EDITOR["title"])
    d.text((W // 2, title_h // 2), f"{filename} - static-analysis-lab - Visual Studio Code",
           font=ui, fill=(204, 204, 204), anchor="mm")
    for i, sym in enumerate(["✕", "□", "—"]):
        d.text((W - (i * 2 + 1) * 22 * S, title_h // 2), sym, font=ui,
               fill=(204, 204, 204), anchor="mm")
    # tab bar
    d.rectangle([0, title_h, W, title_h + tab_h], fill=EDITOR["tabbar"])
    tw = int(ui.getlength(filename) + 50 * S)
    d.rectangle([0, title_h, tw, title_h + tab_h], fill=EDITOR["tab"])
    d.line([0, title_h, tw, title_h], fill=EDITOR["status"], width=2 * S)
    d.text((14 * S, title_h + tab_h // 2), "py", font=_font(MONO_B, 9),
           fill=(255, 202, 40), anchor="lm")
    d.text((34 * S, title_h + tab_h // 2), filename, font=ui, fill=(255, 255, 255), anchor="lm")
    # code
    y0 = title_h + tab_h + 8 * S
    for idx in highlight:
        y = y0 + (idx - first_line) * lh
        d.rectangle([0, y, W, y + lh], fill=(58, 45, 45))
    for i in range(len(lines)):
        d.text((gutter - cw * 1.5, y0 + i * lh), str(first_line + i), font=f,
               fill=EDITOR["ln"], anchor="ra")
    x, row = gutter, 0
    for ttype, val in lex(code.rstrip("\n") + "\n", PythonLexer()):
        parts = val.split("\n")
        for j, p in enumerate(parts):
            if j:
                row += 1
                x = gutter
            if p:
                d.text((x, y0 + row * lh), p, font=f, fill=color_for(ttype))
                x += f.getlength(p)
    # status bar
    d.rectangle([0, H - stat_h, W, H], fill=EDITOR["status"])
    d.text((10 * S, H - stat_h // 2), "⎇ main   ⊗ 0  ⚠ 0", font=ui, fill="white", anchor="lm")
    d.text((W - 10 * S, H - stat_h // 2), "Ln 1, Col 1   Spaces: 4   UTF-8   LF   Python 3.13",
           font=ui, fill="white", anchor="rm")
    img.save(out)
    return out


def terminal_shot(text, out, title="kali@kali: ~/static-analysis-lab", size=12, width_chars=None):
    """Kali/QTerminal-like dark terminal. Lines starting with '$ ' are prompts."""
    f = _font(MONO, size)
    fb = _font(MONO_B, size)
    ui = _font(SANS, 11)
    lines = text.expandtabs(4).rstrip("\n").split("\n")
    cw = f.getlength("M")
    lh = int(size * 1.45 * S)
    width_chars = width_chars or max(len(l) for l in lines) + 4
    W = int(cw * width_chars + 24 * S)
    title_h, menu_h = 28 * S, 24 * S
    rows = sum(2 if l.startswith("$ ") else 1 for l in lines)
    H = title_h + menu_h + lh * rows + 20 * S
    img = Image.new("RGB", (W, H), (22, 25, 31))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, title_h], fill=(40, 44, 52))
    d.text((W // 2, title_h // 2), title, font=_font(SANS, 11), fill=(220, 220, 220), anchor="mm")
    for i, c in enumerate([(73, 125, 255), (90, 90, 90), (90, 90, 90)]):
        cx = W - (14 + i * 22) * S
        d.ellipse([cx - 7 * S, title_h // 2 - 7 * S, cx + 7 * S, title_h // 2 + 7 * S], fill=c)
    d.rectangle([0, title_h, W, title_h + menu_h], fill=(30, 33, 40))
    d.text((12 * S, title_h + menu_h // 2), "Session   Actions   Edit   View   Help", font=ui,
           fill=(200, 200, 200), anchor="lm")
    y = title_h + menu_h + 10 * S
    x0 = 12 * S
    blue, green, red = (52, 120, 230), (80, 220, 100), (255, 85, 85)
    for l in lines:
        if l.startswith("$ "):
            seg = [("┌──(", blue, f), ("kali@kali", red, fb), (")-[", blue, f),
                   ("~/static-analysis-lab", (230, 230, 230), fb), ("]", blue, f)]
            x = x0
            for s, c, ff in seg:
                d.text((x, y), s, font=ff, fill=c)
                x += ff.getlength(s)
            y += lh
            x = x0
            d.text((x, y), "└─", font=f, fill=blue); x += f.getlength("└─")
            d.text((x, y), "$ ", font=fb, fill=blue); x += fb.getlength("$ ")
            d.text((x, y), l[2:], font=fb, fill=green)
        else:
            col = (220, 220, 220)
            if "Severity: High" in l or "Error" in l.split("input")[0]:
                col = (255, 120, 120)
            if "No issues" in l or "No crashes" in l or "10.00/10" in l:
                col = green
            d.text((x0, y), l, font=f, fill=col)
        y += lh
    img.save(out)
    return out
