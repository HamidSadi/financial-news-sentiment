import logging
import os
import json
import time
import random  # Only used for demo when transformer model isn't available
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

logger = logging.getLogger("financial_sentiment")

# Model versioning and tracking constants
MODEL_VERSION = os.environ.get("MODEL_VERSION", "rule-based-v1")
MODEL_REGISTRY = os.environ.get("MODEL_REGISTRY", ".model_registry")

class SentimentModel:
    """
    Sentiment analysis model with MLOps capabilities.
    
    This class provides a framework for model versioning, metrics tracking,
    and easy transition to more sophisticated models like FinBERT.
    """
    
    def __init__(self):
        """Initialize the sentiment model with configuration from environment"""
        self.model_version = MODEL_VERSION
        self.model_path = os.environ.get("MODEL_PATH", "")
        self.batch_size = int(os.environ.get("MODEL_BATCH_SIZE", "16"))
        self.max_length = int(os.environ.get("MODEL_MAX_LENGTH", "512"))
        self.registry_path = MODEL_REGISTRY
        
        # Ensure model registry directory exists
        os.makedirs(self.registry_path, exist_ok=True)
        
        # Load model configuration
        self.config = self._load_config()
        
        # Initialize metrics tracking
        self.request_count = 0
        self.error_count = 0
        self.latency_ms_sum = 0
        self.last_metrics_save = time.time()
        
        logger.info(f"Initialized sentiment model: {self.model_version}")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load model configuration from file or environment"""
        # Default configuration for rule-based model
        default_config = {
            "model_type": "rule-based",
            "positive_keywords": [
                'surge', 'record', 'exceeding', 'strong', 'grow', 'growth', 'breakthrough', 
                'positive', 'gain', 'gains', 'profit', 'profitable', 'success', 'successful',
                'innovation', 'innovative', 'opportunity', 'opportunities', 'upbeat', 'optimistic'
            ],
            "negative_keywords": [
                'downgrade', 'concerns', 'vulnerabilities', 'issues', 'challenges', 'mount',
                'labor', 'divided', 'volatility', 'fears', 'recession', 'loss', 'losses',
                'debt', 'decline', 'fell', 'fall', 'drop', 'bearish', 'pessimistic', 'bankruptcy',
                'lawsuit', 'investigation', 'regulatory', 'scrutiny', 'inflation', 'shortage'
            ],
            "version": self.model_version,
            "created_at": datetime.now().isoformat()
        }
        
        # If model path is specified and exists, load from file
        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading model config from {self.model_path}: {e}")
                return default_config
        
        # Otherwise return default config
        return default_config
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        This method includes tracking for latency and error metrics.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with sentiment label and confidence score
        """
        start_time = time.time()
        self.request_count += 1
        
        # Truncate long texts to max_length
        if len(text) > self.max_length:
            text = text[:self.max_length]
        
        try:
            # In the future, this would be replaced with a call to a real model
            result = self._analyze_rule_based(text)
            
            # Track latency
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            self.latency_ms_sum += latency_ms
            
            # Periodically save metrics
            if time.time() - self.last_metrics_save > 60:  # Save every minute
                self._save_metrics()
            
            # Add model metadata to result
            result.update({
                "model_version": self.model_version,
                "latency_ms": latency_ms
            })
            
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
            
            # Return neutral sentiment as fallback
            return {
                "sentiment": "neutral", 
                "score": 0.5,
                "model_version": self.model_version,
                "error": str(e)
            }
    
    def _analyze_rule_based(self, text: str) -> Dict[str, Any]:
        """
        Rule-based sentiment analysis.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with sentiment label and confidence score
        """
        logger.info(f"Analyzing sentiment for: {text[:50]}...")
        
        # Get keywords from config
        positive_keywords = self.config.get("positive_keywords", [])
        negative_keywords = self.config.get("negative_keywords", [])
        
        # Count keyword occurrences
        positive_count = sum(1 for word in positive_keywords if word.lower() in text.lower())
        negative_count = sum(1 for word in negative_keywords if word.lower() in text.lower())
        
        # Determine sentiment based on keyword counts
        if positive_count > negative_count:
            sentiment = "positive"
            # Calculate score based on the difference between positive and negative counts
            base_score = min(0.7 + 0.1 * (positive_count - negative_count), 0.95)
            # Add some randomness for variety, but less than before
            score = base_score + (random.random() * 0.05)
        elif negative_count > positive_count:
            sentiment = "negative"
            base_score = min(0.7 + 0.1 * (negative_count - positive_count), 0.95)
            score = base_score + (random.random() * 0.05)
        else:
            sentiment = "neutral"
            score = 0.5 + (random.random() * 0.1)
        
        return {
            "sentiment": sentiment, 
            "score": score,
            "details": {
                "positive_count": positive_count,
                "negative_count": negative_count
            }
        }
    
    def _save_metrics(self) -> None:
        """Save model performance metrics to file"""
        metrics_file = os.path.join(self.registry_path, f"{self.model_version}_metrics.json")
        
        # Calculate aggregate metrics
        avg_latency = self.latency_ms_sum / max(1, self.request_count)
        error_rate = self.error_count / max(1, self.request_count)
        
        metrics = {
            "model_version": self.model_version,
            "timestamp": datetime.now().isoformat(),
            "request_count": self.request_count,
            "error_count": self.error_count,
            "avg_latency_ms": avg_latency,
            "error_rate": error_rate
        }
        
        try:
            # Load existing metrics if file exists
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    existing_metrics = json.load(f)
                
                # Update with new data points
                if isinstance(existing_metrics, dict):
                    # Convert to list if it's a single entry
                    existing_metrics = [existing_metrics]
                
                existing_metrics.append(metrics)
                metrics_data = existing_metrics
            else:
                metrics_data = [metrics]
            
            # Save updated metrics
            with open(metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
            self.last_metrics_save = time.time()
            logger.debug(f"Saved model metrics: avg_latency={avg_latency:.2f}ms, error_rate={error_rate:.4f}")
            
        except Exception as e:
            logger.error(f"Error saving model metrics: {e}")

# Create a singleton instance
_model = None

def get_model() -> SentimentModel:
    """
    Get singleton model instance.
    
    This ensures we only load the model once, improving performance.
    """
    global _model
    if _model is None:
        _model = SentimentModel()
    return _model

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze sentiment of a text using the configured model.
    
    This function maintains the same interface as before but uses the
    enhanced SentimentModel class internally.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary with sentiment label and confidence score
    """
    model = get_model()
    return model.analyze(text)