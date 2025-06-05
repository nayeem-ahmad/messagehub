import sqlite3
import pandas as pd

from features.common import DB_FILE

def import_contacts_from_csv(filename):
    data = pd.read_csv(filename)
    required_cols = {'name', 'email', 'mobile'}
    # Normalize column names to lower for robustness
    data.columns = [col.lower() for col in data.columns]
    missing = required_cols - set(data.columns)
    if missing:
        raise Exception(f"CSV is missing required columns: {', '.join(missing)}. Required columns are: name, email, mobile.")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    imported = 0
    for _, row in data.iterrows():
        def safe_str(val):
            if pd.isna(val):
                return ''
            return str(val).strip()
        name = safe_str(row.get('name', ''))
        email = safe_str(row.get('email', ''))
        mobile = safe_str(row.get('mobile', ''))
        if not name or not email:
            continue
        try:
            c.execute("INSERT OR IGNORE INTO contacts (name, email, mobile) VALUES (?, ?, ?)", (name, email, mobile))
            if c.rowcount > 0:
                imported += 1
        except Exception:
            continue
    conn.commit()
    conn.close()
    return imported

def get_contacts_for_group(group_name):
    conn = sqlite3.connect(DB_FILE)
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
