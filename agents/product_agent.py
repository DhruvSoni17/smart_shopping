import json
from agents.base_agent import BaseAgent
from embeddings.embedding_model import EmbeddingModel
from tools.similarity import ProductSimilarityTool

class ProductAgent(BaseAgent):
    """
    Product Agent responsible for product intelligence and analysis.
    """
    
    def __init__(self, model_name="llama3"):
        """Initialize the product agent."""
        super().__init__("product", model_name)
        self.embedding_model = EmbeddingModel()
        self.similarity_tool = ProductSimilarityTool()
    
    def process(self, input_data):
        """
        Process product data and perform product-related tasks.
        
        Args:
            input_data: Dictionary containing input parameters
                - categories: List of product categories
                - customer_data: Customer analysis data (optional)
                - action: Action to perform ('find_relevant_products', 'analyze_product', etc.)
                
        Returns:
            Dictionary containing product analysis or action results
        """
        action = input_data.get('action', 'find_relevant_products')
        
        if action == 'find_relevant_products':
            categories = input_data.get('categories', [])
            customer_data = input_data.get('customer_data', {})
            return self._find_relevant_products(categories, customer_data)
        elif action == 'analyze_product':
            product_id = input_data.get('product_id')
            if not product_id:
                return {"error": "Product ID is required"}
            return self._analyze_product(product_id)
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _find_relevant_products(self, categories, customer_data):
        """
        Find relevant products based on categories and customer data.
        
        Args:
            categories: List of product categories
            customer_data: Customer analysis data
            
        Returns:
            Dictionary containing relevant products and analysis
        """
        if not categories:
            return {"products": [], "explanation": "No categories specified"}
        
        # Get customer insights
        customer_insights = customer_data.get('insights', {})
        customer_segment = customer_data.get('customer_segment', '')
        location = customer_data.get('location', '')
        season = customer_data.get('season', '')
        holiday_shopping = customer_data.get('holiday_shopping', False)
        
        all_products = []
        
        # Get products for each category
        for category in categories:
            category_products = self.db.get_products_by_category(category)
            all_products.extend(category_products)
        
        # If no products found, return empty result
        if not all_products:
            return {"products": [], "explanation": "No products found in specified categories"}
        
        # Filter products based on customer preferences and context
        filtered_products = self._filter_products_for_customer(all_products, customer_data)
        
        # Sort products by relevance score
        sorted_products = sorted(
            filtered_products,
            key=lambda p: p.get('relevance_score', 0),
            reverse=True
        )
        
        # Generate explanation of product selection
        explanation = self._generate_product_selection_explanation(sorted_products, customer_data)
        
        return {
            "products": sorted_products,
            "explanation": explanation,
            "category_distribution": self._get_category_distribution(sorted_products),
            "total_count": len(sorted_products)
        }
    
    def _filter_products_for_customer(self, products, customer_data):
        """
        Filter and score products based on customer data.
        
        Args:
            products: List of product dictionaries
            customer_data: Customer analysis data
            
        Returns:
            List of filtered and scored product dictionaries
        """
        customer_location = customer_data.get('location', '')
        customer_season = customer_data.get('season', '')
        holiday_shopping = customer_data.get('holiday_shopping', False)
        price_sensitivity = customer_data.get('insights', {}).get('price_sensitivity', 'medium')
        
        # Convert price sensitivity to a price range factor
        price_factor = {
            'low': 1.5,     # Less sensitive to price (can recommend higher priced items)
            'medium': 1.0,  # Neutral
            'high': 0.7     # More sensitive to price (prefer lower priced items)
        }.get(price_sensitivity, 1.0)
        
        filtered_products = []
        
        for product in products:
            # Initialize base relevance score from recommendation probability
            relevance_score = product.get('recommendation_probability', 0.5)
            
            # Adjust score based on various factors
            
            # 1. Location match
            if product.get('geographical_location') == customer_location:
                relevance_score += 0.15
            
            # 2. Season match
            if product.get('season') == customer_season:
                relevance_score += 0.1
            
            # 3. Holiday match
            if product.get('holiday') == holiday_shopping:
                relevance_score += 0.1
            
            # 4. Price sensitivity adjustment
            avg_order_value = customer_data.get('avg_order_value', 0)
            product_price = product.get('price', 0)
            
            if product_price <= avg_order_value * price_factor:
                relevance_score += 0.1
            else:
                relevance_score -= 0.1
            
            # 5. Rating adjustment
            product_rating = product.get('product_rating', 0)
            if product_rating >= 4.0:
                relevance_score += 0.1
            elif product_rating <= 2.0:
                relevance_score -= 0.1
            
            # 6. Sentiment score adjustment
            sentiment_score = product.get('sentiment_score', 0)
            if sentiment_score >= 0.7:
                relevance_score += 0.05
            elif sentiment_score <= 0.3:
                relevance_score -= 0.05
            
            # Ensure score is within bounds
            relevance_score = max(0, min(1, relevance_score))
            
            # Add relevance score to product
            product_copy = dict(product)
            product_copy['relevance_score'] = relevance_score
            
            filtered_products.append(product_copy)
        
        return filtered_products
    
    def _analyze_product(self, product_id):
        """
        Analyze a specific product.
        
        Args:
            product_id: ID of the product to analyze
            
        Returns:
            Dictionary containing product analysis
        """
        product = self.db.get_product(product_id)
        if not product:
            return {"error": f"Product {product_id} not found"}
        
        # Generate or retrieve product embedding
        product_text = f"Product {product_id}: {product['category']} - {product['subcategory']} from {product['brand']}. "
        product_text += f"Price: {product['price']}. Rating: {product['product_rating']}. "
        product_text += f"Sentiment score: {product['sentiment_score']}. Season: {product['season']}."
        
        embedding_id = product.get('embedding_id')
        if not embedding_id:
            # Generate new embedding
            vector = self.embedding_model.generate_embedding(product_text)
            embedding_id = self.db.store_embedding('product', product_id, vector)
        
        # Use LLM to analyze product
        system_prompt = """
        You are an AI assistant that analyzes product data. Based on the product information provided,
        generate insights about this product, its potential customer appeal, and selling points.
        """
        
        prompt = f"""
        Analyze the following product data and provide insights:
        
        Product ID: {product_id}
        Category: {product['category']}
        Subcategory: {product['subcategory']}
        Price: ${product['price']}
        Brand: {product['brand']}
        Product Rating: {product['product_rating']}
        Customer Sentiment Score: {product['sentiment_score']}
        Season: {product['season']}
        Applicable for Holidays: {'Yes' if product['holiday'] else 'No'}
        Similar Products: {', '.join(product.get('similar_products', []))}
        
        Provide insights in JSON format with the following structure:
        {{
            "target_demographics": ["demographic1", "demographic2"],
            "key_selling_points": ["point1", "point2"],
            "suggested_customer_segments": ["segment1", "segment2"],
            "product_insights": "brief analysis of the product's appeal"
        }}
        """
        
        # Get insights from LLM
        try:
            insights_text = self.get_llm_response(prompt, system_prompt)
            insights = json.loads(insights_text)
        except Exception as e:
            self.log_activity("llm_analysis_error", {"error": str(e)})
            # Fallback insights if LLM analysis fails
            insights = {
                "target_demographics": ["General"],
                "key_selling_points": ["Quality product"],
                "suggested_customer_segments": ["All segments"],
                "product_insights": "Basic product in its category."
            }
        
        # Store insights in memory for future use
        memory_key = f"insights_{product_id}"
        self.store_memory(memory_key, insights)
        
        # Find similar products using similarity tool
        similar_products = self.similarity_tool.find_similar_products(product_id, limit=5)
        
        # Put together the full analysis
        analysis = {
            "product_id": product_id,
            "product_details": product,
            "insights": insights,
            "embedding_id": embedding_id,
            "similar_products": similar_products
        }
        
        return analysis
    
    def _generate_product_selection_explanation(self, products, customer_data):
        """
        Generate an explanation for the product selection.
        
        Args:
            products: List of product dictionaries
            customer_data: Customer analysis data
            
        Returns:
            Explanation string
        """
        customer_id = customer_data.get('customer_id', '')
        customer_segment = customer_data.get('customer_segment', '')
        
        # Use LLM to generate a natural language explanation
        system_prompt = """
        You are an AI assistant that explains product recommendations. Based on the products selected and
        customer data, explain why these products were chosen in a clear, concise manner that highlights
        the personalization aspects.
        """
        
        # Limit to top 5 products for the explanation
        top_products = products[:5]
        products_info = []
        
        for product in top_products:
            products_info.append({
                "id": product.get('product_id', ''),
                "category": product.get('category', ''),
                "subcategory": product.get('subcategory', ''),
                "price": product.get('price', 0),
                "relevance_score": product.get('relevance_score', 0)
            })
        
        prompt = f"""
        Based on the customer data and selected products, generate a brief explanation for why
        these products were selected for the customer.
        
        Customer ID: {customer_id}
        Customer Segment: {customer_segment}
        Browsing History: {', '.join(customer_data.get('browsing_history', []))}
        Purchase History: {', '.join(customer_data.get('purchase_history', []))}
        
        Selected Products:
        {json.dumps(products_info, indent=2)}
        
        Generate a concise explanation (2-3 sentences) focusing on the personalization aspects.
        """
        
        try:
            explanation = self.get_llm_response(prompt, system_prompt)
        except Exception as e:
            self.log_activity("explanation_generation_error", {"error": str(e)})
            # Fallback explanation
            explanation = "Products were selected based on your browsing and purchase history, as well as seasonal relevance and product ratings."
        
        return explanation
    
    def _get_category_distribution(self, products):
        """
        Get the distribution of products by category.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            Dictionary mapping categories to counts
        """
        distribution = {}
        
        for product in products:
            category = product.get('category', 'Unknown')
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution