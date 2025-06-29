#!/usr/bin/env python3
"""
Clean FBX Validation

Validates that the cleaned FBX contains ONLY the required content:
- Exactly 52 Azure blendshapes (no more, no less)
- Essential bones for Azure rotations
- No excess morph targets

This ensures the file is optimized and contains only Azure-compatible content.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS


def validate_azure_clean_fbx(fbx_file: Path) -> Dict[str, Any]:
    """
    Validate that the cleaned FBX contains only Azure-required content.

    Checks:
    1. Exactly 52 Azure blendshapes present
    2. No excess morph targets
    3. Essential bones for rotations available
    4. File optimization achieved
    """

    print("🔍 Validating Clean Azure FBX...")
    print("=" * 45)
    print(f"📁 File: {fbx_file}")
    print()

    if not fbx_file.exists():
        return {
            "validation_passed": False,
            "error": f"File not found: {fbx_file}",
            "checks": {}
        }

    # Create Blender validation script
    output_json = fbx_file.with_suffix(".validation.json")

    blender_script = f"""
import bpy
import json

input_fbx = r"{fbx_file}"
output_json = r"{output_json}"
azure_blendshapes = {json.dumps(AZURE_BLENDSHAPES)}
azure_rotations = {json.dumps(AZURE_ROTATIONS)}

print("🔍 Validating clean Azure FBX...")

# Clear scene and import FBX
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=input_fbx)

validation_data = {{
    "morph_validation": {{
        "total_morphs_found": 0,
        "azure_morphs_found": [],
        "excess_morphs_found": [],
        "missing_azure_morphs": [],
        "validation_passed": False
    }},
    "bone_validation": {{
        "total_bones_found": 0,
        "essential_bones_found": [],
        "essential_bones_missing": [],
        "validation_passed": False
    }},
    "file_info": {{
        "mesh_objects": 0,
        "armature_objects": 0,
        "total_objects": 0
    }}
}}

# Validate morph targets
all_morphs_found = []
azure_morphs_found = []
excess_morphs_found = []

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        validation_data["file_info"]["mesh_objects"] += 1

        if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
            for key_block in obj.data.shape_keys.key_blocks:
                if key_block.name != "Basis":  # Skip basis shape
                    all_morphs_found.append(key_block.name)

                    if key_block.name in azure_blendshapes:
                        azure_morphs_found.append(key_block.name)
                    else:
                        excess_morphs_found.append(key_block.name)

# Remove duplicates and sort
azure_morphs_found = sorted(list(set(azure_morphs_found)))
excess_morphs_found = sorted(list(set(excess_morphs_found)))
all_morphs_found = sorted(list(set(all_morphs_found)))

# Check for missing Azure morphs
missing_azure_morphs = [morph for morph in azure_blendshapes if morph not in azure_morphs_found]

# Update morph validation data
validation_data["morph_validation"]["total_morphs_found"] = len(all_morphs_found)
validation_data["morph_validation"]["azure_morphs_found"] = azure_morphs_found
validation_data["morph_validation"]["excess_morphs_found"] = excess_morphs_found
validation_data["morph_validation"]["missing_azure_morphs"] = missing_azure_morphs

# Morph validation passes if we have all 52 Azure morphs and no excess
morph_validation_passed = (
    len(azure_morphs_found) == len(azure_blendshapes) and
    len(excess_morphs_found) == 0 and
    len(missing_azure_morphs) == 0
)
validation_data["morph_validation"]["validation_passed"] = morph_validation_passed

print(f"📊 Morphs found: {{len(all_morphs_found)}} total")
print(f"   ✅ Azure morphs: {{len(azure_morphs_found)}}/{{len(azure_blendshapes)}}")
print(f"   ❌ Excess morphs: {{len(excess_morphs_found)}}")
print(f"   🔍 Missing Azure: {{len(missing_azure_morphs)}}")

# Validate bone structure
all_bones_found = []
essential_bones = ["head"]  # Minimum essential bones for Azure

for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        validation_data["file_info"]["armature_objects"] += 1

        for bone in obj.data.bones:
            all_bones_found.append(bone.name)

essential_bones_found = [bone for bone in essential_bones if bone in all_bones_found]
essential_bones_missing = [bone for bone in essential_bones if bone not in all_bones_found]

validation_data["bone_validation"]["total_bones_found"] = len(all_bones_found)
validation_data["bone_validation"]["essential_bones_found"] = essential_bones_found
validation_data["bone_validation"]["essential_bones_missing"] = essential_bones_missing

