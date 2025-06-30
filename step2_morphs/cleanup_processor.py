#!/usr/bin/env python3
"""
Cleanup Processor for Azure FBX Optimization

This module creates web-optimized FBX by keeping ONLY Azure blendshapes.
Optimizes for maximum web performance and minimal file size.

Final output will contain:
- ONLY 52 Azure blendshapes (optimal for web deployment)
- Essential bones for Azure rotations
- Collision meshes removed
- Maximum web performance optimization
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
print("🎯 WEB OPTIMIZATION MODE: Keeping ONLY Azure blendshapes")

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
    "processed_objects": [],
    "optimization_mode": "WEB_OPTIMIZED_AZURE_ONLY"
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

# Process mesh objects - KEEP ONLY AZURE BLENDSHAPES for web optimization
print("📊 WEB OPTIMIZATION - AZURE BLENDSHAPES ONLY:")
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj_stats = {{
            "name": obj.name,
            "original_morphs": 0,
            "kept_morphs": 0,
            "removed_morphs": 0,
            "optimization_status": "WEB_OPTIMIZED"
        }}

        if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
            original_count = len(obj.data.shape_keys.key_blocks) - 1  # Exclude Basis
            obj_stats["original_morphs"] = original_count
            cleanup_stats["original_morphs"] += original_count

            # Get list of shape keys to remove (keep ONLY Azure blendshapes)
            keys_to_remove = []
            azure_kept = 0

            for key_block in obj.data.shape_keys.key_blocks:
                if key_block.name != "Basis":
                    if key_block.name in azure_blendshapes:
                        azure_kept += 1
                    else:
                        keys_to_remove.append(key_block.name)

            # Remove all non-Azure morph targets for web optimization
            for key_name in reversed(keys_to_remove):
                try:
                    key_block = obj.data.shape_keys.key_blocks.get(key_name)
                    if key_block:
                        obj.shape_key_remove(key_block)
                        obj_stats["removed_morphs"] += 1
                        cleanup_stats["removed_morphs"] += 1
                except Exception as e:
                    print(f"Warning: Could not remove {{key_name}}: {{e}}")

            # Count final morphs (should be only Azure)
            final_count = len(obj.data.shape_keys.key_blocks) - 1 if obj.data.shape_keys.key_blocks else 0
            obj_stats["kept_morphs"] = final_count
            cleanup_stats["kept_morphs"] += final_count

            print(f"📦 {{obj.name}}: {{original_count}} → {{final_count}} morphs ({{azure_kept}} Azure kept)")
            print(f"   🎯 Web optimized: {{obj_stats['removed_morphs']}} excess morphs removed")
        else:
            print(f"📦 {{obj.name}}: No morph targets")

        cleanup_stats["processed_objects"].append(obj_stats)

# Process armatures for bone cleanup (conservative approach)
for obj in bpy.data.objects:
    if obj.type == 'ARMATURE':
        armature_data = obj.data
        original_bone_count = len(armature_data.bones)
        cleanup_stats["original_bones"] += original_bone_count

        print(f"🦴 {{obj.name}}: {{original_bone_count}} bones (preserving all)")

        # Keep all bones to maintain skeleton integrity
        cleanup_stats["kept_bones"] += original_bone_count

print(f"")
print(f"📊 WEB OPTIMIZATION SUMMARY:")
print(f"   🎭 Morph Targets: {{cleanup_stats['original_morphs']}} → {{cleanup_stats['kept_morphs']}} (removed {{cleanup_stats['removed_morphs']}})")
print(f"   🗑️  Collision Meshes: {{cleanup_stats['collision_meshes_found']}} found, {{cleanup_stats['collision_meshes_removed']}} removed")
print(f"   🦴 Bones: {{cleanup_stats['original_bones']}} (preserved all for skeleton integrity)")
print(f"   📦 Objects processed: {{len(cleanup_stats['processed_objects'])}}")
print(f"   ✅ Optimization Mode: {{cleanup_stats['optimization_mode']}}")
print(f"   🎯 File size reduction expected: ~{{(cleanup_stats['removed_morphs']/cleanup_stats['original_morphs']*100):.1f}}%")

# Export cleaned FBX
print(f"💾 Exporting web-optimized FBX...")
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

print("✅ Web-optimized Azure FBX cleanup completed!")
print("🎉 Maximum web performance achieved - ONLY Azure blendshapes retained!")

# Save cleanup report
cleanup_report_path = r"{output_fbx.with_suffix('.cleanup_report.json')}"
with open(cleanup_report_path, "w") as f:
    json.dump(cleanup_stats, f, indent=2)

print(f"📄 Cleanup report saved: {{cleanup_report_path}}")
"""


def cleanup_azure_fbx(input_fbx: Path, output_fbx: Path) -> Dict[str, Any]:
    """
    Clean up FBX file for web optimization by keeping ONLY Azure blendshapes.

    Removes:
    - All non-Azure morph targets (771 excess morphs)
    - Collision meshes (UCX_, UBX_, USP_ prefixes)

    Preserves:
    - ONLY 52 Azure blendshapes for maximum web performance
    - All bones for skeleton integrity
    - All essential mesh geometry

    Returns cleanup statistics and results.
    """

    print("🧹 Starting Azure FBX Cleanup Process...")
    print("🎯 WEB OPTIMIZATION MODE: Azure blendshapes only")
    print("=" * 50)
    print(f"📁 Input:  {input_fbx}")
    print(f"📁 Output: {output_fbx}")
    print()

    # Create essential bones list (for reporting only, not removal)
    essential_bones = list(AZURE_ROTATIONS)

    # Create and run Blender cleanup script
    blender_script = create_azure_cleanup_script(
        input_fbx, output_fbx, list(AZURE_BLENDSHAPES), essential_bones
    )

    script_file = output_fbx.with_suffix('.cleanup_script.py')
    try:
        with open(script_file, 'w') as f:
            f.write(blender_script)

        # Run Blender with the script
        result = subprocess.run([
            'blender', '--background', '--python', str(script_file)
        ], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"Blender cleanup failed: {result.stderr}")

        print("✅ Blender cleanup completed successfully")

        # Load and return cleanup report
        report_file = output_fbx.with_suffix('.cleanup_report.json')
        if report_file.exists():
            with open(report_file, 'r') as f:
                cleanup_stats = json.load(f)
            print("📊 Cleanup statistics loaded from report")

            # Clean up temporary files
            script_file.unlink(missing_ok=True)
            report_file.unlink(missing_ok=True)

            return cleanup_stats
        else:
            raise RuntimeError("Cleanup report not found")

    except Exception as e:
        # Clean up on failure
        script_file.unlink(missing_ok=True)
        raise RuntimeError(f"FBX cleanup failed: {e}")

    finally:
        # Ensure cleanup of temporary files
        script_file.unlink(missing_ok=True)


if __name__ == "__main__":
    # Test cleanup with current files
    input_fbx = Path("output-step2-azure.fbx")
    output_fbx = Path("output-step2-azure-clean.fbx")

    if input_fbx.exists():
        results = cleanup_azure_fbx(input_fbx, output_fbx)
        print(json.dumps(results, indent=2))
    else:
        print("❌ Input file not found. Run azure_processor.py first.")
