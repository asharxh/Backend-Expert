import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            type TEXT CHECK(type IN ('Income', 'Expense')) NOT NULL,
            category_id INTEGER,
            description TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    ''')

    conn.commit()
    conn.close()


def add_category(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def get_categories():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return categories


def update_category(category_id, name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE categories SET name = ? WHERE id = ?', (name, category_id))
    conn.commit()
    conn.close()


def delete_category(category_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    c.execute('UPDATE transactions SET category_id = NULL WHERE category_id = ?', (category_id,))
    conn.commit()
    conn.close()


def add_transaction(amount, type_, category_id=None, description="", date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date = date if date else datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO transactions (amount, type, category_id, description, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (amount, type_, category_id, description, date))
    conn.commit()
    conn.close()


def get_transactions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT t.id, t.amount, t.type, c.name, t.description, t.date
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        ORDER BY t.date DESC
    ''')
    transactions = c.fetchall()
    conn.close()
    return transactions


def update_transaction(transaction_id, amount=None, type_=None, category_id=None, description=None, date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT amount, type, category_id, description, date FROM transactions WHERE id = ?', (transaction_id,))
    current = c.fetchone()
    if not current:
        print("Transaction not found.")
        conn.close()
        return
    new_amount = amount if amount else current[0]
    new_type = type_ if type_ else current[1]
    new_category = category_id if category_id is not None else current[2]
    new_description = description if description else current[3]
    new_date = date if date else current[4]

    c.execute('''
        UPDATE transactions
        SET amount = ?, type = ?, category_id = ?, description = ?, date = ?
        WHERE id = ?
    ''', (new_amount, new_type, new_category, new_description, new_date, transaction_id))
    conn.commit()
    conn.close()


def delete_transaction(transaction_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()
    conn.close()


def get_balance():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
    income = c.fetchone()[0] or 0
    c.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
    expense = c.fetchone()[0] or 0
    conn.close()
    return income - expense


def category_expenses():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT c.name, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.type='Expense'
        GROUP BY c.name
    ''')
    data = c.fetchall()
    conn.close()
    return data


def filter_transactions_by_date(date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT t.id, t.amount, t.type, c.name, t.description, t.date
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.date = ?
    ''', (date,))
    transactions = c.fetchall()
    conn.close()
    return transactions


def filter_transactions_by_category(category_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT t.id, t.amount, t.type, c.name, t.description, t.date
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.category_id = ?
    ''', (category_id,))
    transactions = c.fetchall()
    conn.close()
    return transactions


if __name__ == "__main__":
    initialize_db()

    add_category("Food")
    add_category("Transport")
    add_category("Salary")

    categories = get_categories()
    food_id = categories[0][0]
    transport_id = categories[1][0]
    salary_id = categories[2][0]

    add_transaction(5000, "Income", salary_id, "Monthly Salary")
    add_transaction(50, "Expense", food_id, "Lunch")
    add_transaction(20, "Expense", transport_id, "Bus fare")

    print("\nAll Transactions:")
    for t in get_transactions():
        print(t)

    print(f"\nCurrent Balance: {get_balance()}")
    print("\nCategory-wise Expenses:")
    for c in category_expenses():
        print(c)

    print("\nFilter Transactions by Date '2025-10-15':")
    for t in filter_transactions_by_date("2025-10-15"):
        print(t)
