import psycopg2
from connect import get_connection

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE TABLE contacts (
    user_id SERIAL PRIMARY KEY,
    user_name VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) NOT NULL
);""")
    print("Table created successfully")
def insert_from_csv(file_path):
    with get_connection() as conn:
        with conn.cursor() as cur:
            with open(file_path) as f:
                next(f)
                for line in f:
                    data = line.split(",")
                    cur.execute(
                        "INSERT INTO contacts (user_name, phone_number) VALUES (%s, %s) ON CONFLICT (user_name) DO NOTHING",
                        (data[0].strip(), data[1].strip())
                    )
    print("Data was loaded successfully")

def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone number: ")
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO contacts (user_name, phone_number) VALUES (%s, %s)", (name, phone))
        conn.commit()
        print("Contact is saved")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def update_contact():
    target_name = input("Enter name whose name or number you want to change: ")
    update_option = input("""1. Change name
2. Change phone number
Choose option: """)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                if update_option == "1":
                    new_name = input("Enter new name: ")
                    cur.execute("UPDATE contacts SET user_name = %s WHERE user_name = %s", (new_name, target_name))
                    print("Name has been changed")
                elif update_option == "2":
                    new_phone = input("Enter new phone number: ")
                    cur.execute("UPDATE contacts SET phone_number = %s WHERE user_name = %s", (new_phone, target_name))
                    print("Phone number has been changed")
                else:
                    print("Wrong input! Choose 1 or 2 as option")
    except Exception as e:
        print(f"Error: {e}")

def query_contacts(name_filter=None, phone_prefix=None):
    query = 'SELECT * FROM contacts WHERE TRUE'
    params = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            if name_filter:
                query += " AND user_name ILIKE %s"
                params.append(f"%{name_filter}%")
            if phone_prefix:
                query += " AND phone_number LIKE %s"
                params.append(f"{phone_prefix}%")
            cur.execute(query, params)
            for row in cur.fetchall():
                print(f"ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")

def delete_contact():
    target_name = input("Enter name or number: ")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM contacts WHERE user_name = %s OR phone_number = %s", (target_name, target_name))
    print(f"Operation passed successfully")

while True: 
    print("""--- PHONEBOOK MANAGEMENT ---
    1. Create table
    2. Insert data from a CSV file
    3. Insert data from console
    4. Update contact's name or number
    5. Filters contacts
    6. Delete a contact
    0. Exit""")
    option = input("Choose option: ")
    if option == "1":
        create_table()
    elif option == "2":
        insert_from_csv("Practice7\contacts.csv")
    elif option == "3":
        insert_from_console()
    elif option == "4":
        update_contact()
    elif option == "5":
        print("Enter name filter and phone prefix")
        name_filter = input("Name filter: ")
        phone_prefix = input("Phone prefix: ")
        query_contacts(name_filter, phone_prefix)
    elif option == "6":
        delete_contact()
    elif option == "0":
        break
    else:
        print("Wrong input!")