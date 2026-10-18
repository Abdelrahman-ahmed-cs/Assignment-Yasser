"""
Student Records Manager - FIXED version.

Every bug found by the fuzzer and every weakness reported by
Bandit / Pylint in student_app.py has been fixed here.

Input format for a student record:   name,age,grade1;grade2;grade3
Example:                              Ali,20,90;85;77
"""

import ast
import hashlib
import hmac
import json
import operator
import os
import shutil
import sqlite3
from pathlib import Path

# Fix: the admin password hash comes from the environment, never from the source
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

DB_FILE = "students.db"
BACKUP_DIR = Path("backups")

LETTERS = ["F", "F", "F", "F", "F", "F", "D", "C", "B", "A"]


class InvalidRecordError(ValueError):
    """Raised on purpose when the user gives bad input (a controlled error)."""


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def parse_record(line):
    """Turn 'name,age,g1;g2;g3' into a dictionary, validating every field."""
    parts = line.split(",")
    if len(parts) != 3:
        raise InvalidRecordError("expected exactly 3 fields: name,age,grades")
    name, age_text, grades_text = (p.strip() for p in parts)
    if not name:
        raise InvalidRecordError("name is empty")
    if not age_text.isdigit() or not 1 <= int(age_text) <= 120:
        raise InvalidRecordError("age must be a whole number between 1 and 120")
    grades = []
    for g in grades_text.split(";"):
        g = g.strip()
        if not g.isdigit() or int(g) > 100:
            raise InvalidRecordError(f"bad grade {g!r} (must be 0-100)")
        grades.append(int(g))
    return {"name": name, "age": int(age_text), "grades": grades}


def average(grades):
    """Average of a non-empty list of grades."""
    if not grades:
        raise InvalidRecordError("cannot average an empty list of grades")
    return sum(grades) / len(grades)


def letter_grade(score):
    """Convert a numeric score (0-100) to a letter."""
    if not 0 <= score <= 100:
        raise InvalidRecordError(f"score {score} is outside 0-100")
    return LETTERS[min(score // 10, 9)]          # 100 maps to 'A'


def make_username(name):
    """Build a username from the first 3 letters of the first and last name."""
    words = name.split()                          # any amount of whitespace
    if len(words) < 2:
        raise InvalidRecordError("name needs a first and a last name")
    return (words[0][:3] + words[-1][:3]).lower()


def process_line(line):
    """Full pipeline used by the app: parse -> average -> letter."""
    record = parse_record(line)
    avg = average(record["grades"])
    return record["name"], avg, letter_grade(int(avg))


# ---------------------------------------------------------------------------
# Storage / admin features
# ---------------------------------------------------------------------------

def save_student(record):
    """Insert a student using a parameterised query (no SQL injection)."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS students (name TEXT, age INT)")
        conn.execute("INSERT INTO students VALUES (?, ?)",
                     (record["name"], record["age"]))


def find_student(name):
    """Look a student up by name using a parameterised query."""
    with sqlite3.connect(DB_FILE) as conn:
        return conn.execute("SELECT * FROM students WHERE name = ?",
                            (name,)).fetchall()


def hash_password(password, salt=None):
    """Salted PBKDF2-SHA256 instead of MD5. Returns 'salt$hash' in hex."""
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + "$" + digest.hex()


def check_admin(password):
    """Compare against the stored hash in constant time."""
    if "$" not in ADMIN_PASSWORD_HASH:
        return False
    salt_hex, _ = ADMIN_PASSWORD_HASH.split("$", 1)
    candidate = hash_password(password, bytes.fromhex(salt_hex))
    return hmac.compare_digest(candidate, ADMIN_PASSWORD_HASH)


_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos}


def calculate(expression):
    """Safe calculator: only numbers and + - * / are allowed (no eval)."""
    def walk(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.left), walk(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.operand))
        raise InvalidRecordError("only numbers and + - * / are allowed")
    if len(expression) > 100:
        raise InvalidRecordError("expression too long")
    return walk(ast.parse(expression, mode="eval").body)


def backup(filename):
    """Copy the database with shutil - no shell, and the name is sanitised."""
    safe_name = Path(filename).name               # strips any ../ or /path
    if not safe_name or not safe_name.replace(".", "").replace("_", "").isalnum():
        raise InvalidRecordError("backup name may only contain letters, digits, '.' and '_'")
    BACKUP_DIR.mkdir(exist_ok=True)
    shutil.copyfile(DB_FILE, BACKUP_DIR / safe_name)


def load_backup(path):
    """Load backup data as JSON (data only - cannot execute code like pickle)."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Simple menu
# ---------------------------------------------------------------------------

def main():
    """Interactive menu loop."""
    while True:
        print("\n1) Add student  2) Find student  3) Calculator  4) Backup (admin)  5) Quit")
        choice = input("> ").strip()
        try:
            if choice == "1":
                line = input("name,age,grades: ")
                name, avg, letter = process_line(line)   # validate BEFORE saving
                save_student(parse_record(line))
                print(f"Saved {name}: average {avg:.1f} ({letter})")
            elif choice == "2":
                print(find_student(input("name: ")))
            elif choice == "3":
                print(calculate(input("expression: ")))
            elif choice == "4":
                if check_admin(input("admin password: ")):
                    backup(input("backup file name: "))
                    print("Backup done")
                else:
                    print("Wrong password")
            elif choice == "5":
                break
        except (InvalidRecordError, SyntaxError, ZeroDivisionError) as e:
            print("Invalid input:", e)
        except (sqlite3.Error, OSError) as e:
            print("Storage error:", e)


if __name__ == "__main__":
    main()
