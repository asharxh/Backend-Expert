import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "crm.db")


def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            created_at TEXT NOT NULL
        )
    ''')

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            source TEXT,
            status TEXT CHECK(status IN ('New', 'Contacted', 'Qualified', 'Lost')) DEFAULT 'New',
            created_at TEXT NOT NULL
        )
    ''')

   
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            notes TEXT,
            date TEXT NOT NULL,
            customer_id INTEGER,
            lead_id INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(id),
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        )
    ''')

    conn.commit()
    conn.close()


def add_customer(name, email=None, phone=None, company=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO customers (name, email, phone, company, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, email, phone, company, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def get_customers():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone, company, created_at FROM customers')
    customers = c.fetchall()
    conn.close()
    return customers


def update_customer(customer_id, name=None, email=None, phone=None, company=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, email, phone, company FROM customers WHERE id = ?', (customer_id,))
    current = c.fetchone()
    if not current:
        print("Customer not found.")
        conn.close()
        return
    new_name = name if name else current[0]
    new_email = email if email else current[1]
    new_phone = phone if phone else current[2]
    new_company = company if company else current[3]
    c.execute('''
        UPDATE customers SET name=?, email=?, phone=?, company=? WHERE id=?
    ''', (new_name, new_email, new_phone, new_company, customer_id))
    conn.commit()
    conn.close()


def delete_customer(customer_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM interactions WHERE customer_id=?', (customer_id,))
    c.execute('DELETE FROM customers WHERE id=?', (customer_id,))
    conn.commit()
    conn.close()


def add_lead(name, email=None, phone=None, source=None, status="New"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO leads (name, email, phone, source, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, source, status, datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()


def get_leads():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, email, phone, source, status, created_at FROM leads')
    leads = c.fetchall()
    conn.close()
    return leads


def update_lead(lead_id, name=None, email=None, phone=None, source=None, status=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, email, phone, source, status FROM leads WHERE id=?', (lead_id,))
    current = c.fetchone()
    if not current:
        print("Lead not found.")
        conn.close()
        return
    new_name = name if name else current[0]
    new_email = email if email else current[1]
    new_phone = phone if phone else current[2]
    new_source = source if source else current[3]
    new_status = status if status else current[4]
    c.execute('''
        UPDATE leads SET name=?, email=?, phone=?, source=?, status=? WHERE id=?
    ''', (new_name, new_email, new_phone, new_source, new_status, lead_id))
    conn.commit()
    conn.close()


def delete_lead(lead_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM interactions WHERE lead_id=?', (lead_id,))
    c.execute('DELETE FROM leads WHERE id=?', (lead_id,))
    conn.commit()
    conn.close()


def convert_lead_to_customer(lead_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, email, phone FROM leads WHERE id=?', (lead_id,))
    lead = c.fetchone()
    if not lead:
        print("Lead not found.")
        conn.close()
        return
    name, email, phone = lead
    add_customer(name, email, phone)
    delete_lead(lead_id)
    print(f"Lead '{name}' converted to customer.")
    conn.close()


def add_interaction(type_, notes, customer_id=None, lead_id=None, date=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    date = date if date else datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO interactions (type, notes, date, customer_id, lead_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (type_, notes, date, customer_id, lead_id))
    conn.commit()
    conn.close()


def get_interactions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT i.id, i.type, i.notes, i.date,
               c.name as customer_name,
               l.name as lead_name
        FROM interactions i
        LEFT JOIN customers c ON i.customer_id = c.id
        LEFT JOIN leads l ON i.lead_id = l.id
        ORDER BY i.date DESC
    ''')
    interactions = c.fetchall()
    conn.close()
    return interactions


def delete_interaction(interaction_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM interactions WHERE id=?', (interaction_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_db()

    
    add_lead("Alice Johnson", "alice@demo.com", "123456789", "Website")
    add_lead("Bob Smith", "bob@demo.com", "987654321", "Referral")

    add_customer("Charlie Brown", "charlie@demo.com", "555123456", "TechCorp")

    add_interaction("Call", "Follow-up with Alice", lead_id=1)
    add_interaction("Meeting", "Discussed proposal", customer_id=1)

    print("\n--- Leads ---")
    for l in get_leads():
        print(l)

    print("\n--- Customers ---")
    for c in get_customers():
        print(c)

    print("\n--- Interactions ---")
    for i in get_interactions():
        print(i)

    
    convert_lead_to_customer(1)

    print("\n--- Updated Customers ---")
    for c in get_customers():
        print(c)
