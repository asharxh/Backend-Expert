import sys
from blog_backend_full import (
    initialize_db, add_author, get_authors, update_author, delete_author,
    add_category, get_categories, update_category, delete_category,
    create_post, get_all_posts, get_post, update_post, delete_post,
    add_comment, update_comment, delete_comment, search_posts
)


def print_authors():
    authors = get_authors()
    print("\nAuthors:")
    for a in authors:
        print(f"ID: {a[0]}, Name: {a[1]}, Email: {a[2]}")
    print()

def print_categories():
    categories = get_categories()
    print("\nCategories:")
    for c in categories:
        print(f"ID: {c[0]}, Name: {c[1]}")
    print()

def print_posts():
    posts = get_all_posts()
    print("\nPosts:")
    for p in posts:
        print(f"ID: {p[0]}, Title: {p[1]}, Author: {p[2]}, Created At: {p[3]}")
    print()

def view_post_details():
    post_id = int(input("Enter Post ID: "))
    details = get_post(post_id)
    if not details['post']:
        print("Post not found.\n")
        return
    p = details['post']
    print(f"\nTitle: {p[1]}\nAuthor: {p[3]}\nCreated At: {p[4]}\nContent: {p[2]}")
    print(f"Categories: {', '.join(details['categories'])}")
    print("Comments:")
    for c in details['comments']:
        print(f" - {c[0]} ({c[2]}): {c[1]}")
    print()

def menu():
    while True:
        print("========== Mini Blog CLI ==========")
        print("1. Authors")
        print("2. Categories")
        print("3. Posts")
        print("4. Comments")
        print("5. Search Posts")
        print("0. Exit")
        choice = input("Select option: ")

        if choice == '1':
            authors_menu()
        elif choice == '2':
            categories_menu()
        elif choice == '3':
            posts_menu()
        elif choice == '4':
            comments_menu()
        elif choice == '5':
            keyword = input("Enter keyword to search: ")
            results = search_posts(keyword)
            print("\nSearch Results:")
            for r in results:
                print(f"ID: {r[0]}, Title: {r[1]}, Author: {r[2]}, Created At: {r[3]}")
            print()
        elif choice == '0':
            print("Exiting CLI. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice.\n")

def authors_menu():
    while True:
        print("\n--- Authors Menu ---")
        print("1. List Authors")
        print("2. Add Author")
        print("3. Update Author")
        print("4. Delete Author")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_authors()
        elif choice == '2':
            name = input("Name: ")
            email = input("Email (optional): ")
            add_author(name, email)
        elif choice == '3':
            print_authors()
            author_id = int(input("Enter Author ID to update: "))
            name = input("New Name (leave blank to skip): ")
            email = input("New Email (leave blank to skip): ")
            update_author(author_id, name if name else None, email if email else None)
        elif choice == '4':
            print_authors()
            author_id = int(input("Enter Author ID to delete: "))
            delete_author(author_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.\n")


def categories_menu():
    while True:
        print("\n--- Categories Menu ---")
        print("1. List Categories")
        print("2. Add Category")
        print("3. Update Category")
        print("4. Delete Category")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_categories()
        elif choice == '2':
            name = input("Category Name: ")
            add_category(name)
        elif choice == '3':
            print_categories()
            category_id = int(input("Enter Category ID to update: "))
            name = input("New Name: ")
            update_category(category_id, name)
        elif choice == '4':
            print_categories()
            category_id = int(input("Enter Category ID to delete: "))
            delete_category(category_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.\n")


def posts_menu():
    while True:
        print("\n--- Posts Menu ---")
        print("1. List Posts")
        print("2. View Post Details")
        print("3. Add Post")
        print("4. Update Post")
        print("5. Delete Post")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_posts()
        elif choice == '2':
            view_post_details()
        elif choice == '3':
            title = input("Title: ")
            content = input("Content: ")
            print_authors()
            author_id = int(input("Author ID: "))
            print_categories()
            cat_ids = input("Category IDs (comma-separated): ")
            cat_list = [int(x.strip()) for x in cat_ids.split(',')] if cat_ids else None
            create_post(title, content, author_id, cat_list)
        elif choice == '4':
            print_posts()
            post_id = int(input("Enter Post ID to update: "))
            title = input("New Title (leave blank to skip): ")
            content = input("New Content (leave blank to skip): ")
            print_authors()
            author_input = input("New Author ID (leave blank to skip): ")
            author_id = int(author_input) if author_input else None
            print_categories()
            cat_ids = input("New Category IDs (comma-separated, leave blank to skip): ")
            cat_list = [int(x.strip()) for x in cat_ids.split(',')] if cat_ids else None
            update_post(post_id, title if title else None, content if content else None, author_id, cat_list)
        elif choice == '5':
            print_posts()
            post_id = int(input("Enter Post ID to delete: "))
            delete_post(post_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.\n")


def comments_menu():
    while True:
        print("\n--- Comments Menu ---")
        print("1. Add Comment")
        print("2. Update Comment")
        print("3. Delete Comment")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_posts()
            post_id = int(input("Post ID: "))
            author = input("Your Name: ")
            content = input("Comment Content: ")
            add_comment(post_id, author, content)
        elif choice == '2':
            post_id = int(input("Post ID of comment: "))
            details = get_post(post_id)
            if not details['comments']:
                print("No comments found.")
                continue
            print("Comments:")
            for idx, c in enumerate(details['comments'], 1):
                print(f"{idx}. {c[0]} ({c[2]}): {c[1]}")
            comment_num = int(input("Select comment number to update: "))
            new_content = input("New Content: ")
            comment_id = comment_num 
            update_comment(comment_id, new_content)
        elif choice == '3':
            post_id = int(input("Post ID of comment: "))
            details = get_post(post_id)
            if not details['comments']:
                print("No comments found.")
                continue
            print("Comments:")
            for idx, c in enumerate(details['comments'], 1):
                print(f"{idx}. {c[0]} ({c[2]}): {c[1]}")
            comment_num = int(input("Select comment number to delete: "))
            comment_id = comment_num 
            delete_comment(comment_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.\n")

if __name__ == "__main__":
    initialize_db()
    menu()

