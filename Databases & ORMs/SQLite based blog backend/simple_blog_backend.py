import sqlite3
from datetime import datetime

def initialize_db():
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()


def create_post(title, content, author):
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO posts (title, content, author, created_at)
        VALUES (?, ?, ?, ?)
    ''', (title, content, author, created_at))
    conn.commit()
    conn.close()
    print(f"Post '{title}' created successfully.")


def get_all_posts():
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    c.execute('SELECT id, title, author, created_at FROM posts')
    posts = c.fetchall()
    conn.close()
    return posts


def get_post(post_id):
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = c.fetchone()
    conn.close()
    return post


def update_post(post_id, title=None, content=None, author=None):
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    
    c.execute('SELECT title, content, author FROM posts WHERE id = ?', (post_id,))
    current = c.fetchone()
    if not current:
        print("Post not found.")
        conn.close()
        return
    
    new_title = title if title else current[0]
    new_content = content if content else current[1]
    new_author = author if author else current[2]
    
    c.execute('''
        UPDATE posts
        SET title = ?, content = ?, author = ?
        WHERE id = ?
    ''', (new_title, new_content, new_author, post_id))
    
    conn.commit()
    conn.close()
    print(f"Post {post_id} updated successfully.")


def delete_post(post_id):
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    print(f"Post {post_id} deleted successfully.")


def search_posts(keyword):
    conn = sqlite3.connect('simple_blog.db')
    c = conn.cursor()
    query = f"%{keyword}%"
    c.execute('SELECT id, title, author, created_at FROM posts WHERE title LIKE ? OR content LIKE ?', (query, query))
    results = c.fetchall()
    conn.close()
    return results


if __name__ == "__main__":
    initialize_db()
    
    create_post("My First Post", "This is the content of my first post.", "Alice")
    create_post("Python Tips", "Some useful tips for Python.", "Bob")
    
    print("\nAll Posts:")
    for post in get_all_posts():
        print(post)
    
    print("\nGet Post ID 1:")
    print(get_post(1))
    
    update_post(1, content="Updated content of my first post.")
    
    print("\nSearch for 'Python':")
    for post in search_posts("Python"):
        print(post)
    
    delete_post(2)
    
    print("\nAll Posts after deletion:")
    for post in get_all_posts():
        print(post)
