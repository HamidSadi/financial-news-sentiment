import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import random
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Class for news data
class NewsItem:
    def __init__(self, title, publisher, link, published_date, ticker, sentiment, score):
        self.title = title
        self.publisher = publisher
        self.link = link
        self.published_date = published_date
        self.ticker = ticker
        self.sentiment = sentiment
        self.score = score
    
    def to_dict(self):
        return {
            "title": self.title,
            "publisher": self.publisher,
            "link": self.link,
            "published_date": self.published_date,
            "ticker": self.ticker,
            "sentiment": self.sentiment,
            "score": self.score
        }

# Function to analyze sentiment using a simple rule-based approach
def analyze_sentiment(text):
    """Simple rule-based sentiment analysis"""
    # Check for positive keywords
    positive_keywords = ['surge', 'record', 'exceeding', 'strong', 'grow', 'growth', 'breakthrough', 'positive']
    negative_keywords = ['downgrade', 'concerns', 'vulnerabilities', 'issues', 'challenges', 'mount', 'labor', 'divided', 'volatility', 'fears', 'recession']
    
    # Count keyword occurrences
    positive_count = sum(1 for word in positive_keywords if word.lower() in text.lower())
    negative_count = sum(1 for word in negative_keywords if word.lower() in text.lower())
    
    # Determine sentiment based on keyword counts
    if positive_count > negative_count:
        sentiment = "positive"
        # Add some randomness to score for variety
        score = 0.7 + (random.random() * 0.3)
    elif negative_count > positive_count:
        sentiment = "negative"
        score = 0.7 + (random.random() * 0.3)
    else:
        sentiment = "neutral"
        score = 0.5 + (random.random() * 0.4)
    
    return {"sentiment": sentiment, "score": score}

