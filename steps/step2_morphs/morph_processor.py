import subprocess
import json
from pathlib import Path
from typing import Any
from steps.step1_validation.constants import AZURE_BLENDSHAPES, METAHUMAN_NAME_MAPPINGS
from steps.step1_validation.logging_config import logger


def extract_all_blendshapes(input_fbx: Path) -> list[str]:
    """
    Extract all blendshape (shape key) names from the input FBX using Blender.
    Returns a list of all blendshape names found.
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
    Loads input_fbx, ensures all Azure blendshapes are present and named correctly, writes output_fbx.
    Returns a dict with mapping summary.
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

# Find all meshes with shape keys
found = set()
renamed = []
for obj in bpy.data.objects:
    if obj.type == 'MESH' and obj.data.shape_keys:
        key_blocks = obj.data.shape_keys.key_blocks
        # Build a name->block map
        name_map = {{kb.name: kb for kb in key_blocks}}
        # Try to rename MetaHuman variants to Azure names
        for az_name in AZURE_BLENDSHAPES:
            # If exact match, mark as found
            if az_name in name_map:
                found.add(az_name)
                continue
            # If MetaHuman variant exists, rename it
            for meta_name, canonical in METAHUMAN_NAME_MAPPINGS.items():
                if canonical == az_name and meta_name in name_map:
                    key_blocks[meta_name].name = az_name
                    found.add(az_name)
                    renamed.append((meta_name, az_name))
                    break

# Save mapping info
mapping = {{
    "azure_blendshapes": AZURE_BLENDSHAPES,
    "mapped": sorted(list(found)),
    "renamed": renamed,
    "missing": [n for n in AZURE_BLENDSHAPES if n not in found],
}}
with open(mapping_json, "w") as f:
    json.dump(mapping, f, indent=2)

# Export FBX
bpy.ops.export_scene.fbx(filepath=output_fbx, use_selection=False)
"""

    # Run Blender
    try:
        result = subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        logger.console.print("[green]Blender run completed for Step 2[/green]")
    except Exception as e:
        logger.console.print(f"[red]Blender run failed: {e}[/red]")
        raise

    # Read mapping info
    if not mapping_json.exists():
        raise RuntimeError(f"Blender did not produce mapping info: {mapping_json}")
    with open(mapping_json, "r") as f:
        mapping = json.load(f)
    mapping_json.unlink()
    return mapping
