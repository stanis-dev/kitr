#!/usr/bin/env python3
"""
Cleanup Processor for Azure FBX Optimization

This module removes excess morph targets and unnecessary bones from the FBX file,
keeping only the 52 Azure blendshapes and essential skeleton structure.

Final output will contain:
- ONLY 52 Azure blendshapes (no excess morphs)
- Essential bones for Azure rotations
- Cleaned up, optimized file size
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS


def create_azure_cleanup_script(input_fbx: Path, output_fbx: Path, azure_blendshapes: List[str], essential_bones: List[str]) -> str:
    """Create Blender script for cleaning up the FBX file."""

    azure_blendshapes_str = json.dumps(azure_blendshapes)
    essential_bones_str = json.dumps(essential_bones)

    return f"""
import bpy
import json

input_fbx = r"{input_fbx}"
output_fbx = r"{output_fbx}"
azure_blendshapes = {azure_blendshapes_str}
essential_bones = {essential_bones_str}

print("🧹 Starting Azure FBX Cleanup...")

# Clear scene and import FBX
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=input_fbx)

cleanup_stats = {{
    "original_morphs": 0,
    "removed_morphs": 0,
    "kept_morphs": 0,
    "original_bones": 0,
    "removed_bones": 0,
    "kept_bones": 0,
    "collision_meshes_found": 0,
    "collision_meshes_removed": 0,
    "processed_objects": []
}}

# First, identify and remove collision meshes
collision_meshes_to_remove = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        # Check for collision mesh patterns (UCX, UBX, USP prefixes from Unreal Engine)
        if obj.name.startswith(('UCX_', 'UBX_', 'USP_')) or 'collision' in obj.name.lower():
            collision_meshes_to_remove.append(obj)
            cleanup_stats["collision_meshes_found"] += 1
            print(f"🔍 Found collision mesh: {{obj.name}}")

# Remove collision meshes
for obj in collision_meshes_to_remove:
    print(f"🗑️  Removing collision mesh: {{obj.name}}")
    bpy.data.objects.remove(obj, do_unlink=True)
    cleanup_stats["collision_meshes_removed"] += 1

print(f"✅ Collision mesh cleanup: {{cleanup_stats['collision_meshes_removed']}} removed")
print()

# Process remaining mesh objects for morph target cleanup
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        obj_stats = {{
            "name": obj.name,
            "original_morphs": 0,
            "kept_morphs": 0,
            "removed_morphs": 0
        }}

        shape_keys = obj.data.shape_keys
        if shape_keys and shape_keys.key_blocks:
            original_count = len(shape_keys.key_blocks) - 1  # Exclude Basis
            obj_stats["original_morphs"] = original_count
            cleanup_stats["original_morphs"] += original_count

            # Get list of shape keys to remove (reverse order for safe removal)
            keys_to_remove = []
            for i, key_block in enumerate(shape_keys.key_blocks):
                if key_block.name != "Basis" and key_block.name not in azure_blendshapes:
                    keys_to_remove.append(key_block.name)

            # Remove excess morph targets
            for key_name in reversed(keys_to_remove):
                try:
                    key_block = shape_keys.key_blocks.get(key_name)
                    if key_block:
                        obj.shape_key_remove(key_block)
                        obj_stats["removed_morphs"] += 1
                        cleanup_stats["removed_morphs"] += 1
                except Exception as e:
                    print(f"Warning: Could not remove {{key_name}}: {{e}}")

            # Count remaining morphs
            final_count = len(shape_keys.key_blocks) - 1 if shape_keys.key_blocks else 0
            obj_stats["kept_morphs"] = final_count
            cleanup_stats["kept_morphs"] += final_count

            print(f"📦 {{obj.name}}: {{original_count}} → {{final_count}} morphs")

        cleanup_stats["processed_objects"].append(obj_stats)

# Process armatures for bone cleanup (conservative approach)
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature_data = obj.data
        original_bone_count = len(armature_data.bones)
        cleanup_stats["original_bones"] += original_bone_count

        print(f"🦴 {{obj.name}}: {{original_bone_count}} bones (keeping essential structure)")

        # For now, keep all bones to maintain skeleton integrity
        # In the future, we could remove non-essential bones safely
        cleanup_stats["kept_bones"] += original_bone_count

print(f"")
print(f"📊 CLEANUP SUMMARY:")
print(f"   Morph Targets: {{cleanup_stats['original_morphs']}} → {{cleanup_stats['kept_morphs']}} (removed {{cleanup_stats['removed_morphs']}})")
print(f"   Collision Meshes: {{cleanup_stats['collision_meshes_found']}} found, {{cleanup_stats['collision_meshes_removed']}} removed")
print(f"   Bones: {{cleanup_stats['original_bones']}} (kept all for skeleton integrity)")
print(f"   Objects processed: {{len(cleanup_stats['processed_objects'])}}")