# Function to get demo financial news
def get_financial_news(ticker, days=7, max_results=100):
    """
    Get demo financial news for a ticker
    
    Args:
        ticker (str): Stock ticker symbol
        days (int): Number of days to look back (defaults to 7)
        max_results (int): Maximum number of news items to return
        
    Returns:
        List of news items with sentiment analysis
    """
    try:
        # Ensure days is a positive integer (handle None case)
        search_days = 7
        if days is not None:
            search_days = max(1, days)
            
        # Define cutoff date
        cutoff_date = datetime.now() - timedelta(days=search_days)
        
        # Common template news
        common_news = [
            {
                "title": "Markets reach record highs as tech stocks surge",
                "publisher": "Financial Times",
                "link": "https://example.com/markets-record-high",
                "published_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "Federal Reserve announces plans to maintain interest rates",
                "publisher": "Wall Street Journal", 
                "link": "https://example.com/fed-rates",
                "published_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "Global recession fears grow as manufacturing slows",
                "publisher": "Reuters",
                "link": "https://example.com/recession-fears",
                "published_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": "Inflation data shows signs of moderating, analysts say",
                "publisher": "Bloomberg",
                "link": "https://example.com/inflation-data",
                "published_date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        # Ticker-specific news
        ticker_news = {
            "AAPL": [
                {
                    "title": f"{ticker} reports record quarterly earnings, exceeding expectations",
                    "publisher": "CNBC",
                    "link": f"https://example.com/{ticker.lower()}-earnings",
                    "published_date": (datetime.now() - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"New {ticker} product line launches to strong demand",
                    "publisher": "TechCrunch",
                    "link": f"https://example.com/{ticker.lower()}-product-launch",
                    "published_date": (datetime.now() - timedelta(days=2, hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"Analyst downgrades {ticker} citing supply chain concerns",
                    "publisher": "Seeking Alpha",
                    "link": f"https://example.com/{ticker.lower()}-downgrade",
                    "published_date": (datetime.now() - timedelta(days=3, hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
            "MSFT": [
                {
                    "title": f"{ticker} cloud services grow 40% year-over-year",
                    "publisher": "CNBC",
                    "link": f"https://example.com/{ticker.lower()}-cloud-growth",
                    "published_date": (datetime.now() - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"{ticker} announces new AI partnerships with industry leaders",
                    "publisher": "TechCrunch",
                    "link": f"https://example.com/{ticker.lower()}-ai-partnerships",
                    "published_date": (datetime.now() - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"Security vulnerabilities discovered in {ticker} products",
                    "publisher": "ZDNet",
                    "link": f"https://example.com/{ticker.lower()}-security-issues",
                    "published_date": (datetime.now() - timedelta(days=3, hours=7)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
            "GOOGL": [
                {
                    "title": f"{ticker} ad revenue exceeds projections in quarterly report",
                    "publisher": "CNBC",
                    "link": f"https://example.com/{ticker.lower()}-ad-revenue",
                    "published_date": (datetime.now() - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"Regulatory challenges mount for {ticker} in European markets",
                    "publisher": "Financial Times",
                    "link": f"https://example.com/{ticker.lower()}-eu-regulation",
                    "published_date": (datetime.now() - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"{ticker} unveils new search algorithm with enhanced AI capabilities",
                    "publisher": "The Verge",
                    "link": f"https://example.com/{ticker.lower()}-search-ai",
                    "published_date": (datetime.now() - timedelta(days=3, hours=6)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
            "AMZN": [
                {
                    "title": f"{ticker} e-commerce sales surge during holiday season",
                    "publisher": "Reuters",
                    "link": f"https://example.com/{ticker.lower()}-holiday-sales",
                    "published_date": (datetime.now() - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"{ticker} expands logistics network with new fulfillment centers",
                    "publisher": "Business Insider",
                    "link": f"https://example.com/{ticker.lower()}-logistics-expansion",
                    "published_date": (datetime.now() - timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"Labor union pushes for worker rights at {ticker} warehouses",
                    "publisher": "Washington Post",
                    "link": f"https://example.com/{ticker.lower()}-labor-issues",
                    "published_date": (datetime.now() - timedelta(days=3, hours=5)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ],
            "TSLA": [
                {
                    "title": f"{ticker} production numbers hit new record in latest quarter",
                    "publisher": "Electrek",
                    "link": f"https://example.com/{ticker.lower()}-production-record",
                    "published_date": (datetime.now() - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"{ticker} CEO announces new battery technology breakthrough",
                    "publisher": "CleanTechnica",
                    "link": f"https://example.com/{ticker.lower()}-battery-tech",
                    "published_date": (datetime.now() - timedelta(days=2, hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                },
                {
                    "title": f"Analysts divided on {ticker} stock valuation after recent volatility",
                    "publisher": "Barron's",
                    "link": f"https://example.com/{ticker.lower()}-valuation-debate",
                    "published_date": (datetime.now() - timedelta(days=3, hours=3)).strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }
        
        # Default news for any ticker not in our demo set
        default_ticker_news = [
            {
                "title": f"{ticker} shares move on market trends",
                "publisher": "Market Watch",
                "link": f"https://example.com/{ticker.lower()}-shares",
                "published_date": (datetime.now() - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": f"Analysts issue new price targets for {ticker}",
                "publisher": "Seeking Alpha",
                "link": f"https://example.com/{ticker.lower()}-price-targets",
                "published_date": (datetime.now() - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "title": f"{ticker} announces quarterly dividend",
                "publisher": "Investor's Business Daily",
                "link": f"https://example.com/{ticker.lower()}-dividend",
                "published_date": (datetime.now() - timedelta(days=3, hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        # Combine common news with ticker-specific news
        all_news = common_news.copy()
        
        # Add ticker-specific news if available, otherwise use default
        specific_news = ticker_news.get(ticker, default_ticker_news)
        all_news.extend(specific_news)
        
        # Filter by date and analyze sentiment
        processed_news = []
        for item in all_news:
            # Convert string date to datetime object
            publish_date = datetime.strptime(item["published_date"], "%Y-%m-%d %H:%M:%S")
            
            # Skip if older than cutoff date
            if publish_date < cutoff_date:
                continue
                
            # Get headline
            title = item.get("title", "")
            
            # Skip empty headlines
            if not title:
                continue
                
            # Analyze sentiment
            sentiment_result = analyze_sentiment(title)
            
            # Create news item
            news_item = {
                "title": title,
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "published_date": publish_date.strftime("%Y-%m-%d %H:%M:%S"),
                "ticker": ticker,
                "sentiment": sentiment_result["sentiment"],
                "score": sentiment_result["score"]
            }
            
            processed_news.append(news_item)
            
        return processed_news
    except Exception as e:
        logger.error(f"Error getting news for {ticker}: {e}")
        return []

# Endpoint to get news with sentiment analysis
@app.get("/api/news", response_model=List[Dict[str, Any]])
async def get_news(tickers: str = Query(..., description="Comma separated list of stock tickers"),
                  days: Optional[int] = Query(7, description="Number of days to look back"),
                  max_results: Optional[int] = Query(100, description="Maximum number of news items to return per ticker")):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
    
    # Ensure days is a positive integer
    search_days = 7 if days is None else max(1, days)
    
    # Ensure max_results is a positive integer
    results_limit = 100 if max_results is None else max(1, max_results)
    
    logger.info(f"Getting news for tickers: {ticker_list}, days: {search_days}, max_results: {results_limit}")
    
    all_news = []
    for ticker in ticker_list:
        news = get_financial_news(ticker, search_days, results_limit)
        all_news.extend(news)
    
    # Sort by date (newest first)
    all_news = sorted(all_news, key=lambda x: x["published_date"], reverse=True)
    
    # Limit total results if necessary
    if len(all_news) > results_limit * 2:
        logger.info(f"Limiting total results from {len(all_news)} to {results_limit * 2}")
        all_news = all_news[:results_limit * 2]
    
    return all_news

# Endpoint to get sentiment summary stats by ticker
@app.get("/api/sentiment_summary")
async def get_sentiment_summary(tickers: str = Query(..., description="Comma separated list of stock tickers"),
                               days: Optional[int] = Query(7, description="Number of days to look back"),
                               max_results: Optional[int] = Query(100, description="Maximum number of news items to consider per ticker")):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
    
    # Ensure days is a positive integer
    search_days = 7 if days is None else max(1, days)
    
    # Ensure max_results is a positive integer
    results_limit = 100 if max_results is None else max(1, max_results)
    
    logger.info(f"Getting sentiment summary for tickers: {ticker_list}, days: {search_days}, max_results: {results_limit}")
    
    summary = {}
    for ticker in ticker_list:
        news = get_financial_news(ticker, search_days, results_limit)
        
        if not news:
            summary[ticker] = {
                "total_news": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "avg_sentiment_score": 0
            }
            continue
        
        positive = sum(1 for item in news if item["sentiment"] == "positive")
        negative = sum(1 for item in news if item["sentiment"] == "negative")
        neutral = sum(1 for item in news if item["sentiment"] == "neutral")
        
        # Calculate average sentiment score (map sentiment to values: positive=1, neutral=0, negative=-1)
        sentiment_values = {
            "positive": 1,
            "neutral": 0,
            "negative": -1
        }
        
        avg_score = sum(sentiment_values[item["sentiment"]] for item in news) / len(news)
        
        summary[ticker] = {
            "total_news": len(news),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "avg_sentiment_score": avg_score
        }
    
    return summary

# Endpoint to get sentiment data for export
@app.get("/api/export", response_model=List[Dict[str, Any]])
async def export_data(tickers: str = Query(..., description="Comma separated list of stock tickers"),
                     days: Optional[int] = Query(30, description="Number of days to look back"),
                     max_results: Optional[int] = Query(500, description="Maximum number of news items to export")):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
    
    # Ensure days is a positive integer
    search_days = 30 if days is None else max(1, days)
    
    # Ensure max_results is a positive integer - we allow more for exports
    results_limit = 500 if max_results is None else max(1, max_results)
    
    logger.info(f"Exporting data for tickers: {ticker_list}, days: {search_days}, max_results: {results_limit}")
    
    all_news = []
    for ticker in ticker_list:
        news = get_financial_news(ticker, search_days, results_limit // len(ticker_list))
        all_news.extend(news)
    
    # Sort by date
    all_news = sorted(all_news, key=lambda x: x["published_date"])
    
    # Limit total results if necessary
    if len(all_news) > results_limit:
        logger.info(f"Limiting export results from {len(all_news)} to {results_limit}")
        all_news = all_news[:results_limit]
    
    return all_news

# Endpoint for health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Endpoint for analyzing custom text
@app.post("/api/analyze_text")
async def analyze_custom_text(text_data: dict):
    try:
        text = text_data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
            
        # Analyze sentiment
        sentiment_result = analyze_sentiment(text)
        
        return {
            "status": "success",
            "data": {
                "text": text,
                "sentiment": sentiment_result["sentiment"],
                "score": sentiment_result["score"]
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing text: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)