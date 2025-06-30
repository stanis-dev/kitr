#!/usr/bin/env python3
"""
Debug Morph Target Structure

Comprehensive analysis of morph targets focusing exclusively on Face mesh:
- Input FBX structure
- Final GLB structure
- Direct comparison to identify differences
"""

import subprocess
import json
import sys
from pathlib import Path

def analyze_fbx_morphs(fbx_path: Path, output_name: str):
    """Analyze morph target structure in FBX file"""

    print(f"\n🔍 ANALYZING {output_name}: {fbx_path}")
    print("=" * 60)

    analysis_json = fbx_path.with_suffix(f'.{output_name.lower()}_analysis.json')

    blender_script = f"""
import bpy
import json
from pathlib import Path

fbx_path = r"{fbx_path}"
analysis_json = r"{analysis_json}"

print(f"🔍 Analyzing FBX: {{fbx_path}}")

# Clear scene and import FBX
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=fbx_path)

analysis = {{
    "file_path": fbx_path,
    "file_type": "FBX",
    "analysis_name": "{output_name}",
    "total_objects": len(bpy.data.objects),
    "mesh_objects": [],
    "face_mesh_detailed": None,
    "summary": {{}}
}}

print(f"📊 Total objects imported: {{len(bpy.data.objects)}}")

# Analyze ALL mesh objects
mesh_count = 0
total_morph_managers = 0
total_morphs = 0

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mesh_count += 1
        mesh_info = {{
            "name": obj.name,
            "type": "MESH",
            "has_shape_keys": bool(obj.data.shape_keys),
            "morph_count": 0,
            "morph_names": [],
            "shape_key_details": {{}}
        }}

        if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
            # Count morphs (exclude Basis)
            morph_count = len(obj.data.shape_keys.key_blocks) - 1
            mesh_info["morph_count"] = morph_count

            if morph_count > 0:
                total_morph_managers += 1
                total_morphs += morph_count

                # Get all morph names
                morph_names = []
                for i, kb in enumerate(obj.data.shape_keys.key_blocks):
                    if kb.name != "Basis":
                        morph_names.append(kb.name)

                mesh_info["morph_names"] = morph_names

                # Detailed shape key analysis
                mesh_info["shape_key_details"] = {{
                    "total_keys": len(obj.data.shape_keys.key_blocks),
                    "basis_key": obj.data.shape_keys.key_blocks[0].name if obj.data.shape_keys.key_blocks else None,
                    "morph_keys": morph_names,
                    "first_10_morphs": morph_names[:10],
                    "last_10_morphs": morph_names[-10:] if len(morph_names) > 10 else morph_names
                }}

        analysis["mesh_objects"].append(mesh_info)

        print(f"📦 {{obj.name}}: {{mesh_info['morph_count']}} morph targets")
        if mesh_info['morph_count'] > 0:
            print(f"   First 5: {{', '.join(mesh_info['morph_names'][:5])}}")

# Focus on Face mesh specifically
face_meshes = [obj for obj in analysis["mesh_objects"] if "face" in obj["name"].lower()]

if face_meshes:
    face_mesh = face_meshes[0]  # Take first face mesh found
    analysis["face_mesh_detailed"] = {{
        "name": face_mesh["name"],
        "morph_count": face_mesh["morph_count"],
        "all_morph_names": face_mesh["morph_names"],
        "morph_categories": {{}}
    }}

    # Categorize morphs
    if face_mesh["morph_names"]:
        morph_names = face_mesh["morph_names"]

        # Count different types
        azure_morphs = []
        arkit_morphs = []
        metahuman_morphs = []
        other_morphs = []

        # Azure blendshape names (common ones)
        azure_names = [
            "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
            "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
            "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
            "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
            "eyeWideLeft", "eyeWideRight", "jawForward", "jawLeft", "jawRight", "jawOpen",
            "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
            "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
            "mouthDimpleLeft", "mouthDimpleRight", "mouthStretchLeft", "mouthStretchRight",
            "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
            "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight",
            "mouthUpperUpLeft", "mouthUpperUpRight", "noseSneerLeft", "noseSneerRight",
            "cheekPuff", "cheekSquintLeft", "cheekSquintRight"
        ]

        for morph_name in morph_names:
            if morph_name in azure_names:
                azure_morphs.append(morph_name)
            elif morph_name.startswith(("head_lod", "face_lod", "facial_")):
                metahuman_morphs.append(morph_name)
            elif any(pattern in morph_name.lower() for pattern in ["brow", "eye", "mouth", "jaw", "nose", "cheek"]):
                arkit_morphs.append(morph_name)
            else:
                other_morphs.append(morph_name)

        analysis["face_mesh_detailed"]["morph_categories"] = {{
            "azure_morphs": azure_morphs,
            "metahuman_morphs": metahuman_morphs,
            "arkit_morphs": arkit_morphs,
            "other_morphs": other_morphs,
            "counts": {{
                "azure": len(azure_morphs),
                "metahuman": len(metahuman_morphs),
                "arkit": len(arkit_morphs),
                "other": len(other_morphs)
            }}
        }}

analysis["summary"] = {{
    "total_mesh_objects": mesh_count,
    "morph_target_managers": total_morph_managers,
    "total_morph_targets": total_morphs,
    "face_meshes_found": len(face_meshes),
    "face_mesh_name": face_meshes[0]["name"] if face_meshes else None,
    "face_morph_count": face_meshes[0]["morph_count"] if face_meshes else 0
}}

print(f"\\n📊 SUMMARY for {{analysis['analysis_name']}}:")
print(f"   Mesh objects: {{analysis['summary']['total_mesh_objects']}}")
print(f"   Morph managers: {{analysis['summary']['morph_target_managers']}}")
print(f"   Total morphs: {{analysis['summary']['total_morph_targets']}}")
print(f"   Face mesh: {{analysis['summary']['face_mesh_name']}}")
print(f"   Face morphs: {{analysis['summary']['face_morph_count']}}")

if analysis["face_mesh_detailed"]:
    counts = analysis["face_mesh_detailed"]["morph_categories"]["counts"]
    print(f"   Face morph breakdown:")
    print(f"     Azure: {{counts['azure']}}")
    print(f"     MetaHuman: {{counts['metahuman']}}")
    print(f"     ARKit: {{counts['arkit']}}")
    print(f"     Other: {{counts['other']}}")

# Save detailed analysis
with open(analysis_json, "w") as f:
    json.dump(analysis, f, indent=2)

print(f"\\n💾 Analysis saved to: {{analysis_json}}")
"""

    # Run Blender analysis
    try:
        result = subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        print("✅ Blender analysis completed")
        if result.stdout:
            print(result.stdout)
    except Exception as e:
        print(f"❌ Blender analysis failed: {e}")
        return None

    # Load and return analysis results
    if analysis_json.exists():
        with open(analysis_json, "r") as f:
            analysis = json.load(f)
        analysis_json.unlink()  # Clean up
        return analysis
    else:
        print("❌ Analysis file not found")
        return None


