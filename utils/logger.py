"""
Structured Logger Utility for InsightAI Platform.
Provides clean logging formatting for system debugging and monitoring.
"""

import logging
import sys

def get_logger(name: str = "InsightAI") -> logging.Logger:
    """Configures and returns a structured python logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

logger = get_logger("InsightAI")
