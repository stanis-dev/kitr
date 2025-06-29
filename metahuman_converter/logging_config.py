"""
Logging configuration for the MetaHuman converter pipeline.

Provides centralized logging setup with appropriate formatters and handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    include_timestamp: bool = True,
    include_module: bool = True
) -> None:
    """
    Setup logging configuration for the MetaHuman converter.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If None, logs only to console
        include_timestamp: Whether to include timestamp in log format
        include_module: Whether to include module name in log format
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    format_parts = []
    if include_timestamp:
        format_parts.append("%(asctime)s")
    if include_module:
        format_parts.append("%(name)s")
    format_parts.extend(["%(levelname)s", "%(message)s"])
    
    formatter = logging.Formatter(" - ".join(format_parts))
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if requested)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Setup specific logger for our package
    metahuman_logger = logging.getLogger('metahuman_converter')
    metahuman_logger.setLevel(numeric_level)
    
    logging.info(f"Logging configured at {level} level")
    if log_file:
        logging.info(f"Logging to file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)