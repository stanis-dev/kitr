# MetaHuman to Web GLB Pipeline - Project Preferences

## New Architecture Overview (Post-Refactor)

**Status:** 🚧 SKELETON PHASE - Implementation in Progress
**Date:** July 2024
**Architecture:** Unreal Engine DCC Export → Web-Optimized GLB

Designing the **MetaHuman to Web GLB Pipeline** using Unreal Engine's DCC Export assembly for deterministic, production-ready web assets compatible with Babylon.js and Azure Cognitive Services.

## Pipeline Philosophy

The new architecture leverages **Epic's DCC Export pipeline** within Unreal Engine to produce deterministic, repeatable results. Unlike the previous FBX-input approach, this pipeline operates directly on MetaHuman Character assets within Unreal Engine, utilizing Epic's own export tools for maximum compatibility and reliability.

**Key Architectural Shift:**
- **Old:** External FBX processing → Azure optimization → GLB conversion
- **New:** Unreal Engine asset → DCC Export → FBX → GLB → Web optimization

## 5-Step Architecture (NEW)

### Step 1: Ingest & Prepare Asset (`step1_ingest/`)
**Purpose:** MetaHuman asset duplication and morph target preparation
- **Input:** Original MetaHuman Character asset in Unreal Engine
- **Process:** Duplicate asset to temporary package, prepare 52 Azure-compatible morphs
- **Output:** Temporary MetaHuman asset with optimized morph targets
- **Tool:** Unreal Engine Python API
- **Entry Point:** `asset_duplicator.py`

### Step 2: DCC Export Assembly (`step2_dcc_export/`)
**Purpose:** Execute Epic's DCC Export pipeline
- **Input:** Prepared MetaHuman asset
- **Process:** Call `MetaHumanCharacter.RunAssembly("DCC Export")`
- **Output:** Combined skeletal mesh + DCC export folder structure
- **Tool:** Unreal Engine DCC Export assembly
- **Entry Point:** `dcc_assembler.py`

### Step 3: FBX Export (`step3_fbx_export/`)
**Purpose:** Export combined mesh as deterministic FBX
- **Input:** Combined skeletal mesh asset from DCC Export
- **Process:** Execute Unreal Engine's FBX export via Python/commandlet
- **Output:** Deterministic FBX file with 52 morphs + full skeleton
- **Tool:** Unreal Engine FBX Export
- **Entry Point:** `fbx_exporter.py`

### Step 4: GLB Convert (`step4_glb_convert/`)
**Purpose:** Convert FBX to glTF (GLB) format
- **Input:** Deterministic FBX file
- **Process:** Headless Blender automation for FBX → GLB conversion
- **Output:** GLB file with preserved morphs and skeletal data
- **Tool:** Blender (headless mode)
- **Entry Point:** `blender_converter.py`

### Step 5: Web Optimize (`step5_web_optimize/`)
**Purpose:** Optimize GLB for web delivery
- **Input:** Unoptimized GLB file
- **Process:** Apply Draco compression, WebP textures, pruning
- **Output:** Web-optimized GLB ready for Babylon.js
- **Tool:** gltf-transform (v4.x)
- **Entry Point:** `web_optimizer.py`

## Design Principles (PRESERVED)

### File Immutability Principle
- **Original MetaHuman assets never modified** (enhanced protection)
- Each step produces new output files while preserving inputs
- Complete audit trail from source asset to final GLB
- Rollback capability at any stage

### Deterministic Processing
- **Same input always produces identical output**
- Epic's DCC Export ensures consistent mesh generation
- Automated tools eliminate human intervention variables
- Reproducible builds for production environments

### Fail-Fast Philosophy
- **No graceful degradation or fallback modes**
- Pipeline stops immediately on any step failure
- Clear error messages with actionable guidance
- Prerequisites validated before execution begins

### Comprehensive Prerequisites
- **Unreal Engine with Python support**
- **Blender 3.0+** (for GLB conversion)
- **gltf-transform CLI** (for web optimization)
- **Node.js ecosystem** (for gltf-transform)

## File Flow & Naming Convention

```
Original MetaHuman Asset (Unreal Engine)
    ↓ (step1_ingest)
Temp_MetaHuman_Processing/BP_Character
    ↓ (step2_dcc_export)
Combined Skeletal Mesh + DCC Export Folder
    ↓ (step3_fbx_export)
output/step3_fbx_export/character_exported.fbx
    ↓ (step4_glb_convert)
output/step4_glb_convert/character.glb
    ↓ (step5_web_optimize)
output/step5_web_optimize/character_optimized.glb (FINAL)
```

### Output Directory Structure
```
output/
├── step1_ingest/              # Temporary assets (Unreal Engine)
├── step2_dcc_export/          # DCC Export outputs
├── step3_fbx_export/          # Deterministic FBX files
├── step4_glb_convert/         # Converted GLB files
└── step5_web_optimize/        # Web-optimized GLB (final)
```

## Tool Dependencies & Requirements

### Primary Tools
- **Unreal Engine 5.0+** - MetaHuman asset processing, DCC Export, FBX export
- **Blender 3.0+** - FBX to GLB conversion with shape key preservation
- **gltf-transform 4.x** - Web optimization (Draco, WebP, pruning)
- **Python 3.8+** - Pipeline orchestration and Unreal Engine automation

