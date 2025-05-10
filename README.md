# 📊 Financial News Sentiment Analysis Application

A production-ready application that analyzes sentiment in financial news for selected stock tickers. The system uses a rule-based analysis approach with MLOps capabilities to classify news sentiment as positive, neutral, or negative, and presents the results in an interactive dashboard.

## 🧠 Key Features

### 🔄 Backend API

- **Multi-Source News Data**: Retrieves financial news from NewsAPI.org with Excel fallback
- **Advanced Sentiment Analysis**: Rule-based analysis with model versioning and metrics tracking
- **Comprehensive API Endpoints**:
  - `/api/news`: Get news with sentiment analysis
  - `/api/sentiment_summary`: Get summary statistics of sentiment by ticker
  - `/api/export`: Export sentiment data for download
  - `/api/analyze_text`: Custom text sentiment analysis
  - `/health`: Health check endpoint
- **Structured Logging**: JSON-formatted logs for better observability
- **Error Handling**: Graceful error recovery and fallback mechanisms

### 📈 Frontend Dashboard

- **Interactive Controls**: Select stock tickers and custom date ranges
- **Advanced Date Selection**: Choose preset periods or custom date ranges
- **Real-time Sentiment Overview**: Visual metrics for each ticker
- **Dynamic Visualizations**: Sentiment distribution and trends over time
- **Paginated News Display**: Browse headlines with sentiment indicators
- **Custom Text Analysis**: Analyze your own financial text
- **Data Export**: Download analysis results as CSV

## 🚀 Deployment Options

### Local Development

```bash
# Install dependencies
pip install -r project_requirements.txt

# Start the backend server
python run_backend.py

# Start the frontend dashboard in a separate terminal
streamlit run run_frontend.py
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Cloud Deployment (Render.com)

The project is fully configured for one-click deployment on Render.com using `render.yaml`. See [Render_Deployment_Guide.md](Render_Deployment_Guide.md) for detailed instructions.

### Kubernetes Deployment

The project includes Kubernetes configurations for enterprise deployment:

```bash
# Apply Kubernetes configurations
kubectl apply -f kubernetes/
```

## 🏗️ Project Structure

```
financial-news-sentiment/
├── backend/                 # Backend API code
│   ├── app/                 # Application modules
│   │   ├── api.py           # API endpoint definitions
│   │   ├── news_api.py      # News API integration
│   │   ├── news_scraper.py  # News source manager
│   │   ├── sentiment.py     # Sentiment analysis model
│   │   ├── excel_news.py    # Excel data source
│   │   └── utils.py         # Utility functions
│   └── data/                # Data storage
├── frontend/                # Frontend dashboard
│   └── app/                 # Streamlit application
│       └── dashboard.py     # Dashboard UI components
├── kubernetes/              # Kubernetes deployment files
│   ├── backend-deployment.yaml  # Backend K8s deployment
│   ├── frontend-deployment.yaml # Frontend K8s deployment
│   ├── configmap.yaml           # Configuration data
│   ├── secrets.yaml             # Secret management (template)
│   └── ingress.yaml             # Ingress configuration
├── tests/                   # Test suite
│   ├── test_sentiment.py    # Sentiment analysis tests
│   └── test_api.py          # API endpoint tests
├── .github/workflows/       # CI/CD configurations
│   └── ci-cd.yml            # GitHub Actions workflow
├── .dockerignore            # Docker ignore file
├── backend.Dockerfile       # Backend Docker configuration
├── frontend.Dockerfile      # Frontend Docker configuration
├── docker-compose.yml       # Docker Compose configuration
├── render.yaml              # Render.com deployment configuration
├── .env.template            # Environment variables template
├── run_backend.py           # Backend entry point
├── run_frontend.py          # Frontend entry point
├── project_requirements.txt # Python dependencies
├── utils.py                 # Shared utility functions
├── Project_Documentation.md # Detailed technical documentation
└── Render_Deployment_Guide.md # Deployment guide
```

## 📦 Dependencies

- **Backend Dependencies**:
  - FastAPI (API framework)
  - Uvicorn (ASGI server)
  - Requests (HTTP client)
  - Pandas (Data processing)
  - Python Standard Library

- **Frontend Dependencies**:
  - Streamlit (Interactive dashboard)
  - Plotly (Interactive visualizations)
  - Pandas (Data processing)
  - Requests (API client)

## 🔧 Configuration

The application supports multiple configuration methods:

1. **Environment Variables**: Configure via `.env` file or system environment variables
2. **Docker Environment**: Set in `docker-compose.yml` or Dockerfile
3. **Kubernetes ConfigMaps**: Set via `kubernetes/configmap.yaml`
4. **Render.com Environment**: Configure through the Render dashboard

Key configuration options include:

- `NEWS_API_KEY`: API key for NewsAPI.org integration
- `PORT`: Port for backend service (default: 8000)
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, etc.)
- `LOG_FORMAT`: Log format (text or JSON)
- `MODEL_VERSION`: Version of sentiment analysis model

## 🔒 Security Features

- **Container Security**: Non-root users in Docker containers
- **Secret Management**: Environment variables for sensitive data
- **Token Passing**: Secure token passing between services
- **Input Validation**: Request validation and sanitization
- **Error Handling**: Prevents sensitive information disclosure

## 📊 MLOps Capabilities

- **Model Versioning**: Track model versions and configurations
- **Performance Metrics**: Latency and error rate tracking
- **Model Registry**: Store and manage model artifacts
- **A/B Testing**: Framework for comparing model versions
- **Observability**: Advanced logging and metrics collection

## 📚 Documentation

- [Project_Documentation.md](Project_Documentation.md): Detailed technical documentation
- [Render_Deployment_Guide.md](Render_Deployment_Guide.md): Step-by-step Render.com deployment guide

## 🌐 Live Demo

Deploy your own instance on Render.com in minutes following our deployment guide.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.