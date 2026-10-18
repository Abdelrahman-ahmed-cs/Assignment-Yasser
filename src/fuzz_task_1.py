import random
import string
import student_app as app

random.seed(1)          # عشان النتيجة تتكرر نفسها كل مرة
found = {}              # (الدالة, نوع الخطأ) -> أول input فجّره


def record(func, exc, data):
    key = (func, type(exc).__name__)
    if key not in found:
        found[key] = (data, str(exc))


def rand_text():
    chars = string.ascii_letters + string.digits + ",;. -'\""
    return "".join(random.choice(chars) for _ in range(random.randint(0, 25)))


def rand_record():
    # نص قريب من الفورمات الصح عشان نوصل لأعماق الدالة
    name = random.choice(["Ali", "Sara Ahmed", "Omar Bin Ali", "", "A B"])
    age = random.choice(["20", "-5", "abc", "", "999999"])
    grades = ";".join(
        random.choice(["90", "85", "100", "-5", "x", "", "150"])
        for _ in range(random.randint(0, 4))
    )
    return f"{name},{age},{grades}"


for i in range(20000):
    s = rand_text() if i % 2 else rand_record()
    n = random.randint(-300, 300)
    grades = [random.randint(-200, 200) for _ in range(random.randint(0, 5))]

    tests = [
        ("parse_record",  s,      lambda: app.parse_record(s)),
        ("process_line",  s,      lambda: app.process_line(s)),
        ("make_username", s,      lambda: app.make_username(s)),
        ("letter_grade",  n,      lambda: app.letter_grade(n)),
        ("average",       grades, lambda: app.average(grades)),
    ]
    for name, inp, fn in tests:
        try:
            fn()
        except Exception as e:
            record(name, e, inp)

    # فحص الـ bug اللي مفيهوش crash: درجة سالبة (من -1 لـ -10) لازم تطلع F
    if -10 <= n < 0:
        try:
            r = app.letter_grade(n)
            if r != "F":
                record("letter_grade (wrong result)",
                       AssertionError(f"negative {n} gave {r}"), n)
        except Exception:
            pass   # الـ IndexError اتسجل فوق خلاص


print("=== UNIQUE FINDINGS ===")
for (f, e), (inp, msg) in found.items():
    print(f"{f:28} {e:20} input={inp!r}  msg={msg}")