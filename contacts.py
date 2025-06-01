import sqlite3
import pandas as pd

def import_contacts_from_csv(filename):
    data = pd.read_csv(filename)
    conn = sqlite3.connect("contacts.db")
    c = conn.cursor()
    imported = 0
    for _, row in data.iterrows():
        try:
            c.execute("INSERT OR IGNORE INTO contacts (name, email) VALUES (?, ?)", (row['name'], row['email']))
            imported += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return imported

def get_contacts_for_group(group_name):
    conn = sqlite3.connect("contacts.db")
    c = conn.cursor()
    if group_name == "All Contacts":
        c.execute("SELECT name, email FROM contacts")
    else:
        c.execute("""
            SELECT contacts.name, contacts.email FROM contacts
            JOIN group_members ON contacts.id = group_members.contact_id
            JOIN groups ON groups.id = group_members.group_id
            WHERE groups.name=?
        """, (group_name,))
    rows = c.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["name", "email"])