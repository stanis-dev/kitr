#!/usr/bin/env python3
"""
Example usage of the MetaHuman FBX to GLB converter pipeline.

This script demonstrates how to use the validation functionality
and shows the expected workflow for the complete pipeline.
"""

import sys
from pathlib import Path

# Add the module to path for direct execution
sys.path.insert(0, str(Path(__file__).parent))

from metahuman_converter.validation import validate_fbx
from metahuman_converter.logging_config import setup_logging


def main():
    """Main example function."""
    print("🎭 MetaHuman FBX to GLB Converter - Example Usage\n")
    
    # Setup logging
    setup_logging()
    
    # Example 1: Validate a mock FBX file
    print("=" * 60)
    print("Example 1: FBX Validation")
    print("=" * 60)
    
    # Use the actual FBX file provided in the repository
    # This is a real MetaHuman FBX export for testing
    actual_fbx_path = Path("./input-file.fbx")
    
    print(f"Validating FBX file: {actual_fbx_path}")
    print("(Note: Using mock validation since FBX SDK is not available)\n")
    
    try:
        # Validate the FBX file
        result = validate_fbx(actual_fbx_path)
        
        # Display results
        print(f"\n📊 Validation Results:")
        print(f"   Valid: {'✅ Yes' if result.is_valid else '❌ No'}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Warnings: {len(result.warnings)}")
        print(f"   Blendshapes found: {len(result.found_blendshapes)}/52")
        print(f"   Bones found: {len(result.found_bones)}")
        
        if result.errors:
            print(f"\n❌ Errors:")
            for error in result.errors:
                print(f"   - {error}")
                
        if result.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                print(f"   - {warning}")
                
        if result.missing_blendshapes:
            print(f"\n🔍 Missing Blendshapes ({len(result.missing_blendshapes)}):")
            for missing in result.missing_blendshapes[:10]:  # Show first 10
                print(f"   - {missing}")
            if len(result.missing_blendshapes) > 10:
                print(f"   ... and {len(result.missing_blendshapes) - 10} more")
                
        if result.blendshape_mapping:
            print(f"\n🔄 Blendshape Name Mappings:")
            for original, mapped in result.blendshape_mapping.items():
                print(f"   {original} → {mapped}")
                
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1
    
    # Example 2: Show what the complete pipeline would look like
    print("\n" + "=" * 60)
    print("Example 2: Complete Pipeline Overview")
    print("=" * 60)
    
    print("""
The complete MetaHuman FBX to GLB pipeline would include these steps:

🔧 Step 1: FBX Validation (✅ Implemented)
   ✅ Check for required ARKit blendshapes
   ✅ Validate skeleton structure  
   ✅ Verify mesh geometry
   ✅ Analyze material setup

🔧 Step 2: Blendshape Processing (🚧 Next)
   - Map MetaHuman names to Azure ARKit standard
   - Remove unnecessary morph targets
   - Ensure exactly 52 facial blendshapes

🔧 Step 3: Skeleton Optimization (🚧 Planned)
   - Keep head and eye bones for rotations
   - Remove unused body bones if needed
   - Optimize bone hierarchy

🔧 Step 4: FBX to glTF Conversion (🚧 Planned)
   - Use FBX2glTF tool for conversion
   - Handle coordinate system transformation
   - Convert materials to PBR

🔧 Step 5: Texture Optimization (🚧 Planned)
   - Downscale textures to ≤1024x1024
   - Maintain quality while reducing size
   - Optimize for web performance

🔧 Step 6: Final Validation (🚧 Planned)
   - Validate GLB structure
   - Test Babylon.js compatibility
   - Verify Azure viseme mapping
    """)
    
    # Example 3: Show Azure blendshape integration
    print("\n" + "=" * 60)
    print("Example 3: Azure Integration")
    print("=" * 60)
    
    print("""
Azure Cognitive Services outputs 55 parameters for viseme animation:
- 52 ARKit facial blendshapes (indices 0-51)
- 3 rotation parameters (indices 52-54):
  * headRoll
  * leftEyeRoll  
  * rightEyeRoll

Example Azure viseme JSON structure:
{
    "offset": 0.0,
    "duration": 0.1,
    "blendshapes": [
        0.2,  // eyeBlinkLeft
        0.0,  // eyeLookDownLeft
        0.0,  // eyeLookInLeft
        // ... 49 more facial blendshapes
        0.0,  // tongueOut (index 51)
        5.2,  // headRoll (index 52) 
        0.0,  // leftEyeRoll (index 53)
        0.0   // rightEyeRoll (index 54)
    ]
}

The pipeline ensures your MetaHuman avatar can directly consume this data.
    """)
    
    print("\n🎉 Example completed! Next step: Implement blendshape processing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())