### Installation Requirements
```bash
# Unreal Engine (Epic Games Launcher or source build)
# MetaHuman Creator plugin enabled

# Blender
brew install blender  # macOS
# Or download from blender.org

# gltf-transform
npm install -g @gltf-transform/cli

# Python dependencies
pip install -r requirements.txt
```

### System Requirements
- **10GB+ free disk space** (for processing intermediates)
- **Unreal Engine project** with MetaHuman assets
- **Command-line access** to all tools

## Target Compatibility

### Azure Cognitive Services
- **52 Azure blendshapes** (100% compatibility maintained)
- **3 rotation parameters** (head, leftEyeRoll, rightEyeRoll)
- **ARKit facial expression standard** compliance

### Web Platform Support
- **Babylon.js optimized** (primary target)
- **WebGL 2.0 compatible**
- **Draco compression** for reduced download size
- **WebP textures** for optimal quality/size ratio

## Error Handling Strategy

### Prerequisites Validation
```python
✅ Unreal Engine Python environment
✅ Blender available and accessible
✅ gltf-transform CLI installed
✅ All step scripts present
✅ Source MetaHuman asset exists
```

### Step-by-Step Validation
- Each step validates its specific input requirements
- Comprehensive error messages with fix recommendations
- Early termination prevents partial processing
- Clear indication of which step failed and why

## Project Structure (Current)

```
kitr/
├── pipeline.py                        # ⭐ Main orchestrator
├── PIPELINE_ARCHITECTURE.md           # Architecture documentation
├── REFACTOR_REFERENCE.md              # Original pipeline reference
├── PROJECT_PREFERENCES.md             # This file
├── requirements.txt                   # Python dependencies
│
├── docs/                              # 🐍 Preserved Azure mappings & docs
│   ├── azure_blendshapes_complete.py
│   ├── metahuman_to_azure_mappings.py
│   └── validation_requirements.py
│
├── logger/                            # 🔧 Preserved logging system
│   ├── __init__.py
│   └── core.py
│
├── step1_ingest/                      # 🔄 Asset ingestion
│   ├── __init__.py
│   └── asset_duplicator.py
│
├── step2_dcc_export/                  # 🔧 DCC Export assembly
│   ├── __init__.py
│   └── dcc_assembler.py
│
├── step3_fbx_export/                  # 📦 FBX export
│   ├── __init__.py
│   └── fbx_exporter.py
│
├── step4_glb_convert/                 # 🔄 GLB conversion
│   ├── __init__.py
│   └── blender_converter.py
│
├── step5_web_optimize/                # 🚀 Web optimization
│   ├── __init__.py
│   └── web_optimizer.py
│
└── archive_old_pipeline/              # 📦 Preserved original pipeline
    ├── README.md
    ├── old_pipeline.py
    ├── step1_validation/
    ├── step2_morphs/              # ⭐ Perfect Azure optimization (reference)
    ├── step3_glb/
    └── step4_render/
```

## Implementation Status

### Completed ✅
- [x] **Pipeline skeleton structure**
- [x] **Directory organization**
- [x] **Main orchestrator framework**
- [x] **Prerequisites checking**
- [x] **Error handling foundation**
- [x] **Original pipeline preservation**

### In Progress 🚧
- [ ] **Step 1:** Unreal Engine Python API integration
- [ ] **Step 2:** DCC Export assembly automation
- [ ] **Step 3:** FBX export commandlet integration
- [ ] **Step 4:** Blender automation scripts
- [ ] **Step 5:** gltf-transform optimization

### Future Enhancements 🚀
- [ ] **Configuration system** for different MetaHuman types
- [ ] **Batch processing** for multiple characters
- [ ] **Quality validation** at each step
- [ ] **Performance metrics** and optimization reporting
- [ ] **CI/CD integration** for automated builds

## Migration from Original Pipeline

### Preserved Assets
- **Azure mappings** (`docs/azure_blendshapes_complete.py`) - Full compatibility maintained
- **Validation logic** (`archive_old_pipeline/step2_morphs/`) - Perfect optimization reference
- **Logger system** (`logger/`) - Reusable logging infrastructure

### Architectural Benefits
- **Deterministic output** via Epic's DCC Export
- **Source asset protection** (Unreal Engine workspace isolation)
- **Industry standard workflow** (Epic's recommended export process)
- **Scalable processing** (can handle multiple character types)
- **Production readiness** (built for repeatability and automation)

### Backward Compatibility
- Original pipeline preserved in `archive_old_pipeline/`
- Git branches maintain full history and access
- Azure compatibility maintained (52 morphs + 3 rotations)
- File immutability principle enhanced

## Usage Patterns

### Primary Workflow
```bash
# Complete pipeline execution
python pipeline.py

# Expected output: Web-optimized GLB ready for Babylon.js
```

### Development Workflow
```bash
# Individual step testing
python step1_ingest/ingestor.py
python step2_dcc_export/dcc_assembler.py
# ... etc

# Prerequisites checking
python -c "from pipeline import NewPipelineOrchestrator; NewPipelineOrchestrator({}).check_prerequisites()"
```

### Reference Original Pipeline
```bash
# Switch to stable reference
git checkout pre-refactor-stable

# Or use archived version
cd archive_old_pipeline
python old_pipeline.py
```

This new architecture maintains all successful design principles from the original pipeline while leveraging Epic's proven DCC Export workflow for enhanced reliability and industry-standard compatibility.
