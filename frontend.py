import streamlit as st
import requests
from datetime import datetime, timedelta
import json
import io

# Configure page
st.set_page_config(
    page_title="Financial News Sentiment Analysis",
    page_icon="📊",
    layout="wide"
)

# Constants
BACKEND_URL = "http://localhost:8000"  # Backend API URL
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
DEFAULT_DAYS = 7

# Cache API calls
@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_news(tickers, days):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/news",
            params={"tickers": ",".join(tickers), "days": days}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_sentiment_summary(tickers, days):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/sentiment_summary",
            params={"tickers": ",".join(tickers), "days": days}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sentiment summary: {e}")
        return {}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_export_data(tickers, days):
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/export",
            params={"tickers": ",".join(tickers), "days": days}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching export data: {e}")
        return []

# Helper function to check API connection
def check_api_health():
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        return response.status_code == 200
    except:
        return False

# Function to convert data to CSV for download
def convert_to_csv(data):
    # Simple CSV conversion without pandas
    if not data:
        return "".encode('utf-8')
    
    # Get headers
    headers = list(data[0].keys())
    
    # Create CSV content
    csv_content = ",".join(headers) + "\n"
    
    for item in data:
        row = [str(item.get(header, "")) for header in headers]
        csv_content += ",".join(row) + "\n"
    
    return csv_content.encode('utf-8')

