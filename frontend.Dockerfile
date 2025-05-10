FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Copy requirements file and install dependencies
COPY project_requirements.txt .
RUN pip install --no-cache-dir -r project_requirements.txt

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy the app files
COPY . .

# Create Streamlit config directory and add configuration
RUN mkdir -p /app/.streamlit
RUN echo '\
[server]\n\
port = ${PORT}\n\
headless = true\n\
address = "0.0.0.0"\n\
' > /app/.streamlit/config.toml

# Set proper ownership
RUN chown -R appuser:appuser /app

# Run as non-root user
USER appuser

# Expose the port that Streamlit will run on
EXPOSE ${PORT}

# Use an entrypoint script to handle secrets properly
RUN echo '#!/bin/sh\n\
# Load any necessary environment variables\n\
echo "Starting Financial News Sentiment Analysis Frontend"\n\
exec streamlit run run_frontend.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true\n\
' > /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Command to run the Streamlit app
ENTRYPOINT ["/app/docker-entrypoint.sh"]