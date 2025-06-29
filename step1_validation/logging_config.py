"""
Logging configuration for MetaHuman validation.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install

    # Configure rich for better error display
    install(show_locals=True)
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ValidationLogger:
    """Logger for validation operations."""

    def __init__(self, name: str = "validation"):
        self.name = name
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            self._setup_logger()

        # Console for rich output
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    def _setup_logger(self):
        """Configure logger with appropriate handlers."""
        self.logger.setLevel(logging.DEBUG)

        if RICH_AVAILABLE:
            # Rich handler for colorized console output
            rich_handler = RichHandler(
                console=Console(stderr=True),
                show_time=False,
                show_path=False,
                rich_tracebacks=True
            )
            rich_handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(message)s")
            rich_handler.setFormatter(formatter)
            self.logger.addHandler(rich_handler)
        else:
            # Standard console handler
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(message, **kwargs)


# Global logger instance
logger = ValidationLogger("validation")
