#!/usr/bin/env python3
"""
FBX bone processor for Azure rotation parameters.
Analyzes and validates bone structure for Azure compatibility.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Direct imports from docs package for better type inference
from docs import ROTATION_PARAMETERS

# Backwards compatibility
AZURE_ROTATIONS = ROTATION_PARAMETERS


def extract_bone_structure(input_fbx: Path) -> Dict[str, Any]:
    """
    Extract complete bone structure from FBX file using Blender.

    Args:
        input_fbx: Path to input FBX file

    Returns:
        Dictionary containing bone structure data
    """
    output_json = input_fbx.with_suffix(".bones.json")

    # Required bone patterns for Azure rotations
    required_bones_list = [
        "head", "Head", "HeadBone", "skull", "Skull",
        "FACIAL_L_Eye", "leftEye", "LeftEye", "left_eye", "L_Eye", "EyeL",
        "FACIAL_R_Eye", "rightEye", "RightEye", "right_eye", "R_Eye", "EyeR"
    ]

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

    # Run Blender processing
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

    Args:
        bone_data: Bone structure data from extract_bone_structure()

    Returns:
        Dictionary containing verification results and bone mapping suggestions
    """
    verification: Dict[str, Any] = {
        "head_bones_found": [],
        "left_eye_bones_found": [],
        "right_eye_bones_found": [],
        "suggested_mapping": {},
        "missing_bones": [],
        "verification_passed": False
    }

    all_bones = bone_data.get("bones", [])

    # Analyze found bones for head - broader search patterns
    head_candidates = []
    head_patterns = ["head", "Head", "HeadBone", "skull", "Skull"]
    for bone_name in all_bones:
        for pattern in head_patterns:
            if pattern.lower() in bone_name.lower():
                head_candidates.append(bone_name)
                break
    verification["head_bones_found"] = list(set(head_candidates))

    # Analyze found bones for left eye - improved patterns for MetaHuman
    left_eye_candidates = []
    left_eye_patterns = [
        "FACIAL_L_Eye",  # MetaHuman standard
        "leftEye", "LeftEye", "left_eye", "L_Eye", "EyeL",
        "eye_L", "Eye_L", "LeftEyeBone", "EyeBone_L"
    ]
    for bone_name in all_bones:
        for pattern in left_eye_patterns:
            if pattern in bone_name:  # Exact match for FACIAL_L_Eye
                left_eye_candidates.append(bone_name)
                break
    verification["left_eye_bones_found"] = list(set(left_eye_candidates))

    # Analyze found bones for right eye - improved patterns for MetaHuman
    right_eye_candidates = []
    right_eye_patterns = [
        "FACIAL_R_Eye",  # MetaHuman standard
        "rightEye", "RightEye", "right_eye", "R_Eye", "EyeR",
        "eye_R", "Eye_R", "RightEyeBone", "EyeBone_R"
    ]
    for bone_name in all_bones:
        for pattern in right_eye_patterns:
            if pattern in bone_name:  # Exact match for FACIAL_R_Eye
                right_eye_candidates.append(bone_name)
                break
    verification["right_eye_bones_found"] = list(set(right_eye_candidates))

    # Create suggested mapping for Azure rotations
    if verification["head_bones_found"]:
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

    # Overall verification - ALL 3 rotations must be available
    verification["verification_passed"] = len(verification["missing_bones"]) == 0
    verification["rotations_available"] = len(verification["suggested_mapping"])
    verification["all_rotations_found"] = verification["rotations_available"] == 3

    return verification


def process_azure_bones(input_fbx: Path, output_fbx: Path) -> Dict[str, Any]:
    """
    Process and verify bones for Azure rotation compatibility.

    Args:
        input_fbx: Path to input FBX file
        output_fbx: Path to output FBX file

    Returns:
        Dictionary containing bone processing results and Azure verification
    """
    print("🔍 Processing bones for Azure rotations...")

    # Extract bone structure
    bone_data = extract_bone_structure(input_fbx)

    # Verify Azure rotation requirements
    verification = verify_azure_rotation_bones(bone_data)

    # If input and output are different, copy the file (bone structure preserved)
    if input_fbx != output_fbx:
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
    input_fbx = Path("azure_optimized.fbx")
    if input_fbx.exists():
        results = process_azure_bones(input_fbx, input_fbx)
        print(json.dumps(results, indent=2))
    else:
        print("❌ Output file not found. Run azure_processor.py first.")
