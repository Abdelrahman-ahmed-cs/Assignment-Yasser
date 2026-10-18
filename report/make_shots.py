import subprocess, re
from shots import editor_shot, terminal_shot
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
J = lambda a, b, L: "\n".join(L[a-1:b])
editor_shot(J(28, 63, orig), "student_app.py", "img/app_core.png", 28, highlight=[36, 37, 43, 48, 54])
editor_shot(J(65, 142, orig), "student_app.py", "img/app_storage.png", 65, size=12,
            highlight=[20+0] and [73, 81, 88, 92, 97, 102, 108, 137])
editor_shot(J(1, 25, orig), "student_app.py", "img/app_head.png", 1, highlight=[20])
editor_shot(fuzz, "fuzz_task_1.py", "img/fuzz.png", 1, size=12)
editor_shot(J(39, 82, fixed), "student_app_fixed.py", "img/fixed_core.png", 39, size=12)
editor_shot(J(89, 152, fixed), "student_app_fixed.py", "img/fixed_storage.png", 89, size=12)
run = lambda c: subprocess.run(c, shell=True, cwd=src, capture_output=True, text=True).stdout
terminal_shot("$ python3 fuzz_task_1.py\n" + run("python3 fuzz_task_1.py") + "$ ", "img/term_fuzz.png", size=11)
bf = run("bandit student_app_fixed.py 2>/dev/null")
bf = bf[bf.index("Test results"):].split("Files skipped")[0].rstrip()
pf = run("pylint student_app_fixed.py").strip()
terminal_shot("$ python3 fuzz_fixed.py\n" + run("python3 fuzz_fixed.py") +
              "$ bandit student_app_fixed.py\n" + bf + "\n$ pylint student_app_fixed.py\n" + pf + "\n$ ",
              "img/term_fixed.png", size=11)
