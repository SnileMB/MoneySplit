"""
Logging configuration module for MoneySplit application.
Provides structured logging with JSON formatting and file rotation.
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from config import LOG_LEVEL, LOG_FILE


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs JSON-formatted log records."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    logger_name: str = "MoneySplit",
    log_level: str = LOG_LEVEL,
    log_file: str = LOG_FILE,
    use_json: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        logger_name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        use_json: Whether to use JSON formatting

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # File handler with rotation (max 10MB, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))

    # Formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
