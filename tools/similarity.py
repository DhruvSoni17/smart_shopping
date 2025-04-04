from embeddings.vector_store import VectorStore
from database.db_manager import DatabaseManager

class ProductSimilarityTool:
    """
    Tool for finding similar products.
    """
    
    def __init__(self):
        """Initialize the product similarity tool."""
        self.vector_store = VectorStore()
        self.db = DatabaseManager()
    
    def find_similar_products(self, product_id, limit=5):
        """
        Find products similar to the given product.
        
        Args:
            product_id: ID of the product to find similar products for
            limit: Maximum number of results to return
            
        Returns:
            List of similar product dictionaries
        """
        # Get the product data
        product = self.db.get_product(product_id)
        
        if not product:
            return []
        
        # First, check if the product has an embedding
        embedding_id = product.get('embedding_id')
        
        if embedding_id:
            # Use vector search for similarity
            vector = self.vector_store.get_embedding(embedding_id)
            
            if vector is not None:
                # Search for similar products
                similar_product_ids = self.vector_store.search_similar_entities(
                    vector, 'product', limit=limit
                )
                
                # Get full product data for the similar products
                similar_products = []
                
                for pid, similarity in similar_product_ids:
                    if pid != product_id:  # Exclude the original product
                        similar_product = self.db.get_product(pid)
                        if similar_product:
                            similar_product['similarity_score'] = similarity
                            similar_products.append(similar_product)
                
                return similar_products
        
        # Fallback: Use the similar products list from the database
        similar_product_list = product.get('similar_products', [])
        
        # Get full product data for the similar products
        similar_products = []
        
        for similar_product_name in similar_product_list:
            # Query for products with this subcategory
            query = "SELECT * FROM products WHERE subcategory = ? LIMIT ?"
            results = self.db.execute_query(query, (similar_product_name, limit))
            
            for result in results:
                if result['product_id'] != product_id:  # Exclude the original product
                    similar_product = dict(result)
                    
                    # Convert JSON strings to Python objects
                    if similar_product.get('similar_products'):
                        try:
                            similar_product['similar_products'] = json.loads(similar_product['similar_products'])
                        except:
                            similar_product['similar_products'] = []
                    
                    similar_products.append(similar_product)
        
        # Limit to the requested number
        return similar_products[:limit]