import sqlite3
from pathlib import Path

def create_database_schema(db_path='data/smart_shopping.db'):
    """Create SQLite database schema for the Smart Shopping system."""
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        age INTEGER,
        gender TEXT,
        location TEXT,
        browsing_history TEXT,  -- Stored as JSON string
        purchase_history TEXT,  -- Stored as JSON string
        customer_segment TEXT,
        avg_order_value REAL,
        holiday BOOLEAN,
        season TEXT,
        last_activity_date TEXT,
        embedding_id TEXT
    )
    ''')
    
    # Create products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id TEXT PRIMARY KEY,
        category TEXT,
        subcategory TEXT,
        price REAL,
        brand TEXT,
        avg_rating_similar REAL,
        product_rating REAL,
        sentiment_score REAL,
        holiday BOOLEAN,
        season TEXT,
        geographical_location TEXT,
        similar_products TEXT,  -- Stored as JSON string
        recommendation_probability REAL,
        embedding_id TEXT
    )
    ''')
    
    # Create recommendations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        product_id TEXT,
        score REAL,
        reason TEXT,
        timestamp TEXT,
        feedback INTEGER DEFAULT 0,  -- 0=no feedback, 1=positive, -1=negative
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
        FOREIGN KEY (product_id) REFERENCES products (product_id)
    )
    ''')
    
    # Create agent_memory table for long-term memory
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS agent_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_type TEXT,
        memory_key TEXT,
        memory_value TEXT,
        timestamp TEXT
    )
    ''')
    
    # Create embeddings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS embeddings (
        id TEXT PRIMARY KEY,
        entity_type TEXT,  -- 'customer' or 'product'
        entity_id TEXT,
        vector BLOB,       -- Binary blob of vector data
        timestamp TEXT
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database created at {db_path}")