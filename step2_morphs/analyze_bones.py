#!/usr/bin/env python3
"""
Analyze bone structure for Azure rotation mapping

Specifically looks for eye bones that might have different naming conventions
and provides detailed mapping suggestions for Azure's 3 rotation parameters.
"""

import json
import re
from pathlib import Path
from bone_processor import extract_bone_structure


def find_eye_bones(bone_data):
    """Find eye bones using various naming patterns."""
    all_bones = bone_data.get("bones", [])

    # Eye bone search patterns
    eye_patterns = {
        "left_eye": [
            r".*[Ll]eft.*[Ee]ye.*",
            r".*[Ll]_[Ee]ye.*",
            r".*eye.*[Ll].*",
            r".*[Ee]ye_[Ll].*",
            r".*eyeball.*[Ll].*",
            r".*FACIAL.*[Ll].*[Ee]ye.*",
            r".*LeftEye.*",
            r".*left_eye.*"
        ],
        "right_eye": [
            r".*[Rr]ight.*[Ee]ye.*",
            r".*[Rr]_[Ee]ye.*",
            r".*eye.*[Rr].*",
            r".*[Ee]ye_[Rr].*",
            r".*eyeball.*[Rr].*",
            r".*FACIAL.*[Rr].*[Ee]ye.*",
            r".*RightEye.*",
            r".*right_eye.*"
        ]
    }

    found_eyes = {"left_eye": [], "right_eye": []}

    for bone_name in all_bones:
        # Check left eye patterns
        for pattern in eye_patterns["left_eye"]:
            if re.match(pattern, bone_name, re.IGNORECASE):
                found_eyes["left_eye"].append(bone_name)
                break

        # Check right eye patterns
        for pattern in eye_patterns["right_eye"]:
            if re.match(pattern, bone_name, re.IGNORECASE):
                found_eyes["right_eye"].append(bone_name)
                break

    # Remove duplicates and sort
    found_eyes["left_eye"] = sorted(list(set(found_eyes["left_eye"])))
    found_eyes["right_eye"] = sorted(list(set(found_eyes["right_eye"])))

    return found_eyes


def suggest_azure_bone_mapping(bone_data):
    """Suggest the best bone mapping for Azure rotations."""

    # Find head bones
    head_bones = []
    all_bones = bone_data.get("bones", [])

    head_patterns = [r"^head$", r"^Head$", r".*[Hh]ead$", r".*skull.*", r".*cranium.*"]

    for bone_name in all_bones:
        for pattern in head_patterns:
            if re.match(pattern, bone_name, re.IGNORECASE):
                head_bones.append(bone_name)
                break

    # Find eye bones
    eye_bones = find_eye_bones(bone_data)

    # Create mapping suggestions
    mapping = {
        "headRoll": {
            "candidates": head_bones,
            "recommended": head_bones[0] if head_bones else None,
            "description": "Main head bone for head tilt rotation"
        },
        "leftEyeRoll": {
            "candidates": eye_bones["left_eye"],
            "recommended": eye_bones["left_eye"][0] if eye_bones["left_eye"] else None,
            "description": "Left eye bone for left eye rotation"
        },
        "rightEyeRoll": {
            "candidates": eye_bones["right_eye"],
            "recommended": eye_bones["right_eye"][0] if eye_bones["right_eye"] else None,
            "description": "Right eye bone for right eye rotation"
        }
    }

    return mapping


def analyze_azure_bone_compatibility():
    """Complete analysis of bone compatibility for Azure rotations."""

    print("🔍 Analyzing bone structure for Azure rotation compatibility...")
    print("=" * 70)

    # Extract bone structure from current output
    input_fbx = Path("output-step2-azure.fbx")
    if not input_fbx.exists():
        print("❌ output-step2-azure.fbx not found. Run step2_morphs.py first.")
        return

    bone_data = extract_bone_structure(input_fbx)

    # Get Azure mapping suggestions
    azure_mapping = suggest_azure_bone_mapping(bone_data)

    # Print results
    print(f"📊 Total bones found: {len(bone_data.get('bones', []))}")
    print(f"📊 Total armatures: {len(bone_data.get('armatures', []))}")
    print()

    print("🎯 Azure Rotation Parameter Mapping:")
    print("-" * 50)

    all_mapped = True

    for param_name, mapping_info in azure_mapping.items():
        candidates = mapping_info["candidates"]
        recommended = mapping_info["recommended"]
        description = mapping_info["description"]

        print(f"\n{param_name}:")
        print(f"  Description: {description}")

        if candidates:
            print(f"  ✅ Found {len(candidates)} candidate(s)")
            print(f"  📍 Recommended: {recommended}")
            if len(candidates) > 1:
                print(f"  🔄 Alternatives: {', '.join(candidates[1:4])}{'...' if len(candidates) > 4 else ''}")
        else:
            print(f"  ❌ No candidates found")
            all_mapped = False

    # Overall assessment
    print(f"\n🏁 AZURE ROTATION COMPATIBILITY:")
    print("=" * 40)

    if all_mapped:
        print("✅ All 3 Azure rotation parameters can be mapped!")
        print("   The skeleton is compatible with Azure Cognitive Services.")
    else:
        mapped_count = sum(1 for info in azure_mapping.values() if info["recommended"])
        print(f"⚠️  {mapped_count}/3 Azure rotation parameters can be mapped")
        print("   Some rotations may need alternative implementation.")

    # Save detailed report
    report = {
        "azure_rotation_analysis": azure_mapping,
        "total_bones": len(bone_data.get('bones', [])),
        "total_armatures": len(bone_data.get('armatures', [])),
        "compatibility_score": f"{sum(1 for info in azure_mapping.values() if info['recommended'])}/3",
        "fully_compatible": all_mapped
    }

    report_file = Path("azure_bone_mapping_analysis.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved: {report_file.name}")

    return azure_mapping


if __name__ == "__main__":
    analyze_azure_bone_compatibility()
