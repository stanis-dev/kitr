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

def create_blender_script(fbx_path: str, glb_path: str, materials_dir: str = "") -> str:
    """Create Blender script for FBX to GLB conversion with material loading"""
    materials_search_code = ""
    if materials_dir:
        materials_search_code = f'''
    # Search and load materials from {materials_dir}
    import os
    materials_dir = r"{materials_dir}"
    print(f"🎨 Searching for materials in: {{materials_dir}}")

    if os.path.exists(materials_dir):
        material_stats = {{
            "folders_found": 0,
            "textures_found": 0,
            "materials_created": 0
        }}

        # Search material subfolders (Face, Body, Hair, etc.)
        for subfolder in os.listdir(materials_dir):
            subfolder_path = os.path.join(materials_dir, subfolder)
            if os.path.isdir(subfolder_path):
                material_stats["folders_found"] += 1
                print(f"📁 Found material folder: {{subfolder}}")

                # Find texture files in subfolder
                texture_files = []
                for file in os.listdir(subfolder_path):
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tga', '.exr', '.hdr')):
                        texture_files.append(os.path.join(subfolder_path, file))
                        material_stats["textures_found"] += 1

                if texture_files:
                    print(f"  🖼️  Found {{len(texture_files)}} textures")

                    # Create material for this subfolder
                    mat_name = f"{{subfolder}}_Material"
                    if mat_name not in bpy.data.materials:
                        mat = bpy.data.materials.new(name=mat_name)
                        mat.use_nodes = True
                        nodes = mat.node_tree.nodes
                        links = mat.node_tree.links

                        # Clear default nodes
                        nodes.clear()

                        # Add Principled BSDF
                        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
                        bsdf.location = (0, 0)

                        # Add Material Output
                        output = nodes.new(type='ShaderNodeOutputMaterial')
                        output.location = (300, 0)
                        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

                                                # Load textures and connect them
                        for texture_file in texture_files:
                            file_name = os.path.basename(texture_file).lower()

                            # Create texture node
                            tex_node = nodes.new(type='ShaderNodeTexImage')
                            tex_image = bpy.data.images.load(texture_file)

                            # Resize texture to max 1K resolution if needed
                            original_width = tex_image.size[0]
                            original_height = tex_image.size[1]
                            max_size = 1024

                            if original_width > max_size or original_height > max_size:
                                # Calculate new dimensions maintaining aspect ratio
                                if original_width > original_height:
                                    new_width = max_size
                                    new_height = int((original_height * max_size) / original_width)
                                else:
                                    new_height = max_size
                                    new_width = int((original_width * max_size) / original_height)

                                print(f"    📏 Resizing {{file_name}}: {{original_width}}x{{original_height}} → {{new_width}}x{{new_height}}")
                                tex_image.scale(new_width, new_height)
                            else:
                                print(f"    📏 Keeping {{file_name}}: {{original_width}}x{{original_height}} (within 1K limit)")

                            tex_node.image = tex_image

                            # Connect based on texture type
                            if 'diffuse' in file_name or 'albedo' in file_name or 'basecolor' in file_name:
                                tex_node.location = (-300, 200)
                                links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
                                print(f"    📎 Connected diffuse texture: {{file_name}}")
                            elif 'normal' in file_name:
                                tex_node.location = (-300, -100)
                                normal_map = nodes.new(type='ShaderNodeNormalMap')
                                normal_map.location = (-150, -100)
                                links.new(tex_node.outputs['Color'], normal_map.inputs['Color'])
                                links.new(normal_map.outputs['Normal'], bsdf.inputs['Normal'])
                                print(f"    📎 Connected normal texture: {{file_name}}")
                            elif 'roughness' in file_name:
                                tex_node.location = (-300, 0)
                                links.new(tex_node.outputs['Color'], bsdf.inputs['Roughness'])
                                print(f"    📎 Connected roughness texture: {{file_name}}")
                            elif 'metallic' in file_name:
                                tex_node.location = (-300, -50)
                                links.new(tex_node.outputs['Color'], bsdf.inputs['Metallic'])
                                print(f"    📎 Connected metallic texture: {{file_name}}")

                        material_stats["materials_created"] += 1
                        print(f"  ✅ Created material: {{mat_name}}")

        print(f"🎨 Material loading complete:")
        print(f"   📁 Folders: {{material_stats['folders_found']}}")
        print(f"   🖼️  Textures: {{material_stats['textures_found']}}")
        print(f"   🎭 Materials: {{material_stats['materials_created']}}")
    else:
        print(f"⚠️  Materials directory not found: {{materials_dir}}")
    print()
    '''

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
    print()

    # Strip all LOD meshes except LOD0
    print("🔄 Stripping LOD meshes (keeping only LOD0)...")
    lod_stats = {{
        "total_meshes": len(meshes),
        "lod_meshes_found": 0,
        "lod_meshes_removed": 0,
        "kept_meshes": 0
    }}

    meshes_to_remove = []
    for obj in meshes:
        mesh_name = obj.name.lower()
        # Check if this is a LOD mesh (but not LOD0)
        if ('_lod1' in mesh_name or '_lod2' in mesh_name or '_lod3' in mesh_name or
            'lod1' in mesh_name or 'lod2' in mesh_name or 'lod3' in mesh_name):
            meshes_to_remove.append(obj)
            lod_stats["lod_meshes_found"] += 1
            print(f"  🗑️  Marking for removal: {{obj.name}}")

    # Remove LOD meshes
    for obj in meshes_to_remove:
        print(f"  ❌ Removing LOD mesh: {{obj.name}}")
        bpy.data.objects.remove(obj, do_unlink=True)
        lod_stats["lod_meshes_removed"] += 1

    # Update mesh list
    remaining_objects = list(bpy.data.objects)
    remaining_meshes = [obj for obj in remaining_objects if obj.type == 'MESH']
    lod_stats["kept_meshes"] = len(remaining_meshes)

    print(f"✅ LOD stripping complete:")
    print(f"   📊 Original meshes: {{lod_stats['total_meshes']}}")
    print(f"   🗑️  LOD meshes removed: {{lod_stats['lod_meshes_removed']}}")
    print(f"   ✅ Remaining meshes: {{lod_stats['kept_meshes']}}")
    print()