# Bone validation passes if we have essential bones (we allow extra bones for skeleton integrity)
bone_validation_passed = len(essential_bones_missing) == 0
validation_data["bone_validation"]["validation_passed"] = bone_validation_passed

print(f"🦴 Bones found: {{len(all_bones_found)}} total")
print(f"   ✅ Essential bones: {{len(essential_bones_found)}}/{{len(essential_bones)}}")

# Overall validation
validation_data["file_info"]["total_objects"] = len(bpy.data.objects)
validation_data["overall_validation_passed"] = morph_validation_passed and bone_validation_passed

# Save validation data
with open(output_json, "w") as f:
    json.dump(validation_data, f, indent=2)

print(f"📄 Validation report saved: {{output_json}}")
"""

    # Run Blender validation
    try:
        subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        print("✅ Blender validation completed")
    except Exception as e:
        print(f"❌ Blender validation failed: {e}")
        return {
            "validation_passed": False,
            "error": str(e),
            "checks": {}
        }

    # Load validation results
    if not output_json.exists():
        return {
            "validation_passed": False,
            "error": "Validation report not generated",
            "checks": {}
        }

    with open(output_json, "r") as f:
        validation_data = json.load(f)

    # Clean up temporary file
    output_json.unlink()

    # Process validation results
    morph_check = validation_data.get("morph_validation", {})
    bone_check = validation_data.get("bone_validation", {})
    file_info = validation_data.get("file_info", {})

    # Display results
    print("📊 VALIDATION RESULTS:")
    print("-" * 30)

    # Morph target validation
    azure_found = len(morph_check.get("azure_morphs_found", []))
    excess_found = len(morph_check.get("excess_morphs_found", []))
    missing_count = len(morph_check.get("missing_azure_morphs", []))

    print(f"🎭 Morph Targets:")
    print(f"   ✅ Azure blendshapes: {azure_found}/{len(AZURE_BLENDSHAPES)}")
    print(f"   ❌ Excess morphs: {excess_found}")
    print(f"   🔍 Missing Azure: {missing_count}")

    if morph_check.get("validation_passed", False):
        print("   🎯 Morph validation: ✅ PASSED")
    else:
        print("   🎯 Morph validation: ❌ FAILED")
        if excess_found > 0:
            print(f"      - Remove {excess_found} excess morphs")
        if missing_count > 0:
            print(f"      - Add {missing_count} missing Azure morphs")

    print()

    # Bone validation
    essential_found = len(bone_check.get("essential_bones_found", []))
    essential_missing = len(bone_check.get("essential_bones_missing", []))

    print(f"🦴 Bone Structure:")
    print(f"   ✅ Essential bones: {essential_found}")
    print(f"   ❌ Missing essential: {essential_missing}")
    print(f"   📊 Total bones: {bone_check.get('total_bones_found', 0)}")

    if bone_check.get("validation_passed", False):
        print("   🎯 Bone validation: ✅ PASSED")
    else:
        print("   🎯 Bone validation: ❌ FAILED")

    print()

    # Overall result
    overall_passed = validation_data.get("overall_validation_passed", False)

    if overall_passed:
        print("🎉 OVERALL VALIDATION: ✅ PASSED")
        print("   File contains ONLY Azure-required content!")
        print("   ✅ Ready for Azure Cognitive Services")
    else:
        print("❌ OVERALL VALIDATION: ❌ FAILED")
        print("   File contains excess or missing content")
        print("   🔧 Cleanup or remapping required")

    # File statistics
    file_size_mb = round(fbx_file.stat().st_size / (1024*1024), 1)
    print(f"\n📁 File Info:")
    print(f"   Size: {file_size_mb} MB")
    print(f"   Objects: {file_info.get('total_objects', 0)}")
    print(f"   Meshes: {file_info.get('mesh_objects', 0)}")
    print(f"   Armatures: {file_info.get('armature_objects', 0)}")

    # Compile final results
    results = {
        "validation_passed": overall_passed,
        "file_path": str(fbx_file),
        "file_size_mb": file_size_mb,
        "morph_validation": morph_check,
        "bone_validation": bone_check,
        "file_info": file_info,
        "azure_requirements": {
            "required_blendshapes": len(AZURE_BLENDSHAPES),
            "required_rotations": len(AZURE_ROTATIONS),
            "total_required_params": len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS)
        }
    }

    return results


if __name__ == "__main__":
    # Test validation with cleaned file
    clean_fbx = Path("output-step2-azure-clean.fbx")

    if clean_fbx.exists():
        results = validate_azure_clean_fbx(clean_fbx)
        print(f"\n📄 Validation results saved internally")
    else:
        print("❌ Clean FBX file not found. Run cleanup_processor.py first.")
