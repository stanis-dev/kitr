#!/usr/bin/env python3
"""
Extract complete list of morph targets from input-file.fbx

This script extracts all morph targets (blendshapes) from the original MetaHuman FBX file
and saves them to documentation files. No truncation - full lists are preserved.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step2_morphs.morph_processor import extract_all_blendshapes
from step1_validation.constants import AZURE_BLENDSHAPES, AZURE_ROTATIONS


def extract_and_document_morph_targets():
    """Extract all morph targets and create documentation files."""

    # Find input file
    input_fbx = Path("../input-file.fbx")
    if not input_fbx.exists():
        input_fbx = Path("../input-file-original.fbx")

    if not input_fbx.exists():
        print("❌ Could not find input FBX file")
        sys.exit(1)

    print(f"📁 Extracting morph targets from: {input_fbx.name}")

    # Extract all blendshapes from the FBX
    try:
        all_blendshapes = extract_all_blendshapes(input_fbx)
        print(f"✅ Extracted {len(all_blendshapes)} morph targets")
    except Exception as e:
        print(f"❌ Failed to extract blendshapes: {e}")
        sys.exit(1)

    # Create documentation directory
    docs_dir = Path(__file__).parent
    docs_dir.mkdir(exist_ok=True)

    # Save complete list of original FBX morph targets
    original_morphs_file = docs_dir / "original_fbx_morph_targets_complete.txt"
    with open(original_morphs_file, "w") as f:
        f.write(f"Complete List of Morph Targets from {input_fbx.name}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total count: {len(all_blendshapes)}\n")
        f.write(f"Extracted on: {Path(__file__).stat().st_mtime}\n\n")

        for i, morph_name in enumerate(all_blendshapes, 1):
            f.write(f"{i:4d}. {morph_name}\n")

    # Save as JSON for programmatic access
    original_morphs_json = docs_dir / "original_fbx_morph_targets_complete.json"
    with open(original_morphs_json, "w") as f:
        json.dump({
            "source_file": input_fbx.name,
            "total_count": len(all_blendshapes),
            "morph_targets": all_blendshapes
        }, f, indent=2)

    # Save Azure blendshapes list
    azure_blendshapes_file = docs_dir / "azure_blendshapes_complete.txt"
    with open(azure_blendshapes_file, "w") as f:
        f.write("Complete List of Azure Blendshapes (ARKit Compatible)\n")
        f.write("=" * 60 + "\n")
        f.write(f"Total facial blendshapes: {len(AZURE_BLENDSHAPES)}\n")
        f.write(f"Total rotation parameters: {len(AZURE_ROTATIONS)}\n")
        f.write(f"Total parameters: {len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS)}\n\n")

        f.write("FACIAL BLENDSHAPES (52 total):\n")
        f.write("-" * 30 + "\n")
        for i, blendshape in enumerate(AZURE_BLENDSHAPES, 1):
            f.write(f"{i:2d}. {blendshape}\n")

        f.write("\nROTATION PARAMETERS (3 total):\n")
        f.write("-" * 30 + "\n")
        for i, rotation in enumerate(AZURE_ROTATIONS, 53):  # Start from index 53
            f.write(f"{i:2d}. {rotation}\n")

    # Save Azure blendshapes as JSON
    azure_blendshapes_json = docs_dir / "azure_blendshapes_complete.json"
    with open(azure_blendshapes_json, "w") as f:
        json.dump({
            "facial_blendshapes": AZURE_BLENDSHAPES,
            "rotation_parameters": AZURE_ROTATIONS,
            "total_facial_count": len(AZURE_BLENDSHAPES),
            "total_rotation_count": len(AZURE_ROTATIONS),
            "total_parameters": len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS),
            "description": "52 ARKit-compatible facial blendshapes + 3 rotation parameters expected by Azure Cognitive Services"
        }, f, indent=2)

    # Create a summary comparison file
    comparison_file = docs_dir / "morph_targets_comparison.txt"
    with open(comparison_file, "w") as f:
        f.write("Morph Targets Comparison Summary\n")
        f.write("=" * 40 + "\n\n")

        f.write(f"Original FBX morph targets: {len(all_blendshapes)}\n")
        f.write(f"Azure required blendshapes: {len(AZURE_BLENDSHAPES)}\n")
        f.write(f"Azure rotation parameters: {len(AZURE_ROTATIONS)}\n")
        f.write(f"Total Azure parameters: {len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS)}\n\n")

        f.write("Ratio analysis:\n")
        ratio = len(all_blendshapes) / len(AZURE_BLENDSHAPES)
        f.write(f"  Original has {ratio:.1f}x more morphs than Azure requires\n")

        # Find which Azure blendshapes are present in original
        original_set = set(all_blendshapes)
        azure_set = set(AZURE_BLENDSHAPES)
        found_azure = azure_set.intersection(original_set)
        missing_azure = azure_set - original_set

        f.write(f"\nAzure blendshapes found in original: {len(found_azure)}/{len(AZURE_BLENDSHAPES)}\n")
        if missing_azure:
            f.write(f"Missing Azure blendshapes: {len(missing_azure)}\n")
            for missing in sorted(missing_azure):
                f.write(f"  - {missing}\n")

    print(f"\n📄 Documentation files created:")
    print(f"  - {original_morphs_file.name} ({len(all_blendshapes)} morph targets)")
    print(f"  - {original_morphs_json.name}")
    print(f"  - {azure_blendshapes_file.name} ({len(AZURE_BLENDSHAPES)} + {len(AZURE_ROTATIONS)} parameters)")
    print(f"  - {azure_blendshapes_json.name}")
    print(f"  - {comparison_file.name}")
    print(f"\n✅ Complete lists extracted successfully!")


if __name__ == "__main__":
    extract_and_document_morph_targets()
