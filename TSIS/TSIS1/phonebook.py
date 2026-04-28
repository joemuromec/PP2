#!/usr/bin/env python3
"""
phonebook.py – Extended Phonebook Console Application
Covers Tasks 3.1 – 3.4:
  • Extended contact model (phones, email, birthday, group)
  • Advanced search / filter / sort / pagination
  • Import / export (JSON + extended CSV)
  • New stored procedures (add_phone, move_to_group, search_contacts)
"""

import csv
import json
import os
import sys
from datetime import date, datetime

from connect import get_connection, get_cursor

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nPress Enter to continue...")


def header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def fmt_contact(row) -> str:
    """Pretty-print a single contact row (from search/page queries)."""
    bday = row["birthday"].strftime("%Y-%m-%d") if row["birthday"] else "—"
    group = row["group_name"] or "—"
    phones = row["phones"] or "—"
    email = row["email"] or "—"
    return (
        f"  [{row['contact_id']}] {row['name']}\n"
        f"      Email   : {email}\n"
        f"      Birthday: {bday}   Group: {group}\n"
        f"      Phones  : {phones}"
    )


# ─────────────────────────────────────────────────────────────
# 3.1  CRUD helpers
# ─────────────────────────────────────────────────────────────

def add_contact():
    header("Add Contact")
    name = input("Full name       : ").strip()
    if not name:
        print("Name is required."); pause(); return

    email    = input("Email (optional): ").strip() or None
    bday_raw = input("Birthday YYYY-MM-DD (optional): ").strip() or None
    birthday = None
    if bday_raw:
        try:
            birthday = datetime.strptime(bday_raw, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format – birthday skipped.")

    # Show groups
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            groups = cur.fetchall()
            print("\nGroups:")
            for g in groups:
                print(f"  {g['id']}. {g['name']}")
            gid_raw = input("Group ID (optional): ").strip()
            group_id = int(gid_raw) if gid_raw.isdigit() else None

            cur.execute(
                "INSERT INTO contacts (name, email, birthday, group_id) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (name, email, birthday, group_id),
            )
            contact_id = cur.fetchone()[0]
            print(f"\n✓ Contact added with ID {contact_id}.")

            # Add phones
            while True:
                phone = input("Add phone (blank to finish): ").strip()
                if not phone:
                    break
                ptype = input("Type (home/work/mobile): ").strip().lower()
                if ptype not in ("home", "work", "mobile"):
                    ptype = "mobile"
                cur.execute(
                    "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                    (contact_id, phone, ptype),
                )
    conn.close()
    pause()


def delete_contact():
    header("Delete Contact")
    cid = input("Enter contact ID to delete: ").strip()
    if not cid.isdigit():
        print("Invalid ID."); pause(); return
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            cur.execute("DELETE FROM contacts WHERE id = %s RETURNING name", (int(cid),))
            row = cur.fetchone()
            if row:
                print(f"✓ Deleted '{row[0]}'.")
            else:
                print("Contact not found.")
    conn.close()
    pause()


# ─────────────────────────────────────────────────────────────
# 3.2  Advanced Search / Filter / Sort / Pagination
# ─────────────────────────────────────────────────────────────

PAGE_SIZE = 5


def search_menu():
    """Interactive search / filter / sort / pagination loop."""
    header("Search & Filter Contacts")

    # --- Collect filter/sort options ---
    query      = input("Search (name / email / phone – blank for all): ").strip() or None
    email_filt = input("Filter by email fragment (blank to skip)      : ").strip() or None
    sort_by    = input("Sort by [name / birthday / created_at]        : ").strip() or "name"
    if sort_by not in ("name", "birthday", "created_at"):
        sort_by = "name"

    # Group filter
    conn = get_connection()
    group_id = None
    with conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY name")
            groups = cur.fetchall()
            print("\nFilter by group:")
            print("  0. All groups")
            for g in groups:
                print(f"  {g['id']}. {g['name']}")
            gid_raw = input("Group ID (0 = all): ").strip()
            if gid_raw.isdigit() and int(gid_raw) != 0:
                group_id = int(gid_raw)

    page = 1
    while True:
        clear()
        header(f"Results – page {page}  (sort: {sort_by})")

        conn = get_connection()
        rows = []
        total = 0
        with conn:
            with get_cursor(conn) as cur:
                if query:
                    # Use the stored function for full-text search
                    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
                    all_rows = cur.fetchall()
                    # Apply client-side group / email filter on top
                    if group_id:
                        # Need group_id filtering; re-query properly
                        cur.execute(
                            "SELECT * FROM get_contacts_page(%s,%s,%s,%s,%s)",
                            (page, PAGE_SIZE, sort_by, group_id, email_filt),
                        )
                        rows = cur.fetchall()
                        total = rows[0]["total_rows"] if rows else 0
                    else:
                        total = len(all_rows)
                        start = (page - 1) * PAGE_SIZE
                        rows = all_rows[start : start + PAGE_SIZE]
                else:
                    cur.execute(
                        "SELECT * FROM get_contacts_page(%s,%s,%s,%s,%s)",
                        (page, PAGE_SIZE, sort_by, group_id, email_filt),
                    )
                    rows = cur.fetchall()
                    total = rows[0]["total_rows"] if rows else 0
        conn.close()

        if not rows:
            print("  No contacts found.")
        else:
            for r in rows:
                print(fmt_contact(r))
                print()

        total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        print(f"  Page {page}/{total_pages}  |  Total: {total}")
        print("\n  [n] Next  [p] Prev  [q] Quit")
        nav = input("  Choice: ").strip().lower()
        if nav == "n" and page < total_pages:
            page += 1
        elif nav == "p" and page > 1:
            page -= 1
        elif nav == "q":
            break


# ─────────────────────────────────────────────────────────────
# 3.3  Import / Export
# ─────────────────────────────────────────────────────────────

def export_json():
    header("Export to JSON")
    filename = input("Output filename [contacts_export.json]: ").strip() or "contacts_export.json"

    conn = get_connection()
    contacts = []
    with conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """
                SELECT c.id, c.name, c.email, c.birthday, c.created_at,
                       g.name AS group_name
                FROM contacts c
                LEFT JOIN groups g ON g.id = c.group_id
                ORDER BY c.name
                """
            )
            rows = cur.fetchall()
            for r in rows:
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY id",
                    (r["id"],),
                )
                phones = [{"phone": p["phone"], "type": p["type"]} for p in cur.fetchall()]
                contacts.append({
                    "id":         r["id"],
                    "name":       r["name"],
                    "email":      r["email"],
                    "birthday":   r["birthday"].isoformat() if r["birthday"] else None,
                    "group":      r["group_name"],
                    "phones":     phones,
                    "created_at": r["created_at"].isoformat(),
                })
    conn.close()

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)

    print(f"✓ Exported {len(contacts)} contacts to '{filename}'.")
    pause()


