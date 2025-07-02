# Git Protection Rules - MetaHuman Pipeline

## 🚫 NEVER COMMIT These Files

This project has strict rules about what should **NEVER** be committed to git. These protections are in place to keep the repository clean, fast, and focused on source code.

## Protected File Types

### 🎭 Pipeline Outputs
- **FBX files:** `*.fbx`, `*.FBX` - MetaHuman exports, intermediate FBX files
- **GLB/glTF files:** `*.glb`, `*.gltf` - Final web-optimized outputs
- **Output directories:** `output/`, `step*/output/` - All pipeline step outputs
- **DCC Export files:** `*_Combined.*`, `*_Export/` - Unreal Engine exports
- **Reports:** `*_report.json`, `*_statistics.json` - Processing reports

### 🔧 Temporary Files
- **Processing files:** `temp_*`, `tmp_*`, `processing_*`
- **Blender scripts:** `blender_conversion_script.py` (auto-generated)
- **Unreal Engine temps:** `Temp_MetaHuman_Processing/`, `*/Temp_*/`

### 🎮 Unreal Engine Assets
- **Project files:** `*.uproject`, `*.uasset`, `*.umap`
- **Generated directories:** `Binaries/`, `Intermediate/`, `DerivedDataCache/`, `Saved/`

### 📱 System & Development Files
- **Python cache:** `__pycache__/`, `*.pyc`, `*.pyo`
- **System files:** `.DS_Store`, `Thumbs.db`, `desktop.ini`
- **IDE files:** `.vscode/settings.json`, `.idea/`
- **Logs:** `*.log`, `logs/`, `debug_output/`

## Protection Layers

### 1. `.gitignore` File ✅
Comprehensive ignore rules covering all pipeline outputs and temporary files.

### 2. Pre-commit Hook ✅
Actively prevents commits of restricted files with detailed error messages.

**Location:** `.git/hooks/pre-commit`
**Features:**
- Scans staged files for forbidden patterns
- Blocks commits with clear error messages
- Warns about large files (>10MB)
- Provides fix instructions

### 3. File Size Protection ⚠️
Warns when trying to commit files larger than 10MB (usually pipeline outputs).

## What TO Commit ✅

**ONLY commit these types of files:**
- **Source code:** `*.py`, `*.js`, `*.ts`
- **Documentation:** `*.md`, `*.txt`
- **Configuration:** `requirements.txt`, `*.json` (config files)
- **Project structure:** `__init__.py`, directory structure
- **Git configuration:** `.gitignore`, hooks documentation

## Testing Protection

### Test the Pre-commit Hook:
```bash
# Create a test FBX file
touch test.fbx

# Try to commit it (should be blocked)
git add test.fbx
git commit -m "test"
# ❌ Should fail with protection message

# Clean up
rm test.fbx
git reset HEAD
```

### Bypass Protection (EMERGENCY ONLY):
```bash
# Skip pre-commit hook (NOT RECOMMENDED)
git commit --no-verify -m "emergency commit"

# Check what's being ignored
git status --ignored
```

## Common Scenarios

### ✅ Normal Development Workflow:
```bash
# Edit source code
vim step1_duplicate/asset_duplicator.py

# Commit source changes (ALLOWED)
git add step1_duplicate/asset_duplicator.py
git commit -m "Implement asset duplication logic"
```

### ❌ Accidentally Generated Output:
```bash
# Pipeline created output files
ls output/
# -> character.fbx, optimized.glb

# Try to commit (BLOCKED by protection)
git add .
git commit -m "Add outputs"
# ❌ Pre-commit hook blocks this

# Proper response: ignore the outputs
echo "They're already in .gitignore - no action needed"
```

### 🔧 Adding New Protection:
```bash
# Edit .gitignore for new file types
echo "*.new_extension" >> .gitignore

# Edit pre-commit hook for active protection
vim .git/hooks/pre-commit
# Add "*.new_extension" to FORBIDDEN_PATTERNS array
```

## Why These Rules Exist

### 🚀 Repository Performance
- **Small clone size:** Only source code, no large binaries
- **Fast operations:** Git commands stay responsive
- **Clean history:** Focus on code changes, not generated files

### 🔒 Data Protection
- **No accidental overwrites:** Pipeline outputs never conflict
- **Original asset safety:** MetaHuman assets stay in Unreal Engine
- **Deterministic builds:** Outputs generated fresh each time

### 👥 Team Collaboration
- **No merge conflicts:** Generated files don't cause conflicts
- **Clear responsibility:** Only intentional source changes committed
- **Focused reviews:** Code reviews focus on logic, not outputs

## Emergency Procedures

### If Protection Files Are Accidentally Committed:
```bash
# Remove from repository (keep local copy)
git rm --cached unwanted_file.fbx

# Update .gitignore if needed
echo "unwanted_file.fbx" >> .gitignore

# Commit the fix
git add .gitignore
git commit -m "Remove accidentally committed pipeline output"
```

### If Pre-commit Hook Breaks:
```bash
# Temporarily disable
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# Make your commit
git commit -m "fix without hook"

# Re-enable protection
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## Best Practices

1. **Always check status before committing:**
   ```bash
   git status
   # Look for unexpected files before git add
   ```

2. **Use selective staging:**
   ```bash
   git add specific_file.py
   # Rather than git add .
   ```

3. **Review before committing:**
   ```bash
   git diff --cached
   # Review exactly what you're committing
   ```

4. **Trust the protection system:**
   - If the pre-commit hook blocks something, there's a good reason
   - Don't use `--no-verify` unless it's a true emergency
   - When in doubt, ask or check this documentation

**Remember: These protections exist to keep the repository clean and professional. They prevent common mistakes that could bloat the repository or cause team issues.**
