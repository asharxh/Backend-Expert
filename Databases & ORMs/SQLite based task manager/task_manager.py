import sqlite3
from datetime import datetime

def initialize_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            deadline TEXT,
            priority INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


def create_task(title, description="", deadline=None, priority=1, status="Pending"):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO tasks (title, description, deadline, priority, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, deadline, priority, status, created_at))
    conn.commit()
    conn.close()
    print(f"Task '{title}' created.")


def get_all_tasks():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT id, title, status, deadline, priority FROM tasks ORDER BY created_at DESC')
    tasks = c.fetchall()
    conn.close()
    return tasks


def get_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    conn.close()
    return task


def update_task(task_id, title=None, description=None, deadline=None, priority=None, status=None):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT title, description, deadline, priority, status FROM tasks WHERE id = ?', (task_id,))
    current = c.fetchone()
    if not current:
        print("Task not found.")
        conn.close()
        return
    new_title = title if title else current[0]
    new_description = description if description else current[1]
    new_deadline = deadline if deadline else current[2]
    new_priority = priority if priority else current[3]
    new_status = status if status else current[4]

    c.execute('''
        UPDATE tasks
        SET title = ?, description = ?, deadline = ?, priority = ?, status = ?
        WHERE id = ?
    ''', (new_title, new_description, new_deadline, new_priority, new_status, task_id))
    conn.commit()
    conn.close()
    print(f"Task {task_id} updated.")


def delete_task(task_id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    print(f"Task {task_id} deleted.")


def filter_tasks_by_status(status):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT id, title, status, deadline, priority FROM tasks WHERE status = ?', (status,))
    tasks = c.fetchall()
    conn.close()
    return tasks


def filter_tasks_by_deadline(deadline):
    """
    Deadline format: 'YYYY-MM-DD'
    """
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT id, title, status, deadline, priority FROM tasks WHERE deadline = ?', (deadline,))
    tasks = c.fetchall()
    conn.close()
    return tasks


def search_tasks(keyword):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    query = f"%{keyword}%"
    c.execute('SELECT id, title, status, deadline, priority FROM tasks WHERE title LIKE ? OR description LIKE ?', (query, query))
    results = c.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    initialize_db()

    create_task("Finish Python project", "Complete the SQLite blog backend", "2025-10-20", priority=2)
    create_task("Grocery shopping", "Buy fruits and vegetables", "2025-10-16", priority=1)
    create_task("Workout", "30 min cardio", "2025-10-15", priority=3, status="Done")

    print("\nAll Tasks:")
    for t in get_all_tasks():
        print(t)

    print("\nFilter by Status 'Pending':")
    for t in filter_tasks_by_status("Pending"):
        print(t)

    print("\nSearch for 'Python':")
    for t in search_tasks("Python"):
        print(t)

    print("\nGet Task ID 1:")
    print(get_task(1))

    update_task(1, status="Done")
    print("\nAfter Updating Task 1:")
    print(get_task(1))

    delete_task(2)
    print("\nAfter Deleting Task 2:")
    for t in get_all_tasks():
        print(t)
