import os
import sys
import unittest
from unittest.mock import patch

# Add the project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.sentiment import analyze_sentiment, SentimentModel, get_model


class TestSentimentAnalysis(unittest.TestCase):
    """Tests for the sentiment analysis functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Ensure we're using a test model
        os.environ["MODEL_VERSION"] = "test-model-v1"
        # Clear any existing model instance
        if '_model' in globals():
            globals()['_model'] = None
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis with positive text."""
        text = "Markets reach record highs as tech stocks surge with strong growth."
        result = analyze_sentiment(text)
        
        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["score"], 0.5)
        self.assertEqual(result["model_version"], "test-model-v1")
        
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis with negative text."""
        text = "Global recession fears grow as manufacturing slows amid mounting concerns."
        result = analyze_sentiment(text)
        
        self.assertEqual(result["sentiment"], "negative")
        self.assertGreater(result["score"], 0.5)
        self.assertEqual(result["model_version"], "test-model-v1")
        
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis with neutral text."""
        text = "Company files regular quarterly report with SEC."
        result = analyze_sentiment(text)
        
        self.assertEqual(result["sentiment"], "neutral")
        self.assertGreaterEqual(result["score"], 0.5)
        self.assertEqual(result["model_version"], "test-model-v1")
    
    def test_singleton_model(self):
        """Test that get_model returns a singleton instance."""
        model1 = get_model()
        model2 = get_model()
        
        # Should be the same instance
        self.assertIs(model1, model2)
    
    def test_model_handles_empty_text(self):
        """Test that the model properly handles empty text."""
        result = analyze_sentiment("")
        
        # Empty text should default to neutral
        self.assertEqual(result["sentiment"], "neutral")
    
    @patch('backend.app.sentiment.SentimentModel._analyze_rule_based')
    def test_model_error_handling(self, mock_analyze):
        """Test error handling in the sentiment analysis model."""
        # Mock the analysis function to raise an exception
        mock_analyze.side_effect = Exception("Test exception")
        
        # Analysis should still return a result with default neutral sentiment
        result = analyze_sentiment("Test text")
        self.assertEqual(result["sentiment"], "neutral")
        self.assertEqual(result["score"], 0.5)
        self.assertIn("error", result)
        

if __name__ == '__main__':
    unittest.main()