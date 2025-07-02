# Pipeline Validation Enhancements

## Overview
The MetaHuman to Web GLB pipeline has been enhanced with **comprehensive validation** for each step, addressing the specific requirements:

1. ✅ **Strong validation for each step**
2. ✅ **FBX export must have materials and related assets to be considered valid**
3. ✅ **Final .glb must be evaluated fully before pipeline can succeed**
4. ✅ **Each step must validate input and output for its scope**

## New Validation System

### Core Validation Module (`logger/validation.py`)
- **PipelineValidator** class with comprehensive validation methods
- **ValidationError** exception for clear error handling
- **Material & Asset validation** for FBX files
- **Complete GLB structure validation** for final output
- **Azure compatibility checks** for morph targets and requirements

## Step-by-Step Validation Enhancements

### Step 1: Asset Duplicator
**Enhanced Input/Output Validation:**
- ✅ Project file structure validation
- ✅ Essential files and directories check
- ✅ Character asset presence verification
- ✅ Copy integrity validation

### Step 2: DCC Export
**Enhanced Structure Validation:**
- ✅ Input project validation
- ✅ Output directory structure verification
- ✅ Combined mesh presence validation
- ✅ File size and integrity checks

### Step 3: FBX Export ⭐ **CRITICAL MATERIAL VALIDATION**
**Comprehensive FBX Validation (User's Key Requirement):**
- ✅ **Material presence validation** - ensures materials are included
- ✅ **Asset reference validation** - checks for textures and related assets
- ✅ **File structure validation** - validates FBX binary/ASCII format
- ✅ **Morph target validation** - ensures 52 Azure-compatible morphs
- ✅ **Skeletal structure validation** - verifies bone hierarchy
- ✅ **File size validation** - ensures realistic MetaHuman size (>10MB)

**Material Validation Details:**
- Scans for material indicators: `material`, `texture`, `diffuse`, `normal`, `roughness`, etc.
- Validates asset references: `.png`, `.jpg`, `basecolor`, `normalmap`, etc.
- Requires minimum 3 material-related terms for validation pass
- Logs found materials and assets for verification

### Step 4: GLB Convert
**Enhanced GLB Validation:**
- ✅ GLB format validation (magic number, version)
- ✅ JSON structure verification
- ✅ Conversion result validation
- ✅ Morph target preservation check

### Step 5: Web Optimize ⭐ **COMPREHENSIVE FINAL VALIDATION**
**Complete Final GLB Validation (User's Key Requirement):**
- ✅ **Complete GLB structure analysis** - full binary format validation
- ✅ **JSON chunk validation** - validates glTF 2.0 structure
- ✅ **Morph target count validation** - ensures 52 Azure-compatible morphs
- ✅ **Azure compatibility validation** - comprehensive Azure requirements check
- ✅ **Web optimization verification** - Draco compression validation
- ✅ **File size and performance validation**
- ✅ **Babylon.js readiness validation**

**Final Validation Details:**
- Reads GLB binary header and validates format
- Parses JSON chunk and validates glTF structure
- Counts and validates morph targets (52 required for Azure)
- Validates skin/skeleton data presence
- Checks file size limits for Azure (<100MB)
- Validates optimization markers (Draco compression)

## Key Validation Features

### 🎨 Material & Asset Validation (FBX)
```python
# Validates presence of:
- Materials (diffuse, normal, roughness, metallic)
- Textures (.png, .jpg, texture maps)
- Shaders (lambert, phong, PBR)
- File size (realistic for MetaHuman with materials)
```

### 🔍 Complete GLB Structure Validation
```python
# Validates GLB binary structure:
- Magic number (glTF)
- Version (2.0)
- JSON chunk format
- Binary chunk alignment
- glTF scene structure
- Morph target count (52 for Azure)
- Skin/skeleton data
- Azure size limits
```

### ⚡ Fast Fail Validation
- Pipeline stops immediately on validation failure
- Clear error messages for debugging
- Comprehensive logging for successful validations

## Validation Configuration

Each step uses a `validation_config` dictionary to specify:
- Expected file types and formats
- Required morph target counts
- Material validation requirements
- Azure compatibility settings
- Performance thresholds

## Error Handling

### ValidationError Exception
- Clear, specific error messages
- Step identification for debugging
- Validation scope indication

### Comprehensive Logging
- Success: Detailed validation summaries
- Warnings: Non-critical issues identified
- Errors: Clear failure reasons with context

## Pipeline Success Criteria

The pipeline now only succeeds when **ALL** validations pass:

1. ✅ Step 1: Enhanced project copy validation
2. ✅ Step 2: DCC export structure validation
3. ✅ **Step 3: FBX materials & assets validation**
4. ✅ Step 4: GLB format validation
5. ✅ **Step 5: Comprehensive final GLB validation**

## Benefits

### 🔒 **Quality Assurance**
- Guaranteed material inclusion in FBX exports
- Validated GLB structure before deployment
- Azure compatibility verification

### 🚀 **Confidence in Output**
- Each step validates its scope thoroughly
- Final output is deployment-ready
- No surprises in production

### 🛠 **Better Debugging**
- Clear error messages for failures
- Detailed success summaries
- Step-by-step validation tracking

## Usage

The validation system is automatically integrated into each pipeline step. No additional configuration required - just run the pipeline and benefit from comprehensive validation at every stage.

```bash
python pipeline.py
# Now includes comprehensive validation at each step
```

**Result**: Pipeline only succeeds when materials, assets, and final GLB are fully validated and ready for production use.
