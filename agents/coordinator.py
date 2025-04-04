import json
from agents.base_agent import BaseAgent
from agents.customer_agent import CustomerAgent
from agents.product_agent import ProductAgent
from agents.recommendation import RecommendationAgent

class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent that orchestrates the workflow between specialized agents.
    """
    
    def __init__(self, model_name="llama3"):
        """Initialize the coordinator agent."""
        super().__init__("coordinator", model_name)
        
        # Initialize sub-agents
        self.customer_agent = CustomerAgent()
        self.product_agent = ProductAgent()
        self.recommendation_agent = RecommendationAgent()
    
    def process(self, input_data):
        """
        Process input data and coordinate the workflow between agents.
        
        Args:
            input_data: Dictionary containing input parameters
                - customer_id: ID of the customer
                - request_type: Type of request ('recommendation', 'profile_update', etc.)
                - additional parameters depending on request_type
                
        Returns:
            Dictionary containing results from the coordinated agents
        """
        self.log_activity("request_received", input_data)
        
        request_type = input_data.get('request_type', 'recommendation')
        customer_id = input_data.get('customer_id')
        
        if not customer_id:
            return {"error": "Customer ID is required"}
        
        # Step 1: Get customer profile and analysis
        customer_data = self.customer_agent.process({
            "customer_id": customer_id,
            "action": "analyze_profile"
        })
        
        self.log_activity("customer_processed", {"customer_id": customer_id})
        
        # Step 2: Get relevant products based on customer data
        relevant_categories = customer_data.get('relevant_categories', [])
        browsing_history = customer_data.get('browsing_history', [])
        
        product_data = self.product_agent.process({
            "categories": relevant_categories,
            "customer_data": customer_data,
            "action": "find_relevant_products"
        })
        
        self.log_activity("products_processed", {"categories": relevant_categories})
        
        # Step 3: Generate recommendations
        recommendations = self.recommendation_agent.process({
            "customer_data": customer_data,
            "product_data": product_data,
            "action": "generate_recommendations"
        })
        
        self.log_activity("recommendations_generated", {"count": len(recommendations.get('recommendations', []))})
        
        # Step 4: Format and return results
        result = {
            "customer_id": customer_id,
            "customer_segment": customer_data.get('customer_segment'),
            "recommendations": recommendations.get('recommendations', []),
            "explanation": recommendations.get('explanation', "")
        }
        
        return result
    
    def handle_feedback(self, feedback_data):
        """
        Handle feedback on recommendations.
        
        Args:
            feedback_data: Dictionary containing feedback
                - customer_id: ID of the customer
                - product_id: ID of the product
                - feedback: Feedback value (1 for positive, -1 for negative)
        """
        customer_id = feedback_data.get('customer_id')
        product_id = feedback_data.get('product_id')
        feedback = feedback_data.get('feedback')
        
        if not all([customer_id, product_id, feedback]):
            return {"error": "Missing required feedback data"}
        
        # Update the recommendation feedback in the database
        query = """
        UPDATE recommendations 
        SET feedback = ? 
        WHERE customer_id = ? AND product_id = ?
        """
        self.db.execute_query(query, (feedback, customer_id, product_id))
        
        # Inform the recommendation agent about the feedback for learning
        self.recommendation_agent.process({
            "action": "learn_from_feedback",
            "customer_id": customer_id,
            "product_id": product_id,
            "feedback": feedback
        })
        
        return {"status": "feedback_recorded"}