def _upsert_contact_from_dict(cur, record: dict, overwrite: bool) -> str:
    """
    Insert or optionally overwrite a contact from a dict.
    Returns 'inserted', 'overwritten', or 'skipped'.
    """
    name = record.get("name", "").strip()
    if not name:
        return "skipped"

    cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
    existing = cur.fetchone()

    email    = record.get("email") or None
    birthday = None
    if record.get("birthday"):
        try:
            birthday = datetime.strptime(record["birthday"], "%Y-%m-%d").date()
        except ValueError:
            pass

    group_name = record.get("group") or None
    group_id   = None
    if group_name:
        cur.execute("SELECT id FROM groups WHERE name ILIKE %s LIMIT 1", (group_name,))
        g = cur.fetchone()
        if g:
            group_id = g["id"]
        else:
            cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
            group_id = cur.fetchone()[0]

    if existing:
        if not overwrite:
            return "skipped"
        contact_id = existing["id"]
        cur.execute(
            "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
            (email, birthday, group_id, contact_id),
        )
        cur.execute("DELETE FROM phones WHERE contact_id=%s", (contact_id,))
        status = "overwritten"
    else:
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) "
            "VALUES (%s,%s,%s,%s) RETURNING id",
            (name, email, birthday, group_id),
        )
        contact_id = cur.fetchone()[0]
        status = "inserted"

    for ph in record.get("phones", []):
        ptype = ph.get("type", "mobile")
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"
        cur.execute(
            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
            (contact_id, ph["phone"], ptype),
        )
    return status


