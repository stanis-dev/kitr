# Archived Original Pipeline

**Date Archived:** $(date)
**Git Reference:** pre-refactor-stable branch, v1.0-pre-refactor tag

This directory contains the original MetaHuman FBX processing pipeline that was replaced during the refactor to the new Unreal Engine DCC Export-based architecture.

## Original Architecture (ARCHIVED)

The original pipeline processed FBX files through 4 main steps:

### Original Steps:
1. **step1_validation/** - FBX structure validation & Azure blendshape check
2. **step2_morphs/** - Azure FBX optimization (PERFECT - 52 morphs, 93.7% cleanup)
3. **step3_glb/** - FBX to GLB conversion using Blender
4. **step4_render/** - GLB animation validation and rendering

### Key Achievements (Original):
- ✅ **52/52 Azure blendshapes** (100% compatibility)
- ✅ **93.7% morph cleanup** (823 → 52 morphs)
- ✅ **18.1 MB optimized output**
- ✅ **Production ready** for Azure Cognitive Services

## Accessing Original Code

### Git References:
```bash
# Switch to stable backup branch
git checkout pre-refactor-stable

# View tagged version
git show v1.0-pre-refactor

# Compare with current
git diff pre-refactor-stable..refactor-v2
```

### Key Files for Reference:
- **`old_pipeline.py`** - Original orchestrator
- **`step2_morphs/azure_processor.py`** - Perfect Azure optimization logic
- **`step2_morphs/cleanup_processor.py`** - Morph target cleanup (reusable)
- **`step1_validation/validate.py`** - Validation patterns

## Reusable Components

Some components from the original pipeline may be valuable for the new architecture:

### Highly Reusable:
- **Azure mappings and constants** from step1_validation/constants.py
- **Morph target cleanup logic** from step2_morphs/cleanup_processor.py
- **Validation patterns** from step1_validation/validate.py
- **Logger system** (already preserved in main logger/ directory)

### Reference Material:
- **docs/** directory (preserved) - Azure parameters and mappings
- **step2_morphs/** - Perfect Azure optimization example
- **Error handling patterns** from original pipeline.py

## Migration Notes

The new pipeline architecture in the main directory follows the same principles but with a different approach:
- **Old:** FBX input → Azure optimization → GLB output
- **New:** Unreal Engine asset → DCC Export → FBX → GLB → Web optimization

Both maintain:
- File immutability principle
- 52 Azure morph targets
- Comprehensive validation
- Step-by-step processing
