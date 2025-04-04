import sqlite3
import json
import datetime
from pathlib import Path

class DatabaseManager:
    """
    Handles all database operations for the Smart Shopping system.
    """
    
    def __init__(self, db_path='data/smart_shopping.db'):
        """Initialize database connection."""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connect to the SQLite database."""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Return rows as dictionaries
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        """Execute a query and return results."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor.fetchall()
        except Exception as e:
            conn.rollback()
            raise e
    
    def execute_many(self, query, params_list):
        """Execute multiple queries with different parameters."""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            conn.rollback()
            raise e
    
    # Customer methods
    def get_customer(self, customer_id):
        """Get customer by ID."""
        query = "SELECT * FROM customers WHERE customer_id = ?"
        results = self.execute_query(query, (customer_id,))
        
        if results:
            customer = dict(results[0])
            # Convert JSON strings to Python objects
            if customer.get('browsing_history'):
                customer['browsing_history'] = json.loads(customer['browsing_history'])
            if customer.get('purchase_history'):
                customer['purchase_history'] = json.loads(customer['purchase_history'])
            return customer
        return None
    
    def get_all_customers(self):
        """Get all customers."""
        query = "SELECT * FROM customers"
        results = self.execute_query(query)
        
        customers = []
        for row in results:
            customer = dict(row)
            # Convert JSON strings to Python objects
            if customer.get('browsing_history'):
                customer['browsing_history'] = json.loads(customer['browsing_history'])
            if customer.get('purchase_history'):
                customer['purchase_history'] = json.loads(customer['purchase_history'])
            customers.append(customer)
        
        return customers
    
    # Product methods
    def get_product(self, product_id):
        """Get product by ID."""
        query = "SELECT * FROM products WHERE product_id = ?"
        results = self.execute_query(query, (product_id,))
        
        if results:
            product = dict(results[0])
            # Convert JSON strings to Python objects
            if product.get('similar_products'):
                product['similar_products'] = json.loads(product['similar_products'])
            return product
        return None
    
    def get_products_by_category(self, category):
        """Get products by category."""
        query = "SELECT * FROM products WHERE category = ?"
        results = self.execute_query(query, (category,))
        
        products = []
        for row in results:
            product = dict(row)
            # Convert JSON strings to Python objects
            if product.get('similar_products'):
                product['similar_products'] = json.loads(product['similar_products'])
            products.append(product)
        
        return products
    
    # Recommendation methods
    def add_recommendation(self, customer_id, product_id, score, reason):
        """Add a new recommendation."""
        query = """
        INSERT INTO recommendations 
        (customer_id, product_id, score, reason, timestamp) 
        VALUES (?, ?, ?, ?, ?)
        """
        timestamp = datetime.datetime.now().isoformat()
        self.execute_query(query, (customer_id, product_id, score, reason, timestamp))
    
    def get_recommendations_for_customer(self, customer_id, limit=10):
        """Get recommendations for a customer."""
        query = """
        SELECT r.*, p.category, p.subcategory, p.price, p.brand, p.product_rating
        FROM recommendations r
        JOIN products p ON r.product_id = p.product_id
        WHERE r.customer_id = ?
        ORDER BY r.score DESC
        LIMIT ?
        """
        return self.execute_query(query, (customer_id, limit))
    
    # Agent memory methods
    def store_agent_memory(self, agent_type, memory_key, memory_value):
        """Store a memory item for an agent."""
        query = """
        INSERT INTO agent_memory 
        (agent_type, memory_key, memory_value, timestamp) 
        VALUES (?, ?, ?, ?)
        """
        timestamp = datetime.datetime.now().isoformat()
        self.execute_query(query, (agent_type, memory_key, memory_value, timestamp))
    
    def get_agent_memory(self, agent_type, memory_key=None):
        """Get memory items for an agent."""
        if memory_key:
            query = "SELECT * FROM agent_memory WHERE agent_type = ? AND memory_key = ?"
            return self.execute_query(query, (agent_type, memory_key))
        else:
            query = "SELECT * FROM agent_memory WHERE agent_type = ?"
            return self.execute_query(query, (agent_type,))
    
    # Embedding methods
    def store_embedding(self, entity_type, entity_id, vector):
        """Store vector embedding for an entity."""
        embedding_id = f"{entity_type}_{entity_id}"
        query = """
        INSERT OR REPLACE INTO embeddings 
        (id, entity_type, entity_id, vector, timestamp) 
        VALUES (?, ?, ?, ?, ?)
        """
        timestamp = datetime.datetime.now().isoformat()
        self.execute_query(query, (embedding_id, entity_type, entity_id, vector, timestamp))
        
        # Update the entity with the embedding id
        if entity_type == 'customer':
            self.execute_query(
                "UPDATE customers SET embedding_id = ? WHERE customer_id = ?",
                (embedding_id, entity_id)
            )
        elif entity_type == 'product':
            self.execute_query(
                "UPDATE products SET embedding_id = ? WHERE product_id = ?",
                (embedding_id, entity_id)
            )
        
        return embedding_id
    
    def get_embedding(self, embedding_id):
        """Get embedding by ID."""
        query = "SELECT * FROM embeddings WHERE id = ?"
        results = self.execute_query(query, (embedding_id,))
        
        if results:
            return dict(results[0])
        return None