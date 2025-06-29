#!/usr/bin/env python3
"""
Step 2: Azure Blendshape Mapping

Takes input-file.fbx, ensures all Azure blendshapes are present and named correctly, and outputs output-step2-azure.fbx.
No cleanup of extra morphs yet.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step1_validation.logging_config import setup_logging
from step2_morphs.morph_processor import process_azure_blendshapes


def main():
    setup_logging()

    # Find input file - look in current directory first, then parent
    input_fbx = Path("input-file.fbx")
    if not input_fbx.exists():
        input_fbx = Path("../input-file.fbx")

    # Output file should be in this step's directory
    output_fbx = Path(__file__).parent / "output-step2-azure.fbx"

    print("\n🟦 Step 2: Azure Blendshape Mapping\n" + "=" * 40)
    if not input_fbx.exists():
        print(f"❌ File not found: input-file.fbx (checked current dir and parent dir)")
        sys.exit(1)

    result = process_azure_blendshapes(input_fbx, output_fbx)

    print(f"\n📋 Mapping Summary:")
    print(f"  Total Azure blendshapes: {len(result['azure_blendshapes'])}")
    print(f"  Present and mapped: {len(result['mapped'])}")
    print(f"  Renamed: {len(result['renamed'])}")
    print(f"  Missing: {len(result['missing'])}")
    if result["missing"]:
        print(f"  ❗ Missing blendshapes: {', '.join(result['missing'])}")

    # Check if output file was created successfully
    if output_fbx.exists():
        print(f"\n✅ Output written: {output_fbx}")
        print("\nDone!\n")
        # Success: output file created (missing blendshapes are expected for MetaHuman)
        sys.exit(0)
    else:
        print(f"\n❌ Failed to create output file: {output_fbx}")
        sys.exit(1)


if __name__ == "__main__":
    main()
