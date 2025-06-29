#!/usr/bin/env python3
"""
Step 2 Final: Complete Azure FBX Processing Pipeline

This is the definitive Step 2 processor that performs all required operations:
1. Azure blendshape mapping and renaming
2. Bone structure analysis for rotations
3. Morph target cleanup (removes excess morphs)
4. Final validation (ensures only Azure content)

Output: Clean, optimized FBX with ONLY Azure-required content (52 blendshapes + essential bones)
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step2_morphs.morph_processor import process_azure_blendshapes
from step2_morphs.bone_processor import process_azure_bones
from step2_morphs.cleanup_processor import cleanup_azure_fbx
from step2_morphs.validate_clean_fbx import validate_azure_clean_fbx
from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS


def process_step2_complete(input_fbx: Path) -> Dict[str, Any]:
    """
    Complete Step 2 processing pipeline for Azure compatibility.

    Workflow:
    1. Map and rename blendshapes to Azure format
    2. Analyze bone structure for rotation support
    3. Clean up excess morph targets (keep only 52 Azure blendshapes)
    4. Validate final output contains only Azure-required content

    Returns comprehensive results and file paths.
    """

    print("🚀 STEP 2 FINAL: COMPLETE AZURE FBX PROCESSING")
    print("=" * 60)
    print(f"📁 Input: {input_fbx}")
    print()

    if not input_fbx.exists():
        return {
            "success": False,
            "error": f"Input file not found: {input_fbx}",
            "stage": "initialization"
        }

    # Define intermediate and final output files
    mapped_fbx = Path("output-step2-azure-mapped.fbx")
    clean_fbx = Path("azure_optimized.fbx")

    results = {
        "success": False,
        "input_file": str(input_fbx),
        "mapped_file": str(mapped_fbx),
        "final_file": str(clean_fbx),
        "stages": {}
    }

    try:
        # ============================================
        # STAGE 1: Azure Blendshape Mapping
        # ============================================
        print("🎭 STAGE 1: Azure Blendshape Mapping")
        print("-" * 40)

        mapping_results = process_azure_blendshapes(input_fbx, mapped_fbx)
        mapped_count = mapping_results.get("mapped_count", 0)

        print(f"✅ Blendshape mapping completed")
        print(f"   📊 {mapped_count}/{len(AZURE_BLENDSHAPES)} Azure blendshapes mapped")

        results["stages"]["mapping"] = {
            "success": True,
            "azure_blendshapes_mapped": mapped_count,
            "azure_blendshapes_required": len(AZURE_BLENDSHAPES),
            "mapping_complete": mapped_count == len(AZURE_BLENDSHAPES),
            "results": mapping_results
        }

        if mapped_count != len(AZURE_BLENDSHAPES):
            print(f"⚠️  Warning: Only {mapped_count}/52 blendshapes mapped")

        print()

        # ============================================
        # STAGE 2: Bone Structure Analysis
        # ============================================
        print("🦴 STAGE 2: Bone Structure Analysis")
        print("-" * 40)

        bone_results = process_azure_bones(mapped_fbx, mapped_fbx)
        verification = bone_results.get("azure_verification", {})
        rotations_mapped = len([v for v in verification.get("suggested_mapping", {}).values() if v])

        print(f"✅ Bone analysis completed")
        print(f"   📊 {rotations_mapped}/{len(AZURE_ROTATIONS)} Azure rotations available")
        print(f"   🦴 {bone_results.get('total_bones_found', 0)} total bones analyzed")

        results["stages"]["bones"] = {
            "success": True,
            "azure_rotations_mapped": rotations_mapped,
            "azure_rotations_required": len(AZURE_ROTATIONS),
            "rotations_complete": rotations_mapped == len(AZURE_ROTATIONS),
            "results": bone_results
        }

        print()

        # ============================================
        # STAGE 3: Morph Target Cleanup
        # ============================================
        print("🧹 STAGE 3: Morph Target Cleanup")
        print("-" * 40)

        cleanup_results = cleanup_azure_fbx(mapped_fbx, clean_fbx)

        original_morphs = cleanup_results.get("cleanup_stats", {}).get("original_morphs", 0)
        kept_morphs = cleanup_results.get("cleanup_stats", {}).get("kept_morphs", 0)
        removed_morphs = cleanup_results.get("cleanup_stats", {}).get("removed_morphs", 0)

        print(f"✅ Cleanup completed")
        print(f"   📊 Morphs: {original_morphs} → {kept_morphs} (removed {removed_morphs})")
        print(f"   📦 Size: {cleanup_results.get('input_size_mb', 0)} → {cleanup_results.get('output_size_mb', 0)} MB")

        results["stages"]["cleanup"] = {
            "success": True,
            "morphs_removed": removed_morphs,
            "morphs_kept": kept_morphs,
            "target_morphs": len(AZURE_BLENDSHAPES),
            "cleanup_optimal": kept_morphs == len(AZURE_BLENDSHAPES),
            "results": cleanup_results
        }

        print()

        # ============================================
        # STAGE 4: Final Validation
        # ============================================
        print("🔍 STAGE 4: Final Validation")
        print("-" * 40)

        validation_results = validate_azure_clean_fbx(clean_fbx)
        validation_passed = validation_results.get("validation_passed", False)

        morph_validation = validation_results.get("morph_validation", {})
        azure_morphs_found = len(morph_validation.get("azure_morphs_found", []))
        excess_morphs_found = len(morph_validation.get("excess_morphs_found", []))

        print(f"✅ Validation completed")
        print(f"   📊 Azure morphs: {azure_morphs_found}/{len(AZURE_BLENDSHAPES)}")
        print(f"   ❌ Excess morphs: {excess_morphs_found}")

        results["stages"]["validation"] = {
            "success": True,
            "validation_passed": validation_passed,
            "azure_morphs_found": azure_morphs_found,
            "excess_morphs_found": excess_morphs_found,
            "file_optimized": excess_morphs_found == 0,
            "results": validation_results
        }

        print()

        # ============================================
        # FINAL ASSESSMENT
        # ============================================
        print("📊 FINAL ASSESSMENT:")
        print("=" * 50)

        # Calculate overall success metrics
        blendshapes_perfect = mapped_count == len(AZURE_BLENDSHAPES)
        rotations_available = rotations_mapped >= 1  # At least head rotation
        cleanup_successful = kept_morphs == len(AZURE_BLENDSHAPES)
        validation_clean = validation_passed

        total_azure_params = mapped_count + rotations_mapped
        max_azure_params = len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS)
        compatibility_score = (total_azure_params / max_azure_params) * 100

        print(f"📈 Azure Blendshapes: {mapped_count}/{len(AZURE_BLENDSHAPES)} ({(mapped_count/len(AZURE_BLENDSHAPES)*100):.1f}%)")
        print(f"📈 Azure Rotations: {rotations_mapped}/{len(AZURE_ROTATIONS)} ({(rotations_mapped/len(AZURE_ROTATIONS)*100):.1f}%)")
        print(f"📈 Total Parameters: {total_azure_params}/{max_azure_params} ({compatibility_score:.1f}%)")
        print(f"📈 File Optimization: {'✅ Clean' if validation_clean else '❌ Needs work'}")

        # Determine overall status
        if blendshapes_perfect and rotations_available and cleanup_successful and validation_clean:
            status = "PERFECT"
            print("\n🎉 PERFECT AZURE COMPATIBILITY ACHIEVED!")
            print("   ✅ All blendshapes mapped and cleaned")
            print("   ✅ Rotation support available")
            print("   ✅ File contains ONLY Azure content")
            print("   ✅ Ready for Azure Cognitive Services")
        elif mapped_count >= 47 and rotations_mapped >= 1 and validation_clean:
            status = "EXCELLENT"
            print("\n✅ EXCELLENT AZURE COMPATIBILITY!")
            print("   ✅ High blendshape compatibility")
            print("   ✅ File optimized and clean")
            print("   ✅ Suitable for Azure integration")
        elif mapped_count >= 40 and cleanup_successful:
            status = "GOOD"
            print("\n⚠️  GOOD AZURE COMPATIBILITY")
            print("   ✅ Most blendshapes available")
            print("   ✅ File cleaned and optimized")
            print("   ⚠️  Minor limitations present")
        else:
            status = "NEEDS_WORK"
            print("\n❌ PROCESSING INCOMPLETE")
            print("   ❌ Significant issues remain")
            print("   🔧 Additional work required")

        # File information
        input_size = round(input_fbx.stat().st_size / (1024*1024), 1)
        final_size = round(clean_fbx.stat().st_size / (1024*1024), 1) if clean_fbx.exists() else 0
        size_reduction = input_size - final_size

        print(f"\n📁 File Processing:")
        print(f"   Input: {input_size} MB → Final: {final_size} MB")
        print(f"   Size reduction: {size_reduction:.1f} MB")
        print(f"   Final file: {clean_fbx.name}")

        # Update results with final assessment
        results.update({
            "success": True,
            "status": status,
            "azure_compatibility": {
                "blendshapes_mapped": mapped_count,
                "blendshapes_required": len(AZURE_BLENDSHAPES),
                "rotations_mapped": rotations_mapped,
                "rotations_required": len(AZURE_ROTATIONS),
                "total_parameters": total_azure_params,
                "max_parameters": max_azure_params,
                "compatibility_percentage": compatibility_score,
                "file_optimized": validation_clean
            },
            "file_info": {
                "input_size_mb": input_size,
                "final_size_mb": final_size,
                "size_reduction_mb": size_reduction,
                "cleanup_successful": cleanup_successful
            }
        })

        # Save comprehensive report
        report_file = Path("processing_report.json")
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n📄 Complete report: {report_file.name}")
        print(f"🎯 Status: {status}")
        print(f"🚀 Azure Compatibility: {compatibility_score:.1f}%")

        return results

    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        results.update({
            "success": False,
            "error": str(e),
            "stage": "processing"
        })
        return results


def main():
    """Main execution function."""

    # Use original input file
    input_fbx = Path("../input-file.fbx")

    if not input_fbx.exists():
        print("❌ Input file not found: input-file.fbx")
        print("   Please ensure the MetaHuman FBX file exists")
        return 1

    try:
        # Run complete Step 2 processing
        results = process_step2_complete(input_fbx)

        if results["success"]:
            status = results["status"]
            compatibility = results["azure_compatibility"]["compatibility_percentage"]

            print(f"\n🎯 STEP 2 COMPLETE!")
            print(f"   Status: {status}")
            print(f"   Azure Compatibility: {compatibility:.1f}%")

            if status in ["PERFECT", "EXCELLENT"]:
                print(f"   🚀 Ready for Azure Cognitive Services!")
                return 0
            else:
                print(f"   ⚠️  Additional optimization recommended")
                return 0
        else:
            print(f"\n❌ Step 2 failed: {results.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
