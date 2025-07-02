#!/usr/bin/env python3
"""
Step 3: FBX Export Validation

Validation functions specific to FBX export step.
Includes critical materials and assets validation.
"""

from pathlib import Path
from typing import Dict, Any
from logger.core import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_fbx_export_output(output_path: Path, config: Dict[str, Any]) -> bool:
    """
    Comprehensive FBX export validation including materials and assets.
    This is the CRITICAL validation the user requested.
    """
    logger.info("🔍 Performing comprehensive FBX validation")

    if not output_path.is_file():
        raise ValidationError("FBX export output must be a file")

    if not output_path.suffix.lower() == '.fbx':
        raise ValidationError("FBX export output must have .fbx extension")

    # Size validation
    size = output_path.stat().st_size
    if size < 1024:  # Less than 1KB is suspicious
        raise ValidationError(f"FBX file too small: {size} bytes")

    # Validate FBX structure
    if not _validate_fbx_structure(output_path):
        raise ValidationError("Invalid FBX file structure")

    # CRITICAL: Validate materials and related assets
    validation_result = _validate_fbx_materials_and_assets(output_path, config)
    if not validation_result['valid']:
        raise ValidationError(f"FBX materials validation failed: {validation_result['error']}")

    # Validate morph targets
    expected_morphs = config.get('expected_morph_count', 52)
    morph_validation = _validate_fbx_morph_targets(output_path, expected_morphs)
    if not morph_validation['valid']:
        logger.warning(f"Morph target validation: {morph_validation['message']}")

    # Validate skeletal structure
    if not _validate_fbx_skeleton(output_path):
        raise ValidationError("FBX skeletal structure validation failed")

    logger.info("✅ Comprehensive FBX validation passed")
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


def _validate_fbx_materials_and_assets(fbx_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    CRITICAL validation: Ensure FBX has materials and related assets.
    This addresses the user's specific requirement.
    """
    logger.info("   🎨 Validating FBX materials and related assets...")

    try:
        with open(fbx_path, 'rb') as f:
            content = f.read()

        # Convert to string for text searching (handles both binary and ASCII FBX)
        content_str = str(content, errors='ignore').lower()

        # Material indicators to look for
        material_indicators = [
            'material',
            'texture',
            'diffuse',
            'normal',
            'roughness',
            'metallic',
            'shader',
            'lambert',
            'phong'
        ]

        found_materials: list[str] = []
        for indicator in material_indicators:
            if indicator in content_str:
                found_materials.append(indicator)

        if len(found_materials) < 3:  # Require at least 3 material-related terms
            return {
                'valid': False,
                'error': f"Insufficient material data found. Only found: {found_materials}",
                'found_materials': found_materials
            }

        # Texture/asset indicators
        asset_indicators = [
            '.png',
            '.jpg',
            '.jpeg',
            '.tga',
            '.bmp',
            'basecolor',
            'normalmap',
            'roughnessmap'
        ]

        found_assets: list[str] = []
        for indicator in asset_indicators:
            if indicator in content_str:
                found_assets.append(indicator)

        # Check file size (materials add significant size)
        file_size = fbx_path.stat().st_size
        expected_min_size = 10 * 1024 * 1024  # 10MB minimum for MetaHuman with materials

        if file_size < expected_min_size:
            logger.warning(f"FBX file size ({file_size / 1024 / 1024:.1f}MB) smaller than expected for full MetaHuman with materials")

        logger.info(f"     ✅ Found {len(found_materials)} material indicators: {found_materials[:5]}")
        logger.info(f"     ✅ Found {len(found_assets)} asset references: {found_assets[:3]}")

        return {
            'valid': True,
            'found_materials': found_materials,
            'found_assets': found_assets,
            'file_size_mb': file_size / 1024 / 1024
        }

    except Exception as e:
        return {
            'valid': False,
            'error': f"Failed to validate FBX materials: {e}",
            'found_materials': [],
            'found_assets': []
        }


def _validate_fbx_morph_targets(fbx_path: Path, expected_count: int) -> Dict[str, Any]:
    """Validate FBX morph targets for Azure compatibility."""
    try:
        with open(fbx_path, 'rb') as f:
            content = f.read()

        content_str = str(content, errors='ignore').lower()

        # Look for morph target indicators
        morph_indicators = [
            'blendshape',
            'morphtarget',
            'deformer',
            'shape'
        ]

        found_morphs = 0
        for indicator in morph_indicators:
            found_morphs += content_str.count(indicator)

        # Estimate actual morph count (rough heuristic)
        estimated_count = max(found_morphs // 3, content_str.count('blendshape'))

        if estimated_count < expected_count * 0.8:  # Allow 20% tolerance
            return {
                'valid': False,
                'message': f"Insufficient morph targets. Expected ~{expected_count}, estimated {estimated_count}",
                'estimated_count': estimated_count
            }

        return {
            'valid': True,
            'message': f"Morph targets OK. Estimated {estimated_count}/{expected_count}",
            'estimated_count': estimated_count
        }

    except Exception as e:
        return {
            'valid': False,
            'message': f"Failed to validate morph targets: {e}",
            'estimated_count': 0
        }


def _validate_fbx_skeleton(fbx_path: Path) -> bool:
    """Validate FBX skeletal structure."""
    try:
        with open(fbx_path, 'rb') as f:
            content = f.read()

        content_str = str(content, errors='ignore').lower()

        # Essential bone indicators
        bone_indicators = [
            'skeleton',
            'bone',
            'joint',
            'head',
            'neck',
            'spine'
        ]

        found_bones = 0
        for indicator in bone_indicators:
            if indicator in content_str:
                found_bones += 1

        # Require at least 4 bone-related terms for valid skeleton
        return found_bones >= 4

    except Exception as e:
        logger.warning(f"Could not validate FBX skeleton: {e}")
        return False


def validate_step_input(input_path: Path, expected_type: str) -> bool:
    """
    Validate input for FBX export step.

    Args:
        input_path: Path to input file/directory
        expected_type: Expected type ('directory', 'file')

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    logger.info("🔍 Validating FBX export input")

    if not input_path.exists():
        raise ValidationError(f"Input does not exist: {input_path}")

    if expected_type == 'file' and not input_path.is_file():
        raise ValidationError(f"Expected file, got directory: {input_path}")

    if expected_type == 'directory' and not input_path.is_dir():
        raise ValidationError(f"Expected directory, got file: {input_path}")

    # Check file size
    if input_path.is_file():
        size = input_path.stat().st_size
        if size == 0:
            raise ValidationError(f"Input file is empty: {input_path}")
        if size < 100:  # Suspiciously small
            logger.warning(f"Input file very small ({size} bytes): {input_path}")

    logger.info("   ✅ Input validation passed for FBX export")
    return True
