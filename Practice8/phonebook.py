import psycopg2
from connect import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    try:
        with open("Practice8/functions.sql") as f:
            cur.execute(f.read())
        with open("Practice8/procedures.sql") as f:
            cur.execute(f.read())
        conn.commit()
        print("The database was successfully initialized (functions and procedures were updated).")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        cur.close()
        conn.close()

def find_contacts_by_pattern(pattern):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM find_contacts(%s)", (pattern,))
        rows = cur.fetchall()
        if not rows:
            print(f"Nothing found for '{pattern}'.")
        else:
            print(f"\nMatches found: {len(rows)}")
            print("-"*30)
            for row in rows:
                print(f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
            print("-"*30)
    except Exception as e:
        print(f"Search error: {e}")
    finally:
        cur.close()
        conn.close()

def add_or_update_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL insert_update_contact(%s, %s)", (name, phone))
        conn.commit()
        print(f"Contact {name} was saved successfully")
    except Exception as e:
        print(f"Error while inserting: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def mass_import(names, phones):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL mass_insert_contacts(%s, %s, NULL)", (names, phones))
        incorrect = cur.fetchone()
        print(f"Incorrect data: {incorrect}")
        conn.commit()
    except Exception as e:
        print(f"Bulk importin error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_paged_list(page_size, page_number):
    conn = get_connection()
    cur = conn.cursor()
    try:
        offset = (page_number - 1) * page_size
        cur.execute("SELECT * FROM get_contacts_paged(%s, %s)", (page_size, offset))
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Pagination error: {e}")
    finally:
        cur.close()
        conn.close()

def remove_contact(identifier):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL delete_contact(%s)", (identifier,))
        conn.commit()
        print(f"Request to delete '{identifier}' completed.")
    except Exception as e:
        print(f"Deleting error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def print_menu():
    print("\n--- MANAGING YOUR PHONE BOOK ---")
    print("1. Search for a contact with pattern (by name or number)")
    print("2. Add or update a contact")
    print("3. Bulk import contacts")
    print("4. View the list (by pages)")
    print("5. Delete a contact")
    print("0. Exit")
    print("------------------------------------")

def main():
    while True:
        print_menu()
        choise = input("Choose an operation: ")

        if choise == "1":
            pattern = input("Enter part of a name, surname or phone number to serch: ")
            find_contacts_by_pattern(pattern)
        elif choise == "2":
            name = input("Enter name: ")
            phone = input("Enter phone number: ")
            add_or_update_contact(name, phone)
        elif choise == "3":
            print("Enter names separated by commas: ")
            names = [n.strip() for n in input().split(',')]
            print("Enter phone numbers separated by commas: ")
            phones = [p.strip() for p in input().split(',')]

            if len(names) == len(phones):
                mass_import(names, phones)
            else:
                print("Error: the number of names and phone numbers does not match!")
        elif choise == "4":
            try:
                page = int(input("Enter the page number: "))
                size = int(input("Enter the number of lines per page: "))
                get_paged_list(size, page)
            except ValueError:
                print("Error: Please enter an integer.")
        elif choise == "5":
            identifier = input("Enter a name or phone number to delete: ")
            confirm = input(f"Are you sure you want to delete '{identifier}'? (y/n): ")
            if confirm.lower() == "y":
                remove_contact(identifier)
        elif choise == "0":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Incorrect input, please try again.")

if __name__ == "__main__":
    init_db()
    main()