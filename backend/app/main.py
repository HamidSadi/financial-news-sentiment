import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import logging

# Import our application modules
from .api import get_news_endpoint, get_sentiment_summary_endpoint, export_data_endpoint
from .utils import setup_logging

# Set up logging
logger = setup_logging()

# Initialize FastAPI app
app = FastAPI(title="Financial News Sentiment Analysis API")

# Add CORS middleware to allow Streamlit frontend to call our API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.get("/api/news")(get_news_endpoint)
app.get("/api/sentiment_summary")(get_sentiment_summary_endpoint)
app.get("/api/export")(export_data_endpoint)

# Endpoint for health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# For local development
if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)