def analyze_glb_morphs(glb_path: Path, output_name: str):
    """Analyze morph target structure in GLB file"""

    print(f"\n🔍 ANALYZING {output_name}: {glb_path}")
    print("=" * 60)

    analysis_json = glb_path.with_suffix(f'.{output_name.lower()}_analysis.json')

    blender_script = f"""
import bpy
import json
from pathlib import Path

glb_path = r"{glb_path}"
analysis_json = r"{analysis_json}"

print(f"🔍 Analyzing GLB: {{glb_path}}")

# Clear scene and import GLB
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

analysis = {{
    "file_path": glb_path,
    "file_type": "GLB",
    "analysis_name": "{output_name}",
    "total_objects": len(bpy.data.objects),
    "mesh_objects": [],
    "face_mesh_detailed": None,
    "summary": {{}}
}}

print(f"📊 Total objects imported: {{len(bpy.data.objects)}}")

# Analyze ALL mesh objects
mesh_count = 0
total_morph_managers = 0
total_morphs = 0

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        mesh_count += 1
        mesh_info = {{
            "name": obj.name,
            "type": "MESH",
            "has_shape_keys": bool(obj.data.shape_keys),
            "morph_count": 0,
            "morph_names": [],
            "shape_key_details": {{}}
        }}

        if obj.data.shape_keys and obj.data.shape_keys.key_blocks:
            # Count morphs (exclude Basis)
            morph_count = len(obj.data.shape_keys.key_blocks) - 1
            mesh_info["morph_count"] = morph_count

            if morph_count > 0:
                total_morph_managers += 1
                total_morphs += morph_count

                # Get all morph names
                morph_names = []
                for i, kb in enumerate(obj.data.shape_keys.key_blocks):
                    if kb.name != "Basis":
                        morph_names.append(kb.name)

                mesh_info["morph_names"] = morph_names

                # Detailed shape key analysis
                mesh_info["shape_key_details"] = {{
                    "total_keys": len(obj.data.shape_keys.key_blocks),
                    "basis_key": obj.data.shape_keys.key_blocks[0].name if obj.data.shape_keys.key_blocks else None,
                    "morph_keys": morph_names,
                    "first_10_morphs": morph_names[:10],
                    "last_10_morphs": morph_names[-10:] if len(morph_names) > 10 else morph_names
                }}

        analysis["mesh_objects"].append(mesh_info)

        print(f"📦 {{obj.name}}: {{mesh_info['morph_count']}} morph targets")
        if mesh_info['morph_count'] > 0:
            print(f"   First 5: {{', '.join(mesh_info['morph_names'][:5])}}")

# Focus on Face mesh specifically
face_meshes = [obj for obj in analysis["mesh_objects"] if "face" in obj["name"].lower()]

if face_meshes:
    face_mesh = face_meshes[0]  # Take first face mesh found
    analysis["face_mesh_detailed"] = {{
        "name": face_mesh["name"],
        "morph_count": face_mesh["morph_count"],
        "all_morph_names": face_mesh["morph_names"],
        "morph_categories": {{}}
    }}

    # Categorize morphs (same logic as FBX analysis)
    if face_mesh["morph_names"]:
        morph_names = face_mesh["morph_names"]

        # Count different types
        azure_morphs = []
        arkit_morphs = []
        metahuman_morphs = []
        other_morphs = []

        # Azure blendshape names (common ones)
        azure_names = [
            "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
            "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
            "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
            "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
            "eyeWideLeft", "eyeWideRight", "jawForward", "jawLeft", "jawRight", "jawOpen",
            "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
            "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
            "mouthDimpleLeft", "mouthDimpleRight", "mouthStretchLeft", "mouthStretchRight",
            "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
            "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight",
            "mouthUpperUpLeft", "mouthUpperUpRight", "noseSneerLeft", "noseSneerRight",
            "cheekPuff", "cheekSquintLeft", "cheekSquintRight"
        ]

        for morph_name in morph_names:
            if morph_name in azure_names:
                azure_morphs.append(morph_name)
            elif morph_name.startswith(("head_lod", "face_lod", "facial_")):
                metahuman_morphs.append(morph_name)
            elif any(pattern in morph_name.lower() for pattern in ["brow", "eye", "mouth", "jaw", "nose", "cheek"]):
                arkit_morphs.append(morph_name)
            else:
                other_morphs.append(morph_name)

        analysis["face_mesh_detailed"]["morph_categories"] = {{
            "azure_morphs": azure_morphs,
            "metahuman_morphs": metahuman_morphs,
            "arkit_morphs": arkit_morphs,
            "other_morphs": other_morphs,
            "counts": {{
                "azure": len(azure_morphs),
                "metahuman": len(metahuman_morphs),
                "arkit": len(arkit_morphs),
                "other": len(other_morphs)
            }}
        }}

analysis["summary"] = {{
    "total_mesh_objects": mesh_count,
    "morph_target_managers": total_morph_managers,
    "total_morph_targets": total_morphs,
    "face_meshes_found": len(face_meshes),
    "face_mesh_name": face_meshes[0]["name"] if face_meshes else None,
    "face_morph_count": face_meshes[0]["morph_count"] if face_meshes else 0
}}

print(f"\\n📊 SUMMARY for {{analysis['analysis_name']}}:")
print(f"   Mesh objects: {{analysis['summary']['total_mesh_objects']}}")
print(f"   Morph managers: {{analysis['summary']['morph_target_managers']}}")
print(f"   Total morphs: {{analysis['summary']['total_morph_targets']}}")
print(f"   Face mesh: {{analysis['summary']['face_mesh_name']}}")
print(f"   Face morphs: {{analysis['summary']['face_morph_count']}}")

if analysis["face_mesh_detailed"]:
    counts = analysis["face_mesh_detailed"]["morph_categories"]["counts"]
    print(f"   Face morph breakdown:")
    print(f"     Azure: {{counts['azure']}}")
    print(f"     MetaHuman: {{counts['metahuman']}}")
    print(f"     ARKit: {{counts['arkit']}}")
    print(f"     Other: {{counts['other']}}")

# Save detailed analysis
with open(analysis_json, "w") as f:
    json.dump(analysis, f, indent=2)

print(f"\\n💾 Analysis saved to: {{analysis_json}}")
"""

    # Run Blender analysis
    try:
        result = subprocess.run(
            ["blender", "--background", "--python-expr", blender_script],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        print("✅ Blender analysis completed")
        if result.stdout:
            print(result.stdout)
    except Exception as e:
        print(f"❌ Blender analysis failed: {e}")
        return None

    # Load and return analysis results
    if analysis_json.exists():
        with open(analysis_json, "r") as f:
            analysis = json.load(f)
        analysis_json.unlink()  # Clean up
        return analysis
    else:
        print("❌ Analysis file not found")
        return None


def compare_morphs(input_analysis, output_analysis):
    """Compare morph structures between input and output"""

    print(f"\n🔄 COMPARING MORPH STRUCTURES")
    print("=" * 60)

    if not input_analysis or not output_analysis:
        print("❌ Cannot compare - missing analysis data")
        return

    # Basic comparison
    print(f"📊 BASIC COMPARISON:")
    print(f"   Input managers:  {input_analysis['summary']['morph_target_managers']}")
    print(f"   Output managers: {output_analysis['summary']['morph_target_managers']}")
    print(f"   Input morphs:    {input_analysis['summary']['total_morph_targets']}")
    print(f"   Output morphs:   {output_analysis['summary']['total_morph_targets']}")

    # Face-specific comparison
    input_face = input_analysis.get('face_mesh_detailed')
    output_face = output_analysis.get('face_mesh_detailed')

    if input_face and output_face:
        print(f"\\n🎭 FACE MESH COMPARISON:")
        print(f"   Input face name:   {input_face['name']}")
        print(f"   Output face name:  {output_face['name']}")
        print(f"   Input face morphs: {input_face['morph_count']}")
        print(f"   Output face morphs: {output_face['morph_count']}")

        # Compare morph categories
        input_counts = input_face.get('morph_categories', {}).get('counts', {})
        output_counts = output_face.get('morph_categories', {}).get('counts', {})

        print(f"\\n📋 MORPH CATEGORY COMPARISON:")
        for category in ['azure', 'metahuman', 'arkit', 'other']:
            input_count = input_counts.get(category, 0)
            output_count = output_counts.get(category, 0)
            status = "✅" if input_count == output_count else "❌"
            print(f"   {category.capitalize():12} {status} {input_count:3d} → {output_count:3d}")

        # Find missing/added morphs
        input_morphs = set(input_face.get('all_morph_names', []))
        output_morphs = set(output_face.get('all_morph_names', []))

        missing = input_morphs - output_morphs
        added = output_morphs - input_morphs

        if missing:
            print(f"\\n❌ MISSING MORPHS ({len(missing)}):")
            for i, morph in enumerate(sorted(list(missing))[:20]):  # Show first 20
                print(f"   {i+1:2d}. {morph}")
            if len(missing) > 20:
                print(f"   ... and {len(missing) - 20} more")

        if added:
            print(f"\\n➕ ADDED MORPHS ({len(added)}):")
            for i, morph in enumerate(sorted(list(added))[:20]):  # Show first 20
                print(f"   {i+1:2d}. {morph}")
            if len(added) > 20:
                print(f"   ... and {len(added) - 20} more")

        if not missing and not added:
            print(f"\\n✅ MORPH NAMES: Perfect match - all {len(input_morphs)} morphs preserved")

    else:
        print(f"\\n❌ FACE MESH ISSUE:")
        print(f"   Input has face mesh: {bool(input_face)}")
        print(f"   Output has face mesh: {bool(output_face)}")


def main():
    """Main debug function"""

    print("🔍 MORPH TARGET STRUCTURE DEBUG")
    print("=" * 80)
    print("Focusing exclusively on Face mesh morph targets")
    print("Comparing: Input FBX → Final GLB")
    print()

    # File paths
    input_fbx = Path("input-file.fbx")
    output_glb = Path("step3_glb/azure_optimized_web.glb")

    # Check files exist
    if not input_fbx.exists():
        print(f"❌ Input FBX not found: {input_fbx}")
        return

    if not output_glb.exists():
        print(f"❌ Output GLB not found: {output_glb}")
        return

    # Analyze both files
    input_analysis = analyze_fbx_morphs(input_fbx, "INPUT_FBX")
    output_analysis = analyze_glb_morphs(output_glb, "FINAL_GLB")

    # Compare results
    compare_morphs(input_analysis, output_analysis)

    print(f"\\n🎯 DEBUG COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
