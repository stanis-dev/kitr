# New Pipeline Architecture - 5-Step Unreal Engine MetaHuman Export

**Refactor Branch:** refactor-v2
**Status:** 🚧 SKELETON PHASE - Structure Only

## Pipeline Overview

This new pipeline processes MetaHuman assets entirely within Unreal Engine, then exports optimized GLB files for web use. The approach leverages Epic's DCC Export assembly for deterministic, repeatable results.

## 5-Step Architecture

### Step 1: Duplicate & Prepare Asset (`step1_duplicate/`)
**Purpose:** Asset duplication and morph baking preparation
- Duplicate MetaHuman Character asset to temporary package
- Preserve original asset integrity (never modify source)
- Prepare temp asset for baking operations
- Reduce to 52 Azure-compatible morph targets

**Input:** Original MetaHuman Character asset
**Output:** Temporary duplicate with 52 morphs
**Entry Point:** `step1_duplicate/asset_duplicator.py`

### Step 2: DCC Export Assembly (`step2_dcc_export/`)
**Purpose:** Run Epic's DCC Export pipeline
- Call `MetaHumanCharacter.RunAssembly("DCC Export")` on temp asset
- Generate combined skeletal mesh (head + body at highest LOD)
- Produce standardized, deterministic export structure
- Include all morph targets and skeletal data

**Input:** Temp asset with 52 morphs
**Output:** Combined skeletal mesh asset + DCC export folder
**Entry Point:** `step2_dcc_export/dcc_assembler.py`

### Step 3: FBX Export (`step3_fbx_export/`)
**Purpose:** Export combined mesh as FBX
- Retrieve generated combined skeletal mesh asset
- Execute Unreal's FBX export via Python/commandlet
- Include skeleton, skin, and all 52 morph targets
- Preserve eye and head bones for external rotation control

**Input:** Combined skeletal mesh asset
**Output:** Deterministic FBX file with full rig
**Entry Point:** `step3_fbx_export/fbx_exporter.py`

### Step 4: GLB Convert (`step4_glb_convert/`)
**Purpose:** Convert FBX to glTF (GLB) format
- Use headless Blender instance for conversion
- Preserve blendshapes (shape keys) and skeletal bones
- Automated via Blender Python API (no GUI)
- Export to glTF 2.0 with Shape Keys enabled

**Input:** FBX file with 52 morph targets
**Output:** GLB file with geometry, bones, and morphs
**Entry Point:** `step4_glb_convert/blender_converter.py`

### Step 5: Web Optimize (`step5_web_optimize/`)
**Purpose:** Optimize GLB for web delivery
- Use gltf-transform (v4.x) for optimization
- Apply Draco compression for vertex data
- Convert textures to WebP format
- Remove extraneous data while preserving morph targets

**Input:** Unoptimized GLB file
**Output:** Web-optimized GLB ready for Babylon.js
**Entry Point:** `step5_web_optimize/web_optimizer.py`

## Key Design Principles

1. **Deterministic Pipeline:** Every run produces identical results for same input
2. **Asset Immutability:** Original MetaHuman assets never modified
3. **Epic Integration:** Leverages Unreal Engine's built-in DCC Export
4. **Web Optimization:** Final output optimized for Babylon.js/WebGL
5. **Morph Preservation:** 52 Azure morph targets maintained throughout

## File Flow

```
Original MetaHuman Asset
    ↓ (step1_duplicate)
Temp Asset (52 morphs)
    ↓ (step2_dcc_export)
Combined Skeletal Mesh + DCC Export
    ↓ (step3_fbx_export)
Deterministic FBX
    ↓ (step4_glb_convert)
GLB with morphs/bones
    ↓ (step5_web_optimize)
Web-optimized GLB (final)
```

## Implementation Status

- [x] Directory structure created
- [x] Pipeline roadmap documented
- [ ] Step 1: Asset duplication logic
- [ ] Step 2: DCC Export integration
- [ ] Step 3: FBX export automation
- [ ] Step 4: Blender conversion pipeline
- [ ] Step 5: gltf-transform optimization
- [ ] Main pipeline orchestrator
- [ ] Error handling and validation
- [ ] Documentation and testing

## Next Steps

1. Implement Step 1 asset duplication
2. Set up Unreal Engine Python environment
3. Create DCC Export integration
4. Build Blender automation scripts
5. Integrate gltf-transform optimization
