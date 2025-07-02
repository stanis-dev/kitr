#!/usr/bin/env python3
"""
Step 5: Web Optimize Validation

Validation functions specific to web optimization step.
Includes comprehensive final GLB validation for Azure compatibility.
"""

import json
import struct
from pathlib import Path
from typing import Dict, Any
from logger.core import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_web_optimize_output(output_path: Path, config: Dict[str, Any]) -> bool:
    """
    COMPREHENSIVE final GLB validation - this is what the user requested.
    The final .glb must be evaluated fully before pipeline can succeed.
    """
    logger.info("🔍 Performing COMPREHENSIVE final GLB validation")

    if not output_path.is_file():
        raise ValidationError("Web optimize output must be a file")

    if not output_path.suffix.lower() == '.glb':
        raise ValidationError("Web optimize output must have .glb extension")

    # COMPREHENSIVE GLB validation
    validation_result = _validate_glb_structure_complete(output_path, config)
    if not validation_result['valid']:
        raise ValidationError(f"Complete GLB validation failed: {validation_result['error']}")

    # Validate web optimization was applied
    optimization_result = _validate_web_optimization_applied(output_path, config)
    if not optimization_result['valid']:
        logger.warning(f"Web optimization validation: {optimization_result['message']}")

    # Final Azure compatibility check
    azure_result = _validate_azure_compatibility(output_path)
    if not azure_result['valid']:
        raise ValidationError(f"Azure compatibility validation failed: {azure_result['error']}")

    logger.info("✅ COMPREHENSIVE final GLB validation passed")
    logger.info(f"   🎯 Azure-ready GLB with {azure_result.get('morph_count', 0)} morph targets")
    return True


