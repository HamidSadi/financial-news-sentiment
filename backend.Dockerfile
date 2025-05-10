FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Copy requirements file and install dependencies
COPY project_requirements.txt .
RUN pip install --no-cache-dir -r project_requirements.txt

# Create a non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy the app files
COPY . .

# Set proper ownership
RUN chown -R appuser:appuser /app

# Run as non-root user
USER appuser

# Expose the port that the backend API will run on
EXPOSE ${PORT}

# Use an entrypoint script to handle secrets properly
RUN echo '#!/bin/sh\n\
# Load any API keys or sensitive data from environment\n\
echo "Starting Financial News Sentiment Analysis Backend API"\n\
exec python run_backend.py\n\
' > /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# Command to run the backend server
ENTRYPOINT ["/app/docker-entrypoint.sh"]