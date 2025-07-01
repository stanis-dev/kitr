# Project Development Preferences

## Core Philosophy

This project follows a **fail-fast, zero-fallback** approach with deterministic behavior.

## Required Dependencies

- **Python 3.8+**
- **Blender** (accessible via `blender` command)
- **Dependencies**: Install via `pip install -r requirements.txt`

## File Structure

```
kitr/
├── pipeline.py                        # Main orchestrator
├── input-file.fbx                     # Input file (hardcoded name)
├── azure_optimized.fbx                # Output from step 2
├── requirements.txt                   # Dependencies
│
├── step1_validation/                  # Validation logic
├── step2_morphs/                      # Azure optimization
├── step3_glb/                         # GLB conversion
└── step4_render/                      # Animation validation
```

## Development Guidelines

### Code Standards
- Line length: 120 characters
- Fail fast - no fallbacks or graceful degradation
- Single execution path only
- No configuration files or CLI arguments

### Dependencies
- NO optional dependencies
- NO try/except import fallbacks
- Dependencies either work or tool crashes

### File Immutability
Each step produces new output files while preserving the original input:
- `input-file.fbx` → `azure_optimized.fbx` → `step3_glb/azure_optimized_web.glb`

## IDE Configuration

Includes:
- `.vscode/settings.json` - Editor preferences
- `.editorconfig` - Cross-editor consistency

## Pipeline Flow

1. **Step 1**: FBX validation (structure & blendshapes)
2. **Step 2**: Azure optimization (52 blendshapes)
3. **Step 3**: GLB conversion
4. **Step 4**: Animation validation
