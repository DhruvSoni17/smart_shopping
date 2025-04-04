from database.db_manager import DatabaseManager

class CustomerSegmentation:
    """
    Tool for customer segmentation analysis.
    """
    
    def __init__(self):
        """Initialize the customer segmentation tool."""
        self.db = DatabaseManager()
    
    def get_customer_segment(self, customer_id):
        """
        Get the segment for a specific customer.
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Customer segment string
        """
        customer = self.db.get_customer(customer_id)
        
        if customer:
            return customer.get('customer_segment', '')
        
        return ''
    
    def analyze_segment_preferences(self, segment):
        """
        Analyze preferences for a customer segment.
        
        Args:
            segment: Customer segment to analyze
            
        Returns:
            Dictionary with segment preference analysis
        """
        # Query for customers in this segment
        query = "SELECT * FROM customers WHERE customer_segment = ?"
        results = self.db.execute_query(query, (segment,))
        
        if not results:
            return {
                "segment": segment,
                "count": 0,
                "preferences": {},
                "avg_order_value": 0
            }
        
        # Analyze browsing and purchase patterns
        browsing_counts = {}
        purchase_counts = {}
        total_avg_order_value = 0
        
        for customer in results:
            # Add to average order value
            total_avg_order_value += customer['avg_order_value']
            
            # Parse browsing history
            try:
                browsing_history = json.loads(customer['browsing_history'])
                for category in browsing_history:
                    browsing_counts[category] = browsing_counts.get(category, 0) + 1
            except:
                pass
            
            # Parse purchase history
            try:
                purchase_history = json.loads(customer['purchase_history'])
                for category in purchase_history:
                    purchase_counts[category] = purchase_counts.get(category, 0) + 1
            except:
                pass
        
        # Calculate average order value
        avg_order_value = total_avg_order_value / len(results) if results else 0
        
        # Sort browsing and purchase counts
        sorted_browsing = sorted(
            browsing_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        sorted_purchases = sorted(
            purchase_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return segment analysis
        return {
            "segment": segment,
            "count": len(results),
            "preferences": {
                "browsing": dict(sorted_browsing),
                "purchases": dict(sorted_purchases)
            },
            "avg_order_value": avg_order_value
        }
    
    def get_all_segments(self):
        """
        Get all customer segments and their counts.
        
        Returns:
            Dictionary mapping segments to customer counts
        """
        query = "SELECT customer_segment, COUNT(*) as count FROM customers GROUP BY customer_segment"
        results = self.db.execute_query(query)
        
        segments = {}
        for result in results:
            segments[result['customer_segment']] = result['count']
        
        return segments