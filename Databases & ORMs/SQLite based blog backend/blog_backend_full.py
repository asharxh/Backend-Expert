import sqlite3
from datetime import datetime

def initialize_db():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(author_id) REFERENCES authors(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS post_categories (
            post_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(category_id) REFERENCES categories(id),
            PRIMARY KEY(post_id, category_id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id)
        )
    ''')

    conn.commit()
    conn.close()


def add_author(name, email=None):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO authors (name, email) VALUES (?, ?)', (name, email))
    conn.commit()
    conn.close()


def get_authors():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT id, name, email FROM authors')
    authors = c.fetchall()
    conn.close()
    return authors


def update_author(author_id, name=None, email=None):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT name, email FROM authors WHERE id = ?', (author_id,))
    current = c.fetchone()
    if not current:
        print("Author not found.")
        conn.close()
        return
    new_name = name if name else current[0]
    new_email = email if email else current[1]
    c.execute('UPDATE authors SET name = ?, email = ? WHERE id = ?', (new_name, new_email, author_id))
    conn.commit()
    conn.close()


def delete_author(author_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('DELETE FROM authors WHERE id = ?', (author_id,))
    conn.commit()
    conn.close()



def add_category(name):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()


def get_categories():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM categories')
    categories = c.fetchall()
    conn.close()
    return categories


def update_category(category_id, name):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('UPDATE categories SET name = ? WHERE id = ?', (name, category_id))
    conn.commit()
    conn.close()


def delete_category(category_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    c.execute('DELETE FROM post_categories WHERE category_id = ?', (category_id,))
    conn.commit()
    conn.close()


def create_post(title, content, author_id, category_ids=None):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO posts (title, content, author_id, created_at) VALUES (?, ?, ?, ?)',
              (title, content, author_id, created_at))
    post_id = c.lastrowid
    if category_ids:
        for cat_id in category_ids:
            c.execute('INSERT INTO post_categories (post_id, category_id) VALUES (?, ?)', (post_id, cat_id))
    conn.commit()
    conn.close()


def get_all_posts():
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.title, a.name as author, p.created_at
        FROM posts p
        JOIN authors a ON p.author_id = a.id
        ORDER BY p.created_at DESC
    ''')
    posts = c.fetchall()
    conn.close()
    return posts


def get_post(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.title, p.content, a.name as author, p.created_at
        FROM posts p
        JOIN authors a ON p.author_id = a.id
        WHERE p.id = ?
    ''', (post_id,))
    post = c.fetchone()

    c.execute('''
        SELECT c.name
        FROM categories c
        JOIN post_categories pc ON c.id = pc.category_id
        WHERE pc.post_id = ?
    ''', (post_id,))
    categories = [row[0] for row in c.fetchall()]

    c.execute('''
        SELECT author, content, created_at
        FROM comments
        WHERE post_id = ?
        ORDER BY created_at ASC
    ''', (post_id,))
    comments = c.fetchall()

    conn.close()
    return {'post': post, 'categories': categories, 'comments': comments}


def update_post(post_id, title=None, content=None, author_id=None, category_ids=None):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('SELECT title, content, author_id FROM posts WHERE id = ?', (post_id,))
    current = c.fetchone()
    if not current:
        print("Post not found.")
        conn.close()
        return
    new_title = title if title else current[0]
    new_content = content if content else current[1]
    new_author = author_id if author_id else current[2]
    c.execute('UPDATE posts SET title = ?, content = ?, author_id = ? WHERE id = ?',
              (new_title, new_content, new_author, post_id))
    if category_ids is not None:
        c.execute('DELETE FROM post_categories WHERE post_id = ?', (post_id,))
        for cat_id in category_ids:
            c.execute('INSERT INTO post_categories (post_id, category_id) VALUES (?, ?)', (post_id, cat_id))
    conn.commit()
    conn.close()


def delete_post(post_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    c.execute('DELETE FROM post_categories WHERE post_id = ?', (post_id,))
    c.execute('DELETE FROM comments WHERE post_id = ?', (post_id,))
    conn.commit()
    conn.close()


def add_comment(post_id, author, content):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO comments (post_id, author, content, created_at) VALUES (?, ?, ?, ?)',
              (post_id, author, content, created_at))
    conn.commit()
    conn.close()


def update_comment(comment_id, content):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('UPDATE comments SET content = ? WHERE id = ?', (content, comment_id))
    conn.commit()
    conn.close()


def delete_comment(comment_id):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    c.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
    conn.commit()
    conn.close()



def search_posts(keyword):
    conn = sqlite3.connect('blog.db')
    c = conn.cursor()
    query = f"%{keyword}%"
    c.execute('''
        SELECT p.id, p.title, a.name, p.created_at
        FROM posts p
        JOIN authors a ON p.author_id = a.id
        WHERE p.title LIKE ? OR p.content LIKE ?
    ''', (query, query))
    results = c.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    initialize_db()

    add_author("Alice", "alice@example.com")
    add_author("Bob", "bob@example.com")
    alice_id = get_authors()[0][0]
    bob_id = get_authors()[1][0]

    add_category("Python")
    add_category("Tips")
    add_category("Lifestyle")
    python_id = get_categories()[0][0]
    tips_id = get_categories()[1][0]


    create_post("My First Post", "Hello world content", alice_id, [python_id, tips_id])
    create_post("Healthy Living", "Tips for lifestyle", bob_id, [get_categories()[2][0]])

    add_comment(1, "Charlie", "Great post!")
    add_comment(1, "Dana", "Very helpful.")

    print("\nAll Posts:")
    for p in get_all_posts():
        print(p)

    print("\nDetails of Post 1:")
    post_details = get_post(1)
    print(post_details)

    print("\nSearch for 'Tips':")
    for p in search_posts("Tips"):
        print(p)
