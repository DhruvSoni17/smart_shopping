import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name
        log_file: Optional path to log file
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log_file specified
    if log_file:
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger