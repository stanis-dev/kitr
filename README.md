# MetaHuman FBX to GLB Pipeline

A pipeline for converting MetaHuman FBX files to optimized GLB format with Azure Cognitive Services compatibility.

## Project Structure

```
kitr/
├── README.md                          # This file
├── pipeline.py                        # Main pipeline orchestrator
├── input-file.fbx                     # Input MetaHuman FBX file
├── azure_optimized.fbx                # Output from step 2 (Azure optimized)
├── requirements.txt                   # Python dependencies
│
├── docs/                              # Reference documentation
│   ├── README.md                      # Documentation overview
│   ├── azure_blendshapes_complete.*   # Azure blendshape reference
│   └── original_fbx_morph_targets.*   # Original morph reference
│
├── step1_validation/                  # FBX validation
│   ├── validate.py                    # Main validation entry point
│   ├── validation.py                  # Validation logic
│   ├── constants.py                   # Azure mappings & constants
│   └── logging_config.py              # Logging configuration
│
├── step2_morphs/                      # Azure optimization
│   ├── azure_processor.py             # Main step 2 entry point
│   ├── morph_processor.py             # Blendshape mapping
│   ├── bone_processor.py              # Bone structure analysis
│   ├── cleanup_processor.py           # Morph cleanup
│   └── validate_clean_fbx.py          # Final validation
│
├── step3_glb/                         # GLB conversion
│   ├── simple_converter.py            # FBX to GLB converter
│   └── __init__.py
│
└── step4_render/                      # Animation validation
    ├── glb_animator.py                # GLB animation validator
    └── README.md
```

## Quick Start

### Run Complete Pipeline:
```bash
python pipeline.py
```

### Run Individual Steps:
```bash
# Step 1: Validation
python step1_validation/validate.py

# Step 2: Azure Optimization
python step2_morphs/azure_processor.py

# Step 3: GLB Conversion
python step3_glb/simple_converter.py

# Step 4: Animation Validation
python step4_render/glb_animator.py
```

## Pipeline Flow

1. **Step 1**: Validates input FBX structure and blendshapes
2. **Step 2**: Optimizes for Azure Cognitive Services (52 blendshapes)
3. **Step 3**: Converts optimized FBX to GLB format
4. **Step 4**: Validates GLB animation compatibility

## Requirements

- Python 3.8+
- Blender 3.0+ (accessible via `blender` command)
- Dependencies: `pip install -r requirements.txt`

## File Immutability

Each step produces new output files while preserving the original input:

- `input-file.fbx` → `azure_optimized.fbx` → `step3_glb/azure_optimized_web.glb`

Original input file is never modified.
