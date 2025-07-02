# Step 1: MetaHuman Project Validation

**Single deterministic validation path for MetaHuman projects before FBX to GLB conversion.**

## Overview

Step 1 implements a comprehensive 10-step validation roadmap that ensures MetaHuman projects are fully ready for the FBX to GLB conversion pipeline. This is the **only validation path** - deterministic and atomic.

## 10-Step Validation Roadmap

Each sub-task is atomic, has clear input/output types, and testable success/failure criteria:

| #   | Sub-task                    | Input                | Output                          | Success Criteria                           |
|-----|-----------------------------|--------------------- |---------------------------------|--------------------------------------------|
| 1.1 | Locate Project              | `uproj_path: str`    | `ProjectPathInfo`               | File exists, ends with `.uproject`        |
| 1.2 | Read Engine Version         | `ProjectPathInfo`    | `EngineVersion`                 | Major=5, Minor=6 (UE 5.6.x)              |
| 1.3 | Check MetaHuman Plugins     | `ProjectPathInfo`    | `List[PluginStatus]`            | All required plugins found in UE install  |
| 1.4 | Open Project Headless       | `ProjectPathInfo`    | `SessionToken`                  | UE session launches, assets load          |
| 1.5 | Enumerate MetaHumans        | `SessionToken`       | `List[MetaHumanAsset]`          | ≥1 MetaHuman asset found                  |
| 1.6 | Quick-Health Check          | `List[MetaHumanAsset]` | `List[MetaHumanHealthReport]` | LOD0, ≥700 morphs, head/eye bones         |
| 1.7 | Artist-Facing Readiness Report | `List[MetaHumanHealthReport]` | `README.md` | Markdown report generated        |
| 1.8 | Duplicate Working Copy      | `List[MetaHumanHealthReport]` | `List[TempAssetPath]` | Working copies created       |
| 1.9 | Lock Original               | `List[MetaHumanHealthReport]` | `bool`      | Original assets protected              |
| 1.10| Emit Step-1 Checkpoint      | All previous results | `Step1Checkpoint`               | JSON checkpoint with all validation data   |

## Required MetaHuman Plugins (UE 5.6)

Step 1 validates these plugins exist in the UE installation:

- **MetaHumanCharacter** - Core MetaHuman character system
- **MetaHumanSDK** - MetaHuman SDK for export/import
- **MetaHumanCoreTech** - Core technology library

## Architecture

### Files Structure

```
step1_duplicate/
├── asset_duplicator.py      # Main entry point
├── project_validator.py     # 10-step validation implementation
├── validation_models.py     # Data structures for all sub-tasks
└── __init__.py              # Module initialization
```

### Key Classes

- **`ProjectValidator`** - Main validation orchestrator
- **`ProjectPathInfo`** - Project location and validation state
- **`MetaHumanHealthReport`** - Individual asset health status
- **`Step1Checkpoint`** - Final validation results and checkpoint data

### Data Flow

```
User Input (.uproject path)
    ↓
ProjectValidator.execute_validation()
    ↓
10 Sequential Sub-tasks (atomic)
    ↓
Step1Checkpoint (success/failure + data)
    ↓
Pipeline continues to Step 2
```

## Usage

### From Pipeline
```python
from step1_duplicate.asset_duplicator import main

# Execute Step 1 validation
project_path = main("/path/to/project.uproject")
if project_path:
    print("Step 1 validation successful")
else:
    print("Step 1 validation failed")
```

### Direct Validation
```python
from step1_duplicate.project_validator import ProjectValidator

validator = ProjectValidator()
checkpoint = validator.execute_validation("/path/to/project.uproject")

if checkpoint.success:
    print(f"Ready characters: {checkpoint.healthy_characters}")
else:
    print(f"Validation failed: {checkpoint.error}")
```

## Validation Outputs

### Checkpoint Data (`artifacts/step1_checkpoint.json`)
```json
{
  "success": true,
  "project_path": "/path/to/project",
  "engine_version": "5.6.0",
  "plugins": [...],
  "metahumans": [...],
  "healthy_characters": ["ada", ...],
  "temp_asset_paths": [...],
  "timestamp": "2024-01-01T12:00:00"
}
```

### Readiness Report (`artifacts/metahuman_readiness_report.md`)
Artist-friendly markdown report with:
- Character health status
- Issues requiring fixes
- Pipeline readiness recommendations

## Health Check Criteria

For each MetaHuman asset to be considered "healthy":

- ✅ **LOD0 exists** - Base mesh level of detail
- ✅ **≥700 morph targets** - Pre-prune requirement for full facial animation
- ✅ **Head bone present** - Required for head tracking
- ✅ **Eye bones present** - Required for eye movement (eye_l, eye_r)

## Fast-Fail Behavior

The validation **stops immediately** on the first critical failure:
- Invalid project path
- Unsupported engine version
- Missing required plugins
- No MetaHuman assets found

## Production vs Simulation

Currently runs in **simulation mode** for development. In production:
- Step 1.4: Actually launches UE5.6 headless
- Step 1.5: Uses `unreal.AssetRegistryHelpers` for real asset enumeration
- Step 1.6: Loads actual skeletal meshes for validation
- Step 1.8: Uses `unreal.EditorAssetLibrary.duplicate_asset()`
- Step 1.9: Sets real filesystem read-only permissions

## Error Handling

All errors are:
- **Logged clearly** with specific context
- **Structured** in ValidationResult objects
- **Propagated** to checkpoint for debugging
- **Fast-failing** to prevent wasted processing

## Integration

Step 1 is fully integrated with the pipeline validation system and provides structured output for Steps 2-5 to consume. The checkpoint data contains all necessary information for subsequent pipeline stages.
