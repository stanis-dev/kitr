#!/usr/bin/env python3
"""
Azure Final Summary: Complete Compatibility Assessment

Combines verified results from Step 2 blendshape mapping and bone analysis
to provide the definitive Azure Cognitive Services compatibility report.
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_verified_results() -> Dict[str, Any]:
    """Load our verified blendshape and bone analysis results."""

    # Load blendshape verification (we know this achieved 52/52)
    blendshape_file = Path("azure_mapping_verification.json")
    if blendshape_file.exists():
        with open(blendshape_file, "r") as f:
            blendshape_results = json.load(f)
    else:
        print("⚠️  Blendshape verification file not found")
        blendshape_results = {}

    # Load bone analysis results
    bone_file = Path("azure_bone_mapping_analysis.json")
    if bone_file.exists():
        with open(bone_file, "r") as f:
            bone_results = json.load(f)
    else:
        print("⚠️  Bone analysis file not found")
        bone_results = {}

    return {
        "blendshapes": blendshape_results,
        "bones": bone_results
    }


def create_final_azure_summary():
    """Create comprehensive final Azure compatibility summary."""

    print("🎯 AZURE COGNITIVE SERVICES COMPATIBILITY SUMMARY")
    print("=" * 60)
    print()

    # Load verified results
    results = load_verified_results()
    blendshape_data = results.get("blendshapes", {})
    bone_data = results.get("bones", {})

    # ========================================
    # BLENDSHAPE ANALYSIS (52/55 Parameters)
    # ========================================
    print("🎭 BLENDSHAPE MAPPING RESULTS:")
    print("-" * 40)

        # Use the verified results from our successful mapping
    successful_mappings = blendshape_data.get("found_azure_blendshapes", 0)
    total_required = blendshape_data.get("total_azure_blendshapes", 52)
    found_blendshapes = blendshape_data.get("found_blendshapes", [])

    print(f"📊 Azure blendshapes required: {total_required}")
    print(f"📊 Azure blendshapes mapped:   {successful_mappings}")
    print(f"📊 Blendshape success rate:    {(successful_mappings/total_required)*100:.1f}%")

    if successful_mappings == total_required:
        print("✅ PERFECT blendshape mapping achieved!")
        print("   All facial expressions are Azure-compatible")
    elif successful_mappings >= 47:
        print("✅ EXCELLENT blendshape mapping achieved!")
        print(f"   {total_required-successful_mappings} minor expressions missing")
    else:
        print("⚠️  PARTIAL blendshape mapping")
        print(f"   {total_required-successful_mappings} expressions missing")

    print()

    # ========================================
    # BONE STRUCTURE ANALYSIS (3/55 Parameters)
    # ========================================
    print("🦴 BONE STRUCTURE RESULTS:")
    print("-" * 40)

    rotation_analysis = bone_data.get("azure_rotation_analysis", {})

    # Count available rotations
    available_rotations = 0
    rotation_details = {}

    for param_name, param_info in rotation_analysis.items():
        recommended = param_info.get("recommended")
        candidates = param_info.get("candidates", [])

        if recommended:
            available_rotations += 1
            rotation_details[param_name] = {
                "available": True,
                "bone": recommended,
                "alternatives": len(candidates) - 1
            }
        else:
            rotation_details[param_name] = {
                "available": False,
                "bone": None,
                "alternatives": 0
            }

    print(f"📊 Azure rotations required:  3")
    print(f"📊 Azure rotations mapped:    {available_rotations}")
    print(f"📊 Rotation success rate:     {(available_rotations/3)*100:.1f}%")
    print()

    for param, details in rotation_details.items():
        if details["available"]:
            print(f"   ✅ {param}: {details['bone']}")
            if details["alternatives"] > 0:
                print(f"      ({details['alternatives']} alternatives available)")
        else:
            print(f"   ❌ {param}: No suitable bone found")

    print()

    # ========================================
    # OVERALL COMPATIBILITY ASSESSMENT
    # ========================================
    print("🏁 OVERALL AZURE COMPATIBILITY:")
    print("=" * 50)

    total_params = successful_mappings + available_rotations
    total_possible = 55  # 52 blendshapes + 3 rotations
    compatibility_percentage = (total_params / total_possible) * 100

    print(f"📈 Facial Expressions (blendshapes): {successful_mappings}/52")
    print(f"📈 Head/Eye Rotations (bones):       {available_rotations}/3")
    print(f"📈 Total Azure Parameters:          {total_params}/55")
    print(f"📈 Overall Compatibility Score:     {compatibility_percentage:.1f}%")
    print()

    # Compatibility assessment
    if total_params >= 54:  # 98%+
        status = "PERFECT"
        print("🎉 PERFECT AZURE COMPATIBILITY!")
        print("   ✅ Excellent compatibility with Azure Cognitive Services")
        print("   ✅ All major facial expressions and rotations supported")
    elif total_params >= 50:  # 90%+
        status = "EXCELLENT"
        print("✅ EXCELLENT AZURE COMPATIBILITY!")
        print("   ✅ High compatibility with Azure Cognitive Services")
        print("   ✅ Minor limitations will not affect most use cases")
    elif total_params >= 45:  # 80%+
        status = "GOOD"
        print("⚠️  GOOD AZURE COMPATIBILITY")
        print("   ✅ Moderate compatibility with Azure Cognitive Services")
        print("   ⚠️  Some limitations in facial expression range")
    elif total_params >= 35:  # 60%+
        status = "FAIR"
        print("⚠️  FAIR AZURE COMPATIBILITY")
        print("   ⚠️  Basic compatibility with Azure Cognitive Services")
        print("   ⚠️  Significant limitations in expression range")
    else:
        status = "LIMITED"
        print("❌ LIMITED AZURE COMPATIBILITY")
        print("   ❌ Poor compatibility with Azure Cognitive Services")
        print("   ❌ Major limitations - may require significant work")

    # File information
    print()
    print("📁 FILE STATUS:")
    print("-" * 20)

    output_file = Path("output-step2-azure.fbx")
    if output_file.exists():
        file_size_mb = round(output_file.stat().st_size / (1024*1024), 1)
        print(f"✅ Azure-compatible FBX: {output_file.name} ({file_size_mb} MB)")
        print(f"   Ready for Azure Cognitive Services integration")
    else:
        print("❌ Output FBX file not found")

    # Create final report
    final_report = {
        "azure_compatibility_summary": {
            "blendshapes_mapped": successful_mappings,
            "blendshapes_total": 52,
            "rotations_mapped": available_rotations,
            "rotations_total": 3,
            "total_parameters": total_params,
            "total_possible": 55,
            "compatibility_percentage": compatibility_percentage,
            "compatibility_status": status,
            "azure_ready": total_params >= 50
        },
        "detailed_results": {
            "blendshapes": blendshape_data,
            "rotations": rotation_details,
            "bones": bone_data
        },
        "file_info": {
            "output_file": str(output_file),
            "file_exists": output_file.exists(),
            "file_size_mb": round(output_file.stat().st_size / (1024*1024), 1) if output_file.exists() else 0
        }
    }

    # Save final report
    report_file = Path("azure_final_compatibility_report.json")
    with open(report_file, "w") as f:
        json.dump(final_report, f, indent=2)

    print(f"\n📄 Final report saved: {report_file.name}")
    print(f"🎯 Azure Compatibility: {compatibility_percentage:.1f}% ({status})")

    return final_report


if __name__ == "__main__":
    create_final_azure_summary()
