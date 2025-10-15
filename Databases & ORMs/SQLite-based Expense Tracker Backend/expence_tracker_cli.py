import sys
from expense_tracker import (
    initialize_db,
    add_category, get_categories, update_category, delete_category,
    add_transaction, get_transactions, update_transaction, delete_transaction,
    get_balance, category_expenses, filter_transactions_by_date, filter_transactions_by_category
)

def print_categories():
    categories = get_categories()
    print("\nID | Name")
    print("-------------")
    for c in categories:
        print(f"{c[0]} | {c[1]}")
    print()


def print_transactions(transactions=None):
    transactions = transactions or get_transactions()
    print("\nID | Amount | Type | Category | Description | Date")
    print("-----------------------------------------------------")
    for t in transactions:
        print(f"{t[0]} | {t[1]} | {t[2]} | {t[3] or 'None'} | {t[4]} | {t[5]}")
    print()


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
            name = input("Enter category name: ")
            add_category(name)
            print("Category added.")
        elif choice == '3':
            print_categories()
            category_id = int(input("Enter category ID to update: "))
            new_name = input("Enter new name: ")
            update_category(category_id, new_name)
            print("Category updated.")
        elif choice == '4':
            print_categories()
            category_id = int(input("Enter category ID to delete: "))
            delete_category(category_id)
            print("Category deleted.")
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def transactions_menu():
    while True:
        print("\n--- Transactions Menu ---")
        print("1. List Transactions")
        print("2. Add Transaction")
        print("3. Update Transaction")
        print("4. Delete Transaction")
        print("5. Filter by Date")
        print("6. Filter by Category")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_transactions()
        elif choice == '2':
            type_ = input("Enter type (Income/Expense): ").capitalize()
            amount = float(input("Enter amount: "))
            print_categories()
            category_id = input("Enter category ID (or leave blank): ")
            category_id = int(category_id) if category_id else None
            description = input("Enter description (optional): ")
            date = input("Enter date (YYYY-MM-DD or leave blank for today): ")
            add_transaction(amount, type_, category_id, description, date if date else None)
            print("Transaction added.")
        elif choice == '3':
            print_transactions()
            transaction_id = int(input("Enter transaction ID to update: "))
            new_amount = input("Enter new amount (or leave blank): ")
            new_type = input("Enter new type (Income/Expense or blank): ")
            print_categories()
            new_category = input("Enter new category ID (or blank): ")
            new_description = input("Enter new description (or blank): ")
            new_date = input("Enter new date (YYYY-MM-DD or blank): ")
            update_transaction(
                transaction_id,
                float(new_amount) if new_amount else None,
                new_type.capitalize() if new_type else None,
                int(new_category) if new_category else None,
                new_description if new_description else None,
                new_date if new_date else None
            )
            print("Transaction updated.")
        elif choice == '4':
            print_transactions()
            transaction_id = int(input("Enter transaction ID to delete: "))
            delete_transaction(transaction_id)
            print("Transaction deleted.")
        elif choice == '5':
            date = input("Enter date (YYYY-MM-DD): ")
            transactions = filter_transactions_by_date(date)
            print_transactions(transactions)
        elif choice == '6':
            print_categories()
            category_id = int(input("Enter category ID: "))
            transactions = filter_transactions_by_category(category_id)
            print_transactions(transactions)
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def reports_menu():
    while True:
        print("\n--- Reports Menu ---")
        print("1. Current Balance")
        print("2. Category-wise Expenses")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            balance = get_balance()
            print(f"\n💰 Current Balance: {balance}")
        elif choice == '2':
            expenses = category_expenses()
            print("\nCategory | Total Spent")
            print("----------------------")
            for e in expenses:
                print(f"{e[0]} | {e[1]}")
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def main_menu():
    while True:
        print("\n====== Expense Tracker CLI ======")
        print("1. Manage Categories")
        print("2. Manage Transactions")
        print("3. View Reports")
        print("0. Exit")
        choice = input("Select option: ")

        if choice == '1':
            categories_menu()
        elif choice == '2':
            transactions_menu()
        elif choice == '3':
            reports_menu()
        elif choice == '0':
            print("Exiting Expense Tracker. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    initialize_db()
    main_menu()
