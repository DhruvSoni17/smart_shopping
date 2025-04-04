class PromptTemplates:
    """
    Templates for common prompts used in the Smart Shopping system.
    """
    
    @staticmethod
    def customer_analysis_prompt(customer_data):
        """Template for customer analysis."""
        return f"""
        Analyze the following customer data and provide insights on their preferences and potential product interests:
        
        Customer ID: {customer_data.get('customer_id', '')}
        Age: {customer_data.get('age', '')}
        Gender: {customer_data.get('gender', '')}
        Location: {customer_data.get('location', '')}
        Customer Segment: {customer_data.get('customer_segment', '')}
        Average Order Value: ${customer_data.get('avg_order_value', '')}
        Browsing History: {', '.join(customer_data.get('browsing_history', []))}
        Purchase History: {', '.join(customer_data.get('purchase_history', []))}
        Season: {customer_data.get('season', '')}
        Holiday Shopping: {'Yes' if customer_data.get('holiday', False) else 'No'}
        
        Provide insights in JSON format with the following structure:
        {{
            "primary_interests": ["category1", "category2"],
            "secondary_interests": ["category3", "category4"],
            "price_sensitivity": "high/medium/low",
            "likely_next_purchase": ["product1", "product2"],
            "personalization_notes": "brief analysis of customer preferences"
        }}
        """
    
    @staticmethod
    def product_analysis_prompt(product_data):
        """Template for product analysis."""
        return f"""
        Analyze the following product data and provide insights:
        
        Product ID: {product_data.get('product_id', '')}
        Category: {product_data.get('category', '')}
        Subcategory: {product_data.get('subcategory', '')}
        Price: ${product_data.get('price', '')}
        Brand: {product_data.get('brand', '')}
        Product Rating: {product_data.get('product_rating', '')}
        Customer Sentiment Score: {product_data.get('sentiment_score', '')}
        Season: {product_data.get('season', '')}
        Applicable for Holidays: {'Yes' if product_data.get('holiday', False) else 'No'}
        Similar Products: {', '.join(product_data.get('similar_products', []))}
        
        Provide insights in JSON format with the following structure:
        {{
            "target_demographics": ["demographic1", "demographic2"],
            "key_selling_points": ["point1", "point2"],
            "suggested_customer_segments": ["segment1", "segment2"],
            "product_insights": "brief analysis of the product's appeal"
        }}
        """
    
    @staticmethod
    def recommendation_explanation_prompt(customer_data, recommendations, strategy):
        """Template for recommendation explanation."""
        
        rec_info = []
        for rec in recommendations[:5]:  # Use top 5 for the explanation
            rec_info.append({
                "product_id": rec.get('product_id', ''),
                "category": rec.get('category', ''),
                "price": rec.get('price', 0),
                "reason": rec.get('reason', '')
            })
        
        rec_info_json = json.dumps(rec_info, indent=2)
        
        return f"""
        Based on the customer data and recommended products, generate a personalized explanation for why
        these products were recommended to the customer.
        
        Customer ID: {customer_data.get('customer_id', '')}
        Customer Segment: {customer_data.get('customer_segment', '')}
        Recommendation Strategy: {strategy}
        Browsing History: {', '.join(customer_data.get('browsing_history', []))}
        Purchase History: {', '.join(customer_data.get('purchase_history', []))}
        
        Recommended Products:
        {rec_info_json}
        
        Generate a friendly, personalized explanation (2-4 sentences) that would help the customer understand
        why these items were recommended specifically for them.
        """
