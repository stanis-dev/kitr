"""
Azure Blendshape Processing Module.

Handles mapping and renaming of MetaHuman morph targets to Azure blendshapes.
Preserves ALL original morph target managers and ARKit blendshapes completely.
"""

import subprocess
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Direct imports from docs package for better type inference
from docs import FACIAL_BLENDSHAPES, METAHUMAN_NAME_MAPPINGS

# Backwards compatibility
AZURE_BLENDSHAPES = FACIAL_BLENDSHAPES

from step1_validation.logging_config import logger


def extract_all_blendshapes(input_fbx: Path) -> list[str]:
    """
    Extract all blendshape (shape key) names from the input FBX using Blender.

    Args:
        input_fbx: Path to input FBX file

    Returns:
        List of all blendshape names found in the FBX
    """
    output_json = input_fbx.with_suffix(".blendshapes.json")
    blender_script = f"""
import bpy
import json
from pathlib import Path
input_fbx = r"{input_fbx}"
output_json = r"{output_json}"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=input_fbx)
all_blendshapes = set()
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        for kb in obj.data.shape_keys.key_blocks:
            if kb.name != 'Basis':
                all_blendshapes.add(kb.name)
with open(output_json, "w") as f:
    json.dump(sorted(list(all_blendshapes)), f)
"""
    subprocess.run(
        ["blender", "--background", "--python-expr", blender_script],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    with open(output_json, "r") as f:
        names = json.load(f)
    output_json.unlink()
    return names


def process_azure_blendshapes(input_fbx: Path, output_fbx: Path) -> dict[str, Any]:
    """
    Process MetaHuman FBX to preserve ALL original morph target managers.
    Only ensures Azure blendshape naming compatibility without removing anything.

    Args:
        input_fbx: Path to input MetaHuman FBX file
        output_fbx: Path to output Azure-compatible FBX file

    Returns:
        Dictionary containing mapping results and statistics
    """
    azure_blendshapes = list(AZURE_BLENDSHAPES)
    mapping_json = output_fbx.with_suffix(".mapping.json")

    blender_script = f"""
import bpy
import json
from pathlib import Path

input_fbx = r"{input_fbx}"
output_fbx = r"{output_fbx}"
mapping_json = r"{mapping_json}"

# Azure blendshapes and MetaHuman mappings
AZURE_BLENDSHAPES = {json.dumps(azure_blendshapes)}
METAHUMAN_NAME_MAPPINGS = {json.dumps(METAHUMAN_NAME_MAPPINGS)}

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import FBX
bpy.ops.import_scene.fbx(filepath=input_fbx)

print("=== ORIGINAL FBX MORPH TARGET ANALYSIS ===")

# Analyze ALL meshes and their morph targets
original_managers = 0
original_morphs = 0
mesh_breakdown = {{}}
all_morph_names = set()

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mesh_name = obj.name
        morph_count = 0
        morph_names = []

        if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
            morph_count = len(obj.data.shape_keys.key_blocks) - 1  # Exclude Basis
            if morph_count > 0:
                morph_names = [kb.name for kb in obj.data.shape_keys.key_blocks if kb.name != "Basis"]
                for name in morph_names:
                    all_morph_names.add(name)

        print(f"📦 {{mesh_name}}: {{morph_count}} morph targets")
        if morph_count > 0:
            original_managers += 1
            original_morphs += morph_count
            mesh_breakdown[mesh_name] = morph_count
            print(f"   Sample morphs: {{', '.join(morph_names[:5])}}{{('...' if len(morph_names) > 5 else '')}}")

print(f"\\n📊 ORIGINAL STRUCTURE:")
print(f"   Morph target managers: {{original_managers}}")
print(f"   Total morph targets: {{original_morphs}}")
print(f"   Unique morph names: {{len(all_morph_names)}}")

# Process Azure naming compatibility without removing anything
found_azure = set()
renamed = []

print(f"\\n=== AZURE NAMING COMPATIBILITY ===")

for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        key_blocks = obj.data.shape_keys.key_blocks
        obj_renames = 0

        # Build a name->block map for this mesh
        name_map = {{kb.name: kb for kb in key_blocks}}

        # Check for Azure blendshapes that need renaming
        for az_name in AZURE_BLENDSHAPES:
            # If exact match exists, mark as found
            if az_name in name_map:
                found_azure.add(az_name)
                continue

            # Check for MetaHuman variant that needs renaming
            for meta_name, canonical in METAHUMAN_NAME_MAPPINGS.items():
                if canonical == az_name and meta_name in name_map:
                    # Rename MetaHuman variant to Azure standard
                    key_blocks[meta_name].name = az_name
                    found_azure.add(az_name)
                    renamed.append((meta_name, az_name, obj.name))
                    obj_renames += 1
                    break

        if obj_renames > 0:
            print(f"   {{obj.name}}: {{obj_renames}} morphs renamed for Azure compatibility")

print(f"\\nAzure compatibility results:")
print(f"   ✅ Azure blendshapes found/mapped: {{len(found_azure)}}/{{len(AZURE_BLENDSHAPES)}}")
print(f"   🔄 Total renames performed: {{len(renamed)}}")

# Final count after processing
final_managers = 0
final_morphs = 0
final_breakdown = {{}}

for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        morph_count = len(obj.data.shape_keys.key_blocks) - 1
        if morph_count > 0:
            final_managers += 1
            final_morphs += morph_count
            final_breakdown[obj.name] = morph_count

print(f"\\n📊 FINAL STRUCTURE (PRESERVED):")
print(f"   Morph target managers: {{final_managers}}")
print(f"   Total morph targets: {{final_morphs}}")
print(f"   Mesh breakdown: {{final_breakdown}}")

# Verify preservation
if final_managers != original_managers:
    print(f"⚠️  WARNING: Manager count changed from {{original_managers}} to {{final_managers}}")
if final_morphs != original_morphs:
    print(f"⚠️  WARNING: Morph count changed from {{original_morphs}} to {{final_morphs}}")

# Save detailed mapping info
mapping = {{
    "azure_blendshapes": AZURE_BLENDSHAPES,
    "mapped_azure": sorted(list(found_azure)),
    "renamed": renamed,
    "missing_azure": [n for n in AZURE_BLENDSHAPES if n not in found_azure],
    "original_managers": original_managers,
    "original_morphs": original_morphs,
    "final_managers": final_managers,
    "final_morphs": final_morphs,
    "mesh_breakdown": final_breakdown,
    "all_morph_names": sorted(list(all_morph_names)),
    "preservation_status": "COMPLETE" if final_managers == original_managers and final_morphs == original_morphs else "MODIFIED"
}}

with open(mapping_json, "w") as f:
    json.dump(mapping, f, indent=2)

print(f"\\n=== PRESERVATION SUMMARY ===")
print(f"Status: {{mapping['preservation_status']}}")
print(f"Original: {{original_managers}} managers, {{original_morphs}} morphs")
print(f"Final: {{final_managers}} managers, {{final_morphs}} morphs")
print(f"Azure compatibility: {{len(found_azure)}}/{{len(AZURE_BLENDSHAPES)}} ({{len(found_azure)/len(AZURE_BLENDSHAPES)*100:.1f}}%)")

# Export FBX with preserved structure
bpy.ops.export_scene.fbx(filepath=output_fbx, use_selection=False)
"""

    # Run Blender processing
    try:
        result = subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        logger.console.print("[green]Blender processing completed[/green]")
        if result.stdout:
            logger.console.print(f"[dim]Output: {result.stdout}[/dim]")
    except Exception as e:
        logger.console.print(f"[red]Blender processing failed: {e}[/red]")
        raise

    # Read and return mapping results
    if not mapping_json.exists():
        raise RuntimeError(f"Blender did not produce mapping info: {mapping_json}")
    with open(mapping_json, "r") as f:
        mapping = json.load(f)
    mapping_json.unlink()
    return mapping
