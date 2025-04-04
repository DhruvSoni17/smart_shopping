import json
import random
from datetime import datetime
from agents.base_agent import BaseAgent
from tools.similarity import ProductSimilarityTool

class RecommendationAgent(BaseAgent):
    """
    Recommendation Agent responsible for generating personalized product recommendations.
    """
    
    def __init__(self, model_name="llama3"):
        """Initialize the recommendation agent."""
        super().__init__("recommendation", model_name)
        self.similarity_tool = ProductSimilarityTool()
        
        # Different recommendation strategies
        self.strategies = {
            "collaborative_filtering": self._collaborative_filtering_strategy,
            "content_based": self._content_based_strategy,
            "popularity_based": self._popularity_based_strategy,
            "hybrid": self._hybrid_strategy
        }
    
    def process(self, input_data):
        """
        Process input data and generate recommendations.
        
        Args:
            input_data: Dictionary containing input parameters
                - customer_data: Customer analysis data
                - product_data: Product data (optional)
                - action: Action to perform ('generate_recommendations', 'learn_from_feedback', etc.)
                
        Returns:
            Dictionary containing recommendations or action results
        """
        action = input_data.get('action', 'generate_recommendations')
        
        if action == 'generate_recommendations':
            customer_data = input_data.get('customer_data', {})
            product_data = input_data.get('product_data', {})
            
            if not customer_data:
                return {"error": "Customer data is required"}
            
            # Determine the best strategy for this customer
            strategy = self._select_recommendation_strategy(customer_data)
            
            # Generate recommendations using the selected strategy
            return self._generate_recommendations(customer_data, product_data, strategy)
        
        elif action == 'learn_from_feedback':
            customer_id = input_data.get('customer_id')
            product_id = input_data.get('product_id')
            feedback = input_data.get('feedback')
            
            if not all([customer_id, product_id, feedback]):
                return {"error": "Missing required feedback data"}
            
            return self._learn_from_feedback(customer_id, product_id, feedback)
        
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _select_recommendation_strategy(self, customer_data):
        """
        Select the most appropriate recommendation strategy for a customer.
        
        Args:
            customer_data: Customer analysis data
            
        Returns:
            Strategy name (string)
        """
        customer_id = customer_data.get('customer_id')
        segment = customer_data.get('customer_segment', '')
        
        # Check if we have a stored strategy preference for this customer
        strategy_key = f"strategy_preference_{customer_id}"
        stored_strategy = self.recall_memory(strategy_key)
        
        if stored_strategy:
            # Use the stored strategy
            return stored_strategy
        
        # Otherwise, determine based on customer segment and other factors
        if segment == 'New Visitor':
            # New visitors get popularity-based recommendations
            strategy = 'popularity_based'
        elif segment == 'Frequent Buyer':
            # Frequent buyers get collaborative filtering
            strategy = 'collaborative_filtering'
        elif len(customer_data.get('browsing_history', [])) > len(customer_data.get('purchase_history', [])):
            # Browsers get content-based
            strategy = 'content_based'
        else:
            # Default to hybrid approach
            strategy = 'hybrid'
        
        # Store the strategy preference for future use
        self.store_memory(strategy_key, strategy)
        
        return strategy
    
    def _generate_recommendations(self, customer_data, product_data, strategy='hybrid'):
        """
        Generate personalized recommendations for a customer.
        
        Args:
            customer_data: Customer analysis data
            product_data: Product data
            strategy: Recommendation strategy to use
            
        Returns:
            Dictionary containing recommendations and explanation
        """
        customer_id = customer_data.get('customer_id')
        
        # Get recommendations using the selected strategy
        strategy_fn = self.strategies.get(strategy, self._hybrid_strategy)
        recommendations = strategy_fn(customer_data, product_data)
        
        # Log the recommendation generation
        self.log_activity(
            "recommendations_generated",
            {
                "customer_id": customer_id,
                "strategy": strategy,
                "count": len(recommendations)
            }
        )
        
        # Store recommendations in database
        timestamp = datetime.now().isoformat()
        for rec in recommendations:
            product_id = rec.get('product_id')
            score = rec.get('score', 0)
            reason = rec.get('reason', '')
            
            self.db.add_recommendation(customer_id, product_id, score, reason)
        
        # Generate an explanation for the recommendations
        explanation = self._generate_recommendation_explanation(
            recommendations, 
            customer_data,
            strategy
        )
        
        return {
            "recommendations": recommendations,
            "strategy": strategy,
            "explanation": explanation,
            "timestamp": timestamp
        }
        
    def _collaborative_filtering_strategy(self, customer_data, product_data):
        """
        Generate recommendations using collaborative filtering approach.
        
        Args:
            customer_data: Customer analysis data
            product_data: Product data
            
        Returns:
            List of recommendation dictionaries
        """
        customer_id = customer_data.get('customer_id')
        customer_segment = customer_data.get('customer_segment', '')
        
        # In a real system, this would use actual collaborative filtering algorithms
        # For the hackathon, we'll simulate this by finding products that similar customers liked
        
        # Find products that similar customers have purchased
        recommendations = []
        
        # Get products from the product data
        available_products = product_data.get('products', [])
        
        # If no products available, return empty recommendations
        if not available_products:
            return []
        
        # Sort products by relevance score (which was calculated in the Product Agent)
        sorted_products = sorted(
            available_products,
            key=lambda p: p.get('relevance_score', 0),
            reverse=True
        )

        # Take top products as recommendations
        for product in sorted_products[:10]:  # Limit to top 10
            product_id = product.get('product_id')
            category = product.get('category', '')
            price = product.get('price', 0)
            relevance_score = product.get('relevance_score', 0)
            
            recommendations.append({
                "product_id": product_id,
                "category": category,
                "price": price,
                "score": relevance_score,
                "reason": f"Recommended based on preferences of similar {customer_segment} customers"
            })
        
        return recommendations
    
    def _content_based_strategy(self, customer_data, product_data):
        """
        Generate recommendations using content-based approach.
        
        Args:
            customer_data: Customer analysis data
            product_data: Product data
            
        Returns:
            List of recommendation dictionaries
        """
        browsing_history = customer_data.get('browsing_history', [])
        purchase_history = customer_data.get('purchase_history', [])
        
        # In a real system, this would use feature-based similarity
        # For the hackathon, we'll use category matching and product attributes
        
        recommendations = []
        
        # Get products from the product data
        available_products = product_data.get('products', [])
        
        # If no products available, return empty recommendations
        if not available_products:
            return []
        
        # Calculate content-based scores
        scored_products = []
        
        for product in available_products:
            product_id = product.get('product_id')
            category = product.get('category', '')
            subcategory = product.get('subcategory', '')
            
            # Base score is the relevance score
            score = product.get('relevance_score', 0)
            
            # Boost score if category matches browsing or purchase history
            if category in browsing_history:
                score += 0.1
            
            if category in purchase_history:
                score += 0.15
            
            # Add to scored products
            scored_products.append({
                "product_id": product_id,
                "category": category,
                "subcategory": subcategory,
                "price": product.get('price', 0),
                "score": score,
                "reason": f"Recommended based on your interest in {category} products"
            })
        
        # Sort by score and take top recommendations
        sorted_products = sorted(
            scored_products,
            key=lambda p: p.get('score', 0),
            reverse=True
        )
        
        return sorted_products[:10]  # Limit to top 10
    
    def _popularity_based_strategy(self, customer_data, product_data):
        """
        Generate recommendations using popularity-based approach.
        
        Args:
            customer_data: Customer analysis data
            product_data: Product data
            
        Returns:
            List of recommendation dictionaries
        """
        # Get products from the product data
        available_products = product_data.get('products', [])
        
        # If no products available, return empty recommendations
        if not available_products:
            return []
        
        # Sort products by rating (as a proxy for popularity)
        sorted_products = sorted(
            available_products,
            key=lambda p: p.get('product_rating', 0),
            reverse=True
        )
        
        recommendations = []
        
        for product in sorted_products[:10]:  # Limit to top 10
            product_id = product.get('product_id')
            category = product.get('category', '')
            price = product.get('price', 0)
            rating = product.get('product_rating', 0)
            
            recommendations.append({
                "product_id": product_id,
                "category": category,
                "price": price,
                "score": rating / 5.0,  # Normalize to 0-1 scale
                "reason": f"Popular {category} product with a rating of {rating}"
            })
        
        return recommendations
    
    def _hybrid_strategy(self, customer_data, product_data):
        """
        Generate recommendations using a hybrid approach combining multiple strategies.
        
        Args:
            customer_data: Customer analysis data
            product_data: Product data
            
        Returns:
            List of recommendation dictionaries
        """
        # Get recommendations from each strategy
        collaborative_recs = self._collaborative_filtering_strategy(customer_data, product_data)
        content_recs = self._content_based_strategy(customer_data, product_data)
        popularity_recs = self._popularity_based_strategy(customer_data, product_data)
        
        # Combine recommendations
        all_recs = {}
        
        # Add collaborative recommendations with a weight
        for rec in collaborative_recs:
            product_id = rec.get('product_id')
            score = rec.get('score', 0) * 0.4  # Weight of 0.4
            if product_id in all_recs:
                all_recs[product_id]['score'] += score
            else:
                all_recs[product_id] = rec.copy()
                all_recs[product_id]['score'] = score
        
        # Add content-based recommendations with a weight
        for rec in content_recs:
            product_id = rec.get('product_id')
            score = rec.get('score', 0) * 0.4  # Weight of 0.4
            if product_id in all_recs:
                all_recs[product_id]['score'] += score
                # Combine reasons
                all_recs[product_id]['reason'] += f" and {rec.get('reason', '')}"
            else:
                all_recs[product_id] = rec.copy()
                all_recs[product_id]['score'] = score
        
        # Add popularity-based recommendations with a weight
        for rec in popularity_recs:
            product_id = rec.get('product_id')
            score = rec.get('score', 0) * 0.2  # Weight of 0.2
            if product_id in all_recs:
                all_recs[product_id]['score'] += score
            else:
                all_recs[product_id] = rec.copy()
                all_recs[product_id]['score'] = score
        
        # Convert to list and sort by score
        combined_recs = list(all_recs.values())
        sorted_recs = sorted(
            combined_recs,
            key=lambda r: r.get('score', 0),
            reverse=True
        )
        
        return sorted_recs[:10]  # Limit to top 10
    
    def _generate_recommendation_explanation(self, recommendations, customer_data, strategy):
        """
        Generate a natural language explanation for the recommendations.
        
        Args:
            recommendations: List of recommendation dictionaries
            customer_data: Customer analysis data
            strategy: Recommendation strategy used
            
        Returns:
            Explanation string
        """
        customer_id = customer_data.get('customer_id')
        customer_segment = customer_data.get('customer_segment', '')
        
        # Use LLM to generate a natural language explanation
        system_prompt = """
        You are an AI assistant that explains product recommendations. Based on the recommended products and
        customer data, explain why these specific recommendations were made in a personalized, conversational manner.
        Focus on highlighting the personalization aspects and the benefits to the customer.
        """
        
        # Prepare recommendation data for the prompt
        top_recs = recommendations[:5]  # Use top 5 for the explanation
        rec_info = []
        
        for rec in top_recs:
            rec_info.append({
                "product_id": rec.get('product_id', ''),
                "category": rec.get('category', ''),
                "price": rec.get('price', 0),
                "reason": rec.get('reason', '')
            })
        
        prompt = f"""
        Based on the customer data and recommended products, generate a personalized explanation for why
        these products were recommended to the customer.
        
        Customer ID: {customer_id}
        Customer Segment: {customer_segment}
        Recommendation Strategy: {strategy}
        Browsing History: {', '.join(customer_data.get('browsing_history', []))}
        Purchase History: {', '.join(customer_data.get('purchase_history', []))}
        
        Recommended Products:
        {json.dumps(rec_info, indent=2)}
        
        Generate a friendly, personalized explanation (2-4 sentences) that would help the customer understand
        why these items were recommended specifically for them.
        """
        
        try:
            explanation = self.get_llm_response(prompt, system_prompt)
        except Exception as e:
            self.log_activity("explanation_generation_error", {"error": str(e)})
            # Fallback explanation
            explanation = f"These products were selected based on your browsing and purchase history, as well as your preferences as a {customer_segment}. We've highlighted items that we think will be most relevant to your interests."
        
        return explanation
    
    def _learn_from_feedback(self, customer_id, product_id, feedback):
        """
        Learn from customer feedback on recommendations.
        
        Args:
            customer_id: ID of the customer
            product_id: ID of the product
            feedback: Feedback value (1 for positive, -1 for negative)
            
        Returns:
            Dictionary with learning status
        """
        # In a real system, this would update the recommendation model
        # For the hackathon, we'll store the feedback and adjust strategy preferences
        
        # Get current strategy preference
        strategy_key = f"strategy_preference_{customer_id}"
        current_strategy = self.recall_memory(strategy_key)
        
        # If negative feedback, potentially adjust strategy
        if feedback < 0 and current_strategy:
            # Simple adjustment: rotate to next strategy
            strategies = list(self.strategies.keys())
            current_index = strategies.index(current_strategy) if current_strategy in strategies else 0
            next_index = (current_index + 1) % len(strategies)
            next_strategy = strategies[next_index]
            
            # Store new strategy preference
            self.store_memory(strategy_key, next_strategy)
            
            return {
                "status": "learned_from_feedback",
                "action_taken": "adjusted_strategy",
                "previous_strategy": current_strategy,
                "new_strategy": next_strategy
            }
        
        return {
            "status": "feedback_recorded",
            "action_taken": "maintained_strategy",
            "current_strategy": current_strategy
        }
