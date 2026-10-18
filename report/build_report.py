from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Image, Table, TableStyle, PageBreak, KeepTogether)
from PIL import Image as PILImage

IMG = "img/"
USER_SHOTS = "img/"
NAVY = colors.HexColor("#1F3864")
ACCENT = colors.HexColor("#2E75B6")
LIGHT = colors.HexColor("#EAF1FB")
RED = colors.HexColor("#C00000")
GREEN = colors.HexColor("#2E7D32")

ss = getSampleStyleSheet()
body = ParagraphStyle("body", parent=ss["BodyText"], fontName="Helvetica", fontSize=10,
                      leading=14, alignment=TA_JUSTIFY, spaceAfter=5)
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=15,
                    textColor=NAVY, spaceBefore=4, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                    textColor=ACCENT, spaceBefore=6, spaceAfter=4)
cap = ParagraphStyle("cap", parent=body, fontName="Helvetica-Oblique", fontSize=8.5,
                     textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=8)
cell = ParagraphStyle("cell", parent=body, fontSize=8.3, leading=10.5, alignment=0, spaceAfter=0)
cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=12, bulletIndent=2, spaceAfter=2)

W = A4[0] - 4 * cm  # usable width


def img(path, width=None, max_h=None, caption=None, keep=True):
    w, h = PILImage.open(path).size
    width = width or W
    height = width * h / w
    if max_h and height > max_h:
        height = max_h
        width = height * w / h
    im = Image(path, width=width, height=height)
    out = [im]
    if caption:
        out.append(Paragraph(caption, cap))
    return KeepTogether(out) if keep else out


def pair(a, b, ca, cb, gap=0.4 * cm, max_h=None):
    cw = (W - gap) / 2
    t = Table([[img(a, width=cw - 0.2 * cm, max_h=max_h, caption=ca, keep=False), img(b, width=cw - 0.2 * cm, max_h=max_h, caption=cb, keep=False)]],
              colWidths=[cw + gap / 2, cw + gap / 2])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t


def table(rows, widths, head_bg=NAVY, zebra=True):
    data = [[Paragraph(str(c), cellb if i == 0 else cell) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), head_bg),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B4C6E7")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if zebra:
        st += [("BACKGROUND", (0, i), (-1, i), LIGHT) for i in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return t


def P(t, s=body):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, bullet, bulletText="•") for i in items]


def on_page(c, doc):
    c.saveState()
    if doc.page > 1:
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.8)
        c.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        c.drawString(2 * cm, A4[1] - 1.25 * cm, "Software Security Testing - Fuzzing & Static Analysis")
        c.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, "Student Records Manager")
        c.drawCentredString(A4[0] / 2, 1.1 * cm, f"Page {doc.page}")
    c.restoreState()


doc = BaseDocTemplate("Security_Testing_Report.pdf", pagesize=A4, leftMargin=2 * cm,
                      rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.7 * cm,
                      title="Software Security Testing Report", author="Assignment Yasser")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin,
                                                         doc.width, doc.height, id="f")],
                                   onPage=on_page)])
s = []

# ---------------------------------------------------------------- cover (p1)
s += [Spacer(1, 0.6 * cm),
      P("SOFTWARE SECURITY TESTING", ParagraphStyle("k", parent=body, fontName="Helvetica-Bold",
                                                    fontSize=11, textColor=ACCENT, alignment=TA_CENTER)),
      Spacer(1, 6),
      P("Building and Testing a Student Records Manager<br/>with Fuzzing and Static Analysis",
        ParagraphStyle("t", parent=h1, fontSize=21, leading=27, alignment=TA_CENTER)),
      Spacer(1, 10)]
cover = Table([[""]], colWidths=[W * 0.5], rowHeights=[2])
cover.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, -1), 2, ACCENT)]))
s += [cover, Spacer(1, 18)]
s.append(table([
    ["Item", "Details"],
    ["Part 1 - Builder", "Wrote <b>student_app.py</b>, a command-line program that stores students and grades, "
                         "with bugs and security weaknesses planted on purpose."],
    ["Part 2 - Tester", "Attacked the program with a <b>random fuzzer</b> (fuzz_task_1.py) and with the "
                        "<b>static analysers Bandit and Pylint</b>."],
    ["Part 3 - Fixes", "Fixed every finding (student_app_fixed.py) and re-ran all three tools."],
    ["Environment", "Kali Linux (VirtualBox), Python 3, Bandit 1.9, Pylint 4"],
], [W * 0.25, W * 0.75]))
s += [Spacer(1, 18), P("<b>Abstract.</b> One team member built a small Python application and a second "
      "member tested it without changing it, using two complementary techniques. Fuzzing ran the code "
      "20,000 times with random input and found <b>8 unique crashes / wrong results</b> in the core logic. "
      "Static analysis read the code without running it: Bandit reported <b>9 security issues</b> "
      "(2 High, 4 Medium, 3 Low) and Pylint scored the code <b>8.45/10</b> with 12 messages. "
      "After the fixes, the fuzzer finds <b>0</b> problems, Bandit reports <b>0</b> issues and Pylint "
      "gives <b>10.00/10</b>. The report ends with a comparison of the two techniques and a "
      "before/after summary.", body)]

