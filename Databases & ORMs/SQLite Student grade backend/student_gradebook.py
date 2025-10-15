import sqlite3
from datetime import datetime
import csv
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "gradebook.db")

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            teacher TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            grade REAL NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id),
            UNIQUE(student_id, course_id)
        )
    ''')

    conn.commit()
    conn.close()


def add_student(name, email=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO students (name, email) VALUES (?, ?)', (name, email))
    conn.commit()
    conn.close()


def get_students():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, email FROM students')
    students = c.fetchall()
    conn.close()
    return students


def update_student(student_id, name=None, email=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, email FROM students WHERE id = ?', (student_id,))
    current = c.fetchone()
    if not current:
        print("Student not found.")
        conn.close()
        return
    new_name = name if name else current[0]
    new_email = email if email else current[1]
    c.execute('UPDATE students SET name = ?, email = ? WHERE id = ?', (new_name, new_email, student_id))
    conn.commit()
    conn.close()


def delete_student(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM students WHERE id = ?', (student_id,))
    c.execute('DELETE FROM grades WHERE student_id = ?', (student_id,))
    conn.commit()
    conn.close()


def add_course(name, teacher=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO courses (name, teacher) VALUES (?, ?)', (name, teacher))
    conn.commit()
    conn.close()


def get_courses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, teacher FROM courses')
    courses = c.fetchall()
    conn.close()
    return courses


def update_course(course_id, name=None, teacher=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, teacher FROM courses WHERE id = ?', (course_id,))
    current = c.fetchone()
    if not current:
        print("Course not found.")
        conn.close()
        return
    new_name = name if name else current[0]
    new_teacher = teacher if teacher else current[1]
    c.execute('UPDATE courses SET name = ?, teacher = ? WHERE id = ?', (new_name, new_teacher, course_id))
    conn.commit()
    conn.close()


def delete_course(course_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM courses WHERE id = ?', (course_id,))
    c.execute('DELETE FROM grades WHERE course_id = ?', (course_id,))
    conn.commit()
    conn.close()


def add_grade(student_id, course_id, grade):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO grades (student_id, course_id, grade) VALUES (?, ?, ?)',
              (student_id, course_id, grade))
    conn.commit()
    conn.close()


def get_grades():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT g.id, s.name, c.name, g.grade
        FROM grades g
        JOIN students s ON g.student_id = s.id
        JOIN courses c ON g.course_id = c.id
    ''')
    grades = c.fetchall()
    conn.close()
    return grades


def update_grade(grade_id, new_grade):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE grades SET grade = ? WHERE id = ?', (new_grade, grade_id))
    conn.commit()
    conn.close()


def delete_grade(grade_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM grades WHERE id = ?', (grade_id,))
    conn.commit()
    conn.close()


def calculate_student_average(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT AVG(grade) FROM grades WHERE student_id = ?', (student_id,))
    avg = c.fetchone()[0]
    conn.close()
    return avg


def calculate_course_average(course_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT AVG(grade) FROM grades WHERE course_id = ?', (course_id,))
    avg = c.fetchone()[0]
    conn.close()
    return avg


def export_grades_csv(file_path="grades_export.csv"):
    grades = get_grades()
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student", "Course", "Grade"])
        for g in grades:
            writer.writerow([g[1], g[2], g[3]])
    print(f"Grades exported to {file_path}")


def export_grades_json(file_path="grades_export.json"):
    grades = get_grades()
    data = [{"student": g[1], "course": g[2], "grade": g[3]} for g in grades]
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Grades exported to {file_path}")


if __name__ == "__main__":
    initialize_db()

    add_student("Alice", "alice@example.com")
    add_student("Bob", "bob@example.com")

    add_course("Mathematics", "Mr. Smith")
    add_course("Physics", "Dr. Brown")

    students = get_students()
    courses = get_courses()
    alice_id = students[0][0]
    bob_id = students[1][0]
    math_id = courses[0][0]
    physics_id = courses[1][0]

    add_grade(alice_id, math_id, 90)
    add_grade(alice_id, physics_id, 85)
    add_grade(bob_id, math_id, 78)
    add_grade(bob_id, physics_id, 82)

    print("\nStudents:")
    print(get_students())
    print("\nCourses:")
    print(get_courses())
    print("\nGrades:")
    print(get_grades())

    print(f"\nAlice's Average: {calculate_student_average(alice_id)}")
    print(f"Mathematics Average: {calculate_course_average(math_id)}")

    export_grades_csv()
    export_grades_json()