{materials_search_code}

    # Apply materials to remaining meshes by name matching
    if remaining_meshes:
        print("🔗 Applying materials to remaining meshes...")
        for obj in remaining_meshes:
            mesh_name = obj.name.lower()
            print(f"  🔍 Processing mesh: {{obj.name}}")

            # Try to match mesh name to material
            best_material = None
            for mat in bpy.data.materials:
                mat_name = mat.name.lower()
                if 'face' in mesh_name and 'face' in mat_name:
                    best_material = mat
                    break
                elif 'body' in mesh_name and 'body' in mat_name:
                    best_material = mat
                    break
                elif 'hair' in mesh_name and 'hair' in mat_name:
                    best_material = mat
                    break
                elif 'pelo' in mesh_name and 'hair' in mat_name:  # Spanish for hair
                    best_material = mat
                    break

            if best_material:
                # Clear existing materials and assign new one
                obj.data.materials.clear()
                obj.data.materials.append(best_material)
                print(f"    ✅ Applied material: {{best_material.name}}")
            else:
                print(f"    ⚠️  No matching material found for {{obj.name}}")
        print()

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

    # Find materials directory
    materials_dir = ""
    project_root = os.path.dirname(os.path.dirname(fbx_path))  # Go up from file location
    possible_materials_paths = [
        os.path.join(project_root, "materials"),
        os.path.join(os.path.dirname(fbx_path), "materials"),
        "materials",
        "../materials"
    ]

    for path in possible_materials_paths:
        if os.path.exists(path) and os.path.isdir(path):
            materials_dir = os.path.abspath(path)
            logger.info(f"Found materials directory: {materials_dir}")
            break

    if not materials_dir:
        logger.info("No materials directory found, proceeding without material enhancement")

    # Create script
    script_content = create_blender_script(fbx_path, glb_path, materials_dir)

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
