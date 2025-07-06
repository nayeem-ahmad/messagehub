import sqlite3

# Check what's in the template database
conn = sqlite3.connect('template/private/contacts_sample.db')
cursor = conn.cursor()

try:
    cursor.execute('SELECT COUNT(*) FROM contacts')
    count = cursor.fetchone()[0]
    print(f'Contacts in template DB: {count}')
    
    if count > 0:
        cursor.execute('SELECT name, email FROM contacts LIMIT 3')
        print('Sample contacts:')
        for row in cursor.fetchall():
            print(f'  {row}')
except Exception as e:
    print(f'Error: {e}')
finally:
    conn.close()