# Export cleaned FBX
print(f"💾 Exporting cleaned FBX...")
bpy.ops.export_scene.fbx(
    filepath=output_fbx,
    check_existing=False,
    use_selection=False,
    use_active_collection=False,
    global_scale=1.0,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_NONE',
    use_space_transform=True,
    bake_space_transform=False,
    object_types={{'ARMATURE', 'MESH'}},
    use_mesh_modifiers=True,
    use_mesh_modifiers_render=True,
    mesh_smooth_type='OFF',
    use_subsurf=False,
    use_mesh_edges=False,
    use_tspace=False,
    use_custom_props=False,
    add_leaf_bones=True,
    primary_bone_axis='Y',
    secondary_bone_axis='X',
    armature_nodetype='NULL',
    bake_anim=False,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=1.0,
    path_mode='AUTO',
    embed_textures=False,
    batch_mode='OFF',
    use_batch_own_dir=True,
    use_metadata=True
)

print("✅ Azure FBX cleanup completed!")

# Save cleanup report
cleanup_report_path = r"{output_fbx.with_suffix('.cleanup_report.json')}"
with open(cleanup_report_path, "w") as f:
    json.dump(cleanup_stats, f, indent=2)

print(f"📄 Cleanup report saved: {{cleanup_report_path}}")
"""


def cleanup_azure_fbx(input_fbx: Path, output_fbx: Path) -> Dict[str, Any]:
    """
    Clean up FBX file to contain only Azure-required content.

    Removes:
    - All morph targets except the 52 Azure blendshapes
    - Unnecessary bones (conservative approach)

    Returns cleanup statistics and results.
    """

    print("🧹 Starting Azure FBX Cleanup Process...")
    print("=" * 50)
    print(f"📁 Input:  {input_fbx}")
    print(f"📁 Output: {output_fbx}")
    print()

    # Essential bones for Azure rotations (from our bone analysis)
    essential_bones = [
        "head",  # For headRoll
        "FACIAL_L_12IPV_EyeCornerO1",  # For leftEyeRoll
        "FACIAL_R_12IPV_EyeCornerO1",  # For rightEyeRoll (if exists)
        # Keep spine and essential facial bones
        "spine", "neck", "skull", "jaw"
    ]

    # Create Blender cleanup script
    blender_script = create_azure_cleanup_script(input_fbx, output_fbx, AZURE_BLENDSHAPES, essential_bones)

    # Run Blender cleanup
    try:
        subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
            check=True,
        )

        print("✅ Blender cleanup completed successfully")

        # Check if cleanup report was generated
        cleanup_report_file = output_fbx.with_suffix('.cleanup_report.json')
        cleanup_stats = {}

        if cleanup_report_file.exists():
            with open(cleanup_report_file, 'r') as f:
                cleanup_stats = json.load(f)
            print(f"📊 Cleanup statistics loaded from report")
        else:
            print("⚠️  Cleanup report not found, using default stats")
            cleanup_stats = {
                "original_morphs": "unknown",
                "removed_morphs": "unknown",
                "kept_morphs": "unknown",
                "message": "Cleanup completed but statistics unavailable"
            }

    except subprocess.TimeoutExpired:
        print("❌ Blender cleanup timed out after 5 minutes")
        raise RuntimeError("Cleanup process timed out")
    except subprocess.CalledProcessError as e:
        print(f"❌ Blender cleanup failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        raise RuntimeError(f"Cleanup process failed: {e.stderr}")
    except Exception as e:
        print(f"❌ Unexpected error during cleanup: {e}")
        raise

    # Verify output file was created
    if not output_fbx.exists():
        raise RuntimeError(f"Cleanup failed: Output file not created at {output_fbx}")

    # Calculate file size reduction
    input_size_mb = round(input_fbx.stat().st_size / (1024*1024), 1)
    output_size_mb = round(output_fbx.stat().st_size / (1024*1024), 1)
    size_reduction_mb = input_size_mb - output_size_mb
    size_reduction_percent = (size_reduction_mb / input_size_mb) * 100 if input_size_mb > 0 else 0

    print(f"📦 File size: {input_size_mb} MB → {output_size_mb} MB")
    print(f"📉 Size reduction: {size_reduction_mb:.1f} MB ({size_reduction_percent:.1f}%)")

    # Compile results
    results = {
        "cleanup_successful": True,
        "input_file": str(input_fbx),
        "output_file": str(output_fbx),
        "input_size_mb": input_size_mb,
        "output_size_mb": output_size_mb,
        "size_reduction_mb": size_reduction_mb,
        "size_reduction_percent": size_reduction_percent,
        "cleanup_stats": cleanup_stats,
        "azure_blendshapes_target": len(AZURE_BLENDSHAPES),
        "azure_rotations_target": len(AZURE_ROTATIONS)
    }

    return results


if __name__ == "__main__":
    # Test cleanup with current files
    input_fbx = Path("output-step2-azure.fbx")
    output_fbx = Path("output-step2-azure-clean.fbx")

    if input_fbx.exists():
        results = cleanup_azure_fbx(input_fbx, output_fbx)
        print(json.dumps(results, indent=2))
    else:
        print("❌ Input file not found. Run azure_processor.py first.")
