"""
Student Records Manager  (Part 1 - the program under test)

A small command-line program that stores students and their grades.

Input format for a student record:   name,age,grade1;grade2;grade3
Example:                              Ali,20,90;85;77

NOTE FOR THE COURSE: this program contains bugs and security weaknesses
ON PURPOSE so that the testers (fuzzing + static analysis) can find them.
Do NOT use this code in a real system.
"""

import hashlib
import pickle
import sqlite3
import subprocess

# Weakness: hard-coded admin password in the source code
ADMIN_PASSWORD = "admin123"

DB_FILE = "students.db"

# Letter grade table: index 0 = 0-9, 1 = 10-19, ... 9 = 90-99
LETTERS = ["F", "F", "F", "F", "F", "F", "D", "C", "B", "A"]


# ---------------------------------------------------------------------------
# Core logic (these are the functions the fuzzer attacks)
# ---------------------------------------------------------------------------

def parse_record(line):
    """Turn 'name,age,g1;g2;g3' into a dictionary."""
    parts = line.split(",")
    name = parts[0]
    age = int(parts[1])              # Bug: crashes if age is missing or not a number
    grades = [int(g) for g in parts[2].split(";")]   # Bug: crashes on bad grades
    return {"name": name, "age": age, "grades": grades}


def average(grades):
    """Average of a list of grades."""
    return sum(grades) / len(grades)  # Bug: division by zero on empty list


def letter_grade(score):
    """Convert a numeric score to a letter."""
    return LETTERS[score // 10]       # Bug: score 100+ -> IndexError,
                                      #      negative score -> wrong letter


def make_username(name):
    """Build a short username from the first 3 letters of the first and last name."""
    first, last = name.split(" ")     # Bug: crashes unless exactly ONE space
    return (first[:3] + last[:3]).lower()


def process_line(line):
    """Full pipeline used by the app: parse -> average -> letter."""
    record = parse_record(line)
    avg = average(record["grades"])
    return record["name"], avg, letter_grade(int(avg))


# ---------------------------------------------------------------------------
# Storage / admin features (these are where static analysis finds problems)
# ---------------------------------------------------------------------------

def save_student(record):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS students (name TEXT, age INT)")
    # Weakness: SQL built with string formatting -> SQL injection
    conn.execute("INSERT INTO students VALUES ('%s', %d)" % (record["name"], record["age"]))
    conn.commit()
    conn.close()


def find_student(name):
    conn = sqlite3.connect(DB_FILE)
    # Weakness: SQL injection again
    rows = conn.execute("SELECT * FROM students WHERE name = '" + name + "'").fetchall()
    conn.close()
    return rows


def hash_password(password):
    # Weakness: MD5 is a broken hash for passwords
    return hashlib.md5(password.encode()).hexdigest()


def check_admin(password):
    return password == ADMIN_PASSWORD


def calculate(expression):
    # Weakness: eval() runs ANY Python code the user types
    return eval(expression)


def backup(filename):
    # Weakness: user input passed to the shell -> command injection
    subprocess.call("copy " + DB_FILE + " " + filename, shell=True)


def load_backup(path):
    # Weakness: unpickling untrusted data can execute code
    with open(path, "rb") as f:
        return pickle.load(f)


# ---------------------------------------------------------------------------
# Simple menu
# ---------------------------------------------------------------------------

def main():
    while True:
        print("\n1) Add student  2) Find student  3) Calculator  4) Backup (admin)  5) Quit")
        choice = input("> ").strip()
        try:
            if choice == "1":
                line = input("name,age,grades: ")
                save_student(parse_record(line))
                name, avg, letter = process_line(line)
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
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
