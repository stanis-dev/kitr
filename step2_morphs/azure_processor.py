#!/usr/bin/env python3
"""
Azure FBX Processor - MetaHuman to Azure Cognitive Services optimization.

This module provides complete processing of MetaHuman FBX files for Azure compatibility,
including blendshape mapping, bone analysis, cleanup, and validation.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS
from morph_processor import process_azure_blendshapes
from bone_processor import process_azure_bones
from cleanup_processor import cleanup_azure_fbx
from validate_clean_fbx import validate_azure_clean_fbx


def process_azure_optimization(input_fbx: Path) -> Dict[str, Any]:
    """
    Complete Azure FBX optimization process.

    Performs:
    1. Azure blendshape mapping
    2. Bone structure analysis
    3. Morph target cleanup
    4. Final validation

    Args:
        input_fbx: Path to input MetaHuman FBX file

    Returns:
        Dict containing processing results and status
    """
    print("🚀 AZURE FBX OPTIMIZATION")
    print("=" * 60)
    print(f"📁 Input: {input_fbx.name}")
    print()

    # Output file paths
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
        # Stage 1: Azure Blendshape Mapping
        print("🎭 STAGE 1: Azure Blendshape Mapping")
        print("-" * 40)

        # Process blendshapes for Azure compatibility
        mapping_results = process_azure_blendshapes(input_fbx, mapped_fbx)

        # Get mapped count from actual results
        mapped_list = mapping_results.get("mapped", [])
        mapped_count = len(mapped_list)
        mapping_success = mapped_count == len(AZURE_BLENDSHAPES)

        print(f"✅ Blendshape mapping completed")
        print(f"   📊 {mapped_count}/{len(AZURE_BLENDSHAPES)} Azure blendshapes mapped")

        if mapped_count < len(AZURE_BLENDSHAPES):
            print(f"⚠️  Warning: Only {mapped_count}/{len(AZURE_BLENDSHAPES)} blendshapes mapped")

        results["stages"]["mapping"] = {
            "success": True,
            "mapped_count": mapped_count,
            "required_count": len(AZURE_BLENDSHAPES),
            "mapping_percentage": (mapped_count / len(AZURE_BLENDSHAPES)) * 100,
            "mapping_complete": mapping_success,
            "results": mapping_results
        }

        print()

        # Stage 2: Bone Structure Analysis
        print("🦴 STAGE 2: Bone Structure Analysis")
        print("-" * 40)

        # Process bones for Azure rotations
        bone_results = process_azure_bones(mapped_fbx, mapped_fbx)
        azure_verification = bone_results.get("azure_verification", {})
        rotations_mapped = azure_verification.get("rotations_available", 0)
        all_rotations_found = azure_verification.get("all_rotations_found", False)

        print(f"✅ Bone processing completed")
        print(f"   🦴 Bones analyzed: {bone_results.get('total_bones_found', 0)}")
        print(f"   🔄 Azure rotations: {rotations_mapped}/3")

        # All 3 rotations must be found for Azure compatibility
        if not all_rotations_found:
            missing_bones = azure_verification.get("missing_bones", [])
            print(f"   ❌ MISSING ROTATIONS: {missing_bones}")
            print()
            print("💥 PROCESSING FAILED:")
            print("   ❌ All 3 Azure rotations are required for full compatibility")
            print("   ❌ Missing rotation bones prevent Azure Cognitive Services integration")
            print("   🔧 Bone structure insufficient for Azure requirements")

            results["stages"]["bones"] = {
                "success": False,
                "rotations_found": rotations_mapped,
                "rotations_required": len(AZURE_ROTATIONS),
                "all_rotations_available": all_rotations_found,
                "missing_bones": missing_bones,
                "results": bone_results,
                "failure_reason": "Insufficient rotation bones for Azure compatibility"
            }

            # Early failure - don't continue with cleanup/validation
            results.update({
                "success": False,
                "status": "FAILED",
                "error": f"Missing {3-rotations_mapped} required Azure rotation bones",
                "azure_compatibility": {
                    "blendshapes_mapped": mapped_count,
                    "blendshapes_required": len(AZURE_BLENDSHAPES),
                    "rotations_mapped": rotations_mapped,
                    "rotations_required": len(AZURE_ROTATIONS),
                    "compatibility_percentage": 0.0,
                    "failure_reason": "Critical rotation bones missing"
                }
            })
            return results

        print(f"   ✅ All rotation bones found: {list(azure_verification.get('suggested_mapping', {}).keys())}")

        results["stages"]["bones"] = {
            "success": True,
            "rotations_found": rotations_mapped,
            "rotations_required": len(AZURE_ROTATIONS),
            "all_rotations_available": all_rotations_found,
            "bone_mapping": azure_verification.get("suggested_mapping", {}),
            "results": bone_results
        }

        print()

        # Stage 3: Morph Target Cleanup
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

        # Stage 4: Final Validation
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

        # Final Assessment
        print("📊 FINAL ASSESSMENT:")
        print("=" * 50)

        # Calculate overall success metrics
        blendshapes_perfect = mapped_count == len(AZURE_BLENDSHAPES)
        rotations_available = rotations_mapped == len(AZURE_ROTATIONS)  # All 3 rotations required
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
        elif mapped_count >= 47 and rotations_available and validation_clean:
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

        print(f"\n🎯 Status: {status}")
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

    # Use original input file - check both possible locations
    input_fbx_root = Path("input-file.fbx")  # When run from project root
    input_fbx_parent = Path("../input-file.fbx")  # When run from step2_morphs directory

    if input_fbx_root.exists():
        input_fbx = input_fbx_root
    elif input_fbx_parent.exists():
        input_fbx = input_fbx_parent
    else:
        print("❌ Input file not found: input-file.fbx")
        print("   Please ensure the MetaHuman FBX file exists in the project root")
        return 1

    try:
        # Run complete Azure optimization
        results = process_azure_optimization(input_fbx)

        if results["success"]:
            status = results["status"]
            compatibility = results["azure_compatibility"]["compatibility_percentage"]

            print(f"\n🎯 AZURE OPTIMIZATION COMPLETE!")
            print(f"   Status: {status}")
            print(f"   Azure Compatibility: {compatibility:.1f}%")

            if status in ["PERFECT", "EXCELLENT"]:
                print(f"   🚀 Ready for Azure Cognitive Services!")
                return 0
            else:
                print(f"   ⚠️  Additional optimization recommended")
                return 0
        else:
            print(f"\n❌ Azure optimization failed: {results.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
