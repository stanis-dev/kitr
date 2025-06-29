#!/usr/bin/env python3
"""
Example usage of the MetaHuman FBX validation functionality.

This script demonstrates how to validate FBX files for MetaHuman conversion.
"""

import sys
import tempfile
from pathlib import Path

# Add the package to the path for local testing
sys.path.insert(0, str(Path(__file__).parent))

from metahuman_converter.validation import validate_fbx, ValidationResult
from metahuman_converter.logging_config import setup_logging
from metahuman_converter.constants import ARKIT_BLENDSHAPES


def create_example_fbx_files():
    """Create some example FBX files for testing validation."""
    examples = {}
    
    # Create example files with different names to trigger different behaviors
    for scenario in ["complete", "missing", "extra", "noskeleton", "minimal"]:
        tmp_file = tempfile.NamedTemporaryFile(
            suffix=f"_{scenario}.fbx", 
            delete=False
        )
        tmp_file.write(b"Mock FBX content for testing")
        tmp_file.close()
        examples[scenario] = tmp_file.name
    
    return examples


def demonstrate_validation():
    """Demonstrate the FBX validation functionality."""
    print("=== MetaHuman FBX Validation Demo ===\n")
    
    # Setup logging
    setup_logging(level="INFO")
    
    # Create example files
    print("Creating example FBX files...")
    example_files = create_example_fbx_files()
    
    try:
        # Test each scenario
        for scenario, file_path in example_files.items():
            print(f"\n--- Testing {scenario.upper()} scenario ---")
            print(f"File: {Path(file_path).name}")
            
            try:
                # Validate the FBX file
                report = validate_fbx(file_path)
                
                # Display results
                print(f"Overall Result: {report.overall_result.value.upper()}")
                print(f"Valid: {report.is_valid}")
                print(f"File Size: {report.file_size_mb:.2f} MB")
                print(f"Found Blendshapes: {len(report.found_blendshapes)}")
                print(f"Missing Blendshapes: {len(report.missing_blendshapes)}")
                print(f"Found Bones: {len(report.found_bones)}")
                print(f"Missing Bones: {len(report.missing_bones)}")
                print(f"Extra Blendshapes: {len(report.extra_blendshapes)}")
                
                # Show issues if any
                if report.issues:
                    print(f"Issues ({len(report.issues)}):")
                    for i, issue in enumerate(report.issues, 1):
                        print(f"  {i}. [{issue.level.value.upper()}] {issue.message}")
                        if issue.details:
                            for key, value in issue.details.items():
                                if isinstance(value, list) and len(value) > 3:
                                    print(f"     {key}: {value[:3]}... (+{len(value)-3} more)")
                                else:
                                    print(f"     {key}: {value}")
                else:
                    print("No issues found!")
                    
            except Exception as e:
                print(f"ERROR: {e}")
    
    finally:
        # Cleanup example files
        print("\nCleaning up example files...")
        for file_path in example_files.values():
            try:
                Path(file_path).unlink()
            except FileNotFoundError:
                pass


def demonstrate_custom_validation():
    """Demonstrate validation with custom requirements."""
    print("\n\n=== Custom Validation Demo ===\n")
    
    # Create a minimal test file
    tmp_file = tempfile.NamedTemporaryFile(suffix="_minimal.fbx", delete=False)
    tmp_file.write(b"Mock minimal FBX content")
    tmp_file.close()
    
    try:
        # Test with custom requirements
        custom_blendshapes = ["mouthOpen", "mouthClose", "mouthSmileLeft", "mouthSmileRight"]
        custom_bones = ["root", "head"]
        
        print("Testing with custom requirements:")
        print(f"Required blendshapes: {custom_blendshapes}")
        print(f"Required bones: {custom_bones}")
        
        report = validate_fbx(
            tmp_file.name,
            required_blendshapes=custom_blendshapes,
            required_bones=custom_bones,
            strict_mode=False
        )
        
        print(f"\nResult: {report.overall_result.value.upper()}")
        print(f"Valid: {report.is_valid}")
        
        if report.missing_blendshapes:
            print(f"Missing blendshapes: {list(report.missing_blendshapes)}")
        if report.missing_bones:
            print(f"Missing bones: {list(report.missing_bones)}")
            
    finally:
        Path(tmp_file.name).unlink()


def show_arkit_blendshapes():
    """Display information about the ARKit blendshapes."""
    print("\n\n=== ARKit Blendshapes Reference ===\n")
    
    print(f"Total ARKit blendshapes: {len(ARKIT_BLENDSHAPES)}")
    print("\nBlendshapes by category:")
    
    categories = {
        "Eye": [bs for bs in ARKIT_BLENDSHAPES if bs.startswith("eye")],
        "Jaw": [bs for bs in ARKIT_BLENDSHAPES if bs.startswith("jaw")],
        "Mouth": [bs for bs in ARKIT_BLENDSHAPES if bs.startswith("mouth")],
        "Brow": [bs for bs in ARKIT_BLENDSHAPES if bs.startswith("brow")],
        "Cheek": [bs for bs in ARKIT_BLENDSHAPES if bs.startswith("cheek")],
        "Nose": [bs for bs in ARKIT_BLENDSHAPES if bs.startswith("nose")],
        "Other": [bs for bs in ARKIT_BLENDSHAPES if not any(bs.startswith(prefix) 
                 for prefix in ["eye", "jaw", "mouth", "brow", "cheek", "nose"])]
    }
    
    for category, blendshapes in categories.items():
        if blendshapes:
            print(f"\n{category} ({len(blendshapes)}):")
            for bs in blendshapes:
                print(f"  - {bs}")


if __name__ == "__main__":
    try:
        demonstrate_validation()
        demonstrate_custom_validation()
        show_arkit_blendshapes()
        print("\n=== Demo Complete ===")
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        sys.exit(1)