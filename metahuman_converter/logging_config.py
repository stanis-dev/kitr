"""
Logging configuration for MetaHuman FBX validation.
Provides detailed logging for validation steps.
Rich console is required - no fallbacks.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler


class MetaHumanLogger:
    """Custom logger for MetaHuman validation."""

    def __init__(self, name: str = "metahuman_validator", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Initialize Rich console - required dependency
        self.console = Console(
            force_terminal=True,
            width=120,
            color_system="auto"
        )

        # Clear existing handlers
        self.logger.handlers.clear()

        # Setup rich console handler
        console_handler = RichHandler(
            console=self.console,
            show_time=False,
            show_path=False,
            rich_tracebacks=True,
            markup=True
        )
        console_handler.setLevel(level)

        # Simple format for console output
        console_format = logging.Formatter("%(message)s")
        console_handler.setFormatter(console_format)

        self.logger.addHandler(console_handler)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(f"[dim]{message}[/dim]")

    def error(self, message: str):
        """Log error message."""
        self.logger.error(f"[red]{message}[/red]")

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(f"[yellow]{message}[/yellow]")

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def step_start(self, step_name: str, description: str = ""):
        """Log the start of a validation step."""
        self.console.print(f"\n[bold blue]🔧 Step: {step_name}[/bold blue]")
        if description:
            self.console.print(f"[dim]{description}[/dim]")

    def step_complete(self, step_name: str, details: Optional[str] = None):
        """Log the completion of a validation step."""
        self.console.print(f"[bold green]✅ Completed: {step_name}[/bold green]")
        if details:
            self.console.print(f"[dim]{details}[/dim]")

    def step_error(self, step_name: str, error: str):
        """Log an error during a validation step."""
        self.console.print(f"[bold red]❌ Failed: {step_name}[/bold red]")
        self.console.print(f"[red]Error: {error}[/red]")

    def validation_result(self, item: str, success: bool, details: str = ""):
        """Log a validation result."""
        icon = "✅" if success else "❌"
        color = "green" if success else "red"
        self.console.print(f"[{color}]{icon} {item}[/{color}]")
        if details:
            self.console.print(f"  [dim]{details}[/dim]")

    def found_items(self, category: str, items: list, expected_count: Optional[int] = None):
        """Log found items with preview."""
        count = len(items)

        if expected_count:
            status = "✅" if count >= expected_count else "❌"
            self.console.print(f"{status} Found {count}/{expected_count} {category}")
        else:
            self.console.print(f"ℹ️  Found {count} {category}")

        if items and count > 0:
            # Show first few items as examples
            preview_count = min(5, count)
            preview_items = items[:preview_count]
            remaining = count - preview_count

            preview_text = ", ".join(preview_items)
            if remaining > 0:
                preview_text += f" ... and {remaining} more"

            self.console.print(f"  [dim]Examples: {preview_text}[/dim]")


def setup_logging(level: int = logging.INFO, log_file: Optional[Path] = None):
    """Setup logging configuration - Rich is required."""
    # Minimal logging setup - Rich console handles the display
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[logging.NullHandler()]  # Suppress default logging
    )


# Global logger instance
logger = MetaHumanLogger()
