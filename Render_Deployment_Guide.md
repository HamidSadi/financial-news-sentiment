# Financial News Sentiment Analysis - Render.com Deployment Guide

This comprehensive guide will walk you through deploying your Financial News Sentiment Analysis application on Render.com with step-by-step instructions. The guide covers both basic deployment and advanced configuration options.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Render.com Account Setup](#rendercom-account-setup)
4. [Blueprint Deployment Process](#blueprint-deployment-process)
5. [Configuration and Environment Variables](#configuration-and-environment-variables)
6. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
7. [Advanced Configuration](#advanced-configuration)
8. [Performance Optimization](#performance-optimization)
9. [Custom Domain Setup](#custom-domain-setup)
10. [FAQ and Troubleshooting](#faq-and-troubleshooting)

## Prerequisites

Before starting the deployment process, ensure you have:

1. Your complete codebase with all the files in this repository
2. The `render.yaml` file in the root directory
3. A GitHub account (for hosting your code)
4. An email address for Render.com registration
5. (Optional) NewsAPI.org API key for live news data access

## GitHub Repository Setup

### Step 1: Create a New GitHub Repository

1. Log in to your GitHub account at [github.com](https://github.com)
2. Click the "+" icon in the top-right corner and select "New repository"
3. Enter a name for your repository (e.g., "financial-news-sentiment")
4. Add a description: "Financial News Sentiment Analysis Application"
5. Choose "Public" visibility (Render.com needs to access it)
6. Click "Create repository"

### Step 2: Upload Your Project Files

#### Option A: Using GitHub Web Interface

1. In your new repository, click "uploading an existing file"
2. Drag and drop all project files or use the file selector
3. Enter a commit message like "Initial project upload"
4. Click "Commit changes"

#### Option B: Using Git Command Line

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/financial-news-sentiment.git

# Copy all project files to the repository folder

# Add all files
git add .

# Commit the files
git commit -m "Initial project upload"

# Push to GitHub
git push origin main
```

### Step 3: Verify Repository Structure

Ensure your repository contains all necessary files:

- `run_backend.py` and `run_frontend.py`
- `backend/` and `frontend/` directories
- `render.yaml` (critical for deployment)
- `project_requirements.txt`
- All other project files and directories

## Render.com Account Setup

### Step 1: Create a Render.com Account

1. Go to [Render.com](https://render.com)
2. Click "Sign Up" in the top-right corner
3. Select "Sign up with GitHub" for easier integration
4. Authorize Render to access your GitHub account
5. Complete any additional registration steps

### Step 2: Connect Your GitHub Repository

1. Once logged in to Render, you'll see your Dashboard
2. Navigate to the "Blueprints" section (or click "New" and select "Blueprint")
3. If prompted, connect your GitHub account if not already connected
4. Provide necessary permissions for Render to access your repositories

## Blueprint Deployment Process

### Step 1: Create a New Blueprint Instance

1. From your Render Dashboard, click "New" and select "Blueprint"
2. Find your "financial-news-sentiment" repository in the list
3. If you don't see it, ensure your repository is public and contains a `render.yaml` file
4. Select the repository to proceed

### Step 2: Configure and Deploy

1. Render will automatically detect the services defined in your `render.yaml` file
2. You'll see two services:
   - `financial-news-backend`: The Python API server
   - `financial-news-frontend`: The Streamlit dashboard
3. No changes are needed to the default configuration for basic deployment
4. Click "Apply Blueprint" to start the deployment process

### Step 3: Monitor the Deployment

1. Render will start building both services simultaneously
2. The deployment process typically takes 5-10 minutes
3. You can monitor the progress in real-time:
   - First, packages are installed using `pip install -r project_requirements.txt`
   - Then, the services are started using the commands in `render.yaml`
4. Wait until both services show "Deploy successful" status

## Configuration and Environment Variables

### Step 1: Access the Environment Configuration

1. Once deployment is started, click on the `financial-news-backend` service
2. Navigate to the "Environment" tab
3. Here you can configure environment variables for your backend service

### Step 2: Configure API Key (If Using Live News Data)

1. Click "Add Environment Variable"
2. Add the key: `NEWS_API_KEY`
3. Add your NewsAPI.org API key as the value
4. Choose "Yes" for "Secret" to encrypt the key
5. Click "Save Changes"
6. This will trigger a redeployment of the backend service

### Step 3: Additional Configuration Options

You can configure various aspects of your application:

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Logging verbosity (INFO, DEBUG, etc.) | INFO |
| `LOG_FORMAT` | Logging format (text or json) | text |
| `MODEL_VERSION` | Sentiment model version | rule-based-v1 |

## Monitoring and Troubleshooting

### Step 1: Access Service Logs

1. From your Render Dashboard, click on either service
2. Navigate to the "Logs" tab
3. Here you can see real-time logs from your application
4. Use the logs to identify and troubleshoot any issues

### Step 2: Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| Backend fails to start | Missing dependency | Check project_requirements.txt is complete |
| Frontend can't connect to backend | Backend URL issue | Verify BACKEND_URL environment variable |
| No news data | API key issue | Ensure NEWS_API_KEY is correctly set |
| Deployment times out | Memory limits | Optimize code or upgrade to a plan with more resources |

## Advanced Configuration

### Customizing the Render.yaml File

The `render.yaml` file controls how your application is deployed. Here's a breakdown of key configuration options:

```yaml
services:
  - type: web  # Service type (web, worker, cron)
    name: financial-news-backend  # Service name
    env: python  # Runtime environment
    buildCommand: pip install -r project_requirements.txt  # Build command
    startCommand: python run_backend.py  # Start command
    envVars:  # Environment variables
      - key: PORT
        value: 8000
```

You can customize this file to:
- Add additional services
- Modify build or start commands
- Configure auto-scaling or custom domains
- Set up health checks and timeouts

## Performance Optimization

### Step 1: Upgrade Service Plans

For better performance, consider upgrading from the free tier:

1. Go to your service in the Render Dashboard
2. Click on "Settings"
3. Under "Instance Type", select a higher tier
4. Click "Save Changes"

Benefits include:
- No service sleeping (constant availability)
- More CPU and memory resources
- Faster cold starts and response times

### Step 2: Enable Auto-Scaling (Paid Plans Only)

For production environments with varying loads:

1. Go to your service in the Render Dashboard
2. Click on "Settings"
3. Navigate to "Auto-Scaling"
4. Configure min and max instances

## Custom Domain Setup

### Step 1: Add Your Domain

1. Go to your frontend service in the Render Dashboard
2. Click on "Settings"
3. Navigate to "Custom Domain"
4. Click "Add Custom Domain"
5. Enter your domain name and click "Save"

### Step 2: Configure DNS

1. Render will provide you with CNAME or A records
2. Go to your domain registrar's DNS settings
3. Add the CNAME or A records as instructed
4. Wait for DNS propagation (can take up to 48 hours)

## FAQ and Troubleshooting

### How long will deployment take?
Initial deployment typically takes 5-10 minutes. Subsequent updates are faster (2-5 minutes).

### Is my API key secure?
Yes, when you mark environment variables as "Secret", Render encrypts them and they are not visible in logs.

### Will my application always be available?
On the free tier, services "sleep" after 15 minutes of inactivity and take 30-60 seconds to "wake up" when accessed again. Paid tiers remain active.

### How do I update my application?
Push changes to your GitHub repository. Render automatically deploys updates when it detects changes to your code.

### What if I need to roll back to a previous version?
In the Render Dashboard, go to your service, click "Manual Deploy", and select a previous deployment.

### How do I monitor application performance?
Render provides basic metrics for CPU, memory, and response times in the "Metrics" tab of each service.

---

## Technical Reference

### Service Architecture

The application is deployed as two separate services:

1. **Backend Service (financial-news-backend)**:
   - Python API service for fetching and analyzing news
   - Runs on port 8000
   - Handles data processing and sentiment analysis
   - Connects to external news sources

2. **Frontend Service (financial-news-frontend)**:
   - Streamlit web dashboard
   - Runs on port 5000 (mapped to port 10000 by Render)
   - Provides the user interface
   - Connects to the backend service via environment variables

### Environment Variable Connections

Render automatically sets up the connection between services using environment variables:

```yaml
envVars:
  - key: BACKEND_URL
    fromService:
      name: financial-news-backend
      type: web
      property: url
```

This provides the frontend with the correct URL to reach the backend service, regardless of deployment changes.