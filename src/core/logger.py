import logging
import sys
from pathlib import Path

def get_logger(name: str) -> logging.Logger:
    """
    Configures and returns a centralized logger for KnowSphere AI.
    
    Args:
        name (str): The name of the logger (usually __name__).
        
    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times if get_logger is called repeatedly
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger
