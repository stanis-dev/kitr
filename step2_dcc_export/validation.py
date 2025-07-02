#!/usr/bin/env python3
"""
Step 2: DCC Export Validation

Validation functions specific to DCC export assembly step.
"""

from pathlib import Path
from typing import Dict, Any
from logger.core import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_dcc_export_output(output_path: Path, config: Dict[str, Any]) -> bool:
    """Validate DCC export output."""
    logger.info("🔍 Validating DCC export output")

    if not output_path.is_dir():
        raise ValidationError("DCC export output must be a directory")

    # Check for expected subdirectories
    required_dirs = ["FBX", "Textures", "Materials", "Meshes"]
    for dir_name in required_dirs:
        if not (output_path / dir_name).exists():
            raise ValidationError(f"Missing DCC export directory: {dir_name}")

    # Check for combined mesh
    fbx_dir = output_path / "FBX"
    combined_meshes = list(fbx_dir.glob("*_Combined.fbx"))
    if not combined_meshes:
        raise ValidationError("No combined mesh found in DCC export")

    logger.info("   ✅ DCC export output validation passed")
    return True


def validate_step_input(input_path: Path, expected_type: str) -> bool:
    """
    Validate input for DCC export step.

    Args:
        input_path: Path to input file/directory
        expected_type: Expected type ('directory', 'project')

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    logger.info("🔍 Validating DCC export input")

    if not input_path.exists():
        raise ValidationError(f"Input does not exist: {input_path}")

    if expected_type == 'directory' and not input_path.is_dir():
        raise ValidationError(f"Expected directory, got file: {input_path}")

    if expected_type == 'project':
        if not input_path.suffix == '.uproject':
            raise ValidationError(f"Expected .uproject file: {input_path}")
        if not input_path.is_file():
            raise ValidationError(f"Project file does not exist: {input_path}")

    logger.info("   ✅ Input validation passed for DCC export")
    return True
