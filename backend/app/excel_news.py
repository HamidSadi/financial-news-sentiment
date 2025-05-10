"""
Module for reading demo financial news from Excel file.
"""
import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger("financial_sentiment")

def get_news_from_excel(ticker: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    Get financial news from Excel file for a given ticker.
    
    Args:
        ticker: Stock ticker symbol
        days: Number of days to look back
        
    Returns:
        List of news items from Excel file
    """
    logger.info(f"Reading news from Excel for {ticker} for past {days} days")
    
    try:
        # Path to Excel file (relative to script location)
        excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 'data', 'demo_financial_news.xlsx')
        
        # Check if file exists
        if not os.path.exists(excel_path):
            logger.error(f"Excel file not found at {excel_path}")
            return []
        
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # For longer time periods (over 30 days), we want to ensure we have enough data
        # since NewsAPI is limited to 30 days in the free plan
        if days > 30:
            logger.info(f"Looking for {days} days of data from Excel for {ticker}")
        
        # Filter by ticker and date
        filtered_df = df[
            ((df['ticker'] == ticker) | (df['ticker'] == 'GENERAL')) &
            (pd.to_datetime(df['published_date']) >= cutoff_date)
        ]
        
        # Convert to list of dictionaries
        news_items = filtered_df.to_dict('records')
        
        logger.info(f"Found {len(news_items)} news items for {ticker} from Excel")
        return news_items
        
    except Exception as e:
        logger.error(f"Error reading news from Excel for {ticker}: {str(e)}")
        return []