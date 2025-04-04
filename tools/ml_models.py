import numpy as np
import json
from database.db_manager import DatabaseManager

class RecommendationModel:
    """
    Machine learning model for product recommendations.
    """
    
    def __init__(self):
        """Initialize the recommendation model."""
        self.db = DatabaseManager()
        self.weights = {
            'relevance_score': 0.3,
            'product_rating': 0.2,
            'season_match': 0.15,
            'location_match': 0.15,
            'sentiment_score': 0.1,
            'price_factor': 0.1
        }

    def predict_recommendations(self, customer_id, product_ids=None, limit=10):
        """
        Predict product recommendations for a customer.
        
        Args:
            customer_id: ID of the customer
            product_ids: Optional list of product IDs to score (if None, all products are considered)
            limit: Maximum number of recommendations to return
            
        Returns:
            List of (product_id, score) tuples for recommended products
        """
        # Get customer data
        customer = self.db.get_customer(customer_id)
        if not customer:
            return []
        
        # Get products to score
        if product_ids:
            products = [self.db.get_product(pid) for pid in product_ids]
            products = [p for p in products if p]  # Filter out None values
        else:
            # Get all products (in a real system, would use pagination for large catalogs)
            query = "SELECT * FROM products"
            products = self.db.execute_query(query)
            products = [dict(p) for p in products]
        
        # Score each product
        scored_products = []
        
        for product in products:
            score = self._score_product_for_customer(customer, product)
            scored_products.append((product['product_id'], score))
        
        # Sort by score (descending) and limit results
        sorted_products = sorted(scored_products, key=lambda x: x[1], reverse=True)
        return sorted_products[:limit]
    
    def _score_product_for_customer(self, customer, product):
        """
        Score a product for a customer based on various factors.
        
        Args:
            customer: Customer data dictionary
            product: Product data dictionary
            
        Returns:
            Score between 0 and 1
        """
        # Start with base score from recommendation probability
        score = product.get('recommendation_probability', 0.5) * self.weights['relevance_score']
        
        # Add product rating component
        product_rating = product.get('product_rating', 0)
        score += (product_rating / 5.0) * self.weights['product_rating']
        
        # Season match
        if product.get('season') == customer.get('season'):
            score += self.weights['season_match']
        
        # Location match
        if product.get('geographical_location') == customer.get('location'):
            score += self.weights['location_match']
        
        # Sentiment score
        sentiment_score = product.get('sentiment_score', 0)
        score += sentiment_score * self.weights['sentiment_score']
        
        # Price factor
        avg_order_value = customer.get('avg_order_value', 0)
        product_price = product.get('price', 0)
        
        # Price factor: 1 if price is below avg order value, decreases as price increases
        price_factor = 1.0 if product_price <= avg_order_value else avg_order_value / product_price
        score += price_factor * self.weights['price_factor']
        
        # Ensure score is between 0 and 1
        return max(0, min(1, score))
    
    def update_weights(self, new_weights):
        """
        Update the model weights.
        
        Args:
            new_weights: Dictionary with new weight values
            
        Returns:
            Updated weights dictionary
        """
        for key, value in new_weights.items():
            if key in self.weights:
                self.weights[key] = value
        
        # Normalize weights to sum to 1
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
        
        return self.weights