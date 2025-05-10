import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("financial_sentiment")

# Mapping of sentiment values
SENTIMENT_COLORS = {
    "positive": "green",
    "negative": "red",
    "neutral": "gray"
}

SENTIMENT_EMOJI = {
    "positive": "🟢",
    "negative": "🔴",
    "neutral": "⚪"
}

SENTIMENT_VALUES = {
    "positive": 1,
    "neutral": 0,
    "negative": -1
}

def prepare_sentiment_data(news_data):
    """
    Prepare sentiment data for visualization from raw news data.
    
    Args:
        news_data (list): List of news items with sentiment analysis
        
    Returns:
        pd.DataFrame: Processed DataFrame for visualization
    """
    if not news_data:
        logger.warning("No news data to prepare")
        return pd.DataFrame()
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(news_data)
        
        # Convert date strings to datetime
        df['published_date'] = pd.to_datetime(df['published_date'])
        df['date_only'] = df['published_date'].dt.date
        
        # Add numerical sentiment value
        df['sentiment_value'] = df['sentiment'].map(SENTIMENT_VALUES)
        
        return df
    except Exception as e:
        logger.error(f"Error preparing sentiment data: {e}")
        return pd.DataFrame()

def calculate_daily_sentiment(df):
    """
    Calculate daily sentiment metrics for each ticker.
    
    Args:
        df (pd.DataFrame): DataFrame with news and sentiment data
        
    Returns:
        pd.DataFrame: Daily sentiment metrics
    """
    if df.empty:
        return pd.DataFrame()
    
    try:
        # Group by date and ticker
        daily_counts = df.groupby(['date_only', 'ticker', 'sentiment']).size().reset_index(name='count')
        
        # Pivot to get sentiment counts in columns
        pivot_data = daily_counts.pivot_table(
            index=['date_only', 'ticker'],
            columns='sentiment',
            values='count',
            fill_value=0
        ).reset_index()
        
        # Ensure all sentiment columns exist
        for sentiment in ['positive', 'negative', 'neutral']:
            if sentiment not in pivot_data.columns:
                pivot_data[sentiment] = 0
        
        # Calculate total and sentiment score
        pivot_data['total'] = pivot_data['positive'] + pivot_data['negative'] + pivot_data['neutral']
        
        # Calculate sentiment score (range -1 to 1)
        # Use a safe division that handles zero totals
        pivot_data['sentiment_score'] = (pivot_data['positive'] - pivot_data['negative']) / pivot_data['total'].where(pivot_data['total'] > 0, 1)
        
        return pivot_data
    except Exception as e:
        logger.error(f"Error calculating daily sentiment: {e}")
        return pd.DataFrame()

def create_sentiment_distribution_chart(df):
    """
    Create a bar chart showing sentiment distribution by ticker.
    
    Args:
        df (pd.DataFrame): DataFrame with news and sentiment data
        
    Returns:
        plotly.graph_objects.Figure: Sentiment distribution chart
    """
    if df.empty:
        return None
    
    try:
        # Count sentiments by ticker
        sentiment_counts = df.groupby(['ticker', 'sentiment']).size().reset_index(name='count')
        
        # Create a grouped bar chart
        fig = px.bar(
            sentiment_counts,
            x='ticker',
            y='count',
            color='sentiment',
            barmode='group',
            color_discrete_map=SENTIMENT_COLORS,
            title='Sentiment Distribution by Ticker'
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating sentiment distribution chart: {e}")
        return None

def create_sentiment_trend_chart(df):
    """
    Create a line chart showing sentiment score trends by ticker.
    
    Args:
        df (pd.DataFrame): Processed daily sentiment data
        
    Returns:
        plotly.graph_objects.Figure: Sentiment trend chart
    """
    if df.empty:
        return None
    
    try:
        # Create line chart of sentiment scores
        fig = px.line(
            df,
            x='date_only',
            y='sentiment_score',
            color='ticker',
            title='Sentiment Score Trend by Ticker',
            labels={'sentiment_score': 'Sentiment Score (-1 to 1)', 'date_only': 'Date'}
        )
        
        # Add a zero line for reference
        fig.add_shape(
            type='line',
            x0=df['date_only'].min(),
            y0=0,
            x1=df['date_only'].max(),
            y1=0,
            line=dict(color='gray', dash='dash')
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating sentiment trend chart: {e}")
        return None

def format_export_data(news_data):
    """
    Format news data for export.
    
    Args:
        news_data (list): List of news items with sentiment analysis
        
    Returns:
        pd.DataFrame: Formatted DataFrame for export
    """
    if not news_data:
        return pd.DataFrame()
    
    try:
        df = pd.DataFrame(news_data)
        
        # Reorder columns for better readability in export
        columns = [
            'ticker', 
            'published_date', 
            'title', 
            'publisher',
            'sentiment', 
            'score', 
            'link'
        ]
        
        # Only include columns that exist in the dataframe
        export_columns = [col for col in columns if col in df.columns]
        
        return df[export_columns]
    except Exception as e:
        logger.error(f"Error formatting export data: {e}")
        return pd.DataFrame()
