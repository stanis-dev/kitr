#!/usr/bin/env python3
"""
Snapshot test to preserve exact functionality of MetaHuman FBX Validator.
This is the ONLY test file - exists solely to prevent regression during iteration.

Expected behavior captured on 2024-06-29:
- Blender 4.4.3 detection
- 823/52 blendshapes found
- 1574 bones found
- Exit code 0 (success)
"""

import re
import subprocess
import sys
from pathlib import Path


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI color codes from text."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def test_validation_snapshot():
    """Snapshot test - preserves exact current behavior."""

    # Expected results from current working state
    EXPECTED_BLENDSHAPE_COUNT = 823
    EXPECTED_BONE_COUNT = 1574
    EXPECTED_EXIT_CODE = 0
    EXPECTED_OUTPUT_CONTAINS = [
        "🎭 MetaHuman FBX Validator",
        "✅ Blender installation",
        "  Found Blender: 4.4.3",
        "✅ File exists",
        "  Size: 18.9MB",
        "✅ Blender processing",
        "  Processing FBX with Blender",
        "  Successfully processed FBX",
        "✅ Blendshape count",
        f"  Found {EXPECTED_BLENDSHAPE_COUNT}/52",
        f"✅ Found {EXPECTED_BLENDSHAPE_COUNT}/52 blendshapes",
        f"ℹ️  Found {EXPECTED_BONE_COUNT} bones",
        "✅ Completed: FBX Validation",
        "📋 Status: ✅ VALID",
        f"🎭 Blendshapes: {EXPECTED_BLENDSHAPE_COUNT}/52",
        f"🦴 Bones: {EXPECTED_BONE_COUNT}",
        "🎉 Done!"
    ]

    # Verify input file exists
    input_file = Path("input-file.fbx")
    assert input_file.exists(), "input-file.fbx must exist for snapshot test"
    assert input_file.stat().st_size > 19_000_000, "input-file.fbx size sanity check"

    # Run validation
    result = subprocess.run(
        [sys.executable, "validate.py"],
        capture_output=True,
        text=True,
        timeout=120
    )

    # Verify exact exit code
    assert result.returncode == EXPECTED_EXIT_CODE, f"Expected exit code {EXPECTED_EXIT_CODE}, got {result.returncode}"

    # Strip ANSI color codes from output
    clean_output = strip_ansi_codes(result.stdout)

    # Verify all expected output is present
    for expected_text in EXPECTED_OUTPUT_CONTAINS:
        assert expected_text in clean_output, f"Expected text missing from output: {expected_text}"

    # Verify no errors in stderr (should be empty)
    assert result.stderr == "", f"Unexpected stderr output: {result.stderr}"

    # Verify blendshape count precision
    assert f"  Found {EXPECTED_BLENDSHAPE_COUNT}/52" in clean_output
    assert f"✅ Found {EXPECTED_BLENDSHAPE_COUNT}/52 blendshapes" in clean_output
    assert f"🎭 Blendshapes: {EXPECTED_BLENDSHAPE_COUNT}/52" in clean_output

    # Verify bone count precision
    assert f"ℹ️  Found {EXPECTED_BONE_COUNT} bones" in clean_output
    assert f"🦴 Bones: {EXPECTED_BONE_COUNT}" in clean_output

    print(f"✅ Snapshot test PASSED")
    print(f"   - Exit code: {result.returncode}")
    print(f"   - Blendshapes: {EXPECTED_BLENDSHAPE_COUNT}/52")
    print(f"   - Bones: {EXPECTED_BONE_COUNT}")
    print(f"   - All expected output present")


if __name__ == "__main__":
    try:
        test_validation_snapshot()
        print("\n🎯 SNAPSHOT PRESERVED - Current functionality locked in")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 SNAPSHOT FAILED - Functionality has changed!")
        print(f"Error: {e}")
        sys.exit(1)
