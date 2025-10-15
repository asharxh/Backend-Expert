import sys
from task_manager import (
    initialize_db, create_task, get_all_tasks, get_task, update_task, delete_task,
    filter_tasks_by_status, filter_tasks_by_deadline, search_tasks
)

def print_tasks(tasks):
    if not tasks:
        print("No tasks found.\n")
        return
    print("\nID | Title | Status | Deadline | Priority")
    print("--------------------------------------------")
    for t in tasks:
        print(f"{t[0]} | {t[1]} | {t[2]} | {t[3]} | {t[4]}")
    print()


def view_task_details():
    task_id = int(input("Enter Task ID: "))
    task = get_task(task_id)
    if not task:
        print("Task not found.\n")
        return
    print(f"\nID: {task[0]}\nTitle: {task[1]}\nDescription: {task[2]}\nDeadline: {task[3]}\nPriority: {task[4]}\nStatus: {task[5]}\nCreated At: {task[6]}\n")


def menu():
    while True:
        print("========== Task Manager CLI ==========")
        print("1. View All Tasks")
        print("2. Add Task")
        print("3. Update Task")
        print("4. Delete Task")
        print("5. Filter Tasks by Status")
        print("6. Filter Tasks by Deadline")
        print("7. Search Tasks")
        print("8. View Task Details")
        print("0. Exit")
        choice = input("Select option: ")

        if choice == '1':
            tasks = get_all_tasks()
            print_tasks(tasks)
        elif choice == '2':
            title = input("Title: ")
            description = input("Description (optional): ")
            deadline = input("Deadline (YYYY-MM-DD, optional): ")
            priority = input("Priority (1-5, default 1): ")
            status = input("Status (Pending/Done, default Pending): ")
            create_task(
                title,
                description,
                deadline if deadline else None,
                int(priority) if priority else 1,
                status if status else "Pending"
            )
        elif choice == '3':
            task_id = int(input("Task ID to update: "))
            title = input("New Title (leave blank to skip): ")
            description = input("New Description (leave blank to skip): ")
            deadline = input("New Deadline (YYYY-MM-DD, leave blank to skip): ")
            priority = input("New Priority (1-5, leave blank to skip): ")
            status = input("New Status (Pending/Done, leave blank to skip): ")
            update_task(
                task_id,
                title if title else None,
                description if description else None,
                deadline if deadline else None,
                int(priority) if priority else None,
                status if status else None
            )
        elif choice == '4':
            task_id = int(input("Task ID to delete: "))
            delete_task(task_id)
        elif choice == '5':
            status = input("Enter Status to filter (Pending/Done): ")
            tasks = filter_tasks_by_status(status)
            print_tasks(tasks)
        elif choice == '6':
            deadline = input("Enter Deadline to filter (YYYY-MM-DD): ")
            tasks = filter_tasks_by_deadline(deadline)
            print_tasks(tasks)
        elif choice == '7':
            keyword = input("Enter keyword to search: ")
            tasks = search_tasks(keyword)
            print_tasks(tasks)
        elif choice == '8':
            view_task_details()
        elif choice == '0':
            print("Exiting Task Manager CLI. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    initialize_db()
    menu()
