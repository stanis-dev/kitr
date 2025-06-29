#!/usr/bin/env python3
"""
Complete Step 2: Azure Blendshapes + Rotations Processor

This script processes MetaHuman FBX files for complete Azure Cognitive Services compatibility:
- 52 facial blendshapes (morphs) ✅
- 3 rotation parameters (bones) ✅
- Total: 55 Azure parameters

Ensures both blendshape renaming AND bone structure verification.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step2_morphs.morph_processor import process_azure_blendshapes
from step2_morphs.bone_processor import process_azure_bones
from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS


def process_complete_azure_fbx(input_fbx: Path, output_fbx: Path) -> Dict[str, Any]:
    """
    Complete Azure FBX processing: blendshapes + bone structure.

    Returns comprehensive results including:
    - Blendshape mapping results (52 parameters)
    - Bone structure analysis (3 rotation parameters)
    - Overall Azure compatibility assessment
    """

    print("🚀 Starting Complete Azure FBX Processing...")
    print("=" * 60)
    print(f"📁 Input:  {input_fbx}")
    print(f"📁 Output: {output_fbx}")
    print()

    # ========================================
    # STEP 2A: Process Blendshapes (52/55)
    # ========================================
    print("🎭 STEP 2A: Processing Blendshapes...")
    print("-" * 40)

    try:
        morph_results = process_azure_blendshapes(input_fbx, output_fbx)
        mapped_count = morph_results.get('mapped_count', 0)
        print(f"✅ Blendshape processing completed")
        print(f"   📊 {mapped_count}/{len(AZURE_BLENDSHAPES)} Azure blendshapes mapped")

        if mapped_count == len(AZURE_BLENDSHAPES):
            print(f"   🎯 Perfect blendshape mapping achieved!")
        else:
            print(f"   ⚠️  {len(AZURE_BLENDSHAPES) - mapped_count} blendshapes missing")

    except Exception as e:
        print(f"❌ Blendshape processing failed: {e}")
        return {"error": str(e), "stage": "blendshapes"}

    print()

    # ========================================
    # STEP 2B: Process Bone Structure (3/55)
    # ========================================
    print("🦴 STEP 2B: Processing Bone Structure...")
    print("-" * 40)

    try:
        bone_results = process_azure_bones(output_fbx, output_fbx)
        verification = bone_results.get('azure_verification', {})

        mapped_rotations = len([v for v in verification.get('suggested_mapping', {}).values() if v])
        total_rotations = len(AZURE_ROTATIONS)

        print(f"✅ Bone structure analysis completed")
        print(f"   📊 {mapped_rotations}/{total_rotations} Azure rotations mapped")
        print(f"   🦴 {bone_results['total_bones_found']} total bones found")

        if mapped_rotations == total_rotations:
            print(f"   🎯 All rotation parameters available!")
        else:
            missing = verification.get('missing_bones', [])
            print(f"   ⚠️  Missing: {', '.join(missing)}")

    except Exception as e:
        print(f"❌ Bone processing failed: {e}")
        return {"error": str(e), "stage": "bones"}

    print()

    # ========================================
    # STEP 2C: Overall Assessment
    # ========================================
    print("📊 OVERALL AZURE COMPATIBILITY ASSESSMENT:")
    print("=" * 50)

    # Calculate total Azure parameters
    total_blendshapes = mapped_count
    total_rotations = mapped_rotations
    total_azure_params = total_blendshapes + total_rotations
    expected_total = len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS)  # 52 + 3 = 55

    print(f"📈 Blendshapes (facial expressions): {total_blendshapes}/{len(AZURE_BLENDSHAPES)}")
    print(f"📈 Rotations (head/eye movements):   {total_rotations}/{len(AZURE_ROTATIONS)}")
    print(f"📈 Total Azure Parameters:          {total_azure_params}/{expected_total}")

    compatibility_percentage = (total_azure_params / expected_total) * 100
    print(f"📈 Azure Compatibility Score:       {compatibility_percentage:.1f}%")

    if total_azure_params == expected_total:
        print("\n🎉 PERFECT AZURE COMPATIBILITY ACHIEVED!")
        print("   ✅ All 55 Azure parameters are available")
        print("   ✅ Ready for Azure Cognitive Services integration")
        status = "PERFECT"
    elif total_azure_params >= 50:  # 90%+ compatibility
        print(f"\n✅ EXCELLENT AZURE COMPATIBILITY!")
        print(f"   📊 {total_azure_params}/55 parameters available ({compatibility_percentage:.1f}%)")
        print("   ✅ Suitable for Azure Cognitive Services")
        status = "EXCELLENT"
    elif total_azure_params >= 45:  # 80%+ compatibility
        print(f"\n⚠️  GOOD AZURE COMPATIBILITY")
        print(f"   📊 {total_azure_params}/55 parameters available ({compatibility_percentage:.1f}%)")
        print("   ⚠️  May work with Azure Cognitive Services")
        status = "GOOD"
    else:
        print(f"\n❌ LIMITED AZURE COMPATIBILITY")
        print(f"   📊 {total_azure_params}/55 parameters available ({compatibility_percentage:.1f}%)")
        print("   ❌ May not work well with Azure Cognitive Services")
        status = "LIMITED"

    # Compile comprehensive results
    results = {
        "blendshape_results": morph_results,
        "bone_results": bone_results,
        "azure_summary": {
            "total_blendshapes_mapped": total_blendshapes,
            "total_rotations_mapped": total_rotations,
            "total_azure_parameters": total_azure_params,
            "expected_total": expected_total,
            "compatibility_percentage": compatibility_percentage,
            "compatibility_status": status,
            "azure_ready": total_azure_params == expected_total
        },
        "file_info": {
            "input_file": str(input_fbx),
            "output_file": str(output_fbx),
            "output_exists": output_fbx.exists(),
            "output_size_mb": round(output_fbx.stat().st_size / (1024*1024), 1) if output_fbx.exists() else 0
        }
    }

    # Save comprehensive report
    report_file = Path("azure_complete_compatibility_report.json")
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Complete report saved: {report_file.name}")
    print(f"📁 Output FBX: {output_fbx} ({results['file_info']['output_size_mb']} MB)")

    return results


def main():
    """Main execution function."""

    # Use our already-processed file with perfect blendshape mappings as input
    input_fbx = Path("output-step2-azure.fbx")
    output_fbx = Path("output-step2-azure-complete.fbx")

    # Check input file
    if not input_fbx.exists():
        print(f"❌ Input file not found: {input_fbx}")
        print("   Please ensure input-file.fbx exists in the parent directory.")
        return 1

    try:
        # Process complete Azure FBX
        results = process_complete_azure_fbx(input_fbx, output_fbx)

        if "error" in results:
            print(f"\n❌ Processing failed at {results['stage']}: {results['error']}")
            return 1

        # Success summary
        summary = results["azure_summary"]
        print(f"\n🎯 PROCESSING COMPLETE!")
        print(f"   Status: {summary['compatibility_status']}")
        print(f"   Azure Parameters: {summary['total_azure_parameters']}/55")
        print(f"   Compatibility: {summary['compatibility_percentage']:.1f}%")

        if summary["azure_ready"]:
            print(f"   🚀 Ready for Azure Cognitive Services!")

        return 0

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
