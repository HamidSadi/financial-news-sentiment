from datetime import datetime, timedelta
import logging
import json
import os
from typing import List, Dict, Any, Optional

# Import our application modules
from .sentiment import analyze_sentiment
from .utils import format_date
from .news_api import get_news_from_api, is_api_key_valid
from .excel_news import get_news_from_excel

logger = logging.getLogger("financial_sentiment")

def get_financial_news(ticker: str, days: int = 7, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Get financial news headlines and analyze sentiment with improved handling.
    
    This function tries multiple data sources in the following order:
    1. NewsAPI.org (if API key is valid)
    2. Excel file with demo data (especially for historical data beyond 30 days)
    3. Hardcoded demo data (fallback)
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to look back (defaults to 7, will be at least 1)
        max_results: Maximum number of news items to return (default 100)
        
    Returns:
        List of news items with sentiment analysis
    """
    # Ensure days is a positive integer
    if days is None:
        days = 7
    days = max(1, days)
    
    logger.info(f"Getting news for ticker {ticker} over past {days} days, max {max_results} results")
    
    try:
        # Initialize empty news items list
        news_items = []
        news_sources_used = []
        
        # Check if NewsAPI key is valid
        if is_api_key_valid():
            logger.info("Using NewsAPI for retrieving financial news")
            # Get news from NewsAPI (supports pagination)
            news_items = get_news_from_api(ticker, days, max_results)
            if news_items:
                news_sources_used.append("NewsAPI")
                logger.info(f"Retrieved {len(news_items)} news items from NewsAPI")
        else:
            logger.warning("NewsAPI key invalid or rate limited, skipping NewsAPI source")
        
        # For requests over 30 days, also check Excel data which might have historical data
        # Or if NewsAPI returned too few results
        excel_threshold = min(30, max_results // 2)  # Get at least half from Excel for longer periods
        if days > 30 or len(news_items) < excel_threshold:
            logger.info(f"Supplementing with Excel data (NewsAPI items: {len(news_items)}, days: {days})")
            excel_items = get_news_from_excel(ticker, days)
            if excel_items:
                news_sources_used.append("Excel")
                logger.info(f"Retrieved {len(excel_items)} news items from Excel")
                
                # Add Excel items that aren't already in the list
                # (avoiding duplicates by checking normalized titles)
                existing_titles = {item.get("title", "").strip().lower() for item in news_items}
                for item in excel_items:
                    title = item.get("title", "").strip().lower()
                    if title and title not in existing_titles:
                        news_items.append(item)
                        existing_titles.add(title)
        
        # If still no results or not enough, use hardcoded demo data as last resort
        if not news_items or len(news_items) < 5:  # Ensure we have at least a few items
            logger.info(f"Insufficient results ({len(news_items)}), using hardcoded demo data")
            demo_items = get_demo_news(ticker, days)
            if demo_items:
                news_sources_used.append("Demo")
                
                # Add demo items that aren't already in the list
                existing_titles = {item.get("title", "").strip().lower() for item in news_items}
                for item in demo_items:
                    title = item.get("title", "").strip().lower()
                    if title and title not in existing_titles:
                        news_items.append(item)
                        existing_titles.add(title)
        
        # Ensure we don't exceed max_results
        if len(news_items) > max_results:
            logger.info(f"Truncating results from {len(news_items)} to max_results: {max_results}")
            news_items = news_items[:max_results]
            
        # Process each news item to add sentiment analysis
        processed_items = []
        for item in news_items:
            # Get headline
            title = item.get("title", "")
            
            # Skip empty headlines
            if not title:
                continue
                
            # Log the title we're analyzing for debugging
            logger.info(f"Analyzing sentiment for: {title[:50]}...")
                
            # Analyze sentiment
            sentiment_result = analyze_sentiment(title)
            
            # Create news item with sentiment
            news_item = {
                "title": title,
                "publisher": item.get("publisher", ""),
                "link": item.get("link", ""),
                "published_date": item.get("published_date", ""),
                "ticker": ticker,
                "sentiment": sentiment_result["sentiment"],
                "score": sentiment_result["score"]
            }
            
            processed_items.append(news_item)
        
        logger.info(f"Found {len(processed_items)} news items for {ticker} using sources: {', '.join(news_sources_used)}")
        return processed_items
        
    except Exception as e:
        logger.error(f"Error getting news for {ticker}: {str(e)}")
        # Return an empty list rather than propagating the exception
        return []

def get_demo_news(ticker: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Return demo news for a given ticker as a last resort fallback.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to look back
        
    Returns:
        List of demo news items
    """
    logger.info(f"Using hardcoded demo news for {ticker}")
    
    # Define cutoff date
    cutoff_date = datetime.now() - timedelta(days=days)
    
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
    result = common_news.copy()
    
    # Add ticker-specific news if available, otherwise use default
    specific_news = ticker_news.get(ticker, default_ticker_news)
    result.extend(specific_news)
    
    # Filter by date
    filtered_news = []
    for item in result:
        # Convert string date to datetime object
        publish_date = datetime.strptime(item["published_date"], "%Y-%m-%d %H:%M:%S")
        
        # Skip if older than cutoff date
        if publish_date < cutoff_date:
            continue
            
        # Add ticker field
        item["ticker"] = ticker
        filtered_news.append(item)
    
    return filtered_news