# ---------------------------------------------------------------- Part 1 (p2-3)
s += [P("1. Part 1 - Building the Program", h1),
      P("The program under test is a <b>Student Records Manager</b>. A record is typed as "
        "<font face='Courier'>name,age,grade1;grade2;grade3</font> (for example "
        "<font face='Courier'>Ali,20,90;85;77</font>). The program parses it, computes the average, "
        "converts it to a letter grade and stores the student in an SQLite database. "
        "It also offers a search, a calculator and an admin-only backup. The code is split into two "
        "areas so that each testing technique has a clear target:"),
      *bullets(["<b>Core logic</b> (parse_record, average, letter_grade, make_username, process_line) - "
                "pure functions with <i>input-handling bugs</i>, the target of the fuzzer.",
                "<b>Storage / admin features</b> - code with <i>security weaknesses</i> "
                "(SQL injection, eval, shell commands, pickle, MD5, hard-coded password), the target "
                "of static analysis."]),
      pair(IMG + "app_core.png", IMG + "app_storage.png",
           "Figure 1 - Core logic of student_app.py (planted bugs highlighted).",
           "Figure 2 - Storage, admin features and menu (weaknesses highlighted)."),
      Spacer(1, 4),
      P("Besides these, line 20 contains the hard-coded password "
        "<font face='Courier'>ADMIN_PASSWORD = \"admin123\"</font>, and lines 15 and 17 import the risky "
        "<font face='Courier'>pickle</font> and <font face='Courier'>subprocess</font> modules."),
      PageBreak()]

# ---------------------------------------------------------------- Part 2a fuzzing (p4)
s += [P("2. Part 2 - Testing the Program", h1),
      P("2.1 Fuzz Testing", h2),
      P("The tester wrote a <b>random (black-box) fuzzer</b>. Each of 20,000 iterations generates "
        "(a) fully random text and (b) <i>near-valid</i> records built from a list of tricky values "
        "(empty fields, negative ages, <font face='Courier'>999999</font>, grades like 150 or 'x'), "
        "so the input passes the first checks and reaches deeper code. Every core function is called "
        "inside <font face='Courier'>try/except</font>; the first input that raises each (function, "
        "exception) pair is saved. A seed makes the run repeatable, and an extra <b>oracle</b> checks a "
        "bug that does not crash: a negative score must give 'F'."),
      img(IMG + "fuzz.png", max_h=11.5 * cm, caption="Figure 3 - The fuzzer, fuzz_task_1.py "
          "(comments translated to English)."),
      ]
s += [img(IMG + "term_fuzz.png", caption="Figure 4 - Fuzzer output: 8 unique findings."),
      table([
          ["#", "Function", "Exception", "Input that triggered it", "Root cause"],
          ["1-2", "parse_record / process_line", "ValueError", "'Sara Ahmed,999999,'",
           "int('') - the grade list is empty"],
          ["3", "average", "ZeroDivisionError", "[]", "len(grades) is 0"],
          ["4", "make_username", "ValueError", "'58WAm,dX3a5IDnO'", "name has no space, unpack fails"],
          ["5", "letter_grade", "IndexError", "-269", "-269 // 10 = -27 is outside the list"],
          ["6-7", "parse_record / process_line", "IndexError", "'4;DSDC6'", "fewer than 3 comma fields"],
          ["8", "letter_grade (oracle)", "Wrong result", "-4", "-4 // 10 = -1 gives LETTERS[-1] = 'A'"],
      ], [W * 0.06, W * 0.24, W * 0.16, W * 0.22, W * 0.32]),
      Spacer(1, 6),
      P("Finding 8 is the most interesting: the program does not crash, it silently gives a failing "
        "student an <b>A</b>. Only the oracle check could catch it. Note also that the bug at score "
        "100 (<font face='Courier'>100 // 10 = 10</font>, IndexError) was not hit because the fuzzer "
        "picks integers and the average of near-valid grades rarely lands at 100+; it is fixed anyway."),
      ]

