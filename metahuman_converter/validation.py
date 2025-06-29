"""
MetaHuman FBX Validator - Blender-based validation for input-file.fbx

Direct Blender-based validator with zero customization options.
"""

import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass, field

from .constants import AZURE_BLENDSHAPES, REQUIRED_BONES
from .logging_config import logger


@dataclass
class FBXValidationResult:
    """Simple validation result."""
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    found_blendshapes: List[str] = field(default_factory=list)
    found_bones: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)


def validate_blender_installation():
    """Validate that Blender is properly installed and accessible."""
    if not shutil.which("blender"):
        raise RuntimeError("Blender is not installed or not in PATH. Please install Blender and ensure it's accessible from command line.")
    
    # Test Blender version and basic functionality
    try:
        result = subprocess.run(
            ["blender", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            raise RuntimeError(f"Blender version check failed: {result.stderr}")
        
        logger.validation_result("Blender installation", True, f"Found Blender: {result.stdout.split()[1]}")
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("Blender version check timed out")
    except Exception as e:
        raise RuntimeError(f"Blender validation failed: {e}")


def validate_fbx(fbx_path: Path) -> FBXValidationResult:
    """
    Validate FBX file for MetaHuman compatibility using Blender.
    Direct Blender-based validation with no alternatives.
    """
    result = FBXValidationResult()
    
    logger.step_start("FBX Validation", f"Validating MetaHuman FBX: {fbx_path.name}")
    
    # Step 1: Validate Blender installation
    validate_blender_installation()
    
    # Step 2: Basic file checks
    if not fbx_path.exists():
        result.add_error(f"File not found: {fbx_path}")
        return result
    
    logger.validation_result("File exists", True)
    file_size_mb = fbx_path.stat().st_size / (1024 * 1024)
    logger.console.print(f"  Size: {file_size_mb:.1f}MB")
    
    # Step 3: Blender validation
    _process_with_blender(fbx_path, result)
    
    # Step 4: Final validation
    if len(result.found_blendshapes) >= 52:
        logger.validation_result("Blendshape count", True, f"Found {len(result.found_blendshapes)}/52")
        if not result.errors:
            result.is_valid = True
    else:
        missing_count = 52 - len(result.found_blendshapes)
        logger.validation_result("Blendshape count", False, f"Missing {missing_count} blendshapes")
        result.add_error(f"Missing {missing_count} required blendshapes")
    
    # Log results
    logger.found_items("blendshapes", result.found_blendshapes, 52)
    logger.found_items("bones", result.found_bones)
    
    if result.errors:
        for error in result.errors[:2]:  # Show first 2 errors
            logger.console.print(f"❌ ERROR")
            logger.console.print(f"  {error}")
    
    if result.warnings:
        for warning in result.warnings[:2]:  # Show first 2 warnings
            logger.console.print(f"⚠️  WARNING")
            logger.console.print(f"  {warning}")
    
    logger.step_complete("FBX Validation" if result.is_valid else "FBX Validation failed")
    
    return result


def _process_with_blender(fbx_path: Path, result: FBXValidationResult):
    """Process and validate FBX using Blender."""
    # Create temporary output file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        output_file = Path(temp_file.name)
    
    # Create Blender Python script
    blender_script = _create_blender_script(fbx_path, output_file)
    
    logger.validation_result("Blender processing", True, "Processing FBX with Blender")
    
    # Run Blender - fail fast if not available
    cmd = ['blender', '--background', '--python-expr', blender_script]
    
    process = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,  # 1 minute timeout
        check=True  # Raises CalledProcessError if returncode != 0
    )
    
    # Read results - fail fast if output is invalid
    with open(output_file, 'r') as f:
        blender_data = json.load(f)
    
    _process_blender_results(blender_data, result)
    logger.validation_result("Blender processing", True, "Successfully processed FBX")
    
    # Clean up
    output_file.unlink()


def _create_blender_script(input_file: Path, output_file: Path) -> str:
    """Create Blender Python script for FBX processing."""
    return f'''
import bpy
import json
import sys
from pathlib import Path

try:
    # Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    # Import FBX
    bpy.ops.import_scene.fbx(filepath="{input_file}")
    
    # Extract data
    result = {{
        "success": True,
        "blendshapes": [],
        "bones": [],
        "meshes": [],
        "materials": []
    }}
    
    # Extract blendshapes
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.data.shape_keys:
            for key_block in obj.data.shape_keys.key_blocks:
                if key_block.name != 'Basis':
                    result["blendshapes"].append({{
                        "name": key_block.name,
                        "object": obj.name,
                        "value": key_block.value
                    }})
    
    # Extract bones
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            for bone in obj.data.bones:
                result["bones"].append({{
                    "name": bone.name,
                    "armature": obj.name
                }})
    
    # Extract meshes
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            result["meshes"].append({{
                "name": obj.name,
                "vertices": len(obj.data.vertices),
                "faces": len(obj.data.polygons)
            }})
    
    # Extract materials
    for material in bpy.data.materials:
        result["materials"].append({{
            "name": material.name
        }})
    
    # Save results
    with open("{output_file}", 'w') as f:
        json.dump(result, f, indent=2)
        
except Exception as e:
    error_result = {{
        "success": False,
        "error": str(e),
        "blendshapes": [],
        "bones": [],
        "meshes": [],
        "materials": []
    }}
    
    with open("{output_file}", 'w') as f:
        json.dump(error_result, f, indent=2)
    
    sys.exit(1)
'''


def _process_blender_results(blender_data: Dict, result: FBXValidationResult):
    """Process Blender output data."""
    # Fail fast if Blender had an error
    if not blender_data.get("success", False):
        raise RuntimeError(f"Blender processing failed: {blender_data.get('error', 'Unknown error')}")
    
    # Extract blendshapes
    blendshapes = blender_data.get("blendshapes", [])
    for bs in blendshapes:
        result.found_blendshapes.append(bs["name"])
    
    # Extract bones
    bones = blender_data.get("bones", [])
    for bone in bones:
        result.found_bones.append(bone["name"])