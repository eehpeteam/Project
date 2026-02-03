"""Logging configuration module"""

import logging
import logging.handlers
from pathlib import Path
from src.config import Config


def setup_logger(name, log_file=None, level=None):
    """
    Set up logger with both file and console handlers
    
    Args:
        name (str): Logger name
        log_file (str): Path to log file. If None, uses Config.OUTPUT_DIRECTORY/app.log
        level (str): Logging level. If None, uses Config.LOG_LEVEL
        
    Returns:
        logging.Logger: Configured logger
    """
    if level is None:
        level = Config.LOG_LEVEL
    
    if log_file is None:
        log_file = Path(Config.OUTPUT_DIRECTORY) / "app.log"
    else:
        log_file = Path(log_file)
    
    # Ensure log directory exists
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        str(log_file),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Create root logger
root_logger = setup_logger('teams_notes')