# ---------------------------------------------------------------- Part 2b static (p5)
s += [P("2.2 Static Analysis", h2),
      P("Static analysis inspects the source code <b>without running it</b>. Two tools were used on "
        "Kali Linux: <b>Bandit</b>, a security linter that matches the code against known dangerous "
        "patterns (CWE), and <b>Pylint</b>, a quality linter. Commands used: "
        "<font face='Courier'>bandit -f txt -o bandit_report.txt student_manager.py</font>, "
        "<font face='Courier'>bandit -f json -o bandit_report.json student_manager.py</font> and "
        "<font face='Courier'>pylint student_manager.py &gt; pylint_report.txt</font>."),
      table([
          ["Line", "Bandit ID", "Severity", "Problem", "CWE"],
          ["102", "B602", "<font color='#C00000'><b>High</b></font>", "subprocess with shell=True - command injection", "78"],
          ["88", "B324", "<font color='#C00000'><b>High</b></font>", "MD5 used to hash passwords", "327"],
          ["73", "B608", "Medium", "SQL built with % formatting - SQL injection", "89"],
          ["81", "B608", "Medium", "SQL built with + concatenation - SQL injection", "89"],
          ["97", "B307", "Medium", "eval() on user input - arbitrary code execution", "78"],
          ["108", "B301", "Medium", "pickle.load on untrusted file - code execution", "502"],
          ["20", "B105", "Low", "Hard-coded password 'admin123'", "259"],
          ["15", "B403", "Low", "import pickle", "502"],
          ["17", "B404", "Low", "import subprocess", "78"],
      ], [W * 0.08, W * 0.12, W * 0.12, W * 0.58, W * 0.10]),
      Spacer(1, 6),
      ]
s += [P("Pylint reported 12 messages and a score of <b>8.45/10</b>:"),
      table([
          ["Code", "Count", "Message", "Lines"],
          ["C0116", "9", "missing-function-docstring", "69, 78, 86, 91, 95, 100, 105, 115"],
          ["C0209", "1", "consider-using-f-string", "73 (the same line as the SQL injection)"],
          ["W0123", "1", "eval-used", "97"],
          ["W0718", "1", "broad-exception-caught (except Exception)", "137"],
      ], [W * 0.12, W * 0.1, W * 0.43, W * 0.35]),
      Spacer(1, 8),
      pair(USER_SHOTS + "kali_bandit_pylint.jpg", USER_SHOTS + "kali_pylint.jpg",
           "Figure 5 - Bandit reports written (confidence: Medium 3, High 6) and first Pylint run on Kali.",
           "Figure 6 - Pylint output saved to pylint_report.txt (score 8.45/10)."),
      ]

# ---------------------------------------------------------------- Fixes (p7)
s += [P("3. Fixes", h1),
      P("All findings were fixed in <b>student_app_fixed.py</b>. Bad user input is now rejected "
        "with a dedicated <font face='Courier'>InvalidRecordError</font> (a subclass of ValueError) "
        "that the menu catches and shows as a friendly message, instead of an unexpected crash."),
      table([
          ["Problem", "Found by", "Fix"],
          ["Missing / non-numeric fields in parse_record", "Fuzzer", "Check exactly 3 fields, non-empty name, age 1-120, every grade 0-100"],
          ["Division by zero in average", "Fuzzer", "Reject an empty grade list"],
          ["IndexError and wrong 'A' in letter_grade", "Fuzzer", "Reject scores outside 0-100; min(score // 10, 9) so 100 = 'A'"],
          ["make_username needs exactly one space", "Fuzzer", "name.split() on any whitespace, use first and last word"],
          ["SQL injection (2 places)", "Bandit B608", "Parameterised queries with ? placeholders"],
          ["Command injection via shell=True", "Bandit B602/B404", "shutil.copyfile, no shell; file name reduced to a safe base name"],
          ["eval() calculator", "Bandit B307, Pylint W0123", "Small AST evaluator allowing only numbers and + - * /"],
          ["pickle.load backup", "Bandit B301/B403", "Backups loaded as JSON (data only)"],
          ["MD5 password hash", "Bandit B324", "Salted PBKDF2-HMAC-SHA256, 200,000 iterations"],
          ["Hard-coded admin password", "Bandit B105", "Hash read from ADMIN_PASSWORD_HASH env var; hmac.compare_digest"],
          ["Missing docstrings, f-string, broad except", "Pylint", "Docstrings added; specific exceptions caught"],
          ["Student saved before validation", "Code review", "process_line validates before save_student"],
      ], [W * 0.33, W * 0.2, W * 0.47]),
      PageBreak(),
      pair(IMG + "fixed_core.png", IMG + "fixed_storage.png",
           "Figure 7 - Fixed core logic: every input is validated.",
           "Figure 8 - Fixed storage and admin features."),
      PageBreak()]

