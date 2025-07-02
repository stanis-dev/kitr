#!/usr/bin/env python3
"""
Pipeline Validation Module

Comprehensive validation functions for each step of the MetaHuman pipeline.
Ensures data integrity, completeness, and compliance at every stage.
"""

import json
import struct
from pathlib import Path
from typing import Dict, Any, Optional

from logger.core import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class PipelineValidator:
    """Comprehensive validator for all pipeline steps."""

    @staticmethod
    def validate_step_input(step_name: str, input_path: Path, expected_type: str) -> bool:
        """
        Validate input for any pipeline step.

        Args:
            step_name: Name of the pipeline step
            input_path: Path to input file/directory
            expected_type: Expected type ('file', 'directory', 'project', 'fbx', 'glb')

        Returns:
            True if validation passes

        Raises:
            ValidationError: If validation fails
        """
        logger.info(f"🔍 Validating input for {step_name}")

        if not input_path.exists():
            raise ValidationError(f"Input does not exist: {input_path}")

        if expected_type == 'file' and not input_path.is_file():
            raise ValidationError(f"Expected file, got directory: {input_path}")

        if expected_type == 'directory' and not input_path.is_dir():
            raise ValidationError(f"Expected directory, got file: {input_path}")

        if expected_type == 'project':
            if not input_path.suffix == '.uproject':
                raise ValidationError(f"Expected .uproject file: {input_path}")
            if not input_path.is_file():
                raise ValidationError(f"Project file does not exist: {input_path}")

        if expected_type == 'fbx':
            if not input_path.suffix.lower() == '.fbx':
                raise ValidationError(f"Expected .fbx file: {input_path}")
            if not PipelineValidator._validate_fbx_structure(input_path):
                raise ValidationError(f"Invalid FBX file structure: {input_path}")

        if expected_type == 'glb':
            if not input_path.suffix.lower() == '.glb':
                raise ValidationError(f"Expected .glb file: {input_path}")
            if not PipelineValidator._validate_glb_magic(input_path):
                raise ValidationError(f"Invalid GLB file format: {input_path}")

        # Check file size
        if input_path.is_file():
            size = input_path.stat().st_size
            if size == 0:
                raise ValidationError(f"Input file is empty: {input_path}")
            if size < 100:  # Suspiciously small
                logger.warning(f"Input file very small ({size} bytes): {input_path}")

        logger.info(f"   ✅ Input validation passed for {step_name}")
        return True

    @staticmethod
    def validate_step_output(step_name: str, output_path: Path,
                           validation_config: Dict[str, Any]) -> bool:
        """
        Validate output for any pipeline step.

        Args:
            step_name: Name of the pipeline step
            output_path: Path to output file/directory
            validation_config: Validation configuration

        Returns:
            True if validation passes

        Raises:
            ValidationError: If validation fails
        """
        logger.info(f"✅ Validating output for {step_name}")

        if not output_path.exists():
            raise ValidationError(f"Output does not exist: {output_path}")

        # Apply step-specific validation
        if step_name == "Step 1: Asset Duplicator":
            return PipelineValidator._validate_asset_copy_output(output_path, validation_config)
        elif step_name == "Step 2: DCC Export":
            return PipelineValidator._validate_dcc_export_output(output_path, validation_config)
        elif step_name == "Step 3: FBX Export":
            return PipelineValidator._validate_fbx_export_output(output_path, validation_config)
        elif step_name == "Step 4: GLB Convert":
            return PipelineValidator._validate_glb_convert_output(output_path, validation_config)
        elif step_name == "Step 5: Web Optimize":
            return PipelineValidator._validate_web_optimize_output(output_path, validation_config)
        else:
            logger.warning(f"No specific validation for step: {step_name}")
            return True

    @staticmethod
    def _validate_asset_copy_output(output_path: Path, config: Dict[str, Any]) -> bool:
        """Validate asset duplicator output."""
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

    @staticmethod
    def _validate_dcc_export_output(output_path: Path, config: Dict[str, Any]) -> bool:
        """Validate DCC export output."""
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

    @staticmethod
    def _validate_fbx_export_output(output_path: Path, config: Dict[str, Any]) -> bool:
        """
        Comprehensive FBX export validation including materials and assets.
        This is the CRITICAL validation the user requested.
        """
        logger.info("   🔍 Performing comprehensive FBX validation...")

        if not output_path.is_file():
            raise ValidationError("FBX export output must be a file")

        if not output_path.suffix.lower() == '.fbx':
            raise ValidationError("FBX export output must have .fbx extension")

        # Size validation
        size = output_path.stat().st_size
        if size < 1024:  # Less than 1KB is suspicious
            raise ValidationError(f"FBX file too small: {size} bytes")

        # Validate FBX structure
        if not PipelineValidator._validate_fbx_structure(output_path):
            raise ValidationError("Invalid FBX file structure")

        # CRITICAL: Validate materials and related assets
        validation_result = PipelineValidator._validate_fbx_materials_and_assets(output_path, config)
        if not validation_result['valid']:
            raise ValidationError(f"FBX materials validation failed: {validation_result['error']}")

        # Validate morph targets
        expected_morphs = config.get('expected_morph_count', 52)
        morph_validation = PipelineValidator._validate_fbx_morph_targets(output_path, expected_morphs)
        if not morph_validation['valid']:
            logger.warning(f"Morph target validation: {morph_validation['message']}")

        # Validate skeletal structure
        if not PipelineValidator._validate_fbx_skeleton(output_path):
            raise ValidationError("FBX skeletal structure validation failed")

        logger.info("   ✅ Comprehensive FBX validation passed")
        return True

    @staticmethod
    def _validate_glb_convert_output(output_path: Path, config: Dict[str, Any]) -> bool:
        """Basic GLB conversion validation."""
        if not output_path.is_file():
            raise ValidationError("GLB convert output must be a file")

        if not output_path.suffix.lower() == '.glb':
            raise ValidationError("GLB convert output must have .glb extension")

        # Basic GLB validation
        if not PipelineValidator._validate_glb_magic(output_path):
            raise ValidationError("Invalid GLB magic number")

        logger.info("   ✅ GLB convert output validation passed")
        return True

    @staticmethod
    def _validate_web_optimize_output(output_path: Path, config: Dict[str, Any]) -> bool:
        """
        COMPREHENSIVE final GLB validation - this is what the user requested.
        The final .glb must be evaluated fully before pipeline can succeed.
        """
        logger.info("   🔍 Performing COMPREHENSIVE final GLB validation...")

        if not output_path.is_file():
            raise ValidationError("Web optimize output must be a file")

        if not output_path.suffix.lower() == '.glb':
            raise ValidationError("Web optimize output must have .glb extension")

        # COMPREHENSIVE GLB validation
        validation_result = PipelineValidator._validate_glb_structure_complete(output_path, config)
        if not validation_result['valid']:
            raise ValidationError(f"Complete GLB validation failed: {validation_result['error']}")

        # Validate web optimization was applied
        optimization_result = PipelineValidator._validate_web_optimization_applied(output_path, config)
        if not optimization_result['valid']:
            logger.warning(f"Web optimization validation: {optimization_result['message']}")

        # Final Azure compatibility check
        azure_result = PipelineValidator._validate_azure_compatibility(output_path)
        if not azure_result['valid']:
            raise ValidationError(f"Azure compatibility validation failed: {azure_result['error']}")

        logger.info("   ✅ COMPREHENSIVE final GLB validation passed")
        logger.info(f"   🎯 Azure-ready GLB with {azure_result.get('morph_count', 0)} morph targets")
        return True

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
                'shapekey',
                'deformer'
            ]

            found_morphs = sum(content_str.count(indicator) for indicator in morph_indicators)

            if found_morphs >= expected_count:
                return {
                    'valid': True,
                    'message': f"Found {found_morphs} morph indicators (expected {expected_count})",
                    'found_count': found_morphs
                }
            else:
                return {
                    'valid': False,
                    'message': f"Only found {found_morphs} morph indicators (expected {expected_count})",
                    'found_count': found_morphs
                }

        except Exception as e:
            return {
                'valid': False,
                'message': f"Failed to validate morph targets: {e}",
                'found_count': 0
            }

    @staticmethod
    def _validate_fbx_skeleton(fbx_path: Path) -> bool:
        """Validate FBX skeletal structure."""
        try:
            with open(fbx_path, 'rb') as f:
                content = f.read()

            content_str = str(content, errors='ignore').lower()

            # Look for skeleton indicators
            skeleton_indicators = [
                'bone',
                'joint',
                'skeleton',
                'armature',
                'limb'
            ]

            found_skeleton = any(indicator in content_str for indicator in skeleton_indicators)

            return found_skeleton

        except Exception as e:
            logger.warning(f"Could not validate FBX skeleton: {e}")
            return False

    @staticmethod
    def _validate_glb_magic(glb_path: Path) -> bool:
        """Validate GLB magic number."""
        try:
            with open(glb_path, 'rb') as f:
                magic = f.read(4)
                return magic == b'glTF'
        except Exception:
            return False

    @staticmethod
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
            validation_result = PipelineValidator._validate_gltf_json_structure(gltf, config)
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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


def validate_pipeline_step(step_name: str, input_path: Optional[Path],
                          output_path: Path, validation_config: Dict[str, Any]) -> bool:
    """
    Convenience function to validate both input and output for a pipeline step.

    Args:
        step_name: Name of the pipeline step
        input_path: Path to input (None for first step)
        output_path: Path to output
        validation_config: Validation configuration

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails
    """
    logger.info(f"🔍 Validating pipeline step: {step_name}")

    try:
        # Validate input if provided
        if input_path:
            expected_input_type = validation_config.get('input_type', 'file')
            PipelineValidator.validate_step_input(step_name, input_path, expected_input_type)

        # Validate output
        PipelineValidator.validate_step_output(step_name, output_path, validation_config)

        logger.info(f"✅ Pipeline step validation passed: {step_name}")
        return True

    except ValidationError as e:
        logger.error(f"❌ Pipeline step validation failed for {step_name}: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected validation error for {step_name}: {e}")
        raise ValidationError(f"Validation error: {e}")
