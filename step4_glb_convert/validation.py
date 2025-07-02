#!/usr/bin/env python3
"""
Step 4: GLB Convert Validation

Validation functions specific to GLB conversion step.
"""

from pathlib import Path
from typing import Dict, Any
from logger.core import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_glb_convert_output(output_path: Path, config: Dict[str, Any]) -> bool:
    """Basic GLB conversion validation."""
    logger.info("🔍 Validating GLB convert output")

    if not output_path.is_file():
        raise ValidationError("GLB convert output must be a file")

    if not output_path.suffix.lower() == '.glb':
        raise ValidationError("GLB convert output must have .glb extension")

    # Basic GLB validation
    if not _validate_glb_magic(output_path):
        raise ValidationError("Invalid GLB magic number")

    logger.info("   ✅ GLB convert output validation passed")
    return True


def _validate_glb_magic(glb_path: Path) -> bool:
    """Validate GLB magic number (glTF binary signature)."""
    try:
        with open(glb_path, 'rb') as f:
            magic = f.read(4)
            # GLB files start with "glTF" magic number
            return magic == b'glTF'
    except Exception as e:
        logger.warning(f"Could not validate GLB magic: {e}")
        return False


def validate_step_input(input_path: Path, expected_type: str) -> bool:
    """
    Validate input for GLB convert step.

    Args:
        input_path: Path to input file/directory
        expected_type: Expected type ('fbx', 'file')

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    logger.info("🔍 Validating GLB convert input")

    if not input_path.exists():
        raise ValidationError(f"Input does not exist: {input_path}")

    if expected_type == 'file' and not input_path.is_file():
        raise ValidationError(f"Expected file, got directory: {input_path}")

    if expected_type == 'fbx':
        if not input_path.suffix.lower() == '.fbx':
            raise ValidationError(f"Expected .fbx file: {input_path}")
        if not _validate_fbx_structure(input_path):
            raise ValidationError(f"Invalid FBX file structure: {input_path}")

    # Check file size
    if input_path.is_file():
        size = input_path.stat().st_size
        if size == 0:
            raise ValidationError(f"Input file is empty: {input_path}")
        if size < 100:  # Suspiciously small
            logger.warning(f"Input file very small ({size} bytes): {input_path}")

    logger.info("   ✅ Input validation passed for GLB convert")
    return True


def _validate_fbx_structure(fbx_path: Path) -> bool:
    """Validate basic FBX file structure."""
    try:
        with open(fbx_path, 'rb') as f:
            # Read first 23 bytes for FBX header
            header = f.read(23)

            # Check for FBX magic numbers
            if header.startswith(b"Kaydara FBX Binary"):
                return True
            elif b"FBX" in header[:50]:  # ASCII FBX might have FBX somewhere early
                return True

        return False
    except Exception as e:
        logger.warning(f"Could not validate FBX structure: {e}")
        return False
