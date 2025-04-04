import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from datetime import datetime

# API configuration
API_URL = "http://localhost:8000"

def get_customer_list():
    """Get list of customers from API."""
    try:
        # In a real app, would call API endpoint for this
        # For demo purposes, we'll use a pre-loaded list
        return [
            {"id": "C1000", "name": "Emma Davis", "segment": "New Visitor"},
            {"id": "C1001", "name": "Raj Patel", "segment": "Occasional Shopper"},
            {"id": "C1002", "name": "Alex Kim", "segment": "Occasional Shopper"},
            {"id": "C1003", "name": "Sarah Johnson", "segment": "Frequent Buyer"},
            {"id": "C1004", "name": "Taylor Lee", "segment": "Frequent Buyer"},
            {"id": "C1005", "name": "Jordan Miller", "segment": "Frequent Buyer"},
            {"id": "C1006", "name": "Casey Smith", "segment": "New Visitor"},
            {"id": "C1007", "name": "Morgan Wilson", "segment": "Frequent Buyer"},
            {"id": "C1008", "name": "Riley Brown", "segment": "New Visitor"},
            {"id": "C1009", "name": "Sam Taylor", "segment": "Occasional Shopper"},
        ]
    except:
        return []

def get_customer_details(customer_id):
    """Get customer details from API."""
    try:
        response = requests.get(f"{API_URL}/customers/{customer_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        # For demo purposes, return mock data if API not available
        return {
            "customer_id": customer_id,
            "age": 28,
            "gender": "Female",
            "location": "Chennai",
            "browsing_history": ["Books", "Fashion"],
            "purchase_history": ["Biography", "Jeans"],
            "customer_segment": "New Visitor",
            "avg_order_value": 4806.99,
            "holiday": False,
            "season": "Winter"
        }

def get_recommendations(customer_id):
    """Get recommendations for customer from API."""
    try:
        response = requests.post(
            f"{API_URL}/recommendations",
            json={"customer_id": customer_id, "limit": 5}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"recommendations": [], "explanation": "Error getting recommendations"}
    except:
        # For demo purposes, return mock data if API not available
        return {
            "customer_id": customer_id,
            "customer_segment": "New Visitor",
            "recommendations": [
                {"product_id": "P2003", "category": "Books", "price": 4902, "score": 0.85, "reason": "Based on your browsing history"},
                {"product_id": "P2000", "category": "Fashion", "price": 1713, "score": 0.78, "reason": "Popular in your segment"},
                {"product_id": "P2015", "category": "Books", "price": 3954, "score": 0.72, "reason": "Matches your interests"},
                {"product_id": "P2010", "category": "Books", "price": 1285, "score": 0.67, "reason": "Frequently bought together"},
                {"product_id": "P2005", "category": "Fashion", "price": 1451, "score": 0.63, "reason": "Seasonal recommendation"}
            ],
            "explanation": "These recommendations are based on your browsing history of Books and Fashion items, as well as your previous purchases. We've also included some trending items in these categories for the Winter season."
        }

def get_product_details(product_id):
    """Get product details from API."""
    try:
        response = requests.get(f"{API_URL}/products/{product_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        # For demo purposes, return mock data if API not available
        if product_id == "P2003":
            return {
                "product_id": "P2003",
                "category": "Books",
                "subcategory": "Comics",
                "price": 4902,
                "brand": "Brand D",
                "avg_rating_similar": 3.4,
                "product_rating": 4.2,
                "sentiment_score": 0.8,
                "holiday": False,
                "season": "Winter",
                "geographical_location": "Germany",
                "similar_products": ["Biography", "Non-fiction", "Comics"]
            }
        else:
            return {
                "product_id": product_id,
                "category": "Unknown",
                "subcategory": "Unknown",
                "price": 0,
                "brand": "Unknown",
                "product_rating": 0,
                "sentiment_score": 0
            }

def submit_feedback(customer_id, product_id, feedback):
    """Submit feedback on recommendation."""
    try:
        response = requests.post(
            f"{API_URL}/feedback",
            json={"customer_id": customer_id, "product_id": product_id, "feedback": feedback}
        )
        if response.status_code == 200:
            return True
        else:
            return False
    except:
        # For demo purposes, return success if API not available
        return True

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Smart Shopping Demo",
        page_icon="🛍️",
        layout="wide"
    )
    
    st.title("🛍️ Smart Shopping: AI-Powered E-Commerce Recommendations")
    st.markdown("### Multi-Agent Personalized Recommendation System")
    
    # Main layout
    col1, col2 = st.columns([1, 3])
    
    # Sidebar for customer selection
    with col1:
        st.subheader("Select Customer")
        customers = get_customer_list()
        customer_options = {f"{c['name']} ({c['segment']})": c['id'] for c in customers}
        selected_customer_display = st.selectbox(
            "Choose a customer:",
            options=list(customer_options.keys())
        )
        selected_customer_id = customer_options[selected_customer_display]
        
        # Get customer details
        customer = get_customer_details(selected_customer_id)
        
        if customer:
            st.subheader("Customer Profile")
            st.markdown(f"**ID:** {customer['customer_id']}")
            st.markdown(f"**Age:** {customer['age']}")
            st.markdown(f"**Gender:** {customer['gender']}")
            st.markdown(f"**Location:** {customer['location']}")
            st.markdown(f"**Segment:** {customer['customer_segment']}")
            st.markdown(f"**Avg Order Value:** ${customer['avg_order_value']:.2f}")
            
            st.subheader("Browsing History")
            if customer.get('browsing_history'):
                for category in customer['browsing_history']:
                    st.markdown(f"- {category}")
            else:
                st.markdown("No browsing history available")
            
            st.subheader("Purchase History")
            if customer.get('purchase_history'):
                for item in customer['purchase_history']:
                    st.markdown(f"- {item}")
            else:
                st.markdown("No purchase history available")
    
    # Main content area
    with col2:
        st.subheader("Personalized Recommendations")
        
        # Get recommendations
        with st.spinner("Generating recommendations..."):
            recommendations = get_recommendations(selected_customer_id)
        
        # Display explanation
        if recommendations.get('explanation'):
            st.markdown(f"**Why these recommendations?** {recommendations['explanation']}")
        
        # Display recommendations
        if recommendations.get('recommendations'):
            recs = recommendations['recommendations']
            
            # Convert to DataFrame for display
            rec_df = pd.DataFrame(recs)
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["Recommendations", "Analysis"])
            
            with tab1:
                # Display recommendations as cards
                for i, rec in enumerate(recs):
                    with st.container():
                        cols = st.columns([3, 1])
                        
                        # Product info
                        with cols[0]:
                            product = get_product_details(rec['product_id'])
                            if product:
                                st.markdown(f"### {i+1}. {product['subcategory']} ({product['category']})")
                                st.markdown(f"**Brand:** {product['brand']}")
                                st.markdown(f"**Price:** ${product['price']:.2f}")
                                st.markdown(f"**Rating:** {product['product_rating']}/5.0")
                                st.markdown(f"**Why recommended:** {rec['reason']}")
                        
                        # Feedback buttons
                        with cols[1]:
                            st.markdown("### ")  # Spacing
                            if st.button("👍 Like", key=f"like_{rec['product_id']}"):
                                success = submit_feedback(selected_customer_id, rec['product_id'], 1)
                                if success:
                                    st.success("Feedback submitted!")
                            
                            if st.button("👎 Dislike", key=f"dislike_{rec['product_id']}"):
                                success = submit_feedback(selected_customer_id, rec['product_id'], -1)
                                if success:
                                    st.success("Feedback submitted!")
                    
                    st.markdown("---")
            
            with tab2:
                st.subheader("Recommendation Analysis")
                
                # Distribution by category
                st.markdown("#### Category Distribution")
                category_counts = rec_df['category'].value_counts().reset_index()
                category_counts.columns = ['Category', 'Count']
                
                fig1 = px.pie(
                    category_counts, 
                    values='Count', 
                    names='Category', 
                    title='Recommendations by Category',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig1)
                
                # Price distribution
                st.markdown("#### Price Distribution")
                fig2 = px.histogram(
                    rec_df,
                    x='price',
                    nbins=10,
                    title='Price Distribution of Recommendations',
                    labels={'price': 'Price ($)'},
                    color_discrete_sequence=['#3366CC']
                )
                st.plotly_chart(fig2)
                
                # Confidence scores
                st.markdown("#### Recommendation Confidence")
                fig3 = px.bar(
                    rec_df,
                    y='product_id',
                    x='score',
                    orientation='h',
                    title='Recommendation Confidence Scores',
                    labels={'product_id': 'Product', 'score': 'Confidence Score'},
                    color='score',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig3)

        else:
            st.warning("No recommendations available for this customer.")

        # System status
        st.subheader("System Status")
        with st.expander("Agent Status"):
            agent_status = {
                "Customer Profiling Agent": "Active",
                "Product Filtering Agent": "Active",
                "Collaborative Filtering Agent": "Active",
                "Content-Based Filtering Agent": "Active",
                "Ranking Agent": "Active",
                "Explanation Agent": "Active"
            }
            
            for agent, status in agent_status.items():
                st.markdown(f"**{agent}**: {status}")
                
        # Last updated timestamp
        st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

if __name__ == "__main__":
    main()