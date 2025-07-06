import sqlite3
import os

def create_clean_template_db():
    """Create a clean template database with only sample data"""
    
    # Remove existing template database
    template_db = 'template/private/contacts_sample.db'
    if os.path.exists(template_db):
        os.remove(template_db)
        print(f"Removed existing template database")
    
    # Create clean database
    conn = sqlite3.connect(template_db)
    cursor = conn.cursor()
    
    # Get table schemas from the real database to ensure compatibility
    if os.path.exists('private/contacts.db'):
        print("Getting table schemas from existing database...")
        source_conn = sqlite3.connect('private/contacts.db')
        source_cursor = source_conn.cursor()
        
        # Get all table creation statements, excluding system tables
        source_cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL AND name NOT LIKE 'sqlite_%';")
        table_schemas = source_cursor.fetchall()
        source_conn.close()
        
        # Create tables with same structure
        for schema in table_schemas:
            cursor.execute(schema[0])
            table_name = schema[0].split('(')[0].replace('CREATE TABLE ', '').strip()
            print(f"Created table: {table_name}")
    else:
        print("Creating default table structure...")
        # Default table structures
        tables = [
            '''CREATE TABLE contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                surname TEXT,
                email TEXT,
                mobile TEXT,
                address TEXT
            )''',
            '''CREATE TABLE groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT
            )''',
            '''CREATE TABLE contact_groups (
                contact_id INTEGER,
                group_id INTEGER,
                PRIMARY KEY (contact_id, group_id)
            )''',
            '''CREATE TABLE email_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                subject TEXT,
                body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE sms_campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE email_campaign_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                contact_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error TEXT,
                personalized_subject TEXT,
                personalized_body TEXT
            )''',
            '''CREATE TABLE sms_campaign_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                contact_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                error TEXT,
                personalized_message TEXT
            )''',
            '''CREATE TABLE email_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                subject TEXT,
                body TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )''',
            '''CREATE TABLE sms_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT
            )'''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
            table_name = table_sql.split('(')[0].replace('CREATE TABLE ', '').strip()
            print(f"Created table: {table_name}")
    
    # Add ONLY sample/demo data
    print("\nAdding sample data...")
    sample_contacts = [
        ('John Doe', 'john.doe@example.com', '+1-555-0123'),
        ('Jane Smith', 'jane.smith@example.com', '+1-555-0124'),
        ('Demo User', 'demo.user@example.com', '+1-555-0125'),
        ('Sample Contact', 'sample@example.com', '+1-555-0126')
    ]
    
    for contact in sample_contacts:
        cursor.execute('INSERT INTO contacts (name, email, mobile) VALUES (?, ?, ?)', contact)
        print(f"Added sample contact: {contact[0]}")
    
    # Add sample groups
    sample_groups = [
        ('sample', 'Sample Group', 'Demo group for new users'),
        ('test', 'Test Group', 'Example group for testing features')
    ]
    
    for group in sample_groups:
        cursor.execute('INSERT INTO groups (short_name, name, description) VALUES (?, ?, ?)', group)
        print(f"Added sample group: {group[1]}")
    
    # Link some contacts to groups (using group_members table)
    cursor.execute('INSERT INTO group_members (contact_id, group_id) VALUES (?, ?)', (1, 1))
    cursor.execute('INSERT INTO group_members (contact_id, group_id) VALUES (?, ?)', (2, 1))
    cursor.execute('INSERT INTO group_members (contact_id, group_id) VALUES (?, ?)', (3, 2))
    
    conn.commit()
    conn.close()
    
    # Verify the clean database
    conn = sqlite3.connect(template_db)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM contacts')
    count = cursor.fetchone()[0]
    print(f"\n✅ Clean template database created with {count} sample contacts")
    
    cursor.execute('SELECT name, email FROM contacts')
    print("Sample contacts in clean database:")
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]})")
    
    conn.close()
    
    # Check file size
    size_kb = os.path.getsize(template_db) / 1024
    print(f"Database size: {size_kb:.1f} KB (should be much smaller than 270KB)")

if __name__ == "__main__":
    create_clean_template_db()
