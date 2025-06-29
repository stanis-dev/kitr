#!/usr/bin/env python3
"""
FBX to GLB Converter
Converts optimized MetaHuman FBX files to web-ready GLB format using Blender.
"""

import os
import subprocess
import tempfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_blender_script(fbx_path: str, glb_path: str) -> str:
    """Create Blender script for FBX to GLB conversion"""
    script = f'''
import bpy
import sys
import traceback

try:
    print("=== BLENDER CONVERSION START ===")
    print(f"Python version: {{sys.version}}")
    print(f"Blender version: {{bpy.app.version}}")

    # Clear scene
    print("Clearing scene...")
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    print("Scene cleared")

    # Import FBX
    print(f"Importing FBX: {fbx_path}")
    result = bpy.ops.import_scene.fbx(filepath="{fbx_path}")
    print(f"Import result: {{result}}")

    # Check what was imported
    objects = list(bpy.data.objects)
    print(f"Objects after import: {{len(objects)}}")
    for obj in objects:
        print(f"  - {{obj.name}} ({{obj.type}})")

    meshes = [obj for obj in objects if obj.type == 'MESH']
    print(f"Mesh objects: {{len(meshes)}}")

    # Export GLB
    print(f"Exporting GLB: {glb_path}")
    result = bpy.ops.export_scene.gltf(
        filepath="{glb_path}",
        export_format='GLB',
        export_yup=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials='EXPORT',
        export_animations=True,
        export_morph=True
    )
    print(f"Export result: {{result}}")

    # Check if file was created
    import os
    if os.path.exists("{glb_path}"):
        size = os.path.getsize("{glb_path}")
        print(f"GLB file created successfully! Size: {{size}} bytes")
    else:
        print("ERROR: GLB file was not created!")

    print("=== BLENDER CONVERSION END ===")

except Exception as e:
    print(f"ERROR: {{str(e)}}")
    print(f"Traceback: {{traceback.format_exc()}}")
    sys.exit(1)
'''
    return script

def convert_fbx_to_glb(fbx_path: str, output_dir: str) -> bool:
    """Convert FBX file to GLB format using Blender"""

    # Check if input exists
    if not os.path.exists(fbx_path):
        logger.error(f"FBX file not found: {fbx_path}")
        return False

    # Setup paths
    fbx_path = os.path.abspath(fbx_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    glb_path = os.path.join(output_dir, "azure_optimized_web.glb")

    logger.info(f"Converting {fbx_path} to {glb_path}")

    # Find Blender
    blender_path = "/Applications/Blender.app/Contents/MacOS/Blender"
    if not os.path.exists(blender_path):
        logger.error("Blender not found")
        return False

    # Create script
    script_content = create_blender_script(fbx_path, glb_path)

    # Write script to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script_content)
        script_path = f.name

    try:
        # Run Blender
        cmd = [blender_path, '--background', '--python', script_path]
        logger.info(f"Running command: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        logger.info("=== BLENDER STDOUT ===")
        logger.info(result.stdout)

        if result.stderr:
            logger.info("=== BLENDER STDERR ===")
            logger.info(result.stderr)

        logger.info(f"Return code: {result.returncode}")

        # Check if GLB was created
        if os.path.exists(glb_path):
            size = os.path.getsize(glb_path)
            logger.info(f"SUCCESS: GLB created! Size: {size} bytes")
            return True
        else:
            logger.error("GLB file was not created")
            return False

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return False

    finally:
        # Clean up
        if os.path.exists(script_path):
            os.unlink(script_path)

if __name__ == "__main__":
    import sys
    import os

    # Check multiple possible locations for the input file
    possible_paths = [
        "../azure_optimized.fbx",  # Current location
        "azure_optimized.fbx",     # Pipeline location
        "../step2_morphs/azure_optimized.fbx"  # Original step2 location
    ]

    input_path = None
    for path in possible_paths:
        if os.path.exists(path):
            input_path = path
            break

    if input_path is None:
        print("Error: Could not find azure_optimized.fbx in any expected location")
        print("Checked paths:")
        for path in possible_paths:
            print(f"  - {os.path.abspath(path)}")
        sys.exit(1)

    print(f"Using input file: {input_path}")
    success = convert_fbx_to_glb(input_path, ".")
    print(f"Conversion {'succeeded' if success else 'failed'}")
    sys.exit(0 if success else 1)
