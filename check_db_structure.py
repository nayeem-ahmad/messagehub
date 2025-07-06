import sqlite3

# Check the real database structure
conn = sqlite3.connect('private/contacts.db')
cursor = conn.cursor()

print("Contacts table structure:")
cursor.execute('PRAGMA table_info(contacts)')
for row in cursor.fetchall():
    print(f"  {row}")

print("\nFirst 3 contacts for reference:")
cursor.execute('SELECT * FROM contacts LIMIT 3')
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
