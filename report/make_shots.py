import subprocess, re, glob, os
from shots import editor_shot, terminal_shot
for f in glob.glob("img/*.png"):
    os.remove(f)
src = "../src/"
orig = open(src + "student_app.py").read().split("\n")
fixed = open(src + "student_app_fixed.py").read().split("\n")
fuzz = open(src + "fuzz_task_1.py").read()
# translate the Arabic comments for the screenshot
fuzz = (fuzz.replace("# عشان النتيجة تتكرر نفسها كل مرة", "# so the results repeat the same every run")
            .replace("# (الدالة, نوع الخطأ) -> أول input فجّره", "# (function, error type) -> first input that broke it")
            .replace("# نص قريب من الفورمات الصح عشان نوصل لأعماق الدالة", "# text close to the valid format to reach deeper code")
            .replace("# فحص الـ bug اللي مفيهوش crash: درجة سالبة (من -1 لـ -10) لازم تطلع F",
                     "# oracle for the silent bug: negative score (-1..-10) must give F")
            .replace("# الـ IndexError اتسجل فوق خلاص", "# the IndexError was already recorded above"))
assert not re.search(r"[؀-ۿ]", fuzz)
fz = fuzz.split("\n")
J = lambda a, b, L: "\n".join(L[a-1:b])
GREEN = (34, 58, 42)


def H(L, a, b, *keys):
    return [i for i in range(a, b + 1) if any(k in L[i - 1] for k in keys)]
editor_shot(J(1, 26, orig), "student_app.py", "img/o1_head.png", 1, highlight=H(orig, 1, 26, "import pickle", "import subprocess", "ADMIN_PASSWORD ="))
editor_shot(J(28, 63, orig), "student_app.py", "img/o2_core.png", 28, highlight=[36, 37, 43, 48, 54])
editor_shot(J(65, 98, orig), "student_app.py", "img/o3_storage.png", 65, highlight=[73, 81, 88, 92, 97])
editor_shot(J(99, 142, orig), "student_app.py", "img/o4_menu.png", 99, highlight=[102, 108, 137])
editor_shot(J(1, 30, fz), "fuzz_task_1.py", "img/f1_fuzz.png", 1)
editor_shot(J(31, 62, fz), "fuzz_task_1.py", "img/f2_fuzz.png", 31)
editor_shot(J(30, 56, fixed), "student_app_fixed.py", "img/x1_parse.png", 30,
            highlight=H(fixed, 30, 56, "len(parts) != 3", "if not name", "age_text.isdigit()", "g.isdigit()"), hl_color=GREEN)
editor_shot(J(57, 84, fixed), "student_app_fixed.py", "img/x2_core.png", 57,
            highlight=H(fixed, 57, 84, "if not grades", "0 <= score <= 100", "min(score", "name.split()", "len(words) < 2"), hl_color=GREEN)
editor_shot(J(86, 120, fixed), "student_app_fixed.py", "img/x3_storage.png", 86,
            highlight=H(fixed, 86, 120, "VALUES (?, ?)", "name = ?", "pbkdf2_hmac", "compare_digest"), hl_color=GREEN)
editor_shot(J(121, 153, fixed), "student_app_fixed.py", "img/x4_admin.png", 121,
            highlight=H(fixed, 121, 153, "ast.parse", "raise InvalidRecordError(\"only", "Path(filename).name", "shutil.copyfile", "json.load"), hl_color=GREEN)
editor_shot(J(155, 189, fixed), "student_app_fixed.py", "img/x5_menu.png", 155,
            highlight=H(fixed, 155, 189, "validate BEFORE", "except (InvalidRecordError", "except (sqlite3"), hl_color=GREEN)
run = lambda c: subprocess.run(c, shell=True, cwd=src, capture_output=True, text=True).stdout
terminal_shot("$ python3 fuzz_task_1.py\n" + run("python3 fuzz_task_1.py") + "$ ", "img/t1_fuzz.png", size=11)
bf = run("bandit student_app_fixed.py 2>/dev/null")
bf = bf[bf.index("Test results"):].split("Files skipped")[0].rstrip()
pf = run("pylint student_app_fixed.py").strip()
terminal_shot("$ python3 fuzz_fixed.py\n" + run("python3 fuzz_fixed.py") +
              "$ bandit student_app_fixed.py\n" + bf + "\n$ pylint student_app_fixed.py\n" + pf + "\n$ ",
              "img/t2_fixed.png", size=11)
