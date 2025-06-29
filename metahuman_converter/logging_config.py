"""
Logging configuration for the MetaHuman converter pipeline.
Provides detailed logging for each step of the conversion process.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback console
    class Console:
        def print(self, text):
            # Simple markup removal for fallback
            if isinstance(text, str):
                text = text.replace("[bold blue]", "").replace("[/bold blue]", "")
                text = text.replace("[bold green]", "").replace("[/bold green]", "")
                text = text.replace("[bold red]", "").replace("[/bold red]", "")
                text = text.replace("[red]", "").replace("[/red]", "")
                text = text.replace("[green]", "").replace("[/green]", "")
                text = text.replace("[dim]", "").replace("[/dim]", "")
            print(text)
    
    class RichHandler(logging.Handler):
        def __init__(self, **kwargs):
            super().__init__()
        def emit(self, record):
            print(self.format(record))


class MetaHumanLogger:
    """Custom logger for the MetaHuman conversion pipeline."""
    
    def __init__(self, name: str = "metahuman_converter", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.console = Console()
        
        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # Setup rich console handler
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True
        )
        console_handler.setLevel(level)
        
        # Format for console output
        console_format = logging.Formatter(
            "%(message)s",
            datefmt="[%X]"
        )
        console_handler.setFormatter(console_format)
        
        self.logger.addHandler(console_handler)
        
    def add_file_handler(self, log_file: Path, level: int = logging.DEBUG):
        """Add file handler for detailed logging to file."""
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Detailed format for file output
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        file_handler.setFormatter(file_format)
        
        self.logger.addHandler(file_handler)
        
    def step_start(self, step_name: str, description: str):
        """Log the start of a pipeline step."""
        self.console.print(f"\n[bold blue]🔧 Step: {step_name}[/bold blue]")
        self.console.print(f"[dim]{description}[/dim]")
        self.logger.info(f"Starting step: {step_name}")
        
    def step_complete(self, step_name: str, details: Optional[str] = None):
        """Log the completion of a pipeline step."""
        self.console.print(f"[bold green]✅ Completed: {step_name}[/bold green]")
        if details:
            self.console.print(f"[dim]{details}[/dim]")
        self.logger.info(f"Completed step: {step_name}")
        
    def step_error(self, step_name: str, error: str):
        """Log an error during a pipeline step."""
        self.console.print(f"[bold red]❌ Failed: {step_name}[/bold red]")
        self.console.print(f"[red]Error: {error}[/red]")
        self.logger.error(f"Step {step_name} failed: {error}")
        
    def validation_result(self, item: str, status: bool, details: str = ""):
        """Log validation results with visual indicators."""
        icon = "✅" if status else "❌"
        color = "green" if status else "red"
        self.console.print(f"[{color}]{icon} {item}[/{color}]")
        if details:
            self.console.print(f"  [dim]{details}[/dim]")
            
    def found_items(self, category: str, items: list, expected_count: Optional[int] = None):
        """Log found items (e.g., blendshapes, bones) with counts."""
        count = len(items)
        if expected_count:
            status = "✅" if count >= expected_count else "⚠️"
            self.console.print(f"{status} Found {count}/{expected_count} {category}")
        else:
            self.console.print(f"ℹ️  Found {count} {category}")
            
        # Log first few items as examples
        if items:
            preview = items[:5] if len(items) > 5 else items
            preview_text = ", ".join(preview)
            if len(items) > 5:
                preview_text += f" ... and {len(items) - 5} more"
            self.console.print(f"  [dim]Examples: {preview_text}[/dim]")


# Global logger instance
logger = MetaHumanLogger()


def setup_logging(level: int = logging.INFO, log_file: Optional[Path] = None):
    """Setup logging for the application."""
    global logger
    logger = MetaHumanLogger(level=level)
    
    if log_file:
        logger.add_file_handler(log_file)
        
    return logger