def import_json():
    header("Import from JSON")
    filename = input("JSON filename [contacts_export.json]: ").strip() or "contacts_export.json"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found."); pause(); return

    with open(filename, encoding="utf-8") as f:
        records = json.load(f)

    inserted = overwritten = skipped = 0
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            for rec in records:
                name = rec.get("name", "").strip()
                cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
                existing = cur.fetchone()

                if existing:
                    ans = input(f"  '{name}' already exists. [s]kip / [o]verwrite? ").strip().lower()
                    overwrite = ans == "o"
                else:
                    overwrite = False   # doesn't matter – no duplicate

                result = _upsert_contact_from_dict(cur, rec, overwrite)
                if result == "inserted":     inserted += 1
                elif result == "overwritten": overwritten += 1
                else:                         skipped += 1

    conn.close()
    print(f"\n✓ Done – inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}.")
    pause()


def import_csv():
    """Extended CSV importer – handles email, birthday, group, phone, phone_type."""
    header("Import from CSV")
    filename = input("CSV filename [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found."); pause(); return

    # Group rows by contact name (one CSV row per phone number is allowed)
    contact_map: dict = {}
    with open(filename, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                continue
            if name not in contact_map:
                contact_map[name] = {
                    "name":     name,
                    "email":    row.get("email", "").strip() or None,
                    "birthday": row.get("birthday", "").strip() or None,
                    "group":    row.get("group", "").strip() or None,
                    "phones":   [],
                }
            phone = row.get("phone", "").strip()
            ptype = row.get("phone_type", "mobile").strip().lower()
            if ptype not in ("home", "work", "mobile"):
                ptype = "mobile"
            if phone:
                contact_map[name]["phones"].append({"phone": phone, "type": ptype})

    inserted = overwritten = skipped = 0
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            for name, rec in contact_map.items():
                cur.execute("SELECT id FROM contacts WHERE name ILIKE %s LIMIT 1", (name,))
                existing = cur.fetchone()

                if existing:
                    ans = input(f"  '{name}' already exists. [s]kip / [o]verwrite? ").strip().lower()
                    overwrite = ans == "o"
                else:
                    overwrite = False

                result = _upsert_contact_from_dict(cur, rec, overwrite)
                if result == "inserted":      inserted += 1
                elif result == "overwritten": overwritten += 1
                else:                         skipped += 1

    conn.close()
    print(f"\n✓ Done – inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}.")
    pause()


# ─────────────────────────────────────────────────────────────
# 3.4  Stored-procedure wrappers
# ─────────────────────────────────────────────────────────────

def call_add_phone():
    header("Add Phone to Contact")
    name  = input("Contact name : ").strip()
    phone = input("Phone number : ").strip()
    ptype = input("Type (home/work/mobile): ").strip().lower()
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            try:
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
                print("✓ Phone added.")
            except Exception as e:
                print(f"Error: {e}")
    conn.close()
    pause()


def call_move_to_group():
    header("Move Contact to Group")
    name  = input("Contact name : ").strip()
    group = input("Group name   : ").strip()
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            try:
                cur.execute("CALL move_to_group(%s, %s)", (name, group))
                print("✓ Contact moved.")
            except Exception as e:
                print(f"Error: {e}")
    conn.close()
    pause()


def call_search_contacts():
    header("Search Contacts (stored function)")
    query = input("Search query: ").strip()
    conn = get_connection()
    with conn:
        with get_cursor(conn) as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
    conn.close()
    if not rows:
        print("  No results found.")
    else:
        for r in rows:
            print(fmt_contact(r))
            print()
    pause()


# ─────────────────────────────────────────────────────────────
# Main menu
# ─────────────────────────────────────────────────────────────

MENU = """
  ── Contacts ──────────────────────────
  1. Add contact
  2. Delete contact
  3. Search / Filter / Sort (paginated)

  ── Stored Procedures ─────────────────
  4. Add phone to contact
  5. Move contact to group
  6. Search via stored function

  ── Import / Export ───────────────────
  7. Export to JSON
  8. Import from JSON
  9. Import from CSV (extended)

  0. Exit
"""


def main():
    while True:
        clear()
        header("📒  PHONEBOOK")
        print(MENU)
        choice = input("  Choice: ").strip()
        actions = {
            "1": add_contact,
            "2": delete_contact,
            "3": search_menu,
            "4": call_add_phone,
            "5": call_move_to_group,
            "6": call_search_contacts,
            "7": export_json,
            "8": import_json,
            "9": import_csv,
        }
        if choice == "0":
            print("Goodbye!")
            sys.exit(0)
        elif choice in actions:
            actions[choice]()
        else:
            print("Invalid choice."); pause()


if __name__ == "__main__":
    main()