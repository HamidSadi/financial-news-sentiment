from fastapi import Query, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

# Import our application modules
from .news_scraper import get_financial_news
from .utils import format_response

logger = logging.getLogger("financial_sentiment")

async def get_news_endpoint(tickers: str = Query(..., description="Comma separated list of stock tickers"),
                           days: Optional[int] = Query(7, description="Number of days to look back"),
                           max_results: Optional[int] = Query(100, description="Maximum number of news items to return per ticker")):
    """
    Endpoint to get news with sentiment analysis for specified tickers.
    """
    try:
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        
        # Ensure days has a valid value
        search_days = 7 if days is None else max(1, days)
        
        # Ensure max_results has a valid value
        results_limit = 100 if max_results is None else max(1, max_results)
        
        all_news = []
        for ticker in ticker_list:
            news = get_financial_news(ticker, search_days, results_limit)
            all_news.extend(news)
        
        # Sort by date (newest first)
        all_news = sorted(all_news, key=lambda x: x["published_date"], reverse=True)
        
        # Limit the total number of results across all tickers
        if len(all_news) > results_limit * 2:  # Allow more results for multiple tickers
            logger.info(f"Limiting total results from {len(all_news)} to {results_limit * 2}")
            all_news = all_news[:results_limit * 2]
            
        return all_news
    except Exception as e:
        logger.error(f"Error in get_news: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

async def get_sentiment_summary_endpoint(tickers: str = Query(..., description="Comma separated list of stock tickers"),
                                        days: Optional[int] = Query(7, description="Number of days to look back"),
                                        max_results: Optional[int] = Query(100, description="Maximum number of news items to consider per ticker")):
    """
    Endpoint to get sentiment summary stats by ticker.
    """
    try:
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        
        # Ensure days has a valid value
        search_days = 7 if days is None else max(1, days)
        
        # Ensure max_results has a valid value
        results_limit = 100 if max_results is None else max(1, max_results)
        
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
            
            # Calculate weighted average score based on sentiment score (confidence)
            weighted_sum = sum(sentiment_values[item["sentiment"]] * item["score"] for item in news)
            total_weight = sum(item["score"] for item in news)
            weighted_avg_score = weighted_sum / total_weight if total_weight > 0 else 0
            
            # Regular average score
            avg_score = sum(sentiment_values[item["sentiment"]] for item in news) / len(news)
            
            summary[ticker] = {
                "total_news": len(news),
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "avg_sentiment_score": avg_score,
                "weighted_avg_score": weighted_avg_score
            }
        
        return summary
    except Exception as e:
        logger.error(f"Error in get_sentiment_summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

async def export_data_endpoint(tickers: str = Query(..., description="Comma separated list of stock tickers"),
                              days: Optional[int] = Query(30, description="Number of days to look back"),
                              max_results: Optional[int] = Query(500, description="Maximum number of news items to export")):
    """
    Endpoint to get sentiment data for export.
    """
    try:
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        
        # Ensure days has a valid value
        search_days = 30 if days is None else max(1, days)
        
        # Ensure max_results has a valid value
        results_limit = 500 if max_results is None else max(10, max_results)
        
        all_news = []
        for ticker in ticker_list:
            # For exports, we allow more data than regular API calls
            news = get_financial_news(ticker, search_days, results_limit)
            all_news.extend(news)
        
        # Sort by date (oldest first for chronological order in exports)
        all_news = sorted(all_news, key=lambda x: x["published_date"])
        
        # Limit the total size of the export if it's very large
        if len(all_news) > results_limit:
            logger.info(f"Limiting export data from {len(all_news)} to {results_limit} items")
            all_news = all_news[:results_limit]
        
        return all_news
    except Exception as e:
        logger.error(f"Error in export_data: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")