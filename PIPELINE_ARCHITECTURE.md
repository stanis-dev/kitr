# MetaHuman to Web GLB Pipeline Architecture

**Branch:** refactor-v2
**Status:** 🚧 SKELETON PHASE - Implementation Ready

## Pipeline Overview

This pipeline processes MetaHuman assets entirely within Unreal Engine, then exports optimized GLB files for web use. The approach leverages Epic's DCC Export assembly for deterministic, repeatable results and industry-standard compatibility.

## 5-Step Architecture

### Step 1: Ingest & Prepare Asset (`step1_ingest/`)

**Purpose:** Asset ingestion and morph baking preparation

-   Ingest MetaHuman Character asset to temporary package
-   Preserve original asset integrity (never modify source)
-   Prepare temp asset for baking operations
-   Reduce to 52 Azure-compatible morph targets

**Input:** Original MetaHuman Character asset
**Output:** Temporary working copy with 52 morphs
**Entry Point:** `step1_ingest/ingestor.py`

### Step 2: DCC Export Assembly (`step2_dcc_export/`)

**Purpose:** Run Epic's DCC Export pipeline

-   Call `MetaHumanCharacter.RunAssembly("DCC Export")` on temp asset
-   Generate combined skeletal mesh (head + body at highest LOD)
-   Produce standardized, deterministic export structure
-   Include all morph targets and skeletal data

**Input:** Temp asset with 52 morphs
**Output:** Combined skeletal mesh asset + DCC export folder
**Entry Point:** `step2_dcc_export/dcc_assembler.py`

### Step 3: FBX Export (`step3_fbx_export/`)

**Purpose:** Export combined mesh as FBX

-   Retrieve generated combined skeletal mesh asset
-   Execute Unreal's FBX export via Python/commandlet
-   Include skeleton, skin, and all 52 morph targets
-   Preserve eye and head bones for external rotation control

**Input:** Combined skeletal mesh asset
**Output:** Deterministic FBX file with full rig
**Entry Point:** `step3_fbx_export/fbx_exporter.py`

### Step 4: GLB Convert (`step4_glb_convert/`)

**Purpose:** Convert FBX to glTF (GLB) format

-   Use headless Blender instance for conversion
-   Preserve blendshapes (shape keys) and skeletal bones
-   Automated via Blender Python API (no GUI)
-   Export to glTF 2.0 with Shape Keys enabled

**Input:** FBX file with 52 morph targets
**Output:** GLB file with geometry, bones, and morphs
**Entry Point:** `step4_glb_convert/blender_converter.py`

### Step 5: Web Optimize (`step5_web_optimize/`)

**Purpose:** Optimize GLB for web delivery

-   Use gltf-transform (v4.x) for optimization
-   Apply Draco compression for vertex data
-   Convert textures to WebP format
-   Remove extraneous data while preserving morph targets

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
    ↓ (step1_ingest)
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

### Foundation Complete ✅

-   [x] **Directory structure created** - All 5 steps organized
-   [x] **Pipeline roadmap documented** - Complete architecture defined
-   [x] **Main pipeline orchestrator** - `pipeline.py` with comprehensive error handling
-   [x] **Prerequisites validation** - Blender, gltf-transform, script availability
-   [x] **Project documentation** - README.md, PROJECT_PREFERENCES.md updated
-   [x] **Windows-only configuration** - Complete WSL2 compatibility

### Implementation Ready 🚧

-   [ ] **Step 1: Asset ingestion logic** - Unreal Engine Python API integration
-   [ ] **Step 2: DCC Export integration** - MetaHumanCharacter.RunAssembly automation
-   [ ] **Step 3: FBX export automation** - Unreal Engine commandlet integration
-   [ ] **Step 4: Blender conversion pipeline** - Headless FBX→GLB automation
-   [ ] **Step 5: gltf-transform optimization** - Web delivery optimization

### Future Enhancements 🚀

-   [ ] **Configuration system** - Support multiple MetaHuman types
-   [ ] **Batch processing** - Multiple character automation
-   [ ] **Quality validation** - Automated testing at each step
-   [ ] **Performance metrics** - Optimization reporting
-   [ ] **CI/CD integration** - Automated build pipeline

## Development Workflow

### Primary Command

```bash
# Run complete pipeline
python pipeline.py
```

### Individual Step Testing

```bash
# Test specific steps during development
python step1_ingest/ingestor.py
python step2_dcc_export/dcc_assembler.py
python step3_fbx_export/fbx_exporter.py
python step4_glb_convert/blender_converter.py
python step5_web_optimize/web_optimizer.py
```

### Prerequisites Check

```bash
# Validate environment before implementation
python -c "from pipeline import NewPipelineOrchestrator; NewPipelineOrchestrator({}).check_prerequisites()"
```

## Configuration

### Windows Setup

```bash
# Update paths in config.py for your system
# Default paths use F: drive for WSL2 compatibility
```

### Reusable Components

-   **Azure mappings:** `docs/azure_blendshapes_complete.py`
-   **Logger system:** `logger/core.py` (already preserved)
-   **Configuration:** `config.py` (Windows-specific paths)
