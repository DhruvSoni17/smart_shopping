from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import json

from agents.coordinator import CoordinatorAgent
from database.db_manager import DatabaseManager
from database.schema import create_database_schema

# Initialize FastAPI app
app = FastAPI(
    title="Smart Shopping API",
    description="API for Smart Shopping multi-agent recommendation system",
    version="1.0.0"
)

# Initialize agents and services
coordinator = CoordinatorAgent()
db = DatabaseManager()


# Models for request and response data
class RecommendationRequest(BaseModel):
    customer_id: str
    limit: Optional[int] = 10

class FeedbackRequest(BaseModel):
    customer_id: str
    product_id: str
    feedback: int  # 1 for positive, -1 for negative

class CustomerProfileRequest(BaseModel):
    customer_id: str
    updates: Optional[Dict[str, Any]] = None


# Endpoints
@app.get("/")
async def root():
    """Root endpoint returning API info."""
    return {
        "name": "Smart Shopping API",
        "version": "1.0.0",
        "description": "Multi-agent system for personalized e-commerce recommendations"
    }


@app.post("/recommendations")
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized product recommendations for a customer.
    """
    try:
        # Process recommendation request through coordinator agent
        result = coordinator.process({
            "customer_id": request.customer_id,
            "request_type": "recommendation",
            "limit": request.limit
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on a recommendation.
    """
    try:
        # Process feedback through coordinator agent
        result = coordinator.handle_feedback({
            "customer_id": request.customer_id,
            "product_id": request.product_id,
            "feedback": request.feedback
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """
    Get customer profile data.
    """
    try:
        customer = db.get_customer(customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        return customer
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/customers/{customer_id}")
async def update_customer(customer_id: str, request: Dict[str, Any] = Body(...)):
    """
    Update customer profile data.
    """
    try:
        # Check if customer exists
        customer = db.get_customer(customer_id)
        
        if not customer:
            raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
        
        # Process customer update through coordinator agent
        result = coordinator.customer_agent.process({
            "customer_id": customer_id,
            "action": "update_profile",
            "updates": request
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products/{product_id}")
async def get_product(product_id: str):
    """
    Get product data.
    """
    try:
        product = db.get_product(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        
        return product
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/products")
async def get_products(category: Optional[str] = None, limit: int = 20, offset: int = 0):
    """
    Get products, optionally filtered by category.
    """
    try:
        if category:
            query = "SELECT * FROM products WHERE category = ? LIMIT ? OFFSET ?"
            products = db.execute_query(query, (category, limit, offset))
        else:
            query = "SELECT * FROM products LIMIT ? OFFSET ?"
            products = db.execute_query(query, (limit, offset))
        
        return {"products": [dict(p) for p in products]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/product/{product_id}")
async def analyze_product(product_id: str):
    """
    Analyze a product using the product agent.
    """
    try:
        # Process product analysis through coordinator agent
        result = coordinator.product_agent.process({
            "product_id": product_id,
            "action": "analyze_product"
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/customer/{customer_id}")
async def analyze_customer(customer_id: str):
    """
    Analyze a customer using the customer agent.
    """
    try:
        # Process customer analysis through coordinator agent
        result = coordinator.customer_agent.process({
            "customer_id": customer_id,
            "action": "analyze_profile"
        })
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# App startup and shutdown events
@app.on_event("startup")
async def startup():
    """Startup event to initialize database and other resources."""
    # Ensure database schema exists
    create_database_schema()


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event to clean up resources."""
    # Close database connection
    db.close()