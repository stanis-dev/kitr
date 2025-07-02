#!/usr/bin/env python3
"""
MetaHuman FBX Validator

Blender-based validation script for input-file.fbx
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from step1_validation.validation import validate_fbx
from logger import setup_logging


def main():
    """Validate input-file.fbx - that's it!"""
    setup_logging(level="normal")

    # Find input file - look in current directory first, then parent
    input_file = Path("input-file.fbx")
    if not input_file.exists():
        input_file = Path("../input-file.fbx")

    if not input_file.exists():
        print(f"❌ File not found: input-file.fbx (checked current dir and parent dir)")
        return 1

    print("🎭 MetaHuman FBX Validator")
    print("=" * 30)

    print(f"📁 File: {input_file}")
    print(f"📊 Size: {input_file.stat().st_size / (1024*1024):.1f} MB")
    print()

    # No safeguards - fail fast if Blender is not available
    result = validate_fbx(input_file)

    status = "✅ VALID" if result.is_valid else "❌ INVALID"
    print(f"📋 Status: {status}")
    print(f"🎭 Blendshapes: {len(result.found_blendshapes)}/52")
    print(f"🦴 Bones: {len(result.found_bones)}")

    if result.errors:
        print(f"❌ Errors: {len(result.errors)}")

    if result.warnings:
        print(f"⚠️  Warnings: {len(result.warnings)}")

    print("=" * 30)
    print("🎉 Done!" if result.is_valid else "💥 Failed!")

    return 0 if result.is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
