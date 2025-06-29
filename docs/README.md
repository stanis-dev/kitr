# Documentation - Morph Targets and Blendshapes

This directory contains complete documentation of morph targets (blendshapes) for the MetaHuman FBX processing pipeline.

## Overview

The MetaHuman FBX file contains **823 morph targets**, while Azure Cognitive Services expects only **55 parameters** (52 facial blendshapes + 3 rotation parameters). This documentation provides complete, untruncated lists of both sets.

## Files in this Directory

### Original FBX Morph Targets

- **`original_fbx_morph_targets_complete.txt`** - Human-readable list of all 823 morph targets from the input FBX file
- **`original_fbx_morph_targets_complete.json`** - Machine-readable JSON format of the same data

### Azure Blendshapes Reference

- **`azure_blendshapes_complete.txt`** - Human-readable list of all 55 Azure parameters (52 blendshapes + 3 rotations)
- **`azure_blendshapes_complete.json`** - Machine-readable JSON format with detailed structure

### Analysis and Comparison

- **`morph_targets_comparison.txt`** - Summary comparing original FBX targets vs Azure requirements
- **`extract_morph_targets.py`** - Script used to generate this documentation

## Key Statistics

| Metric | Value |
|--------|-------|
| Original FBX morph targets | 823 |
| Azure facial blendshapes | 52 |
| Azure rotation parameters | 3 |
| Total Azure parameters | 55 |
| Ratio (Original:Azure) | 15.8:1 |

## Important Notes

### No Truncated Output
All files contain **complete**, untruncated lists. No data has been omitted due to length constraints.

### Azure Blendshape Mapping
The comparison analysis shows that **0 of 52** Azure blendshapes have exact name matches in the original FBX. This is expected because:
- MetaHuman uses different naming conventions (e.g., `_L`/`_R` suffixes instead of `Left`/`Right`)
- The pipeline includes a mapping step to handle these naming differences
- Step 2 of the pipeline performs automatic renaming and mapping

### File Sizes
- Original FBX morph targets: ~39KB (823 entries)
- Azure blendshapes: ~1.4KB (55 entries)
- Total documentation: ~83KB

## Usage

### For Developers
Use the JSON files for programmatic access:
```python
import json

# Load original morph targets
with open('original_fbx_morph_targets_complete.json') as f:
    original_data = json.load(f)
    print(f"Total morphs: {original_data['total_count']}")

# Load Azure blendshapes
with open('azure_blendshapes_complete.json') as f:
    azure_data = json.load(f)
    print(f"Azure facial: {azure_data['total_facial_count']}")
```

### For Review
Use the text files for manual inspection:
- `original_fbx_morph_targets_complete.txt` - Browse all MetaHuman morphs
- `azure_blendshapes_complete.txt` - Reference Azure requirements
- `morph_targets_comparison.txt` - Quick overview and analysis

## Pipeline Context

This documentation supports the MetaHuman-to-Azure pipeline:

1. **Step 1**: Validation (identifies 823 morph targets)
2. **Step 2**: Azure mapping (maps to 52 required blendshapes)
3. **Step 3**: Cleanup (removes excess morphs)
4. **Steps 4-6**: Conversion and optimization

## Regenerating Documentation

To regenerate this documentation:
```bash
cd docs
python extract_morph_targets.py
```

**Requirements**: Blender must be installed and available in PATH.

---

*Generated automatically by extract_morph_targets.py*
*All data extracted from: input-file.fbx*
