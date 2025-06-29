# MetaHuman FBX Validator

Blender-based validation tool for MetaHuman FBX files.

## Requirements

- Docker
- Input file must be named `input-file.fbx` in project root
- Validates 52 required Azure-compatible blendshapes

## Usage

```bash
docker build -t metahuman-validator . && docker run --rm -v $(pwd)/input-file.fbx:/app/input-file.fbx:ro metahuman-validator
```

## What it does

- Validates FBX file using Blender
- Checks for required facial blendshapes
- Extracts bone structure information
- Exits with status 0 (valid) or 1 (invalid/error)

**Note:** Tool fails immediately if Blender is not available - no fallbacks or graceful error handling. 