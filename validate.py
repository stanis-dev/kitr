#!/usr/bin/env python3
"""
MetaHuman FBX Validator

Blender-based validation script for input-file.fbx
"""

import sys
import logging
from pathlib import Path

# Add current directory to path for direct imports
sys.path.insert(0, '.')

from metahuman_converter.validation import validate_fbx
from metahuman_converter.logging_config import setup_logging


def main():
    """Validate input-file.fbx - that's it!"""
    setup_logging(level=logging.INFO)
    
    input_file = Path("input-file.fbx")
    
    print("🎭 MetaHuman FBX Validator")
    print("=" * 30)
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return 1
    
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