import http.server
import socketserver
import json
import random
import re
import urllib.parse
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("financial_sentiment")

# Get port from environment variable or use default
import os
PORT = int(os.environ.get("PORT", 8000))

# Demo data for financial news sentiment analysis
class NewsAPI:
    def __init__(self):
        """Initialize the news API with demo data"""
        logger.info("Initializing Financial News Sentiment Analysis API")
        
    def analyze_sentiment(self, text):
        """Enhanced rule-based sentiment analysis"""
        # Expanded keyword lists for better sentiment detection
        positive_keywords = [
            'surge', 'record', 'exceeding', 'strong', 'grow', 'growth', 'breakthrough', 'positive',
            'profit', 'gains', 'upgrade', 'beat', 'success', 'innovation', 'outperform', 'bullish',
            'earnings', 'upside', 'rally', 'recovery', 'advantage', 'rise', 'improved', 'expand'
        ]
        
        negative_keywords = [
            'downgrade', 'concerns', 'vulnerabilities', 'issues', 'challenges', 'mount', 'labor', 
            'divided', 'volatility', 'fears', 'recession', 'plunge', 'crash', 'drop', 'fall', 'loss',
            'decline', 'bearish', 'disappointing', 'missed', 'lawsuit', 'investigation', 'problem',
            'risk', 'struggle', 'warn', 'warning', 'crisis', 'cut', 'debt', 'layoff', 'bankruptcy',
            'scandal', 'fraud', 'fine', 'penalty', 'default', 'negative', 'underperform', 'slump',
            'downturn', 'trouble', 'failure', 'weak', 'poor'
        ]
        
        # Check for strongly negative phrases that should automatically determine sentiment
        strong_negative_phrases = [
            'stock plunges', 'shares plunge', 'stock plummets', 'shares plummet', 'stock crashes', 
            'shares crash', 'stock tanks', 'shares tank', 'stock collapses', 'shares collapse',
            'disappointing results', 'missed expectations', 'shareholder lawsuit', 'class action',
            'stock downgrade', 'rating downgrade', 'bankruptcy filing', 'fraud allegations',
            'major losses', 'financial troubles', 'revenue miss'
        ]
        
        # Check for strong negative phrases first
        for phrase in strong_negative_phrases:
            if phrase.lower() in text.lower():
                # Strong negative phrase found, return negative with high confidence
                return {"sentiment": "negative", "score": 0.8 + (random.random() * 0.2)}
        
        # Count keyword occurrences with word boundary checks to avoid partial matches
        positive_count = 0
        negative_count = 0
        
        # Check for word boundaries to improve accuracy
        words = re.findall(r'\b\w+\b', text.lower())
        
        for word in words:
            if word in [kw.lower() for kw in positive_keywords]:
                positive_count += 1
            if word in [kw.lower() for kw in negative_keywords]:
                negative_count += 1
                
        # Weight negative sentiment slightly higher to better detect negative news
        weighted_negative = negative_count * 1.2
        
        # Determine sentiment based on keyword counts
        if positive_count > weighted_negative:
            sentiment = "positive"
            # Add some randomness to score for variety
            score = 0.7 + (random.random() * 0.3)
        elif weighted_negative > positive_count:
            sentiment = "negative"
            score = 0.7 + (random.random() * 0.3)
        else:
            sentiment = "neutral"
            score = 0.5 + (random.random() * 0.4)
        
        return {"sentiment": sentiment, "score": score}
    
    def get_financial_news(self, ticker, days=7):
        """Get financial news for a ticker using our updated sources"""
        try:
            # Import the new implementation from backend/app
            import sys
            import os
            
            # Add backend directory to path if not already there
            backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
            if backend_dir not in sys.path:
                sys.path.append(backend_dir)
                
            # Try to import our improved news fetching module
            try:
                from backend.app.news_scraper import get_financial_news as get_news
                logger.info(f"Using improved news sources for {ticker}")
                return get_news(ticker, days)
            except ImportError:
                logger.warning(f"Could not import improved news sources, falling back to demo data for {ticker}")
            
            # Define cutoff date for fallback implementation
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
                sentiment_result = self.analyze_sentiment(title)
                
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
    
    def get_news(self, tickers, days=7, start_date=None, end_date=None, max_results=None):
        """Get news for multiple tickers with custom date range support"""
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        logger.info(f"Getting news for tickers: {ticker_list}, days: {days}, date range: {start_date} to {end_date}")
        
        all_news = []
        for ticker in ticker_list:
            # If we have a proper backend module, try to use it with custom params
            try:
                from backend.app.news_scraper import get_financial_news as get_news
                news = get_news(ticker, days=days, max_results=10000)  # Very high limit = effectively no limit
            except (ImportError, AttributeError):
                # Fallback to basic implementation
                news = self.get_financial_news(ticker, days)
                
            all_news.extend(news)
        
        # Apply custom date filtering if provided
        if start_date or end_date:
            filtered_news = []
            try:
                # Convert string dates to datetime if needed
                start_dt = None
                end_dt = None
                
                if start_date:
                    if isinstance(start_date, str):
                        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    else:
                        start_dt = start_date
                        
                if end_date:
                    if isinstance(end_date, str):
                        # Set end date to end of day
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                        end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    else:
                        end_dt = end_date
                
                # Filter news items by date
                for item in all_news:
                    item_date_str = item.get("published_date", "")
                    if item_date_str:
                        try:
                            item_date = datetime.strptime(item_date_str, "%Y-%m-%d %H:%M:%S")
                            
                            # Check if item is within date range
                            include_item = True
                            if start_dt and item_date < start_dt:
                                include_item = False
                            if end_dt and item_date > end_dt:
                                include_item = False
                                
                            if include_item:
                                filtered_news.append(item)
                        except ValueError:
                            # Skip items with invalid date format
                            pass
                
                all_news = filtered_news
                logger.info(f"Filtered to {len(all_news)} news items within date range")
            except Exception as e:
                logger.error(f"Error filtering by date range: {e}")
        
        # Sort by date (newest first)
        all_news = sorted(all_news, key=lambda x: x["published_date"], reverse=True)
        
        # Apply max_results only if specified and after date filtering
        if max_results and int(max_results) > 0:
            all_news = all_news[:int(max_results)]
            logger.info(f"Limited to {len(all_news)} news items based on max_results")
        
        logger.info(f"Returning {len(all_news)} total news items")
        return all_news
    
    def get_sentiment_summary(self, tickers, days=7, start_date=None, end_date=None, max_results=None):
        """Get sentiment summary for multiple tickers with custom date range support"""
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        logger.info(f"Getting sentiment summary for tickers: {ticker_list}, days: {days}, date range: {start_date} to {end_date}")
        
        summary = {}
        for ticker in ticker_list:
            # Get news with date filtering if provided
            if start_date or end_date:
                news = self.get_news(ticker, days, start_date, end_date, max_results)
            else:
                news = self.get_financial_news(ticker, days)
            
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
        
        logger.info(f"Generated sentiment summary for {len(ticker_list)} tickers")
        return summary
    
    def export_data(self, tickers, days=30, start_date=None, end_date=None, max_results=None):
        """Export data for multiple tickers with custom date range support"""
        ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
        logger.info(f"Exporting data for tickers: {ticker_list}, days: {days}, date range: {start_date} to {end_date}")
        
        # Use the get_news method which already handles date filtering
        all_news = self.get_news(tickers, days, start_date, end_date, max_results)
        
        # Sort by date (chronological order for exports)
        all_news = sorted(all_news, key=lambda x: x["published_date"])
        
        logger.info(f"Exporting {len(all_news)} news items")
        return all_news

