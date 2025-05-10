import pandas as pd
import random
from datetime import datetime, timedelta

# Create demo news data
def create_demo_news_excel():
    # Common template news
    common_news = [
        {
            "title": "Markets reach record highs as tech stocks surge",
            "publisher": "Financial Times",
            "link": "https://example.com/markets-record-high",
            "published_date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": "GENERAL"
        },
        {
            "title": "Federal Reserve announces plans to maintain interest rates",
            "publisher": "Wall Street Journal", 
            "link": "https://example.com/fed-rates",
            "published_date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": "GENERAL"
        },
        {
            "title": "Global recession fears grow as manufacturing slows",
            "publisher": "Reuters",
            "link": "https://example.com/recession-fears",
            "published_date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": "GENERAL"
        },
        {
            "title": "Inflation data shows signs of moderating, analysts say",
            "publisher": "Bloomberg",
            "link": "https://example.com/inflation-data",
            "published_date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": "GENERAL"
        }
    ]
    
    # Ticker-specific news
    ticker_specific_news = []
    
    # AAPL News
    ticker = "AAPL"
    ticker_specific_news.extend([
        {
            "title": f"{ticker} reports record quarterly earnings, exceeding expectations",
            "publisher": "CNBC",
            "link": f"https://example.com/{ticker.lower()}-earnings",
            "published_date": (datetime.now() - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"New {ticker} product line launches to strong demand",
            "publisher": "TechCrunch",
            "link": f"https://example.com/{ticker.lower()}-product-launch",
            "published_date": (datetime.now() - timedelta(days=2, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"Analyst downgrades {ticker} citing supply chain concerns",
            "publisher": "Seeking Alpha",
            "link": f"https://example.com/{ticker.lower()}-downgrade",
            "published_date": (datetime.now() - timedelta(days=3, hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        }
    ])
    
    # MSFT News
    ticker = "MSFT"
    ticker_specific_news.extend([
        {
            "title": f"{ticker} cloud services grow 40% year-over-year",
            "publisher": "CNBC",
            "link": f"https://example.com/{ticker.lower()}-cloud-growth",
            "published_date": (datetime.now() - timedelta(days=1, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"{ticker} announces new AI partnerships with industry leaders",
            "publisher": "TechCrunch",
            "link": f"https://example.com/{ticker.lower()}-ai-partnerships",
            "published_date": (datetime.now() - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"Security vulnerabilities discovered in {ticker} products",
            "publisher": "ZDNet",
            "link": f"https://example.com/{ticker.lower()}-security-issues",
            "published_date": (datetime.now() - timedelta(days=3, hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        }
    ])
    
    # GOOGL News
    ticker = "GOOGL"
    ticker_specific_news.extend([
        {
            "title": f"{ticker} ad revenue exceeds projections in quarterly report",
            "publisher": "CNBC",
            "link": f"https://example.com/{ticker.lower()}-ad-revenue",
            "published_date": (datetime.now() - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"Regulatory challenges mount for {ticker} in European markets",
            "publisher": "Financial Times",
            "link": f"https://example.com/{ticker.lower()}-eu-regulation",
            "published_date": (datetime.now() - timedelta(days=2, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"{ticker} unveils new search algorithm with enhanced AI capabilities",
            "publisher": "The Verge",
            "link": f"https://example.com/{ticker.lower()}-search-ai",
            "published_date": (datetime.now() - timedelta(days=3, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        }
    ])
    
    # AMZN News
    ticker = "AMZN"
    ticker_specific_news.extend([
        {
            "title": f"{ticker} e-commerce sales surge during holiday season",
            "publisher": "Reuters",
            "link": f"https://example.com/{ticker.lower()}-holiday-sales",
            "published_date": (datetime.now() - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"{ticker} expands logistics network with new fulfillment centers",
            "publisher": "Business Insider",
            "link": f"https://example.com/{ticker.lower()}-logistics-expansion",
            "published_date": (datetime.now() - timedelta(days=2, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"Labor union pushes for worker rights at {ticker} warehouses",
            "publisher": "Washington Post",
            "link": f"https://example.com/{ticker.lower()}-labor-issues",
            "published_date": (datetime.now() - timedelta(days=3, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        }
    ])
    
    # TSLA News
    ticker = "TSLA"
    ticker_specific_news.extend([
        {
            "title": f"{ticker} production numbers hit new record in latest quarter",
            "publisher": "Electrek",
            "link": f"https://example.com/{ticker.lower()}-production-record",
            "published_date": (datetime.now() - timedelta(days=1, hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"{ticker} CEO announces new battery technology breakthrough",
            "publisher": "CleanTechnica",
            "link": f"https://example.com/{ticker.lower()}-battery-tech",
            "published_date": (datetime.now() - timedelta(days=2, hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        },
        {
            "title": f"Analysts divided on {ticker} stock valuation after recent volatility",
            "publisher": "Barron's",
            "link": f"https://example.com/{ticker.lower()}-valuation-debate",
            "published_date": (datetime.now() - timedelta(days=3, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": ticker
        }
    ])
    
    # Create more news for various time periods
    all_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    
    # News headlines templates for historical data
    positive_templates = [
        "{ticker} reports better-than-expected earnings for Q{quarter}",
        "{ticker} stock rises after analyst upgrade",
        "{ticker} announces new product launch scheduled for next quarter",
        "{ticker} expands into new markets with strategic acquisition",
        "{ticker} signs multi-year partnership with {partner}",
        "{ticker} increases dividend by 10%",
        "{ticker} beats revenue expectations for {quarter_name} quarter",
        "{ticker} shares climb after positive analyst coverage"
    ]
    
    negative_templates = [
        "{ticker} misses earnings expectations for Q{quarter}",
        "{ticker} stock slips after analyst downgrade",
        "{ticker} faces regulatory scrutiny in {region} market",
        "{ticker} delays product launch amid supply chain concerns",
        "{ticker} reports lower margins amid rising costs",
        "{ticker} cuts {number} jobs in restructuring effort",
        "{ticker} warns of slower growth in {quarter_name} quarter",
        "{ticker} shares drop on competitive pressure concerns"
    ]
    
    neutral_templates = [
        "{ticker} to report earnings next week",
        "{ticker} holds annual shareholder meeting",
        "{ticker} maintains guidance for fiscal year",
        "{ticker} CEO to speak at industry conference",
        "{ticker} releases sustainability report",
        "{ticker} announces management changes",
        "{ticker} updates investors on long-term strategy",
        "{ticker} files annual report with SEC"
    ]
    
    publishers = ["Wall Street Journal", "Bloomberg", "CNBC", "Reuters", "Financial Times", 
                 "MarketWatch", "Seeking Alpha", "The Motley Fool", "Barron's", "Forbes"]
    partners = ["Microsoft", "Amazon", "Google", "Apple", "Meta", "IBM", "Oracle", "Salesforce"]
    regions = ["European", "Asian", "Latin American", "North American", "African", "Australian"]
    quarters = [1, 2, 3, 4]
    quarter_names = ["first", "second", "third", "fourth"]
    numbers = [100, 200, 500, 1000, 2000, 5000]
    
    # Generate much more historical news data
    for ticker in all_tickers:
        # Create news items every few days going back 1 year
        for day in range(5, 365, 7):  # Every week going back a year
            # Choose random templates
            positive_template = random.choice(positive_templates)
            negative_template = random.choice(negative_templates)
            neutral_template = random.choice(neutral_templates)
            
            # Choose random details
            quarter = random.choice(quarters)
            quarter_name = random.choice(quarter_names)
            partner = random.choice(partners)
            region = random.choice(regions)
            number = random.choice(numbers)
            publisher = random.choice(publishers)
            
            # Randomly choose if we add positive, negative, or neutral news (or some combination)
            news_types = random.sample(["positive", "negative", "neutral"], random.randint(1, 3))
            
            # Add positive news
            if "positive" in news_types:
                ticker_specific_news.append({
                    "title": positive_template.format(
                        ticker=ticker, quarter=quarter, partner=partner, 
                        quarter_name=quarter_name, region=region, number=number
                    ),
                    "publisher": publisher,
                    "link": f"https://example.com/{ticker.lower()}-news-positive-{day}",
                    "published_date": (datetime.now() - timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S"),
                    "ticker": ticker
                })
            
            # Add negative news
            if "negative" in news_types:
                ticker_specific_news.append({
                    "title": negative_template.format(
                        ticker=ticker, quarter=quarter, partner=partner, 
                        quarter_name=quarter_name, region=region, number=number
                    ),
                    "publisher": publisher,
                    "link": f"https://example.com/{ticker.lower()}-news-negative-{day}",
                    "published_date": (datetime.now() - timedelta(days=day, hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
                    "ticker": ticker
                })
            
            # Add neutral news
            if "neutral" in news_types:
                ticker_specific_news.append({
                    "title": neutral_template.format(
                        ticker=ticker, quarter=quarter, partner=partner, 
                        quarter_name=quarter_name, region=region, number=number
                    ),
                    "publisher": publisher,
                    "link": f"https://example.com/{ticker.lower()}-news-neutral-{day}",
                    "published_date": (datetime.now() - timedelta(days=day, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
                    "ticker": ticker
                })
    
    # Combine all news
    all_news = common_news + ticker_specific_news
    
    # Convert to DataFrame
    df = pd.DataFrame(all_news)
    
    # Save to Excel - use local path since we're already in the backend/data directory
    df.to_excel('demo_financial_news.xlsx', index=False)
    print(f"Created demo news Excel file with {len(df)} entries")

if __name__ == "__main__":
    create_demo_news_excel()