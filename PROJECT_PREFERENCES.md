# MetaHuman FBX Validator - Project Preferences

## Core Philosophy: Extreme Determinism

This project follows a **zero-deviation, zero-fallback** approach. Every aspect of the application must follow a single, predetermined path with no alternatives.

## Required Dependencies (No Fallbacks)

### HARD REQUIREMENTS - Must be present or tool fails:
- **Python 3** (any recent version)
- **Blender** (accessible via `blender` command in PATH)
- **Rich library** (for console output - no fallback console implementation)

### Dependency Philosophy:
- NO optional dependencies
- NO try/except imports with fallbacks
- NO "if library available" checks
- Dependencies either work or the tool crashes immediately

## Code Standards

### Deterministic Behavior:
- Single execution path only
- No configuration files or customization options
- Hardcoded input file: `input-file.fbx`
- No CLI arguments or parameters
- No environment variable checks
- No platform-specific code paths

### Error Handling:
- Fail fast and loud
- No graceful degradation
- No fallback modes
- Clear error messages pointing to missing requirements

### Forbidden Patterns:
```python
# ❌ NEVER DO THIS:
try:
    import optional_library
    USE_OPTIONAL = True
except ImportError:
    USE_OPTIONAL = False

# ❌ NEVER DO THIS:
if library_available:
    use_library()
else:
    fallback_implementation()

# ✅ ALWAYS DO THIS:
from required_library import something  # Let it crash if missing
```

## Development Guidelines

### File Structure:
- Minimal file count
- Zero test files (except single snapshot test for preserving deterministic behavior)
- Zero documentation beyond this file and README
- Zero configuration files beyond IDE settings

### Exception: Snapshot Test
- `test_snapshot.py` - ONLY test file, preserves exact functionality
- Captures precise output format, counts, and exit codes
- Prevents regression during future iterations
- Must be updated when intentional changes are made

### Code Quality:
- Line length: 120 characters
- Black formatting required
- Type hints encouraged but not required
- Minimal imports only

### Iteration Rules:
- Always prefer deletion over addition
- Always prefer simplification over features
- Always prefer crashing over fallback behavior
- Never add options or configuration

## IDE Configuration

This project includes:
- `.vscode/settings.json` - Cursor/VSCode preferences
- `.editorconfig` - Cross-editor consistency
- This preferences file for team consistency

These files ensure that the deterministic philosophy is maintained across different computers and developers.

## Validation Workflow

The tool follows exactly one path:
1. Validate Blender installation (crash if missing)
2. Validate Rich library (crash if missing)
3. Validate input-file.fbx exists (crash if missing)
4. Process with Blender (crash if fails)
5. Validate blendshapes (exit 1 if insufficient)
6. Exit 0 (success) or Exit 1 (failure)

**No other paths are permitted.**