# ---------------------------------------------------------------- Retest & comparison (p8-9)
s += [P("4. Re-testing and Comparison", h1),
      P("The same fuzzer (same seed, same 20,000 iterations) was re-run against the fixed module; the only "
        "change is that the controlled <font face='Courier'>InvalidRecordError</font> is counted as correct "
        "behaviour, not as a bug. Bandit and Pylint were run again with the same settings."),
      img(IMG + "term_fixed.png", width=W * 0.85, caption="Figure 9 - Re-test of the fixed version."),
      P("4.1 Before vs After", h2),
      table([
          ["Metric", "Original", "Fixed"],
          ["Fuzzer unique findings", "<font color='#C00000'><b>8</b></font>", "<font color='#2E7D32'><b>0</b></font>"],
          ["Bandit High / Medium / Low", "<font color='#C00000'><b>2 / 4 / 3</b></font>", "<font color='#2E7D32'><b>0 / 0 / 0</b></font>"],
          ["Pylint score", "8.45 / 10 (12 messages)", "<font color='#2E7D32'><b>10.00 / 10</b></font> (0 messages)"],
          ["Bad input such as 'Ali,abc,'", "Crash / generic error", "Clear 'Invalid input' message"],
          ["Calculator input __import__('os')", "Executes code", "Rejected"],
      ], [W * 0.38, W * 0.31, W * 0.31]),
      ]
s += [PageBreak(), P("4.2 Fuzzing vs Static Analysis", h2),
      table([
          ["Aspect", "Fuzzing", "Static analysis (Bandit + Pylint)"],
          ["How it works", "Runs the code with many random inputs", "Reads the source code without running it"],
          ["What it found here", "8 runtime crashes and 1 logic error in the core logic", "9 security issues + 12 quality messages in storage/admin code"],
          ["Overlap", "None - it never touched SQL, eval, shell or pickle", "None - it saw no problem in parse_record, average, letter_grade"],
          ["False positives", "None: every finding came with a real input", "Some: B403/B404 only flag an import, not a real flaw"],
          ["Silent logic bugs", "Yes, if an oracle is written (negative = 'A')", "No - the code is valid Python"],
          ["Coverage", "Only code it reaches; may miss rare values (score 100)", "Every line, every path, in seconds"],
          ["Proof / reproduction", "Gives the exact failing input", "Gives file, line and CWE, but no exploit input"],
          ["Cost", "Must write a harness and run many iterations", "One command, no setup"],
      ], [W * 0.2, W * 0.38, W * 0.42]),
      Spacer(1, 8),
      P("<b>Conclusion.</b> The two techniques found <b>completely different</b> problems - neither "
        "alone would have revealed all 17 issues. Fuzzing is best for robustness: it proves with a concrete "
        "input that the program crashes or returns wrong data. Static analysis is best for known dangerous "
        "patterns such as injection, unsafe deserialisation and weak cryptography, which random input "
        "rarely triggers. Using both, then fixing and re-testing, took the program from 8 crashes, "
        "9 security issues and 8.45/10 to <b>0 crashes, 0 issues and 10/10</b>."),
      P("4.3 Lessons Learned", h2),
      *bullets(["<b>Validate input at the boundary.</b> Seven of the eight fuzzer findings came from trusting "
                "the format of user input; one validation function removed all of them.",
                "<b>Never build code, SQL or shell commands from strings.</b> Parameterised queries, an AST "
                "evaluator and shutil remove whole classes of injection instead of patching single cases.",
                "<b>Crash-free is not the same as correct.</b> The negative-score bug only appeared because "
                "the fuzzer had an oracle that knew the expected answer.",
                "<b>Some static warnings are informational.</b> B403/B404 flag imports; the real fix was to "
                "stop needing pickle and subprocess at all, so the imports disappeared.",
                "<b>Re-test after fixing.</b> Running the same seed and the same tools again is what proves "
                "the fixes work and did not break valid input (e.g. 'Ali,20,90;85;100' still gives A)."]),
      ]

doc.build(s)
