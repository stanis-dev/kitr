#!/usr/bin/env python3
"""
Verify Azure Blendshape Mapping in Step 2 Output

This script verifies that the output-step2-azure.fbx file contains all 52 required
Azure blendshapes with the correct naming conventions.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step2_morphs.morph_processor import extract_all_blendshapes
from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS


def verify_azure_mapping():
    """Verify that the output FBX contains all required Azure blendshapes."""

    output_fbx = Path(__file__).parent / "output-step2-azure.fbx"

    if not output_fbx.exists():
        print("❌ Output file not found: output-step2-azure.fbx")
        print("   Run step2_morphs.py first to generate the mapped file.")
        sys.exit(1)

    print(f"🔍 Verifying Azure mapping in: {output_fbx.name}")
    print("=" * 60)

    # Extract all blendshapes from the output FBX
    try:
        output_blendshapes = extract_all_blendshapes(output_fbx)
        print(f"✅ Extracted {len(output_blendshapes)} morph targets from output FBX")
    except Exception as e:
        print(f"❌ Failed to extract blendshapes: {e}")
        sys.exit(1)

    # Convert to set for faster lookup
    output_set = set(output_blendshapes)

    # Check each required Azure blendshape
    found_azure = []
    missing_azure = []

    print(f"\n📋 Checking {len(AZURE_BLENDSHAPES)} required Azure blendshapes:")
    print("-" * 40)

    for i, azure_name in enumerate(AZURE_BLENDSHAPES, 1):
        if azure_name in output_set:
            found_azure.append(azure_name)
            print(f"✅ {i:2d}. {azure_name}")
        else:
            missing_azure.append(azure_name)
            print(f"❌ {i:2d}. {azure_name} - MISSING")

    # Summary
    print(f"\n📊 VERIFICATION RESULTS:")
    print("=" * 30)
    print(f"✅ Azure blendshapes found: {len(found_azure)}/52")
    print(f"❌ Azure blendshapes missing: {len(missing_azure)}/52")
    print(f"📄 Total morphs in output: {len(output_blendshapes)}")

    # Additional info about Azure rotations (not morphs)
    print(f"\n📝 Note: Azure also expects {len(AZURE_ROTATIONS)} rotation parameters:")
    for i, rotation in enumerate(AZURE_ROTATIONS, 53):
        print(f"   {i}. {rotation} (handled by skeleton, not morphs)")

    # Success/failure determination
    if len(missing_azure) == 0:
        print(f"\n🎉 SUCCESS: All 52 Azure blendshapes are present!")
        print(f"   The output FBX is ready for Azure Cognitive Services integration.")

        # Save verification report
        report_file = Path(__file__).parent / "azure_mapping_verification.json"
        with open(report_file, "w") as f:
            json.dump({
                "verification_passed": True,
                "total_azure_blendshapes": len(AZURE_BLENDSHAPES),
                "found_azure_blendshapes": len(found_azure),
                "missing_azure_blendshapes": len(missing_azure),
                "total_output_morphs": len(output_blendshapes),
                "found_blendshapes": found_azure,
                "missing_blendshapes": missing_azure,
                "azure_rotations": AZURE_ROTATIONS,
                "notes": "All 52 Azure blendshapes successfully mapped from MetaHuman naming conventions"
            }, f, indent=2)

        print(f"📄 Verification report saved: {report_file.name}")
        return True

    else:
        print(f"\n❌ FAILURE: {len(missing_azure)} Azure blendshapes are missing!")
        print(f"   Missing: {', '.join(missing_azure)}")
        return False


if __name__ == "__main__":
    success = verify_azure_mapping()
    sys.exit(0 if success else 1)
