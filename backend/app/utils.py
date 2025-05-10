import logging
import logging.handlers
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings after parsing the log record.
    
    Usage:
        formatter = JSONFormatter()
        json_handler.setFormatter(formatter)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add exception info if available
        if record.exc_info:
            exc_type = record.exc_info[0]
            exc_type_name = exc_type.__name__ if exc_type else "Exception"
            log_data["exception"] = {
                "type": exc_type_name,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra attributes (if any were attached using LoggerAdapter)
        for key, value in record.__dict__.items():
            if key not in ["args", "asctime", "created", "exc_info", "exc_text", "filename",
                          "funcName", "id", "levelname", "levelno", "lineno", "module",
                          "msecs", "message", "msg", "name", "pathname", "process",
                          "processName", "relativeCreated", "stack_info", "thread", "threadName"]:
                log_data[key] = value
            
        return json.dumps(log_data)

def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up advanced logging configuration for the application with structured logs
    
    Args:
        log_level: Optional log level from environment, defaults to INFO if not provided
        
    Returns:
        Configured logger instance
    """
    # Get log level from environment or use default
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Create logger
    logger = logging.getLogger("financial_sentiment")
    logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Choose format based on environment
    if os.environ.get("LOG_FORMAT", "").lower() == "json":
        # JSON formatter for structured logging (useful in production)
        formatter = JSONFormatter()
    else:
        # Human-readable formatter (useful in development)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optionally add file handler for persistent logs
    log_file = os.environ.get("LOG_FILE")
    if log_file:
        # Use rotating file handler to prevent log files from growing too large
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10485760, backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized at {log_level} level")
    return logger

def format_date(dt: datetime) -> str:
    """
    Format datetime object to string
    
    Args:
        dt: Datetime object
        
    Returns:
        Formatted date string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format API response to ensure JSON serialization
    
    Args:
        data: Response data to format
        
    Returns:
        Formatted response data
    """
    # Convert to and from JSON to ensure serialization
    try:
        json_str = json.dumps(data)
        return json.loads(json_str)
    except Exception as e:
        logger = logging.getLogger("financial_sentiment")
        logger.error(f"Error formatting response: {e}")
        return {"error": "Error formatting response"}