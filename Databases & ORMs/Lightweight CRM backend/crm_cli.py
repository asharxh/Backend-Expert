import sys
from crm_backend import (
    initialize_db,
    add_customer, get_customers, update_customer, delete_customer,
    add_lead, get_leads, update_lead, delete_lead, convert_lead_to_customer,
    add_interaction, get_interactions, delete_interaction
)

def print_customers():
    customers = get_customers()
    print("\nID | Name | Email | Phone | Company | Created At")
    print("-------------------------------------------------")
    for c in customers:
        print(f"{c[0]} | {c[1]} | {c[2] or ''} | {c[3] or ''} | {c[4] or ''} | {c[5]}")
    print()


def print_leads():
    leads = get_leads()
    print("\nID | Name | Email | Phone | Source | Status | Created At")
    print("-----------------------------------------------------------")
    for l in leads:
        print(f"{l[0]} | {l[1]} | {l[2] or ''} | {l[3] or ''} | {l[4] or ''} | {l[5]} | {l[6]}")
    print()


def print_interactions():
    interactions = get_interactions()
    print("\nID | Type | Notes | Date | Customer | Lead")
    print("------------------------------------------------")
    for i in interactions:
        print(f"{i[0]} | {i[1]} | {i[2]} | {i[3]} | {i[4] or ''} | {i[5] or ''}")
    print()


def customers_menu():
    while True:
        print("\n--- Customers Menu ---")
        print("1. List Customers")
        print("2. Add Customer")
        print("3. Update Customer")
        print("4. Delete Customer")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_customers()
        elif choice == '2':
            name = input("Name: ")
            email = input("Email (optional): ")
            phone = input("Phone (optional): ")
            company = input("Company (optional): ")
            add_customer(name, email, phone, company)
            print("Customer added.")
        elif choice == '3':
            print_customers()
            customer_id = int(input("Enter Customer ID to update: "))
            name = input("New Name (leave blank to skip): ")
            email = input("New Email (leave blank to skip): ")
            phone = input("New Phone (leave blank to skip): ")
            company = input("New Company (leave blank to skip): ")
            update_customer(customer_id, name or None, email or None, phone or None, company or None)
            print("Customer updated.")
        elif choice == '4':
            print_customers()
            customer_id = int(input("Enter Customer ID to delete: "))
            delete_customer(customer_id)
            print("Customer deleted.")
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def leads_menu():
    while True:
        print("\n--- Leads Menu ---")
        print("1. List Leads")
        print("2. Add Lead")
        print("3. Update Lead")
        print("4. Delete Lead")
        print("5. Convert Lead → Customer")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_leads()
        elif choice == '2':
            name = input("Name: ")
            email = input("Email (optional): ")
            phone = input("Phone (optional): ")
            source = input("Source (optional): ")
            add_lead(name, email, phone, source)
            print("Lead added.")
        elif choice == '3':
            print_leads()
            lead_id = int(input("Enter Lead ID to update: "))
            name = input("New Name (blank to skip): ")
            email = input("New Email (blank to skip): ")
            phone = input("New Phone (blank to skip): ")
            source = input("New Source (blank to skip): ")
            status = input("New Status (New/Contacted/Qualified/Lost, blank to skip): ")
            update_lead(lead_id, name or None, email or None, phone or None, source or None, status or None)
            print("Lead updated.")
        elif choice == '4':
            print_leads()
            lead_id = int(input("Enter Lead ID to delete: "))
            delete_lead(lead_id)
            print("Lead deleted.")
        elif choice == '5':
            print_leads()
            lead_id = int(input("Enter Lead ID to convert: "))
            convert_lead_to_customer(lead_id)
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


def interactions_menu():
    while True:
        print("\n--- Interactions Menu ---")
        print("1. List Interactions")
        print("2. Add Interaction")
        print("3. Delete Interaction")
        print("0. Back")
        choice = input("Select option: ")

        if choice == '1':
            print_interactions()
        elif choice == '2':
            type_ = input("Type (Call/Email/Meeting): ")
            notes = input("Notes: ")
            print("\n1. Link to Customer\n2. Link to Lead\n0. None")
            link_choice = input("Select: ")
            customer_id = lead_id = None
            if link_choice == '1':
                print_customers()
                customer_id = int(input("Customer ID: "))
            elif link_choice == '2':
                print_leads()
                lead_id = int(input("Lead ID: "))
            add_interaction(type_, notes, customer_id=customer_id, lead_id=lead_id)
            print("Interaction added.")
        elif choice == '3':
            print_interactions()
            interaction_id = int(input("Enter Interaction ID to delete: "))
            delete_interaction(interaction_id)
            print("Interaction deleted.")
        elif choice == '0':
            break
        else:
            print("Invalid choice.")



def main_menu():
    while True:
        print("\n====== CRM System CLI ======")
        print("1. Manage Customers")
        print("2. Manage Leads")
        print("3. Manage Interactions")
        print("0. Exit")
        choice = input("Select option: ")

        if choice == '1':
            customers_menu()
        elif choice == '2':
            leads_menu()
        elif choice == '3':
            interactions_menu()
        elif choice == '0':
            print("Exiting CRM System. Goodbye!")
            sys.exit()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    initialize_db()
    main_menu()
