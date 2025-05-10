import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import json
import io
import os

# Configure page
st.set_page_config(
    page_title="Financial News Sentiment Analysis",
    page_icon="📊",
    layout="wide"
)

# Constants
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")  # Backend API URL from environment or default

# Include minimal debugging in collapsible section
# This helps troubleshoot connection issues between frontend and backend
with st.sidebar.expander("Connection Diagnostics", expanded=False):
    st.write(f"BACKEND_URL: {BACKEND_URL}")
    
    # Test health endpoint directly
    try:
        health_url = f"{BACKEND_URL}/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            st.success("✓ Backend API connection successful")
        else:
            st.error(f"✗ Backend API returned unexpected status: {response.status_code}")
    except Exception as e:
        st.error(f"✗ Backend API connection failed: {str(e)}")
        st.info("This likely means the backend server is not running or not accessible at the configured URL.")
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
DEFAULT_DAYS = 7

# Cache API calls with proper keys to ensure cache invalidation when parameters change
@st.cache_data(ttl=300, max_entries=10, show_spinner=False)  # Cache for 5 minutes
def fetch_news(tickers, days):
    """
    Fetch news data from the backend API
    
    We explicitly include tickers and days in the key to ensure
    different values for these parameters result in new API calls
    """
    try:
        # Check if force refresh is set
        force_refresh = st.session_state.get('force_refresh', False)
        if force_refresh:
            st.session_state['force_refresh'] = False
            # Add a random parameter to force a cache miss
            cache_buster = f"&_={int(time.time())}"
        else:
            cache_buster = ""
        
        # Get date range information
        date_range = st.session_state.get('date_range', {'method': 'days', 'days': days})
        
        # Build parameters
        params = {
            "tickers": ",".join(tickers),
            "days": days,
            "max_results": 1000,  # Increased to get more results
            "cache_buster": cache_buster  # This ensures cache invalidation when needed
        }
        
        # Add date range parameters if using custom dates
        if date_range.get('method') == 'custom' and date_range.get('start_date') and date_range.get('end_date'):
            params['start_date'] = date_range['start_date']
            params['end_date'] = date_range['end_date']
            
        # Log for debugging
        st.session_state.setdefault('api_calls', []).append(f"Fetching news for {tickers} with {days} days")
        
        # Include the days parameter in the URL path to ensure cache invalidation
        response = requests.get(
            f"{BACKEND_URL}/api/news",
            params=params
        )
        response.raise_for_status()
        results = response.json()
        # Keep track of results count for debugging
        st.session_state['last_news_count'] = len(results)
        return results
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news: {e}")
        return []

