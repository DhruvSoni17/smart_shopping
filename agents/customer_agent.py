import json
from agents.base_agent import BaseAgent
from embeddings.embedding_model import EmbeddingModel
from tools.segmentation import CustomerSegmentation

class CustomerAgent(BaseAgent):
    """
    Customer Agent responsible for analyzing customer data and preferences.
    """
    
    def __init__(self, model_name="llama3"):
        """Initialize the customer agent."""
        super().__init__("customer", model_name)
        self.embedding_model = EmbeddingModel()
        self.segmentation_tool = CustomerSegmentation()
    
    def process(self, input_data):
        """
        Process customer data and perform customer-related tasks.
        
        Args:
            input_data: Dictionary containing input parameters
                - customer_id: ID of the customer
                - action: Action to perform ('analyze_profile', 'update_profile', etc.)
                
        Returns:
            Dictionary containing customer analysis or action results
        """
        action = input_data.get('action', 'analyze_profile')
        customer_id = input_data.get('customer_id')
        
        if not customer_id:
            return {"error": "Customer ID is required"}
        
        # Get customer data from database
        customer = self.db.get_customer(customer_id)
        if not customer:
            return {"error": f"Customer {customer_id} not found"}
        
        if action == 'analyze_profile':
            return self._analyze_customer_profile(customer)
        elif action == 'update_profile':
            return self._update_customer_profile(customer, input_data.get('updates', {}))
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _analyze_customer_profile(self, customer):
        """
        Analyze a customer profile to extract insights.
        
        Args:
            customer: Customer data dictionary from database
            
        Returns:
            Dictionary containing customer analysis
        """
        # Extract basic customer data
        customer_id = customer['customer_id']
        browsing_history = customer.get('browsing_history', [])
        purchase_history = customer.get('purchase_history', [])
        segment = customer.get('customer_segment', '')
        
        # Generate or retrieve customer embedding
        customer_text = f"Customer {customer_id} from {customer['location']} is {customer['age']} years old, {customer['gender']}. "
        customer_text += f"They browse {', '.join(browsing_history)} and have purchased {', '.join(purchase_history)}. "
        customer_text += f"They are a {segment} with average order value of {customer['avg_order_value']}."
        
        embedding_id = customer.get('embedding_id')
        if not embedding_id:
            # Generate new embedding
            vector = self.embedding_model.generate_embedding(customer_text)
            embedding_id = self.db.store_embedding('customer', customer_id, vector)
        
        # Determine relevant product categories based on browsing and purchase history
        all_categories = list(set(browsing_history + purchase_history))
        
        # Use LLM to analyze customer preferences
        system_prompt = """
        You are an AI assistant that analyzes customer shopping profiles. Based on the customer data provided,
        identify their preferences, interests, and potential product needs. Focus on extracting insights that
        would be useful for personalized product recommendations.
        """
        
        prompt = f"""
        Analyze the following customer data and provide insights on their preferences and potential product interests:
        
        Customer ID: {customer_id}
        Age: {customer['age']}
        Gender: {customer['gender']}
        Location: {customer['location']}
        Customer Segment: {segment}
        Average Order Value: ${customer['avg_order_value']}
        Browsing History: {', '.join(browsing_history)}
        Purchase History: {', '.join(purchase_history)}
        Season: {customer['season']}
        Holiday Shopping: {'Yes' if customer['holiday'] else 'No'}
        
        Provide insights in JSON format with the following structure:
        {{
            "primary_interests": ["category1", "category2"],
            "secondary_interests": ["category3", "category4"],
            "price_sensitivity": "high/medium/low",
            "likely_next_purchase": ["product1", "product2"],
            "personalization_notes": "brief analysis of customer preferences"
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
                "primary_interests": browsing_history[:2] if browsing_history else [],
                "secondary_interests": [],
                "price_sensitivity": "medium",
                "likely_next_purchase": [],
                "personalization_notes": "Basic analysis based on browsing and purchase history."
            }
        
        # Store insights in memory for future use
        memory_key = f"insights_{customer_id}"
        self.store_memory(memory_key, insights)
        
        # Put together the full analysis
        analysis = {
            "customer_id": customer_id,
            "customer_segment": segment,
            "age_group": self._get_age_group(customer['age']),
            "browsing_history": browsing_history,
            "purchase_history": purchase_history,
            "relevant_categories": all_categories,
            "insights": insights,
            "embedding_id": embedding_id,
            "location": customer['location'],
            "season": customer['season'],
            "holiday_shopping": customer['holiday']
        }
        
        return analysis
    
    def _update_customer_profile(self, customer, updates):
        """
        Update a customer profile with new information.
        
        Args:
            customer: Current customer data dictionary
            updates: Dictionary containing fields to update
            
        Returns:
            Dictionary with update status
        """
        # Implement update logic
        # This would update the customer record in the database
        
        return {"status": "profile_updated", "customer_id": customer['customer_id']}
    
    def _get_age_group(self, age):
        """Determine age group from age."""
        if age < 18:
            return "under_18"
        elif age < 25:
            return "18_24"
        elif age < 35:
            return "25_34"
        elif age < 45:
            return "35_44"
        elif age < 55:
            return "45_54"
        elif age < 65:
            return "55_64"
        else:
            return "65_plus"