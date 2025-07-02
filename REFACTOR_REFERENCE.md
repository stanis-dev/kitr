# Pre-Refactor Architecture Reference

**Date:** $(date)
**Git Tag:** v1.0-pre-refactor
**Backup Branch:** pre-refactor-stable

## Current Architecture Overview

This document serves as a reference for the working architecture before the major refactor.

### Main Pipeline (`pipeline.py`)
- **Purpose:** Single entry point orchestrator
- **Pattern:** Step-by-step subprocess execution
- **Current Steps:** 7 planned (4 implemented)
- **Key Features:**
  - File immutability principle
  - Comprehensive prerequisite checking
  - Detailed progress reporting
  - Error handling with rollback capability

### Step Structure

#### Step 1: Validation (`step1_validation/`)
- **Entry:** `validate.py`
- **Purpose:** FBX structure validation & Azure blendshape check
- **Output:** Validation report only
- **Key Files:**
  - `constants.py` - Azure mappings & parameters
  - `validation.py` - Validation logic

#### Step 2: Morphs (`step2_morphs/`)
- **Entry:** `azure_processor.py`
- **Purpose:** Azure FBX optimization (COMPLETE & PERFECT)
- **Output:** `azure_optimized.fbx` (18.1 MB, 52 Azure blendshapes)
- **Key Achievement:** 93.7% morph cleanup (823 → 52 morphs)
- **Key Files:**
  - `morph_processor.py` - Azure blendshape mapping
  - `bone_processor.py` - Bone structure analysis
  - `cleanup_processor.py` - Morph target cleanup
  - `validate_clean_fbx.py` - Final validation

#### Step 3: GLB Conversion (`step3_glb/`)
- **Entry:** `simple_converter.py`
- **Purpose:** FBX to GLB conversion
- **Output:** `step3_glb/azure_optimized_web.glb`

#### Step 4: Render (`step4_render/`)
- **Entry:** `glb_animator.py`
- **Purpose:** GLB animation validation
- **Output:** Animation validation report + rendered frames

### Documentation (`docs/`)
- **Python modules with IDE support**
- **Complete Azure parameter definitions**
- **Mapping utilities and validation functions**
- **Original FBX morph documentation (823 morphs)**

### Logger (`logger/`)
- **Centralized logging system**
- **Configurable log levels**
- **Core logging utilities**

## Key Design Patterns

1. **File Immutability:** Original input-file.fbx never modified
2. **Step Isolation:** Each step produces new output files
3. **Comprehensive Validation:** Each step validates its output
4. **Modular Architecture:** Clear separation of concerns
5. **Error Recovery:** Failed steps don't corrupt previous work

## Success Metrics (Current)

- ✅ **52/52 Azure blendshapes** (100% compatibility)
- ✅ **3/3 Azure rotations** supported
- ✅ **Zero excess morph targets** (perfect cleanup)
- ✅ **Complete validation passed** (Azure-certified)
- ✅ **18.1 MB optimized output**
- ✅ **Production ready** for Azure Cognitive Services

## Reference Commands

### Switch to stable backup:
```bash
git checkout pre-refactor-stable
```

### Compare with current:
```bash
git diff pre-refactor-stable..main
```

### View this tag:
```bash
git show v1.0-pre-refactor
```

### Run current pipeline:
```bash
python pipeline.py
```

## Files to Reference During Refactor

### Core Logic:
- `pipeline.py` - Orchestration patterns
- `step2_morphs/azure_processor.py` - Perfect Azure optimization
- `docs/azure_blendshapes_complete.py` - Azure parameter definitions

### Validation Patterns:
- `step1_validation/validate.py` - Validation architecture
- `step2_morphs/validate_clean_fbx.py` - Validation examples

### Documentation:
- `docs/metahuman_to_azure_mappings.py` - Mapping utilities
- `docs/validation_requirements.py` - Validation specs

## Notes for Refactor

- Step 2 is PERFECT and may be reusable as-is
- Validation patterns are well-established
- File immutability principle should be preserved
- Documentation architecture provides good IDE support
- Logger system is comprehensive and reusable