@st.cache_data(ttl=300, max_entries=10, show_spinner=False)  # Cache for 5 minutes
def fetch_sentiment_summary(tickers, days):
    """
    Fetch sentiment summary data from the backend API
    
    Cache is keyed by tickers and days to ensure proper cache invalidation
    """
    try:
        # Check if force refresh is set
        force_refresh = st.session_state.get('force_refresh', False)
        if force_refresh:
            # Add a random parameter to force a cache miss
            cache_buster = f"&_={int(time.time())}"
        else:
            cache_buster = ""
        
        # Get date range information
        date_range = st.session_state.get('date_range', {'method': 'days', 'days': days})
        
        # Build parameters
        params = {
            "tickers": ",".join(tickers),
            "days": days,
            "max_results": 1000,  # Increased to get more results
            "cache_buster": cache_buster  # This ensures cache invalidation when needed
        }
        
        # Add date range parameters if using custom dates
        if date_range.get('method') == 'custom' and date_range.get('start_date') and date_range.get('end_date'):
            params['start_date'] = date_range['start_date']
            params['end_date'] = date_range['end_date']
            
        # Log for debugging
        st.session_state.setdefault('api_calls', []).append(f"Fetching sentiment summary for {tickers} with {days} days")
        
        response = requests.get(
            f"{BACKEND_URL}/api/sentiment_summary",
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching sentiment summary: {e}")
        return {}

@st.cache_data(ttl=300, max_entries=10, show_spinner=False)  # Cache for 5 minutes
def fetch_export_data(tickers, days):
    """
    Fetch data for export from the backend API
    
    We use a shorter TTL for export data to ensure freshness
    """
    try:
        # Check if force refresh is set
        force_refresh = st.session_state.get('force_refresh', False)
        if force_refresh:
            # Add a random parameter to force a cache miss
            cache_buster = f"&_={int(time.time())}"
        else:
            cache_buster = ""
            
        # Get date range information
        date_range = st.session_state.get('date_range', {'method': 'days', 'days': days})
        
        # Build parameters
        params = {
            "tickers": ",".join(tickers),
            "days": days,
            "max_results": 5000,  # Significantly increased to get more results for export
            "cache_buster": cache_buster  # This ensures cache invalidation when needed
        }
        
        # Add date range parameters if using custom dates
        if date_range.get('method') == 'custom' and date_range.get('start_date') and date_range.get('end_date'):
            params['start_date'] = date_range['start_date']
            params['end_date'] = date_range['end_date']
        
        # Log for debugging
        st.session_state.setdefault('api_calls', []).append(f"Fetching export data for {tickers} with {days} days")
        
        response = requests.get(
            f"{BACKEND_URL}/api/export",
            params=params
        )
        response.raise_for_status()
        data = response.json()
        st.session_state['last_export_count'] = len(data)
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching export data: {e}")
        return []
        
def analyze_custom_text(text):
    """Send text to backend for sentiment analysis"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/analyze_text",
            json={"text": text},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error analyzing text: {str(e)}")
        return None

# Helper function to check API connection
def check_api_health():
    """Check if the backend API is available"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        return response.status_code == 200
    except:
        return False

# Function to convert data to CSV for download
def convert_to_csv(data):
    """Convert data to CSV format for download"""
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

def display_sentiment_visualizations(news_data, backend_available):
    """Display sentiment visualizations section"""
    st.header("Sentiment Analysis Visualizations")
    
    if news_data and backend_available:
        # Create a simple sentiment count visualization
        st.subheader("Sentiment Distribution")
        
        # Count sentiments
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for item in news_data:
            sentiments[item["sentiment"]] += 1
        
        # Create a simple horizontal bar chart with text
        total = sum(sentiments.values())
        if total > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                pos_pct = (sentiments["positive"] / total) * 100
                st.markdown(f"🟢 **Positive**: {sentiments['positive']} ({pos_pct:.1f}%)")
                st.progress(sentiments["positive"] / total)
                
            with col2:
                neg_pct = (sentiments["negative"] / total) * 100
                st.markdown(f"🔴 **Negative**: {sentiments['negative']} ({neg_pct:.1f}%)")
                st.progress(sentiments["negative"] / total)
                
            with col3:
                neu_pct = (sentiments["neutral"] / total) * 100
                st.markdown(f"⚪ **Neutral**: {sentiments['neutral']} ({neu_pct:.1f}%)")
                st.progress(sentiments["neutral"] / total)
        
        # Display sentiment by ticker
        st.subheader("Sentiment by Ticker")
        
        # Group by ticker
        ticker_sentiments = {}
        for item in news_data:
            ticker = item["ticker"]
            sentiment = item["sentiment"]
            
            if ticker not in ticker_sentiments:
                ticker_sentiments[ticker] = {"positive": 0, "negative": 0, "neutral": 0, "total": 0}
            
            ticker_sentiments[ticker][sentiment] += 1
            ticker_sentiments[ticker]["total"] += 1
        
        # Display as a table
        ticker_cols = st.columns(len(ticker_sentiments))
        for i, (ticker, counts) in enumerate(ticker_sentiments.items()):
            with ticker_cols[i % len(ticker_cols)]:
                st.write(f"**{ticker}**")
                if counts["total"] > 0:
                    pos_pct = (counts["positive"] / counts["total"]) * 100
                    neg_pct = (counts["negative"] / counts["total"]) * 100
                    neu_pct = (counts["neutral"] / counts["total"]) * 100
                    
                    st.write(f"🟢 Positive: {pos_pct:.1f}%")
                    st.write(f"🔴 Negative: {neg_pct:.1f}%")
                    st.write(f"⚪ Neutral: {neu_pct:.1f}%")
                    st.write(f"Total News: {counts['total']}")
                else:
                    st.write("No news found")
                st.write("---")
                
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

def main():
    """Main function to run the Streamlit dashboard"""
    # Initialize session state for pagination if not already set
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
        
    # Title and description
    st.title("📊 Financial News Sentiment Analysis")
    st.markdown("""
    This application analyzes sentiment in financial news for selected stock tickers using 
    a specialized financial sentiment analysis model.
    """)

    with st.sidebar:
        st.title("Settings")
        
        # Check if backend is reachable
        backend_available = check_api_health()
        if not backend_available:
            st.warning("⚠️ Backend API is not available. This is a demo interface.")
        else:
            st.success("✅ Connected to backend API")
        
        # Stock ticker selection (with default options)
        all_tickers = st.text_input(
            "Enter stock tickers (comma separated)",
            value=",".join(DEFAULT_TICKERS)
        )
        
        selected_tickers = [ticker.strip().upper() for ticker in all_tickers.split(",") if ticker.strip()]
        
        if not selected_tickers:
            st.warning("Please enter at least one stock ticker.")
            st.stop()
        
        # Date range selection - offer both preset days and custom date range
        date_selection_method = st.radio(
            "Select time period by:",
            options=["Preset days", "Custom date range"],
            horizontal=True
        )
        
        if date_selection_method == "Preset days":
            days_options = [1, 7, 14, 30, 90, 180, 365]
            selected_days = st.selectbox(
                "Look back period (days)",
                options=days_options,
                index=days_options.index(DEFAULT_DAYS) if DEFAULT_DAYS in days_options else 1
            )
            # Calculate start date from days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=selected_days)
            # Store for API call
            st.session_state['date_range'] = {
                'method': 'days',
                'days': selected_days,
                'start_date': None,
                'end_date': None
            }
        else:
            # Custom date range picker - default to last 30 days
            today = datetime.now().date()
            default_start = today - timedelta(days=30)
            
            start_date = st.date_input(
                "Start date",
                value=default_start,
                max_value=today
            )
            
            end_date = st.date_input(
                "End date",
                value=today,
                min_value=start_date,
                max_value=today
            )
            
            # Calculate days between dates for API compatibility
            delta = end_date - start_date
            selected_days = delta.days + 1  # Include both start and end dates
            
            # Store for API call
            st.session_state['date_range'] = {
                'method': 'custom',
                'days': selected_days,
                'start_date': start_date.strftime("%Y-%m-%d"),
                'end_date': end_date.strftime("%Y-%m-%d")
            }
            
        # Display selected date range in human-readable format
        st.write(f"Analyzing news from {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')} ({selected_days} days)")
    
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
        
        The backend server can be started with:
        ```
        python run_backend.py
        ```

        This will start a simple HTTP server on port 8000 that provides demo financial news data with sentiment analysis.
        """)
    
    # Display debug info
    with st.expander("Debug Information", expanded=False):
        st.write(f"**Selected Days:** {selected_days}")
        st.write(f"**Selected Tickers:** {selected_tickers}")
        
        # Display stats
        debug_cols = st.columns(3)
        with debug_cols[0]:
            if 'last_news_count' in st.session_state:
                st.write(f"**News Count:** {st.session_state['last_news_count']}")
        with debug_cols[1]:
            if 'last_export_count' in st.session_state:
                st.write(f"**Export Data Count:** {st.session_state['last_export_count']}")
                
        # Add request history
        st.write("**API Call History:**")
        if 'api_calls' in st.session_state:
            for call in st.session_state['api_calls'][-5:]:  # Show last 5 calls
                st.write(f"- {call}")
        
        # Add clear cache button for troubleshooting        
        if st.button("Clear Cache"):
            # Reset session state data
            st.session_state['api_calls'] = []
            # Clear all st.cache_data entries
            try:
                # This will only work in newer Streamlit versions
                st.cache_data.clear()
            except:
                # Fallback - force recreation of cached data
                st.session_state['force_refresh'] = True
            st.success("Cache cleared! Refresh page to fetch new data.")
    
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
    
    # Display sentiment visualizations
    display_sentiment_visualizations(news_data, backend_available)
    
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
        filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])
        
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
            
        with filter_col3:
            # Add a sort option
            sort_option = st.selectbox(
                "Sort by",
                options=["Newest first", "Oldest first", "Sentiment: Positive first", "Sentiment: Negative first"],
                index=0
            )
        
        # Apply filters
        filtered_news = [
            news for news in news_data 
            if news["sentiment"] in filter_sentiment and news["ticker"] in filter_ticker
        ]
        
        # Sort the news based on the selected option
        if sort_option == "Newest first":
            filtered_news.sort(key=lambda x: x.get("published_date", ""), reverse=True)
        elif sort_option == "Oldest first":
            filtered_news.sort(key=lambda x: x.get("published_date", ""))
        elif sort_option == "Sentiment: Positive first":
            filtered_news.sort(key=lambda x: (x["sentiment"] != "positive", x["sentiment"] != "neutral", x.get("published_date", "")))
        elif sort_option == "Sentiment: Negative first":
            filtered_news.sort(key=lambda x: (x["sentiment"] != "negative", x["sentiment"] != "neutral", x.get("published_date", "")))
        
        # Add pagination
        if filtered_news:
            total_news = len(filtered_news)
            items_per_page = 10  # Show 10 news items per page
            
            # Calculate total pages
            total_pages = (total_news + items_per_page - 1) // items_per_page  # Ceiling division
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"Showing {total_news} news items")
                
            with col2:
                # Only show pagination if we have more than one page
                if total_pages > 1:
                    # Use session state to remember the page number
                    page_number = st.selectbox(
                        "Page", 
                        options=range(1, total_pages + 1), 
                        index=min(st.session_state.page_number - 1, total_pages - 1)
                    )
                    # Update session state when page changes via dropdown
                    if page_number != st.session_state.page_number:
                        st.session_state.page_number = page_number
                else:
                    page_number = 1
                    st.session_state.page_number = 1
            
            # Calculate start and end indices for the current page
            start_idx = (page_number - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, total_news)
            
            # Get news items for the current page
            page_news = filtered_news[start_idx:end_idx]
            
            # Display each news item with sentiment for the current page
            for news in page_news:
                # Set color based on sentiment
                if news["sentiment"] == "positive":
                    sentiment_color = "green"
                    sentiment_emoji = "🟢"
                elif news["sentiment"] == "negative":
                    sentiment_color = "red"
                    sentiment_emoji = "🔴"
                else:
                    sentiment_color = "gray"
                    sentiment_emoji = "⚪"
                
                # Create a more compact card for each news item
                st.markdown(f"""
                **[{news['title']}]({news['link']})**  
                *{news['publisher']} - {news['published_date']}* | Ticker: **{news['ticker']}** | Sentiment: **<span style='color:{sentiment_color}'>{sentiment_emoji} {news['sentiment'].capitalize()}</span>** (Score: {news['score']:.2f})
                """, unsafe_allow_html=True)
                
                st.divider()
            
            # Show pagination navigation at the bottom too if many pages
            if total_pages > 3:
                # Create pagination buttons at the bottom
                pagination_cols = st.columns([1, 1, 1, 1, 1])
                
                if page_number > 1:
                    with pagination_cols[0]:
                        if st.button("⏮️ First"):
                            st.session_state.page_number = 1
                            st.rerun()
                    with pagination_cols[1]:
                        if st.button("◀️ Previous"):
                            st.session_state.page_number = page_number - 1
                            st.rerun()
                
                with pagination_cols[2]:
                    st.write(f"Page {page_number} of {total_pages}")
                
                if page_number < total_pages:
                    with pagination_cols[3]:
                        if st.button("Next ▶️"):
                            st.session_state.page_number = page_number + 1
                            st.rerun()
                    with pagination_cols[4]:
                        if st.button("Last ⏭️"):
                            st.session_state.page_number = total_pages
                            st.rerun()
        
        else:
            st.info("No news matching the selected filters.")
    
    # Custom Text Analysis Section
    st.header("Custom Text Analysis")
    st.markdown("""
    Analyze the sentiment of any financial news or text. Paste your text below and click 'Analyze' 
    to see the sentiment analysis results.
    """)
    
    # Create a text area for entering custom text
    custom_text = st.text_area(
        "Enter financial news text to analyze:",
        height=150,
        placeholder="Paste any financial news article or text here to analyze its sentiment..."
    )
    
    # Create a button to trigger analysis
    if st.button("Analyze Text Sentiment"):
        if not custom_text:
            st.warning("Please enter some text to analyze.")
        elif not backend_available:
            st.error("Text analysis requires an active backend connection.")
        else:
            with st.spinner("Analyzing sentiment..."):
                # Call the API to analyze the text
                result = analyze_custom_text(custom_text)
                
                if result and "data" in result:
                    data = result["data"]
                    
                    # Define sentiment color and emoji based on the result
                    sentiment = data["sentiment"]
                    score = data["score"]
                    
                    if sentiment == "positive":
                        color = "green"
                        emoji = "🟢"
                    elif sentiment == "negative":
                        color = "red"
                        emoji = "🔴"
                    else:
                        color = "gray"
                        emoji = "⚪"
                    
                    # Display the results
                    st.subheader("Analysis Results")
                    
                    st.markdown(f"""
                    **Sentiment: <span style='color:{color}'>{emoji} {sentiment.capitalize()}</span>**
                    
                    **Score: {score:.2f}** (on a scale from -1.0 to 1.0)
                    
                    *Note: This analysis uses a specialized financial sentiment model optimized for financial news and reports.*
                    """, unsafe_allow_html=True)
                    
                    # Display a summary of what the result means
                    if sentiment == "positive":
                        st.success("This text expresses a positive sentiment, which may indicate optimistic news about the company or market.")
                    elif sentiment == "negative":
                        st.error("This text expresses a negative sentiment, which may indicate concerning news about the company or market.")
                    else:
                        st.info("This text expresses a neutral sentiment, which may indicate factual reporting without strong positive or negative bias.")
                else:
                    st.error("Failed to analyze the text. Please try again or check the backend connection.")
    
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