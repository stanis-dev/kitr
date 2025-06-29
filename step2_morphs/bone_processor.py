#!/usr/bin/env python3
"""
Bone Processor for Azure Rotation Parameters

This module handles the skeleton/bone structure needed for Azure's 3 rotation parameters:
- headRoll (head tilt rotation)
- leftEyeRoll (left eye rotation)
- rightEyeRoll (right eye rotation)
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step1_validation.constants import REQUIRED_BONES, AZURE_ROTATIONS
from step1_validation.logging_config import logger


def extract_bone_structure(input_fbx: Path) -> Dict[str, Any]:
    """
    Extract bone/armature structure from FBX using Blender.
    Returns information about bones, their hierarchy, and naming.
    """
    output_json = input_fbx.with_suffix(".bones.json")

    # Prepare required bones list for Blender script
    required_bones_list = json.dumps(REQUIRED_BONES)

    blender_script = f"""
import bpy
import json
from mathutils import Vector, Euler

input_fbx = r"{input_fbx}"
output_json = r"{output_json}"

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import FBX
bpy.ops.import_scene.fbx(filepath=input_fbx)

bone_data = {{
    "armatures": [],
    "bones": [],
    "bone_hierarchy": {{}},
    "required_bones_found": {{}},
    "bone_name_mapping": {{}}
}}

# Process all armatures
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature_info = {{
            "name": obj.name,
            "bones": [],
            "pose_bones": []
        }}

        # Get edit bones (structure)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')

        for bone in obj.data.edit_bones:
            bone_info = {{
                "name": bone.name,
                "head": list(bone.head),
                "tail": list(bone.tail),
                "parent": bone.parent.name if bone.parent else None,
                "children": [child.name for child in bone.children]
            }}
            armature_info["bones"].append(bone_info)
            bone_data["bones"].append(bone.name)

            # Check for parent-child relationships
            if bone.parent:
                parent_name = bone.parent.name
                if parent_name not in bone_data["bone_hierarchy"]:
                    bone_data["bone_hierarchy"][parent_name] = []
                bone_data["bone_hierarchy"][parent_name].append(bone.name)

        bpy.ops.object.mode_set(mode='OBJECT')
        bone_data["armatures"].append(armature_info)

# Check for required bones (head and eye bones for Azure rotations)
required_bone_patterns = {required_bones_list}
for pattern in required_bone_patterns:
    bone_data["required_bones_found"][pattern] = []
    for bone_name in bone_data["bones"]:
        if pattern.lower() in bone_name.lower():
            bone_data["required_bones_found"][pattern].append(bone_name)

# Save bone structure data
with open(output_json, "w") as f:
    json.dump(bone_data, f, indent=2)
"""

    # Run Blender
    try:
        subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        print("✅ Bone extraction completed")
    except Exception as e:
        print(f"❌ Bone extraction failed: {e}")
        raise

    # Read bone data
    if not output_json.exists():
        raise RuntimeError(f"Blender did not produce bone data: {output_json}")

    with open(output_json, "r") as f:
        bone_data = json.load(f)

    output_json.unlink()  # Clean up temporary file
    return bone_data


def verify_azure_rotation_bones(bone_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify that the required bones for Azure rotations are present.
    Returns verification results and suggestions for bone mapping.
    """
    verification: Dict[str, Any] = {
        "head_bones_found": [],
        "left_eye_bones_found": [],
        "right_eye_bones_found": [],
        "suggested_mapping": {},
        "missing_bones": [],
        "verification_passed": False
    }

    required_found = bone_data.get("required_bones_found", {})

    # Analyze found bones for head
    head_candidates = []
    for pattern in ["head", "Head", "HeadBone"]:
        if pattern in required_found:
            head_candidates.extend(required_found[pattern])
    verification["head_bones_found"] = list(set(head_candidates))

    # Analyze found bones for left eye
    left_eye_candidates = []
    for pattern in ["leftEye", "LeftEye", "left_eye"]:
        if pattern in required_found:
            left_eye_candidates.extend(required_found[pattern])
    verification["left_eye_bones_found"] = list(set(left_eye_candidates))

    # Analyze found bones for right eye
    right_eye_candidates = []
    for pattern in ["rightEye", "RightEye", "right_eye"]:
        if pattern in required_found:
            right_eye_candidates.extend(required_found[pattern])
    verification["right_eye_bones_found"] = list(set(right_eye_candidates))

    # Create suggested mapping for Azure rotations
    if verification["head_bones_found"]:
        # Use the first/best head bone candidate
        verification["suggested_mapping"]["headRoll"] = verification["head_bones_found"][0]
    else:
        verification["missing_bones"].append("head bone for headRoll")

    if verification["left_eye_bones_found"]:
        verification["suggested_mapping"]["leftEyeRoll"] = verification["left_eye_bones_found"][0]
    else:
        verification["missing_bones"].append("left eye bone for leftEyeRoll")

    if verification["right_eye_bones_found"]:
        verification["suggested_mapping"]["rightEyeRoll"] = verification["right_eye_bones_found"][0]
    else:
        verification["missing_bones"].append("right eye bone for rightEyeRoll")

    # Overall verification
    verification["verification_passed"] = len(verification["missing_bones"]) == 0

    return verification


def process_azure_bones(input_fbx: Path, output_fbx: Path) -> Dict[str, Any]:
    """
    Process and verify bones for Azure rotation compatibility.
    Ensures the output FBX has properly identified bones for the 3 Azure rotations.
    """
    print("🔍 Processing bones for Azure rotations...")

    # Extract bone structure
    bone_data = extract_bone_structure(input_fbx)

    # Verify Azure rotation requirements
    verification = verify_azure_rotation_bones(bone_data)

    # If input and output are different, we need to process the FBX
    if input_fbx != output_fbx:
        # For now, just copy the file since we're not modifying bone structure
        # In future iterations, we might rename bones here
        import shutil
        if output_fbx.exists():
            print("⚠️  Output FBX already exists, using existing file")
        else:
            shutil.copy2(input_fbx, output_fbx)
            print("✅ Copied FBX with bone structure preserved")

    # Combine results
    results = {
        "bone_data": bone_data,
        "azure_verification": verification,
        "azure_rotations": AZURE_ROTATIONS,
        "total_bones_found": len(bone_data.get("bones", [])),
        "total_armatures": len(bone_data.get("armatures", [])),
    }

    return results


if __name__ == "__main__":
    # Test with current output file
    input_fbx = Path("output-step2-azure.fbx")
    if input_fbx.exists():
        results = process_azure_bones(input_fbx, input_fbx)
        print(json.dumps(results, indent=2))
    else:
        print("❌ output-step2-azure.fbx not found. Run step2_morphs.py first.")
