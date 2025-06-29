# MetaHuman FBX Validator

Blender-based validation tool for MetaHuman FBX files.

## Requirements

- **Blender** (any recent version 3.0+) installed and accessible from command line
- **Python 3** with pip
- Input file must be named `input-file.fbx` in project root
- Validates 52 required Azure-compatible blendshapes

## Installation

1. Install Blender from [blender.org](https://www.blender.org/download/)
2. Ensure `blender` command is available in your PATH
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

```bash
python validate.py
```

## What it does

- Validates Blender installation before processing
- Processes FBX file using Blender headless mode
- Extracts and validates facial blendshapes
- Extracts bone structure information
- Exits with status 0 (valid) or 1 (invalid/error)

**Note:** Tool fails immediately if Blender is not available or if validation fails - no fallbacks. 