# Main application
def main():
    # Title and description
    st.title("📊 Financial News Sentiment Analysis")
    st.markdown("""
    This application analyzes sentiment in financial news for selected stock tickers using the FinBERT model.
    """)
    
    # Sidebar for controls
    st.sidebar.title("Settings")
    
    # Check if backend is reachable
    backend_available = check_api_health()
    if not backend_available:
        st.warning("⚠️ Backend API is not available. This is a demo interface. The backend server needs to be started to get real data.")
    
    # Stock ticker selection (with default options)
    all_tickers = st.sidebar.text_input(
        "Enter stock tickers (comma separated)",
        value=",".join(DEFAULT_TICKERS)
    )
    
    selected_tickers = [ticker.strip().upper() for ticker in all_tickers.split(",") if ticker.strip()]
    
    if not selected_tickers:
        st.warning("Please enter at least one stock ticker.")
        return
    
    # Date range selection
    days_options = [1, 7, 14, 30, 90]
    selected_days = st.sidebar.selectbox(
        "Look back period (days)",
        options=days_options,
        index=days_options.index(DEFAULT_DAYS) if DEFAULT_DAYS in days_options else 1
    )
    
    # If backend is available, fetch real data
    news_data = []
    sentiment_summary = {}
    
    if backend_available:
        with st.spinner("Fetching and analyzing financial news..."):
            news_data = fetch_news(selected_tickers, selected_days)
            sentiment_summary = fetch_sentiment_summary(selected_tickers, selected_days)
    
    # Display status message
    if not backend_available:
        st.error("Backend server is not running. To see real data, you need to start the backend server.")
        st.markdown("""
        ### How to start the backend:
        
        The backend server needs the following dependencies:
        - FastAPI
        - Uvicorn
        - Pandas
        - YFinance
        - Transformers (with PyTorch)
        
        Once dependencies are installed, start the backend with:
        ```
        python backend.py
        ```
        """)
    
    # Display summary metrics
    st.header("Sentiment Overview")
    
    if not sentiment_summary:
        if backend_available:
            st.warning("No sentiment data available for the selected tickers.")
        else:
            st.info("This section will show sentiment summary when the backend is available.")
            # Create dummy demo layout
            cols = st.columns(len(selected_tickers))
            for i, ticker in enumerate(selected_tickers):
                with cols[i]:
                    st.subheader(f"{ticker}")
                    st.metric("Sentiment Score", "N/A")
                    st.write("Backend connection required")
    else:
        # Display real data
        cols = st.columns(len(selected_tickers))
        
        for i, ticker in enumerate(selected_tickers):
            if ticker in sentiment_summary:
                ticker_data = sentiment_summary[ticker]
                
                # Create a color indicator based on average sentiment score
                avg_score = ticker_data["avg_sentiment_score"]
                color = "green" if avg_score > 0.2 else "red" if avg_score < -0.2 else "gray"
                
                # Display ticker metrics
                with cols[i]:
                    st.subheader(f"{ticker}")
                    st.metric(
                        "Sentiment Score", 
                        f"{avg_score:.2f}",
                        delta=None
                    )
                    
                    total = ticker_data["total_news"]
                    if total > 0:
                        pos_pct = (ticker_data["positive"] / total) * 100
                        neg_pct = (ticker_data["negative"] / total) * 100
                        neu_pct = (ticker_data["neutral"] / total) * 100
                        
                        st.write(f"Total News: {total}")
                        st.write(f"🟢 Positive: {pos_pct:.1f}%")
                        st.write(f"🔴 Negative: {neg_pct:.1f}%") 
                        st.write(f"⚪ Neutral: {neu_pct:.1f}%")
                    else:
                        st.write("No news found")
    
    # Visualizations
    st.header("Sentiment Analysis Visualizations")
    
    if news_data and backend_available:
        st.info("Visualizations will be displayed here when the backend is connected and data is available.")
        # Visualization options would be shown when backend is connected
        viz_type = st.radio(
            "Select visualization",
            ["Sentiment Distribution", "Sentiment Over Time", "Sentiment Score Trend"],
            horizontal=True,
            disabled=not backend_available
        )
    else:
        if backend_available:
            st.info("No data available for visualization. Try selecting different tickers or expanding the time range.")
        else:
            st.info("When the backend is connected, this section will display interactive charts for sentiment analysis.")
            
            # Show static example of visualization
            st.markdown("""
            **Example Visualizations (when backend is connected):**
            - Sentiment Distribution by Ticker
            - Sentiment Trends Over Time
            - Sentiment Score Trends by Ticker
            """)
            
            # Create simple visualization example using ASCII art
            st.code("""
Sentiment Distribution Example:
            
AAPL    |  ██████ Positive (60%)  
        |  ██ Negative (20%)
        |  ██ Neutral (20%)
        
MSFT    |  ████ Positive (40%)
        |  ██ Negative (20%)
        |  ████ Neutral (40%)
            """)
    
    # News display with sentiment
    st.header("Recent Financial News with Sentiment Analysis")
    
    if not news_data:
        if backend_available:
            st.info("No news found for the selected tickers in the specified time range.")
        else:
            st.info("This section will display news with sentiment analysis when the backend is available.")
            # Create demo news items
            st.markdown("""
            **Example News Format:**
            
            **[Company XYZ Announces Record Earnings](#)**  
            *Financial Publisher - 2023-05-08 09:30:00*  
            Ticker: **DEMO** | Sentiment: **<span style='color:green'>🟢 Positive</span>** (Score: 0.85)
            """, unsafe_allow_html=True)
            
            st.divider()
            
            st.markdown("""
            **[Market Uncertainty Ahead of Federal Reserve Decision](#)**  
            *Market News - 2023-05-07 16:45:00*  
            Ticker: **DEMO** | Sentiment: **<span style='color:gray'>⚪ Neutral</span>** (Score: 0.60)
            """, unsafe_allow_html=True)
    else:
        # Filter options
        filter_col1, filter_col2 = st.columns([1, 1])
        
        with filter_col1:
            filter_sentiment = st.multiselect(
                "Filter by sentiment",
                options=["positive", "negative", "neutral"],
                default=["positive", "negative", "neutral"]
            )
        
        with filter_col2:
            filter_ticker = st.multiselect(
                "Filter by ticker",
                options=selected_tickers,
                default=selected_tickers
            )
        
        # Apply filters
        filtered_news = [
            news for news in news_data 
            if news["sentiment"] in filter_sentiment and news["ticker"] in filter_ticker
        ]
        
        # Display news
        for news in filtered_news:
            # Determine sentiment color
            if news["sentiment"] == "positive":
                sentiment_color = "green"
                sentiment_emoji = "🟢"
            elif news["sentiment"] == "negative":
                sentiment_color = "red"
                sentiment_emoji = "🔴"
            else:
                sentiment_color = "gray"
                sentiment_emoji = "⚪"
            
            # Create a card for each news item
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                **[{news['title']}]({news['link']})**  
                *{news['publisher']} - {news['published_date']}*  
                Ticker: **{news['ticker']}** | Sentiment: **<span style='color:{sentiment_color}'>{sentiment_emoji} {news['sentiment'].capitalize()}</span>** (Score: {news['score']:.2f})
                """, unsafe_allow_html=True)
            
            st.divider()
        
        if not filtered_news:
            st.info("No news matching the selected filters.")
    
    # Data export
    st.header("Export Data")
    
    export_days = st.slider("Data export time range (days)", min_value=1, max_value=90, value=30)
    
    if st.button("Export Sentiment Data (CSV)"):
        if backend_available:
            with st.spinner("Preparing export data..."):
                export_data = fetch_export_data(selected_tickers, export_days)
                
                if export_data:
                    csv_data = convert_to_csv(export_data)
                    
                    filename = f"financial_news_sentiment_{datetime.now().strftime('%Y%m%d')}.csv"
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv"
                    )
                else:
                    st.error("No data available to export.")
        else:
            st.error("Export functionality requires an active backend connection.")

if __name__ == "__main__":
    main()
