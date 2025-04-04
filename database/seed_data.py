import pandas as pd
import json
import sqlite3
from pathlib import Path

def seed_database(customer_csv_path, product_csv_path, db_path='data/smart_shopping.db'):
    """Seed the database with initial customer and product data."""
    
    # Ensure the database directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Read CSV files
    try:
        customer_df = pd.read_csv(customer_csv_path)
        product_df = pd.read_csv(product_csv_path)
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing data to prevent duplicate entries
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM products")
    conn.commit()
    
    # Insert customer data
    for _, row in customer_df.iterrows():
        try:
            browsing_history = json.dumps(eval(row['Browsing_History'])) if isinstance(row['Browsing_History'], str) else json.dumps([])
            purchase_history = json.dumps(eval(row['Purchase_History'])) if isinstance(row['Purchase_History'], str) else json.dumps([])
            
            cursor.execute('''
            INSERT INTO customers (
                customer_id, age, gender, location, browsing_history, purchase_history,
                customer_segment, avg_order_value, holiday, season
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Customer_ID'], row['Age'], row['Gender'], row['Location'],
                browsing_history, purchase_history, row['Customer_Segment'], 
                row['Avg_Order_Value'], row['Holiday'] == 'Yes', row['Season']
            ))
        except Exception as e:
            print(f"Error inserting customer data: {e} for row {row}")
    
    # Insert product data
    for _, row in product_df.iterrows():
        try:
            similar_products = json.dumps(eval(row['Similar_Product_List'])) if isinstance(row['Similar_Product_List'], str) else json.dumps([])
            
            cursor.execute('''
            INSERT INTO products (
                product_id, category, subcategory, price, brand, avg_rating_similar,
                product_rating, sentiment_score, holiday, season, geographical_location,
                similar_products, recommendation_probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['Product_ID'], row['Category'], row['Subcategory'], row['Price'],
                row['Brand'], row['Average_Rating_of_Similar_Products'], row['Product_Rating'],
                row['Customer_Review_Sentiment_Score'], row['Holiday'] == 'Yes', row['Season'],
                row['Geographical_Location'], similar_products, row['Probability_of_Recommendation']
            ))
        except Exception as e:
            print(f"Error inserting product data: {e} for row {row}")
    
    conn.commit()
    conn.close()
    
    print(f"Database seeded with {len(customer_df)} customers and {len(product_df)} products")

# Run the function with correct paths
if __name__ == "__main__":
    seed_database('data/customer_data.csv', 'data/product_data.csv')