# Create an HTTP request handler
class FinancialNewsHandler(http.server.BaseHTTPRequestHandler):
    api = NewsAPI()
    
    def _set_headers(self, content_type="application/json"):
        self.send_response(200)
        self.send_header("Content-type", content_type)
        # CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type, Accept")
        self.end_headers()
    
    def _parse_query_params(self):
        # Parse query parameters
        if "?" in self.path:
            path, query_string = self.path.split("?", 1)
            params = {}
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = urllib.parse.unquote_plus(value)
            return path, params
        else:
            return self.path, {}
    
    def do_GET(self):
        """Handle GET requests"""
        path, params = self._parse_query_params()
        
        # API endpoints
        if path == "/api/news":
            if "tickers" in params:
                tickers = params.get("tickers", "")
                days = int(params.get("days", 7))
                max_results = params.get("max_results")
                start_date = params.get("start_date")
                end_date = params.get("end_date")
                
                # Convert max_results to int if provided
                if max_results:
                    try:
                        max_results = int(max_results)
                    except ValueError:
                        max_results = None
                
                news = self.api.get_news(tickers, days, start_date, end_date, max_results)
                self._set_headers()
                self.wfile.write(json.dumps(news).encode())
            else:
                self.send_error(400, "Missing 'tickers' parameter")
        
        elif path == "/api/sentiment_summary":
            if "tickers" in params:
                tickers = params.get("tickers", "")
                days = int(params.get("days", 7))
                max_results = params.get("max_results")
                start_date = params.get("start_date")
                end_date = params.get("end_date")
                
                # Convert max_results to int if provided
                if max_results:
                    try:
                        max_results = int(max_results)
                    except ValueError:
                        max_results = None
                
                summary = self.api.get_sentiment_summary(tickers, days, start_date, end_date, max_results)
                self._set_headers()
                self.wfile.write(json.dumps(summary).encode())
            else:
                self.send_error(400, "Missing 'tickers' parameter")
        
        elif path == "/api/export":
            if "tickers" in params:
                tickers = params.get("tickers", "")
                days = int(params.get("days", 30))
                max_results = params.get("max_results")
                start_date = params.get("start_date")
                end_date = params.get("end_date")
                
                # Convert max_results to int if provided
                if max_results:
                    try:
                        max_results = int(max_results)
                    except ValueError:
                        max_results = None
                
                export_data = self.api.export_data(tickers, days, start_date, end_date, max_results)
                self._set_headers()
                self.wfile.write(json.dumps(export_data).encode())
            else:
                self.send_error(400, "Missing 'tickers' parameter")
        
        elif path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            # Get content length
            content_length = int(self.headers['Content-Length'])
            
            # Read request body
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            # Parse path
            path, _ = self._parse_query_params()
            
            # Handle analyze_text endpoint
            if path == "/api/analyze_text":
                text = body.get("text", "")
                if not text:
                    self.send_error(400, "Missing 'text' parameter")
                    return
                
                # Analyze sentiment
                sentiment_result = self.api.analyze_sentiment(text)
                
                # Return response
                self._set_headers()
                response = {
                    "status": "success",
                    "data": {
                        "text": text,
                        "sentiment": sentiment_result["sentiment"],
                        "score": sentiment_result["score"]
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self._set_headers()
        self.wfile.write("".encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s", self.address_string(), format % args)

def run_server():
    """Run the HTTP server"""
    handler = FinancialNewsHandler
    
    # Allow socket reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    # Log environment variables for debugging on Render.com
    logger.info(f"Starting server with PORT={PORT}")
    logger.info(f"Environment variables: PORT={os.environ.get('PORT')}")
    
    try:
        # Using empty string "" instead of "0.0.0.0" for better compatibility
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            logger.info(f"Financial News Sentiment Analysis API running at http://0.0.0.0:{PORT}")
            logger.info("Press Ctrl+C to stop the server")
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                logger.info("Server stopped by user")
            finally:
                httpd.server_close()
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"Port {PORT} is already in use. Please stop any running instance or change the port.")
        else:
            logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    run_server()