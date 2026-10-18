"""Build Security_Testing_Report.pdf (run make_shots.py first)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Flowable,
                                Table, TableStyle, PageBreak, KeepTogether, NextPageTemplate,
                                CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage

# ------------------------------------------------------------------ fonts
CX = "/usr/share/fonts/truetype/crosextra/"
DJ = "/usr/share/fonts/truetype/dejavu/"
for name, file in [("Serif", "Caladea-Regular"), ("Serif-B", "Caladea-Bold"),
                   ("Serif-I", "Caladea-Italic"), ("Serif-BI", "Caladea-BoldItalic"),
                   ("Sans", "Carlito-Regular"), ("Sans-B", "Carlito-Bold"),
                   ("Sans-I", "Carlito-Italic"), ("Sans-BI", "Carlito-BoldItalic")]:
    pdfmetrics.registerFont(TTFont(name, CX + file + ".ttf"))
pdfmetrics.registerFont(TTFont("Mono", DJ + "DejaVuSansMono.ttf"))
pdfmetrics.registerFont(TTFont("Mono-B", DJ + "DejaVuSansMono-Bold.ttf"))
for fam in ("Serif", "Sans"):
    addMapping(fam, 0, 0, fam)
    addMapping(fam, 1, 0, fam + "-B")
    addMapping(fam, 0, 1, fam + "-I")
    addMapping(fam, 1, 1, fam + "-BI")
addMapping("Mono", 0, 0, "Mono")
addMapping("Mono", 1, 0, "Mono-B")
addMapping("Mono", 0, 1, "Mono")
addMapping("Mono", 1, 1, "Mono-B")

# ------------------------------------------------------------------ palette
INK = colors.HexColor("#12202F")
INK2 = colors.HexColor("#1B2E44")
AMBER = colors.HexColor("#E08A2C")
TEAL = colors.HexColor("#2B7A78")
RED = colors.HexColor("#B23A3A")
GREEN = colors.HexColor("#2E7D4F")
TINT = colors.HexColor("#F6F2EA")
ZEBRA = colors.HexColor("#FAF8F4")
RULE = colors.HexColor("#D9D4CA")
MUTED = colors.HexColor("#6B7380")

PAGE_W, PAGE_H = A4
MARGIN = 2 * cm
W = PAGE_W - 2 * MARGIN
IMG = "img/"

TEAM = [("Abdelrahman Ahmed Abdelhamied", "2406244656"),
        ("Mahmoud Osama Elsayed", "2406241599"),
        ("Omar Muhammad Muhammed", "2406241065")]

# ------------------------------------------------------------------ styles
body = ParagraphStyle("body", fontName="Serif", fontSize=10.8, leading=16, alignment=TA_JUSTIFY,
                      textColor=colors.HexColor("#222831"), spaceAfter=7)
lead = ParagraphStyle("lead", parent=body, fontSize=12, leading=17.5, textColor=INK2, spaceAfter=10)
h2 = ParagraphStyle("h2", fontName="Sans-B", fontSize=13, leading=16, textColor=INK,
                    spaceBefore=10, spaceAfter=6)
cap = ParagraphStyle("cap", fontName="Sans", fontSize=9, leading=12, textColor=MUTED,
                     alignment=TA_LEFT, spaceBefore=5, spaceAfter=14)
cell = ParagraphStyle("cell", fontName="Sans", fontSize=9.3, leading=11.8, textColor=colors.HexColor("#222831"))
cellh = ParagraphStyle("cellh", parent=cell, fontName="Sans-B", textColor=colors.white)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=2, spaceAfter=4)
callout_s = ParagraphStyle("callout", parent=body, fontName="Serif", fontSize=10.5, leading=15.5,
                           textColor=INK2, spaceAfter=0)


def code(t):
    return f"<font name='Mono' size='9' color='#8A3B12'>{t}</font>"


def P(t, s=body):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, bullet, bulletText="▪") for i in items]


# ------------------------------------------------------------------ flowables
class SectionHeader(Flowable):
    """Big amber section number + title, registered in the table of contents."""

    def __init__(self, num, title):
        super().__init__()
        self.num, self.title = num, title
        self.key = f"sec{num}"

    def wrap(self, aw, ah):
        return aw, 2.3 * cm

    def draw(self):
        c = self.canv
        c.setFillColor(AMBER)
        c.setFont("Serif-B", 40)
        c.drawString(0, 0.75 * cm, f"{self.num:02d}")
        c.setFillColor(INK)
        c.setFont("Serif-B", 22)
        c.drawString(2.15 * cm, 0.95 * cm, self.title)
        c.setStrokeColor(AMBER)
        c.setLineWidth(2)
        c.line(0, 0.35 * cm, 1.6 * cm, 0.35 * cm)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        c.line(1.6 * cm, 0.35 * cm, W, 0.35 * cm)
        c.bookmarkPage(self.key)
        c.addOutlineEntry(f"{self.num}. {self.title}", self.key, 0)


class Figure(Flowable):
    """Screenshot with a soft drop shadow and a thin frame."""

    def __init__(self, path, width=W, max_h=None):
        super().__init__()
        self.path = path
        w, h = PILImage.open(path).size
        self.w = width - 4
        self.h = self.w * h / w
        if max_h and self.h > max_h:
            self.h = max_h
            self.w = self.h * w / h

    def wrap(self, aw, ah):
        return W, self.h + 4

    def draw(self):
        c = self.canv
        x = (W - self.w) / 2
        c.saveState()
        for i, a in enumerate([0.05, 0.07, 0.09]):
            c.setFillColor(colors.Color(0, 0, 0, alpha=a))
            o = 3 - i
            c.roundRect(x + o, -o + 2, self.w, self.h, 3, stroke=0, fill=1)
        c.restoreState()
        c.drawImage(self.path, x, 2, self.w, self.h)
        c.setStrokeColor(colors.HexColor("#3A3F47"))
        c.setLineWidth(0.5)
        c.rect(x, 2, self.w, self.h, stroke=1, fill=0)


fig_no = [0]


def figure(path, text, max_h=21.5 * cm, width=W):
    fig_no[0] += 1
    return KeepTogether([Figure(path, width, max_h),
                         Paragraph(f"<font name='Sans-B' color='#E08A2C'>FIGURE {fig_no[0]}</font>"
                                   f"&nbsp;&nbsp;{text}", cap)])


def callout(text, title=None, color=AMBER):
    inner = []
    if title:
        inner.append(Paragraph(f"<font name='Sans-B' size='9' color='#{color.hexval()[2:]}'>"
                               f"{title.upper()}</font>", ParagraphStyle("ct", parent=cell, spaceAfter=3)))
    inner.append(Paragraph(text, callout_s))
    t = Table([[inner]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, color),
                           ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                           ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 11)]))
    return KeepTogether([Spacer(1, 4), t, Spacer(1, 12)])


def table(rows, widths, align_top=False):
    data = [[Paragraph(str(c), cellh if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[W * w for w in widths], repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), INK),
          ("LINEBELOW", (0, 1), (-1, -1), 0.5, RULE),
          ("VALIGN", (0, 0), (-1, -1), "TOP" if align_top else "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7)]
    st += [("BACKGROUND", (0, i), (-1, i), ZEBRA) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return KeepTogether([t, Spacer(1, 12)])


class Pipeline(Flowable):
    """Build -> Fuzz -> Static -> Fix -> Re-test process strip."""
    STEPS = [("1", "Build", "student_app.py"), ("2", "Fuzz", "20,000 random inputs"),
             ("3", "Static analysis", "Bandit + Pylint"), ("4", "Fix", "student_app_fixed.py"),
             ("5", "Re-test", "same seed, same tools")]

    def wrap(self, aw, ah):
        return W, 2.3 * cm

    def draw(self):
        c = self.canv
        n = len(self.STEPS)
        gap = 0.45 * cm
        bw = (W - gap * (n - 1)) / n
        for i, (num, t, sub) in enumerate(self.STEPS):
            x = i * (bw + gap)
            c.setFillColor(INK if i != 3 else AMBER)
            c.roundRect(x, 0.15 * cm, bw, 1.95 * cm, 4, stroke=0, fill=1)
            c.setFillColor(AMBER if i != 3 else INK)
            c.setFont("Serif-B", 15)
            c.drawString(x + 0.3 * cm, 1.45 * cm, num)
            c.setFillColor(colors.white)
            c.setFont("Sans-B", 10.5)
            c.drawString(x + 0.3 * cm, 0.95 * cm, t)
            c.setFont("Sans", 8)
            c.setFillColor(colors.HexColor("#C9D3DE") if i != 3 else INK)
            c.drawString(x + 0.3 * cm, 0.5 * cm, sub)
            if i < n - 1:
                c.setFillColor(AMBER)
                ax = x + bw + gap / 2
                p = c.beginPath()
                p.moveTo(ax - 4, 1.32 * cm)
                p.lineTo(ax + 4, 1.12 * cm)
                p.lineTo(ax - 4, 0.92 * cm)
                p.close()
                c.drawPath(p, stroke=0, fill=1)


class ScoreBoard(Flowable):
    """Before -> after big-number tiles."""
    TILES = [("Fuzzer findings", "8", "0"), ("Bandit issues", "9", "0"), ("Pylint score", "8.45", "10.00")]

    def wrap(self, aw, ah):
        return W, 3.3 * cm

    def draw(self):
        c = self.canv
        gap = 0.5 * cm
        bw = (W - 2 * gap) / 3
        for i, (label, before, after) in enumerate(self.TILES):
            x = i * (bw + gap)
            c.setFillColor(TINT)
            c.roundRect(x, 0, bw, 3.2 * cm, 5, stroke=0, fill=1)
            c.setFillColor(MUTED)
            c.setFont("Sans-B", 9)
            c.drawString(x + 0.45 * cm, 2.55 * cm, label.upper())
            c.setFont("Serif-B", 26)
            c.setFillColor(RED)
            c.drawString(x + 0.45 * cm, 1.05 * cm, before)
            bw1 = c.stringWidth(before, "Serif-B", 26)
            c.setFillColor(MUTED)
            c.setFont("Sans", 16)
            c.drawString(x + 0.45 * cm + bw1 + 0.25 * cm, 1.2 * cm, "→")
            c.setFillColor(GREEN)
            c.setFont("Serif-B", 26)
            c.drawString(x + 0.45 * cm + bw1 + 1.0 * cm, 1.05 * cm, after)
            c.setFillColor(MUTED)
            c.setFont("Sans", 8.5)
            c.drawString(x + 0.45 * cm, 0.4 * cm, "original  →  fixed")


# ------------------------------------------------------------------ page decoration
def draw_cover(c, doc):
    c.saveState()
    c.setFillColor(INK)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    # code texture
    src = open("../src/student_app.py").read().split("\n")
    c.setFont("Mono", 7)
    c.setFillColor(colors.HexColor("#1D3049"))
    y, i = PAGE_H - 1.2 * cm, 30
    while y > 9.5 * cm:
        c.drawString(9.2 * cm, y, src[i % len(src)][:70])
        y -= 9.2
        i += 1
    # top label
    c.setFillColor(AMBER)
    c.rect(MARGIN, PAGE_H - 3.05 * cm, 1.2 * cm, 3, stroke=0, fill=1)
    t = c.beginText(MARGIN, PAGE_H - 3.8 * cm)
    t.setFont("Sans-B", 11)
    t.setCharSpace(2.2)
    t.textLine("SECURE SOFTWARE DEVELOPMENT COURSE")
    t.setCharSpace(0)
    c.saveState(); c.drawText(t); c.restoreState()
    t = c.beginText(MARGIN, PAGE_H - 4.45 * cm)
    t.setFont("Sans", 9.5)
    t.setCharSpace(1.6)
    t.setFillColor(colors.HexColor("#8EA0B5"))
    t.textLine("ASSIGNMENT REPORT  ·  FUZZING & STATIC ANALYSIS")
    c.saveState(); c.drawText(t); c.restoreState()
    # title
    c.setFillColor(colors.white)
    c.setFont("Serif-B", 40)
    for k, line in enumerate(["Breaking & Fixing", "a Student Records", "Manager"]):
        c.drawString(MARGIN, PAGE_H - (7.6 + k * 1.55) * cm, line)
    c.setFillColor(AMBER)
    c.rect(MARGIN, PAGE_H - 12.2 * cm, 3 * cm, 4, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#B9C6D4"))
    c.setFont("Serif-I", 14)
    c.drawString(MARGIN, PAGE_H - 13.2 * cm, "How fuzz testing and static analysis uncovered 17 problems")
    c.drawString(MARGIN, PAGE_H - 13.9 * cm, "in a Python application — and how every one of them was fixed.")
    # stat chips
    chips = [("8", "crashes & wrong results", "found by the fuzzer"),
             ("9", "security issues", "reported by Bandit"),
             ("10/10", "Pylint score", "after the fixes")]
    cw, gap = (W - 2 * 0.5 * cm) / 3, 0.5 * cm
    for k, (big, l1, l2) in enumerate(chips):
        x = MARGIN + k * (cw + gap)
        yb = PAGE_H - 18.0 * cm
        c.setFillColor(INK2)
        c.roundRect(x, yb, cw, 2.75 * cm, 5, stroke=0, fill=1)
        c.setFillColor(AMBER)
        c.rect(x, yb + 2.75 * cm - 3, cw, 3, stroke=0, fill=1)
        c.setFont("Serif-B", 26)
        c.drawString(x + 0.45 * cm, yb + 1.45 * cm, big)
        c.setFillColor(colors.white)
        c.setFont("Sans-B", 9.5)
        c.drawString(x + 0.45 * cm, yb + 0.85 * cm, l1)
        c.setFillColor(colors.HexColor("#8EA0B5"))
        c.setFont("Sans", 8.5)
        c.drawString(x + 0.45 * cm, yb + 0.4 * cm, l2)
    # bottom panel
    ph = 8.6 * cm
    c.setFillColor(TINT)
    c.rect(0, 0, PAGE_W, ph, stroke=0, fill=1)
    c.setFillColor(AMBER)
    c.rect(0, ph, PAGE_W, 4, stroke=0, fill=1)

    def label(x, y, s):
        t = c.beginText(x, y)
        t.setFont("Sans-B", 8.5)
        t.setCharSpace(1.8)
        t.setFillColor(AMBER)
        t.textLine(s)
        t.setCharSpace(0)
        c.saveState(); c.drawText(t); c.restoreState()

    label(MARGIN, ph - 1.3 * cm, "SUPERVISED BY")
    c.setFillColor(INK)
    c.setFont("Serif-B", 17)
    c.drawString(MARGIN, ph - 2.05 * cm, "Dr. Yasser Foad")
    c.setFont("Sans", 9.5)
    c.setFillColor(MUTED)
    c.drawString(MARGIN, ph - 2.6 * cm, "Secure Software Development")

    tx = MARGIN + 6.4 * cm
    label(tx, ph - 1.3 * cm, "PREPARED BY")
    for k, (name, sid) in enumerate(TEAM):
        yy = ph - (2.05 + k * 0.95) * cm
        c.setFillColor(INK)
        c.setFont("Serif-B", 13)
        c.drawString(tx, yy, name)
        c.setFont("Mono", 9.5)
        c.setFillColor(AMBER)
        c.drawRightString(PAGE_W - MARGIN, yy + 1, sid)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        if k < 2:
            c.line(tx, yy - 0.33 * cm, PAGE_W - MARGIN, yy - 0.33 * cm)
    c.setStrokeColor(RULE)
    c.line(MARGIN, 1.9 * cm, PAGE_W - MARGIN, 1.9 * cm)
    c.setFont("Sans", 9)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN, 1.25 * cm, "October 2026")
    c.restoreState()


def draw_page(c, doc):
    c.saveState()
    t = c.beginText(MARGIN, PAGE_H - 1.25 * cm)
    t.setFont("Sans-B", 8)
    t.setCharSpace(1.3)
    t.setFillColor(INK)
    t.textOut("SECURE SOFTWARE DEVELOPMENT")
    t.setCharSpace(0)
    t.setFont("Sans", 8.5)
    t.setFillColor(MUTED)
    t.textOut("   ·   Fuzzing & Static Analysis Report")
    c.saveState(); c.drawText(t); c.restoreState()
    c.setFont("Sans", 8.5)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.25 * cm, "Dr. Yasser Foad")
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MARGIN, PAGE_H - 1.45 * cm, PAGE_W - MARGIN, PAGE_H - 1.45 * cm)
    # footer
    c.line(MARGIN, 1.45 * cm, PAGE_W - MARGIN - 1.3 * cm, 1.45 * cm)
    c.setFont("Sans", 8)
    c.drawString(MARGIN, 1.0 * cm, "A. Abdelhamied  ·  M. Elsayed  ·  O. Muhammed")
    c.setFillColor(AMBER)
    c.rect(PAGE_W - MARGIN - 1.0 * cm, 0.8 * cm, 1.0 * cm, 0.85 * cm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Sans-B", 11)
    c.drawCentredString(PAGE_W - MARGIN - 0.5 * cm, 1.07 * cm, f"{doc.page:02d}")
    c.restoreState()


class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if isinstance(f, SectionHeader):
            self.notify("TOCEntry", (0, f"{f.num:02d} {f.title}", self.page, f.key))


doc = Doc("Security_Testing_Report.pdf", pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
          topMargin=2.1 * cm, bottomMargin=2.0 * cm, title="Breaking & Fixing a Student Records Manager",
          author="Abdelrahman Ahmed Abdelhamied, Mahmoud Osama Elsayed, Omar Muhammad Muhammed",
          subject="Secure Software Development - Fuzzing & Static Analysis")
frame = Frame(MARGIN, 2.0 * cm, W, PAGE_H - 4.1 * cm, id="f", leftPadding=0, rightPadding=0,
              topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPage=draw_cover),
                      PageTemplate(id="page", frames=[frame], onPage=draw_page)])

s = [NextPageTemplate("page"), PageBreak()]

# ------------------------------------------------------------------ contents
toc = TableOfContents()
toc.dotsMinLevel = 0
toc.levelStyles = [ParagraphStyle("toc0", fontName="Serif", fontSize=13, leading=17, textColor=INK,
                                  leftIndent=0, firstLineIndent=0, spaceBefore=7)]
s += [Spacer(1, 0.6 * cm),
      P("Contents", ParagraphStyle("ct", fontName="Serif-B", fontSize=30, leading=34, textColor=INK)),
      Spacer(1, 0.2 * cm)]
bar = Table([[""]], colWidths=[1.6 * cm], rowHeights=[3], hAlign="LEFT")
bar.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), AMBER)]))
s += [bar, Spacer(1, 0.6 * cm), toc,
      PageBreak()]

# ------------------------------------------------------------------ 01 overview
s += [SectionHeader(1, "Overview"),
      P("Software that only works on <i>good</i> input is not secure software. The goal of this "
        "assignment is to see, in practice, how two different testing techniques find different kinds "
        "of problems in the same program, and what it takes to fix them.", lead),
      P("The work was split into roles, like a small development team. One member acted as the "
        "<b>builder</b> and wrote the program. The other members acted as <b>testers</b>: they were not "
        "allowed to change the code, only to attack it and report what they found. Finally the team "
        "fixed the program together and re-ran every test."),
      Spacer(1, 4), Pipeline(), Spacer(1, 14),
      P("Tools and environment", h2),
      table([["Tool", "Type", "What it was used for"],
             ["Python 3", "Language / runtime", "The program under test and the fuzzer"],
             ["Custom fuzzer (fuzz_task_1.py)", "Dynamic testing", "20,000 random and near-valid inputs against the core functions"],
             ["Bandit 1.9", "Static analysis (security)", "Finds dangerous patterns: injection, eval, pickle, weak hashes..."],
             ["Pylint", "Static analysis (quality)", "Coding-standard problems, risky constructs, code score out of 10"],
             ["Kali Linux in VirtualBox", "Environment", "Where the static analysis was run and the reports saved"]],
            [0.32, 0.24, 0.44]),
      P("Assignment parts", h2),
      table([["Part", "Role", "Deliverable"],
             ["Part 1", "Builder", "student_app.py - a working program with planted bugs and weaknesses"],
             ["Part 2", "Testers", "Fuzzing results and Bandit / Pylint reports, with every finding explained"],
             ["Part 3", "Whole team", "student_app_fixed.py, re-test results and a comparison of both techniques"]],
            [0.15, 0.2, 0.65]),
      PageBreak()]

# ------------------------------------------------------------------ 02 building
s += [SectionHeader(2, "Part 1 — Building the Program"),
      P("The program under test is a command-line <b>Student Records Manager</b>. A user types a record in "
        "the format " + code("name,age,grade1;grade2;grade3") + ", for example " + code("Ali,20,90;85;77") +
        ". The program parses the record, calculates the average, converts it to a letter grade and saves "
        "the student in an SQLite database. A small menu also offers a search, a calculator and an "
        "admin-only database backup.", lead),
      P("The code was written in two clearly separated areas, so that each testing technique has a "
        "realistic target:"),
      *bullets(["<b>Core logic</b> - " + code("parse_record") + ", " + code("average") + ", " +
                code("letter_grade") + ", " + code("make_username") + ", " + code("process_line") +
                ". Pure functions that trust their input. These contain <i>robustness bugs</i> and are the "
                "fuzzer’s target.",
                "<b>Storage and admin features</b> - database access, password handling, calculator and "
                "backup. These contain <i>security weaknesses</i> that are hard to hit with random input but "
                "easy to recognise in the source, the static analysers’ target."]),
      Spacer(1, 6),
      P("Planted problems", h2),
      table([["Where", "Problem planted on purpose", "Expected to be found by"],
             ["parse_record", "No check of field count, empty or non-numeric age / grades", "Fuzzing"],
             ["average", "Division by zero for an empty grade list", "Fuzzing"],
             ["letter_grade", "Score ≥ 100 overflows the table; negative score gives a wrong letter", "Fuzzing"],
             ["make_username", "Crashes unless the name has exactly one space", "Fuzzing"],
             ["save_student / find_student", "SQL built by string formatting (SQL injection)", "Static analysis"],
             ["hash_password", "MD5 used for passwords", "Static analysis"],
             ["ADMIN_PASSWORD", "Hard-coded password “admin123”", "Static analysis"],
             ["calculate", "eval() on user input (code execution)", "Static analysis"],
             ["backup", "shell=True with user input (command injection)", "Static analysis"],
             ["load_backup", "pickle.load on a user-chosen file (code execution)", "Static analysis"],
             ["main", "except Exception hides every error", "Static analysis"]],
            [0.27, 0.53, 0.2]),
      figure(IMG + "o1_head.png", "student_app.py, lines 1–26: module header, risky imports "
             "(pickle, subprocess) and the hard-coded admin password."),
      figure(IMG + "o2_core.png", "Core logic, lines 28–63. Highlighted lines are the planted "
             "input-handling bugs that the fuzzer will attack."),
      figure(IMG + "o3_storage.png", "Storage and admin features, lines 65–98: SQL injection (73, 81), "
             "MD5 (88), plain-text password comparison (92) and eval (97)."),
      figure(IMG + "o4_menu.png", "Lines 99–142: shell command injection (102), unsafe pickle "
             "loading (108) and the menu with a catch-all exception handler (137)."),
      PageBreak()]

# ------------------------------------------------------------------ 03 fuzzing
s += [SectionHeader(3, "Part 2a — Fuzz Testing"),
      P("Fuzzing is a <b>dynamic</b> technique: the program is executed over and over with automatically "
        "generated input, and every crash or wrong answer is recorded. It needs no knowledge of how the code "
        "is written, only a way to call it.", lead),
      P("How the fuzzer works", h2),
      *bullets(["<b>20,000 iterations</b> with a fixed random seed (" + code("random.seed(1)") +
                "), so the run is repeatable and the results can be checked by anyone.",
                "<b>Two kinds of input</b>, alternating: completely random text, and <i>near-valid</i> "
                "records built from a list of tricky values (empty fields, negative ages, " + code("999999") +
                ", grades such as 150 or “x”). Near-valid input passes the first checks and reaches "
                "deeper code, which pure noise rarely does.",
                "<b>Every core function</b> is called inside " + code("try / except") +
                "; the first input that raises each (function, exception) pair is stored, so the report "
                "contains unique findings, not 20,000 duplicates.",
                "<b>An oracle</b> checks a bug that does <i>not</i> crash: a negative score must always give "
                "“F”. Without it, a wrong result would go unnoticed."]),
      Spacer(1, 6),
      figure(IMG + "f1_fuzz.png", "fuzz_task_1.py, lines 1–30: setup, finding recorder and input "
             "generators (comments translated to English)."),
      figure(IMG + "f2_fuzz.png", "fuzz_task_1.py, lines 31–62: the main loop, the test table and the "
             "wrong-result oracle."),
      figure(IMG + "t1_fuzz.png", "Running the fuzzer: 8 unique findings in the original program."),
      P("Fuzzing results", h2),
      table([["#", "Function", "Exception", "Failing input", "Root cause"],
             ["1", "parse_record", "ValueError", code("'Sara Ahmed,999999,'"), "Empty grade text: int('') fails"],
             ["2", "process_line", "ValueError", code("'Sara Ahmed,999999,'"), "Same bug, reached through the pipeline"],
             ["3", "average", "ZeroDivisionError", code("[]"), "len(grades) is 0"],
             ["4", "make_username", "ValueError", code("'58WAm,dX3a5IDnO'"), "No space in the name, unpacking fails"],
             ["5", "letter_grade", "IndexError", code("-269"), "-269 // 10 = -27, outside the table"],
             ["6", "parse_record", "IndexError", code("'4;DSDC6'"), "Fewer than three comma-separated fields"],
             ["7", "process_line", "IndexError", code("'4;DSDC6'"), "Same bug, reached through the pipeline"],
             ["8", "letter_grade", "Wrong result", code("-4"), "-4 // 10 = -1, LETTERS[-1] is “A”"]],
            [0.05, 0.17, 0.17, 0.25, 0.36]),
      callout("Finding 8 is the most dangerous one. The program does not crash, it quietly gives a failing "
              "student an <b>A</b>. Only the oracle caught it, which shows that fuzzing finds logic errors "
              "only when the tester also tells it what the correct answer should be.",
              "Key observation"),
      P("The fuzzer did <b>not</b> hit the score-100 bug (" + code("100 // 10 = 10") + " is past the end of the "
        "list), because random averages of near-valid grades almost never land exactly on 100 or above. "
        "Random testing can miss narrow edge cases; this one was found by reading the code and is fixed "
        "anyway. The fuzzer also never touched SQL, eval, the shell or pickle, because it only called the "
        "core functions."),
      PageBreak()]

# ------------------------------------------------------------------ 04 static
s += [SectionHeader(4, "Part 2b — Static Analysis"),
      P("Static analysis reads the source code <b>without running it</b> and compares it against "
        "known dangerous patterns and coding rules. It sees every line, including code that random input "
        "never reaches.", lead),
      P("Bandit - security linter", h2),
      P("Bandit parses the Python code into a syntax tree and checks it against a list of insecure "
        "patterns, each linked to a CWE weakness ID. It was run on Kali Linux and the report saved in "
        "text and JSON form:"),
      callout(code("bandit -f txt  -o bandit_report.txt  student_manager.py") + "<br/>" +
              code("bandit -f json -o bandit_report.json student_manager.py") + "<br/>" +
              code("pylint student_manager.py &gt; pylint_report.txt 2&gt;&amp;1"),
              "Commands used", TEAL),
      table([["Line", "Test", "Severity", "Confidence", "Problem", "CWE"],
             ["102", "B602", "<font color='#B23A3A'><b>High</b></font>", "High", "subprocess call with shell=True - command injection", "78"],
             ["88", "B324", "<font color='#B23A3A'><b>High</b></font>", "High", "Weak MD5 hash used for passwords", "327"],
             ["73", "B608", "<font color='#C27A1A'><b>Medium</b></font>", "Medium", "SQL query built with % formatting - SQL injection", "89"],
             ["81", "B608", "<font color='#C27A1A'><b>Medium</b></font>", "Medium", "SQL query built with + concatenation - SQL injection", "89"],
             ["97", "B307", "<font color='#C27A1A'><b>Medium</b></font>", "High", "eval() on user input - arbitrary code execution", "78"],
             ["108", "B301", "<font color='#C27A1A'><b>Medium</b></font>", "High", "pickle.load on an untrusted file - code execution", "502"],
             ["20", "B105", "Low", "Medium", "Hard-coded password string 'admin123'", "259"],
             ["15", "B403", "Low", "High", "import pickle", "502"],
             ["17", "B404", "Low", "High", "import subprocess", "78"]],
            [0.07, 0.09, 0.11, 0.12, 0.51, 0.10]),
      P("In total Bandit reported <b>9 issues</b>: 2 High, 4 Medium and 3 Low severity (by confidence: "
        "6 High, 3 Medium). The two Low “import” warnings are informational: importing pickle "
        "or subprocess is not a flaw by itself, but it tells the reviewer where to look."),
      figure(IMG + "kali_bandit_pylint.jpg", "Bandit summary and report files on Kali Linux, followed by the "
             "first Pylint run on the same file.", max_h=20 * cm),
      P("Pylint - code quality", h2),
      P("Pylint checks coding standards and risky constructs. It rated the program <b>8.45 / 10</b> "
        "with 12 messages. Two of them (eval-used and broad-exception-caught) point at the same "
        "weaknesses that matter for security; the rest are maintainability issues."),
      table([["Code", "Count", "Message", "Lines"],
             ["C0116", "9", "missing-function-docstring", "69, 78, 86, 91, 95, 100, 105, 115"],
             ["C0209", "1", "consider-using-f-string", "73 - the same line as the SQL injection"],
             ["W0123", "1", "eval-used", "97"],
             ["W0718", "1", "broad-exception-caught (except Exception)", "137"]],
            [0.12, 0.1, 0.4, 0.38]),
      figure(IMG + "kali_pylint.jpg", "Pylint output saved to pylint_report.txt - score 8.45 / 10.",
             max_h=20 * cm),
      PageBreak()]

# ------------------------------------------------------------------ 05 fixes
s += [SectionHeader(5, "Part 3 — Fixing the Problems"),
      P("All findings were fixed in a new file, <b>student_app_fixed.py</b>. The guiding rule was to fix "
        "the <i>cause</i>, not the symptom: validate input once at the boundary, and stop building code, "
        "SQL or shell commands out of strings.", lead),
      P("Bad user input is now rejected with a dedicated exception, " + code("InvalidRecordError") +
        " (a subclass of ValueError). The menu catches it and shows a clear message, so invalid input is an "
        "expected, controlled outcome instead of a crash."),
      table([["Problem", "Found by", "Fix applied"],
             ["parse_record crashes on missing / bad fields", "Fuzzer", "Exactly 3 fields, non-empty name, age 1–120, every grade 0–100"],
             ["Division by zero in average", "Fuzzer", "Empty grade list is rejected"],
             ["letter_grade IndexError and wrong “A”", "Fuzzer", "Scores outside 0–100 rejected; min(score // 10, 9) so 100 = A"],
             ["make_username needs exactly one space", "Fuzzer", "name.split() on any whitespace; first and last word used"],
             ["SQL injection (2 places)", "Bandit B608", "Parameterised queries with ? placeholders"],
             ["Command injection via shell=True", "Bandit B602, B404", "shutil.copyfile - no shell; file name reduced to a safe base name"],
             ["eval() calculator", "Bandit B307, Pylint W0123", "Small AST evaluator: only numbers and + − × ÷"],
             ["pickle.load backup", "Bandit B301, B403", "Backups stored and loaded as JSON (data only)"],
             ["MD5 password hash", "Bandit B324", "Salted PBKDF2-HMAC-SHA256, 200,000 iterations"],
             ["Hard-coded admin password", "Bandit B105", "Hash read from the ADMIN_PASSWORD_HASH environment variable, hmac.compare_digest"],
             ["Docstrings, f-string, broad except", "Pylint", "Docstrings added; only specific exceptions are caught"],
             ["Student saved before validation", "Code review", "Record is validated before save_student is called"]],
            [0.33, 0.22, 0.45], align_top=True),
      PageBreak(),
      figure(IMG + "x1_parse.png", "Fixed parse_record: every field is validated before use "
             "(green lines are new checks)."),
      figure(IMG + "x2_core.png", "Fixed average, letter_grade, make_username and process_line."),
      figure(IMG + "x3_storage.png", "Parameterised SQL, salted PBKDF2 password hashing and a "
             "constant-time admin check."),
      figure(IMG + "x4_admin.png", "eval replaced by a safe AST calculator, shell replaced by shutil with a "
             "sanitised name, pickle replaced by JSON."),
      figure(IMG + "x5_menu.png", "The menu validates before saving and catches only specific exceptions."),
      PageBreak()]

# ------------------------------------------------------------------ 06 retest
s += [SectionHeader(6, "Re-testing the Fixed Program"),
      P("A fix is only proven when the same test that found the problem passes. The fuzzer was run again "
        "with the <b>same seed and the same 20,000 iterations</b>; the only change is that the controlled "
        + code("InvalidRecordError") + " counts as correct behaviour. Bandit and Pylint were run again with "
        "the same settings.", lead),
      ScoreBoard(), Spacer(1, 16),
      P("Valid input still works", h2),
      P("Fixing must not break normal use. The fixed program was also checked by hand with valid and "
        "malicious input:"),
      table([["Input", "Original program", "Fixed program"],
             [code("Ali,20,90;85;100"), "Average 91.7, A", "Average 91.7, A"],
             [code("Ali,abc,"), "ValueError - generic error", "“Invalid input: age must be a whole number…”"],
             ["Calculator: " + code("2*(3+4)"), "14", "14"],
             ["Calculator: " + code("__import__('os')"), "<font color='#B23A3A'>Executes the code</font>", "<font color='#2E7D4F'>Rejected</font>"],
             ["Search: " + code("' OR '1'='1"), "<font color='#B23A3A'>Returns every student</font>", "<font color='#2E7D4F'>Returns nothing (treated as a name)</font>"],
             ["Backup name: " + code("x; whoami"), "<font color='#B23A3A'>Runs a shell command</font>", "<font color='#2E7D4F'>Rejected by the name check</font>"]],
            [0.34, 0.31, 0.35]),
      figure(IMG + "t2_fixed.png", "Re-test of student_app_fixed.py: no fuzzer findings, no Bandit issues "
             "and a Pylint score of 10.00 / 10.", max_h=19 * cm, width=W * 0.92),
      PageBreak()]

# ------------------------------------------------------------------ 07 comparison
s += [SectionHeader(7, "Fuzzing vs Static Analysis"),
      P("The most striking result of this assignment is that the two techniques found <b>no problem in "
        "common</b>. Each one was blind to everything the other one found.", lead),
      table([["Aspect", "Fuzzing", "Static analysis (Bandit + Pylint)"],
             ["How it works", "Runs the code with thousands of generated inputs", "Reads the source code without running it"],
             ["What it found here", "8 crashes / wrong results in the core logic", "9 security issues + 12 quality messages in storage and admin code"],
             ["Blind spot here", "Never reached SQL, eval, shell or pickle", "Saw nothing wrong in parse_record, average or letter_grade"],
             ["Logic (wrong-answer) bugs", "Yes - when an oracle is written", "No - the code is valid Python"],
             ["False positives", "None: each finding comes with a real input", "Some: B403 / B404 only flag an import"],
             ["Coverage", "Only paths the inputs reach; missed score = 100", "Every line and path, in seconds"],
             ["Evidence", "Exact failing input - easy to reproduce", "File, line and CWE - no exploit input"],
             ["Effort", "Write a harness, choose inputs, run many iterations", "One command, no set-up"],
             ["Best at", "Robustness and input handling", "Known insecure patterns and code hygiene"]],
            [0.2, 0.38, 0.42], align_top=True),
      P("Overall findings", h2),
      table([["Category", "Found by fuzzing", "Found by static analysis", "Fixed"],
             ["Crashes on bad input", "7", "0", "7 / 7"],
             ["Wrong result (silent)", "1", "0", "1 / 1"],
             ["Security weaknesses", "0", "9 (Bandit)", "9 / 9"],
             ["Code-quality messages", "0", "12 (Pylint)", "12 / 12"]],
            [0.34, 0.2, 0.26, 0.2]),
      callout("Neither technique alone would have been enough. Fuzzing proved, with concrete inputs, that the "
              "program falls over or lies on unexpected data. Static analysis pointed straight at the "
              "injection, deserialisation and cryptography mistakes that random input almost never triggers. "
              "Used together - and followed by fixing and re-testing - they took the program from "
              "<b>8 crashes, 9 security issues and 8.45 / 10</b> to <b>0, 0 and 10 / 10</b>.",
              "Verdict"),
      ]

# ------------------------------------------------------------------ 08 conclusion
s += [CondPageBreak(12 * cm), SectionHeader(8, "Conclusion & Lessons Learned"),
      *bullets(["<b>Validate input at the boundary.</b> Seven of the eight fuzzer findings came from trusting "
                "the format of user input. One validation step in parse_record removed all of them.",
                "<b>Never build code, SQL or shell commands from strings.</b> Parameterised queries, an AST "
                "evaluator and shutil remove whole classes of injection instead of patching single cases.",
                "<b>Crash-free does not mean correct.</b> The negative-score bug appeared only because the "
                "fuzzer had an oracle that knew the expected answer.",
                "<b>Read the warnings, don’t just silence them.</b> The best fix for the pickle and "
                "subprocess warnings was to stop needing those modules, so the risky imports disappeared.",
                "<b>Re-test after fixing.</b> Running the same seed and the same tools again is what proves "
                "that the fixes work and that valid input still gives the same answers."]),
      Spacer(1, 10),
      P("Submitted files", h2),
      table([["File", "Contents"],
             ["student_app.py", "Part 1 - the original program with planted bugs and weaknesses"],
             ["fuzz_task_1.py", "Part 2 - the random fuzzer"],
             ["bandit_report.txt / .json, pylint_report.txt", "Part 2 - static analysis reports"],
             ["student_app_fixed.py", "Part 3 - the fixed program"],
             ["fuzz_fixed.py", "Part 3 - the same fuzzer run against the fixed program"]],
            [0.42, 0.58]),
      ]

doc.multiBuild(s)