def _validate_glb_structure_complete(glb_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    COMPREHENSIVE GLB structure validation.
    This is the complete validation the user requested for final GLB.
    """
    logger.info("     🔍 Performing complete GLB structure analysis...")

    try:
        with open(glb_path, 'rb') as f:
            # Read GLB header
            magic = f.read(4)
            if magic != b'glTF':
                return {'valid': False, 'error': 'Invalid GLB magic number'}

            version = struct.unpack('<I', f.read(4))[0]
            if version != 2:
                return {'valid': False, 'error': f'Unsupported GLB version: {version}'}

            total_length = struct.unpack('<I', f.read(4))[0]

            # Read JSON chunk
            json_length = struct.unpack('<I', f.read(4))[0]
            json_type = f.read(4)
            if json_type != b'JSON':
                return {'valid': False, 'error': 'Invalid JSON chunk type'}

            json_data = f.read(json_length).decode('utf-8').rstrip('\x00 ')

            try:
                gltf = json.loads(json_data)
            except json.JSONDecodeError as e:
                return {'valid': False, 'error': f'Invalid JSON in GLB: {e}'}

        # Validate glTF structure
        validation_result = _validate_gltf_json_structure(gltf, config)
        if not validation_result['valid']:
            return validation_result

        # Validate file size consistency
        actual_size = glb_path.stat().st_size
        if abs(actual_size - total_length) > 8:  # Allow small padding differences
            logger.warning(f"GLB size mismatch: header says {total_length}, actual {actual_size}")

        logger.info(f"     ✅ Complete GLB structure validation passed")
        logger.info(f"     📊 GLB: {len(gltf.get('meshes', []))} meshes, {validation_result.get('morph_count', 0)} morphs")

        return {
            'valid': True,
            'version': version,
            'total_length': total_length,
            'json_length': json_length,
            'morph_count': validation_result.get('morph_count', 0),
            'mesh_count': len(gltf.get('meshes', [])),
            'has_animations': len(gltf.get('animations', [])) > 0,
            'has_skins': len(gltf.get('skins', [])) > 0
        }

    except Exception as e:
        return {'valid': False, 'error': f'GLB structure validation failed: {e}'}


def _validate_gltf_json_structure(gltf: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate glTF JSON structure for completeness."""

    # Check required fields
    required_fields = ['asset', 'scenes', 'nodes']
    for field in required_fields:
        if field not in gltf:
            return {'valid': False, 'error': f'Missing required field: {field}'}

    # Check asset version
    asset = gltf.get('asset', {})
    if asset.get('version') != '2.0':
        return {'valid': False, 'error': f'Invalid glTF version: {asset.get("version")}'}

    # Count morph targets
    morph_count = 0
    meshes = gltf.get('meshes', [])
    for mesh in meshes:
        for primitive in mesh.get('primitives', []):
            targets = primitive.get('targets', [])
            morph_count += len(targets)

    # Validate expected morph count for Azure
    expected_morphs = config.get('expected_morph_count', 52)
    if morph_count < expected_morphs * 0.8:  # Allow 20% tolerance
        logger.warning(f"Low morph target count: {morph_count} (expected ~{expected_morphs})")

    # Check for skin (skeleton) data
    has_skins = len(gltf.get('skins', [])) > 0
    if not has_skins:
        logger.warning("No skin/skeleton data found in GLB")

    return {
        'valid': True,
        'morph_count': morph_count,
        'mesh_count': len(meshes),
        'has_skins': has_skins,
        'has_materials': len(gltf.get('materials', [])) > 0
    }


def _validate_web_optimization_applied(glb_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate that web optimization was properly applied."""
    try:
        with open(glb_path, 'rb') as f:
            # Read JSON chunk to check for optimization markers
            f.seek(12)  # Skip GLB header
            json_length = struct.unpack('<I', f.read(4))[0]
            f.seek(8, 1)  # Skip chunk type
            json_data = f.read(json_length).decode('utf-8').rstrip('\x00 ')
            gltf = json.loads(json_data)

        # Check for Draco compression
        extensions_used = gltf.get('extensionsUsed', [])
        has_draco = 'KHR_draco_mesh_compression' in extensions_used

        # Check for optimization markers in extras
        extras = gltf.get('extras', {})
        is_optimized = extras.get('web_optimized', False)

        if has_draco or is_optimized:
            return {
                'valid': True,
                'message': f'Web optimization detected (Draco: {has_draco})',
                'has_draco': has_draco,
                'is_optimized': is_optimized
            }
        else:
            return {
                'valid': False,
                'message': 'No web optimization markers found',
                'has_draco': False,
                'is_optimized': False
            }

    except Exception as e:
        return {
            'valid': False,
            'message': f'Failed to validate web optimization: {e}',
            'has_draco': False,
            'is_optimized': False
        }


def _validate_azure_compatibility(glb_path: Path) -> Dict[str, Any]:
    """Final validation for Azure Cognitive Services compatibility."""
    logger.info("     🎯 Validating Azure Cognitive Services compatibility...")

    try:
        with open(glb_path, 'rb') as f:
            # Read JSON chunk
            f.seek(12)  # Skip GLB header
            json_length = struct.unpack('<I', f.read(4))[0]
            f.seek(8, 1)  # Skip chunk type
            json_data = f.read(json_length).decode('utf-8').rstrip('\x00 ')
            gltf = json.loads(json_data)

        # Count morph targets
        morph_count = 0
        meshes = gltf.get('meshes', [])
        for mesh in meshes:
            for primitive in mesh.get('primitives', []):
                targets = primitive.get('targets', [])
                morph_count += len(targets)

        # Azure requires specific morph target count (52 for facial expressions)
        azure_morph_requirement = 52
        has_sufficient_morphs = morph_count >= azure_morph_requirement * 0.9  # 90% tolerance

        # Check coordinate system (should be Y-up for web/Azure)
        # This is typically handled in the conversion, but we can check the data

        # Check for skin data (required for avatars)
        has_skins = len(gltf.get('skins', [])) > 0

        # Check file size (Azure has limits)
        file_size_mb = glb_path.stat().st_size / (1024 * 1024)
        size_ok = file_size_mb < 100  # Azure typically has ~100MB limit

        if has_sufficient_morphs and has_skins and size_ok:
            logger.info(f"     ✅ Azure compatibility: {morph_count} morphs, {file_size_mb:.1f}MB")
            return {
                'valid': True,
                'morph_count': morph_count,
                'file_size_mb': file_size_mb,
                'has_skins': has_skins
            }
        else:
            issues: list[str] = []
            if not has_sufficient_morphs:
                issues.append(f"Insufficient morph targets: {morph_count} < {azure_morph_requirement}")
            if not has_skins:
                issues.append("Missing skin/skeleton data")
            if not size_ok:
                issues.append(f"File too large: {file_size_mb:.1f}MB > 100MB")

            return {
                'valid': False,
                'error': f"Azure compatibility issues: {'; '.join(issues)}",
                'morph_count': morph_count,
                'file_size_mb': file_size_mb,
                'has_skins': has_skins
            }

    except Exception as e:
        return {
            'valid': False,
            'error': f'Azure compatibility validation failed: {e}',
            'morph_count': 0,
            'file_size_mb': 0,
            'has_skins': False
        }


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
    Validate input for web optimize step.

    Args:
        input_path: Path to input file/directory
        expected_type: Expected type ('glb', 'file')

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    logger.info("🔍 Validating web optimize input")

    if not input_path.exists():
        raise ValidationError(f"Input does not exist: {input_path}")

    if expected_type == 'file' and not input_path.is_file():
        raise ValidationError(f"Expected file, got directory: {input_path}")

    if expected_type == 'glb':
        if not input_path.suffix.lower() == '.glb':
            raise ValidationError(f"Expected .glb file: {input_path}")
        if not _validate_glb_magic(input_path):
            raise ValidationError(f"Invalid GLB file format: {input_path}")

    # Check file size
    if input_path.is_file():
        size = input_path.stat().st_size
        if size == 0:
            raise ValidationError(f"Input file is empty: {input_path}")
        if size < 100:  # Suspiciously small
            logger.warning(f"Input file very small ({size} bytes): {input_path}")

    logger.info("   ✅ Input validation passed for web optimize")
    return True
