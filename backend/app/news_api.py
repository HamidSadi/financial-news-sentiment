"""
Module for fetching financial news from external News API.
"""
import logging
import requests
from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional

logger = logging.getLogger("financial_sentiment")

# Get API key from environment variables with fallback to default value
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "7b1d5085942941a381128b6349c59e19")

def get_news_from_api(ticker: str, days: int = 7, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch financial news from NewsAPI.org for a given ticker with improved error handling,
    rate limiting awareness, and comprehensive search.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, MSFT)
        days: Number of days to look back (capped at 30 due to API limits)
        max_results: Maximum number of news items to return (default 100)
        
    Returns:
        List of news items with basic information
    """
    logger.info(f"Fetching news from NewsAPI for {ticker} for past {days} days, max {max_results} results")
    
    try:
        # Calculate date range
        end_date = datetime.now()
        
        # NewsAPI free plan only allows us to get news from the last 30 days
        # So we'll cap the days at 30 to avoid empty results for longer periods
        search_days = min(days, 30)
        logger.info(f"Using search period of {search_days} days (NewsAPI free plan limitation)")
        
        start_date = end_date - timedelta(days=search_days)
        
        # Format dates for API
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Create search query for company by combining ticker and company name
        # This helps get more relevant results
        company_names = {
            'AAPL': 'Apple',
            'MSFT': 'Microsoft',
            'GOOGL': 'Google',
            'AMZN': 'Amazon',
            'TSLA': 'Tesla',
            'META': 'Facebook OR Meta',
            'NFLX': 'Netflix',
            'NVDA': 'Nvidia',
            'IBM': 'IBM',
            'INTC': 'Intel',
            'AMD': 'AMD',
            'ORCL': 'Oracle',
            'CRM': 'Salesforce',
            'ADBE': 'Adobe',
            'PYPL': 'PayPal',
            'CSCO': 'Cisco',
            # Add more mappings as needed
        }
        
        # Use company name if available, otherwise use ticker
        company_name = company_names.get(ticker, ticker)
        
        # Create a more comprehensive search query
        # The format below will match articles that:
        # 1. Contain the company name AND stock/shares/market/earnings, OR
        # 2. Contain the ticker symbol AND stock/shares/market/earnings
        query = f"({company_name} AND (stock OR shares OR market OR earnings OR investor OR financial)) OR ({ticker} AND (stock OR shares OR market OR earnings OR investor OR financial))"
        
        # Make API request with pagination support
        url = "https://newsapi.org/v2/everything"
        all_articles = []
        page = 1
        page_size = min(100, max_results)  # NewsAPI allows max 100 per page
        
        # Keep fetching pages until we hit max_results or run out of articles
        while len(all_articles) < max_results:
            params = {
                'q': query,
                'from': from_date,
                'to': to_date,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': page_size,
                'page': page,
                'apiKey': NEWS_API_KEY
            }
            
            logger.info(f"Making request to NewsAPI for {ticker} (page {page})")
            response = requests.get(url, params=params)
            
            # Handle rate limiting (429) and other errors
            if response.status_code == 429:
                logger.warning("Rate limit exceeded for NewsAPI. Try again later.")
                break
            elif response.status_code != 200:
                logger.error(f"NewsAPI request failed with status {response.status_code}: {response.text}")
                break
            
            # Parse response
            data = response.json()
            articles = data.get('articles', [])
            all_articles.extend(articles)
            
            # If we got fewer articles than page size, we've reached the end
            if len(articles) < page_size:
                break
                
            # Move to next page
            page += 1
            
            # Check if we've reached API limit
            if data.get('totalResults', 0) <= len(all_articles):
                break
                
        # Format into our expected structure
        news_items = []
        seen_titles = set()  # Track titles to avoid duplicates
        
        for article in all_articles[:max_results]:
            # Skip articles without title
            title = article.get('title', '')
            if not title:
                continue
                
            # Skip duplicate titles (some news gets republished in different sources)
            # Strip whitespace and convert to lowercase for comparison
            normalized_title = title.strip().lower()
            if normalized_title in seen_titles:
                continue
                
            seen_titles.add(normalized_title)
            
            try:
                # Format published date
                published_date = datetime.strptime(
                    article.get('publishedAt', ''), 
                    "%Y-%m-%dT%H:%M:%SZ"
                ).strftime("%Y-%m-%d %H:%M:%S")
                
                # Create news item
                news_item = {
                    "title": title,
                    "publisher": article.get('source', {}).get('name', ''),
                    "link": article.get('url', ''),
                    "published_date": published_date,
                    "ticker": ticker,
                }
                
                news_items.append(news_item)
            except (ValueError, TypeError) as e:
                # Log but continue processing other articles
                logger.warning(f"Error processing article date for {title}: {e}")
                continue
        
        logger.info(f"Found {len(news_items)} news items for {ticker} from NewsAPI")
        return news_items
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching news from NewsAPI for {ticker}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error fetching news from NewsAPI for {ticker}: {str(e)}")
        return []

def is_api_key_valid() -> bool:
    """
    Check if the NewsAPI key is valid by making a test request.
    
    This function makes a lightweight request to the NewsAPI to verify if:
    1. The API key is valid (not unauthorized)
    2. We haven't exceeded rate limits
    3. The API endpoint is accessible
    
    Returns:
        bool: True if the API key is valid and accessible, False otherwise
    """
    try:
        logger.info(f"Validating NewsAPI key: {NEWS_API_KEY[:4]}...{NEWS_API_KEY[-4:]}")
        
        # Use a very small query to minimize API usage
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'market',  # Simple query term relevant to financial news
            'pageSize': 1,  # Request minimum possible results
            'language': 'en',
            'apiKey': NEWS_API_KEY
        }
        
        logger.info(f"Making test request to NewsAPI: {url}")
        
        # Add timeout to prevent hanging if API is down
        response = requests.get(url, params=params, timeout=5)
        
        # Handle different response codes
        if response.status_code == 200:
            # Success
            logger.info(f"NewsAPI key is valid and working! Response: {response.text[:100]}")
            return True
        elif response.status_code == 401:
            # Unauthorized - invalid API key
            logger.error(f"NewsAPI key is invalid. Status: 401. Please check your API key.")
            return False
        elif response.status_code == 429:
            # Rate limited
            logger.warning(f"NewsAPI rate limit exceeded. Please try again later.")
            return False
        else:
            # Other errors
            logger.warning(f"NewsAPI key validation failed: Status {response.status_code}, Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Request to NewsAPI timed out. The service might be slow or down.")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to NewsAPI. Please check your internet connection.")
        return False
    except Exception as e:
        logger.error(f"Error validating NewsAPI key: {str(e)}")
        return False