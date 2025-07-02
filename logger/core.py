"""
Simple logging with normal/debug levels and validation support.
"""

import logging
import sys
from typing import List, Optional, Any

class SimpleLogger:
    """Simple logger with normal/debug levels."""

    def __init__(self, name: str, level: str = "normal"):
        self.name = name
        self.level = level
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            self._setup_logger()

        # Try to get rich console if available
        self.console = self._get_rich_console()

    def _get_rich_console(self) -> Any:
        """Get Rich console if available, otherwise None."""
        try:
            import rich.console  # type: ignore
            return rich.console.Console()  # type: ignore
        except ImportError:
            return None

    def _setup_logger(self):
        """Setup basic logger."""
        log_level = logging.DEBUG if self.level == "debug" else logging.INFO
        self.logger.setLevel(log_level)

        # Try Rich handler first, fall back to standard
        handler = self._get_rich_handler(log_level) or self._get_standard_handler(log_level)
        self.logger.addHandler(handler)  # type: ignore

    def _get_rich_handler(self, log_level: int) -> Any:
        """Get Rich handler if available."""
        try:
            import rich.logging  # type: ignore
            handler = rich.logging.RichHandler(show_time=False, show_path=False)  # type: ignore
            handler.setLevel(log_level)  # type: ignore
            formatter = logging.Formatter("%(message)s")
            handler.setFormatter(formatter)  # type: ignore
            return handler
        except ImportError:
            return None

    def _get_standard_handler(self, log_level: int) -> Any:  # type: ignore
        """Get standard console handler."""
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        return handler

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    # Validation-specific methods for backwards compatibility
    def step_start(self, step_name: str, description: str):
        """Start a validation step."""
        message = f"🔍 {step_name}: {description}"
        if self.console and hasattr(self.console, 'print'):
            self.console.print(message)
        else:
            self.info(message)

    def step_complete(self, step_name: str):
        """Complete a validation step."""
        message = f"✅ {step_name} completed"
        if self.console and hasattr(self.console, 'print'):
            self.console.print(message)
        else:
            self.info(message)

    def validation_result(self, check_name: str, passed: bool, message: str = ""):
        """Log a validation result."""
        status = "✅" if passed else "❌"
        full_message = f"{status} {check_name}"
        if message:
            full_message += f": {message}"

        if self.console and hasattr(self.console, 'print'):
            self.console.print(full_message)
        else:
            self.info(full_message)

    def found_items(self, item_type: str, items: List[str], expected: Optional[int] = None):
        """Log found items count."""
        count = len(items)
        if expected:
            message = f"📊 Found {count}/{expected} {item_type}"
        else:
            message = f"📊 Found {count} {item_type}"

        if self.console and hasattr(self.console, 'print'):
            self.console.print(message)
        else:
            self.info(message)

def get_logger(name: str, level: str = "normal") -> SimpleLogger:
    """Get a simple logger instance."""
    return SimpleLogger(name, level)

def setup_logging(level: str = "normal"):
    """Setup global logging."""
    log_level = logging.DEBUG if level == "debug" else logging.INFO
    logging.basicConfig(level=log_level)
