import sys
from student_gradebook import (
    initialize_db, add_student, get_students, update_student, delete_student,
    add_course, get_courses, update_course, delete_course,
    add_grade, get_grades, update_grade, delete_grade,
    calculate_student_average, calculate_course_average,
    export_grades_csv, export_grades_json
)

def print_students():
    students = get_students()
    print("\nID | Name | Email")
    print("---------------------")
    for s in students:
        print(f"{s[0]} | {s[1]} | {s[2]}")
    print()


def print_courses():
    courses = get_courses()
    print("\nID | Name | Teacher")
    print("----------------------")
    for c in courses:
        print(f"{c[0]} | {c[1]} | {c[2]}")
    print()


def print_grades():
    grades = get_grades()
    print("\nID | Student | Course | Grade")
    print("-------------------------------")
    for g in grades:
        print(f"{g[0]} | {g[1]} | {g[2]} | {g[3]}")
    print()


def students_menu():
    while True:
        print("\n--- Students Menu ---")
        print("1. List Students")
        print("2. Add Student")
        print("3. Update Student")
        print("4. Delete Student")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_students()
        elif choice == '2':
            name = input("Name: ")
            email = input("Email (optional): ")
            add_student(name, email)
        elif choice == '3':
            print_students()
            student_id = int(input("Enter Student ID to update: "))
            name = input("New Name (leave blank to skip): ")
            email = input("New Email (leave blank to skip): ")
            update_student(student_id, name if name else None, email if email else None)
        elif choice == '4':
            print_students()
            student_id = int(input("Enter Student ID to delete: "))
            delete_student(student_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def courses_menu():
    while True:
        print("\n--- Courses Menu ---")
        print("1. List Courses")
        print("2. Add Course")
        print("3. Update Course")
        print("4. Delete Course")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_courses()
        elif choice == '2':
            name = input("Course Name: ")
            teacher = input("Teacher (optional): ")
            add_course(name, teacher)
        elif choice == '3':
            print_courses()
            course_id = int(input("Enter Course ID to update: "))
            name = input("New Name (leave blank to skip): ")
            teacher = input("New Teacher (leave blank to skip): ")
            update_course(course_id, name if name else None, teacher if teacher else None)
        elif choice == '4':
            print_courses()
            course_id = int(input("Enter Course ID to delete: "))
            delete_course(course_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def grades_menu():
    while True:
        print("\n--- Grades Menu ---")
        print("1. List Grades")
        print("2. Add Grade")
        print("3. Update Grade")
        print("4. Delete Grade")
        print("5. Calculate Student Average")
        print("6. Calculate Course Average")
        print("7. Export Grades CSV")
        print("8. Export Grades JSON")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_grades()
        elif choice == '2':
            print_students()
            student_id = int(input("Student ID: "))
            print_courses()
            course_id = int(input("Course ID: "))
            grade = float(input("Grade: "))
            add_grade(student_id, course_id, grade)
        elif choice == '3':
            print_grades()
            grade_id = int(input("Enter Grade ID to update: "))
            new_grade = float(input("New Grade: "))
            update_grade(grade_id, new_grade)
        elif choice == '4':
            print_grades()
            grade_id = int(input("Enter Grade ID to delete: "))
            delete_grade(grade_id)
        elif choice == '5':
            print_students()
            student_id = int(input("Enter Student ID: "))
            avg = calculate_student_average(student_id)
            print(f"Student Average: {avg if avg else 'No grades'}")
        elif choice == '6':
            print_courses()
            course_id = int(input("Enter Course ID: "))
            avg = calculate_course_average(course_id)
            print(f"Course Average: {avg if avg else 'No grades'}")
        elif choice == '7':
            export_grades_csv()
        elif choice == '8':
            export_grades_json()
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def main_menu():
    while True:
        print("\n====== Student Gradebook CLI ======")
        print("1. Students")
        print("2. Courses")
        print("3. Grades")
        print("0. Exit")
        choice = input("Select option: ")

        if choice == '1':
            students_menu()
        elif choice == '2':
            courses_menu()
        elif choice == '3':
            grades_menu()
        elif choice == '0':
            print("Exiting Gradebook CLI. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    initialize_db()
    main_menu()
