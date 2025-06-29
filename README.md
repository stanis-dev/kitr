# MetaHuman FBX to GLB Pipeline

Complete pipeline for processing MetaHuman FBX files into optimized GLB format with Azure viseme support.

## Pipeline Overview

```
input-file.fbx → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6 → output-final-avatar.glb
```

**Current Implementation Status:**
- ✅ **Step 1**: FBX Validation & Azure Blendshape Check
- ✅ **Step 2**: Azure Blendshape Mapping & Renaming
- 🚧 **Step 3**: Cleanup Unused Morphs & Skeleton *(planned)*
- 🚧 **Step 4**: FBX to GLB Conversion *(planned)*
- 🚧 **Step 5**: Texture Resolution Optimization *(planned)*
- 🚧 **Step 6**: Final Validation & Babylon.js Compatibility *(planned)*

## Requirements

- **Blender** (any recent version 3.0+) installed and accessible from command line
- **Python 3** with pip
- Input file must be named `input-file.fbx` in project root

## Installation

1. Install Blender from [blender.org](https://www.blender.org/download/)
2. Ensure `blender` command is available in your PATH
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Single Entry Point (Recommended)

Run the complete pipeline:
```bash
python3 pipeline.py
```

This will:
1. Check all prerequisites (Blender, input file, scripts)
2. Show pipeline overview and file outputs
3. Execute all implemented steps in sequence
4. Provide comprehensive progress logging
5. Display final summary with file status

### Individual Steps

You can also run individual steps:

```bash
# Step 1: Validation only
python3 validate.py

# Step 2: Azure blendshape mapping
python3 step2_morphs.py
```

## File Immutability

🔒 **Critical Design Principle**: The original `input-file.fbx` is **never modified**. Each step reads from the input and produces a new output file:

- **Input**: `input-file.fbx` (preserved)
- **Step 1**: Validation report only
- **Step 2**: `output-step2-azure.fbx`
- **Step 3**: `output-step3-cleaned.fbx` *(planned)*
- **Step 4**: `output-step4-converted.glb` *(planned)*
- **Step 5**: `output-step5-optimized.glb` *(planned)*
- **Step 6**: `output-final-avatar.glb` *(planned)*

## What Each Step Does

### Step 1: FBX Validation & Azure Blendshape Check
- Validates Blender installation
- Processes FBX using Blender headless mode
- Extracts and counts facial blendshapes (expects 823 from MetaHuman)
- Checks for Azure-compatible blendshape names
- Extracts bone structure information
- Reports validation status and warnings

### Step 2: Azure Blendshape Mapping & Renaming
- Reads input-file.fbx and processes all blendshapes
- Maps MetaHuman blendshapes to Azure naming convention where possible
- Creates output-step2-azure.fbx with any renamed blendshapes
- Reports mapping summary (expected: 0 direct matches for MetaHuman files)

## Technical Notes

- **Fail-Fast**: Pipeline stops immediately on errors - no fallbacks
- **Deterministic**: Single execution path, no configuration options
- **Comprehensive Logging**: Rich console output with step-by-step progress
- **Blender-Based**: All FBX processing uses Blender's robust FBX support

## Expected Behavior for MetaHuman Files

MetaHuman exports typically:
- Contain ~823 blendshapes with UE naming (not Azure compatible)
- Require mapping/renaming for Azure viseme support
- Have complex bone structures (~1574 bones)
- Step 1 will show warnings about missing Azure blendshapes (expected)
- Step 2 will report 0 direct matches and 52 missing Azure blendshapes (expected)
