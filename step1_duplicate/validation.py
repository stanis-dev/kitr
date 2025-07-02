#!/usr/bin/env python3
"""
Step 1: Asset Duplicator Validation

Validation functions specific to asset duplication step.
"""

from pathlib import Path
from typing import Dict, Any
from logger.core import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_asset_copy_output(output_path: Path, config: Dict[str, Any]) -> bool:
    """Validate asset duplicator output."""
    logger.info("🔍 Validating asset copy output")

    if not output_path.is_dir():
        raise ValidationError("Asset copy output must be a directory")

    # Check for essential files
    required_files = [
        f"{config.get('project_name', 'project')}.uproject",
        "character_selection_manifest.json"
    ]

    required_dirs = ["Config", "Content"]

    for file_name in required_files:
        if not (output_path / file_name).exists():
            raise ValidationError(f"Missing required file: {file_name}")

    for dir_name in required_dirs:
        if not (output_path / dir_name).exists():
            raise ValidationError(f"Missing required directory: {dir_name}")

    logger.info("   ✅ Asset copy output validation passed")
    return True


def validate_step_input(input_path: Path, expected_type: str) -> bool:
    """
    Validate input for asset duplicator step.

    Args:
        input_path: Path to input file/directory
        expected_type: Expected type ('project', 'directory')

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    logger.info("🔍 Validating asset duplicator input")

    if not input_path.exists():
        raise ValidationError(f"Input does not exist: {input_path}")

    if expected_type == 'directory' and not input_path.is_dir():
        raise ValidationError(f"Expected directory, got file: {input_path}")

    if expected_type == 'project':
        if not input_path.suffix == '.uproject':
            raise ValidationError(f"Expected .uproject file: {input_path}")
        if not input_path.is_file():
            raise ValidationError(f"Project file does not exist: {input_path}")

    logger.info("   ✅ Input validation passed for asset duplicator")
    return True
