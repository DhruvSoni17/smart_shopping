import sqlite3

conn = sqlite3.connect("data/smart_shopping.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# Display table size and description
for table_name in tables:
    table_name = table_name[0]
    print(f"\nTable: {table_name}")
    
    # Get table description (columns)
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("Columns:")
    for column in columns:
        print(column)
    
    # Get table size (row count)
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"Row count: {row_count}")
    
    # # Display all data in the table
    # cursor.execute(f"SELECT * FROM {table_name}")
    # rows = cursor.fetchall()
    # print("Data:")
    # for row in rows:
    #     print(row)

conn.close()
