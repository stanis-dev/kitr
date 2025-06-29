# 🐳 MetaHuman FBX to GLB Converter - Docker Guide

This guide explains how to use the dockerized version of the MetaHuman FBX to GLB converter, which packages all required dependencies in a consistent, reproducible environment.

## 🚀 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (usually included with Docker Desktop)

### 1. Build the Docker Image
```bash
# Build the image
docker-compose build metahuman-converter

# Or build manually
docker build -t metahuman-converter .
```

### 2. Prepare Your Files
```bash
# Place your FBX files in the input directory
cp your-metahuman-file.fbx ./input/

# The example input-file.fbx is already included for testing
```

### 3. Run Validation
```bash
# Validate the example file
docker-compose run --rm metahuman-converter python -c "
from pathlib import Path
from metahuman_converter.validation import validate_fbx
from metahuman_converter.logging_config import setup_logging
setup_logging()
result = validate_fbx(Path('input-file.fbx'))
print(f'Valid: {result.is_valid}')
print(f'Blendshapes: {len(result.found_blendshapes)}/52')
"

# Or validate a specific file
INPUT_FILE=your-file.fbx docker-compose run --rm metahuman-converter-convert
```

## 📋 Available Services

### `metahuman-converter` (Default)
Main service for running the converter with your files.

**Usage:**
```bash
# Run with default example
docker-compose up metahuman-converter

# Run with custom command
docker-compose run --rm metahuman-converter python your_script.py
```

### `metahuman-converter-dev` (Development)
Development service with source code mounted for live editing.

**Usage:**
```bash
# Start development environment
docker-compose run --rm metahuman-converter-dev bash

# Inside the container, you can:
python example_usage.py
python -m pytest tests/
metahuman-convert validate input-file.fbx
```

### `metahuman-converter-test` (Testing)
Service specifically for running tests.

**Usage:**
```bash
# Run all tests
docker-compose run --rm metahuman-converter-test

# Run specific tests
docker-compose run --rm metahuman-converter-test python -m pytest tests/test_validation.py -v
```

### `metahuman-converter-convert` (Conversion)
Service for processing specific files with environment variables.

**Usage:**
```bash
# Process specific file
INPUT_FILE=your-file.fbx OUTPUT_FILE=output.glb docker-compose run --rm metahuman-converter-convert

# Batch process files in input directory
docker-compose run --rm metahuman-converter-convert python -c "
from pathlib import Path
for fbx_file in Path('input').glob('*.fbx'):
    print(f'Processing {fbx_file}...')
    # Add your processing logic here
"
```

## 🖥️ CLI Usage

The Docker image includes command-line tools for easy interaction:

### Validate FBX Files
```bash
# Validate a single file
docker-compose run --rm metahuman-converter metahuman-convert validate input/your-file.fbx

# Validate with detailed output
docker-compose run --rm metahuman-converter metahuman-convert validate input/your-file.fbx --output output/

# Batch validate all files in input directory
docker-compose run --rm metahuman-converter metahuman-convert batch --input-dir input --output-dir output
```

### Convert FBX to GLB (Future)
```bash
# Convert a file (when conversion is implemented)
docker-compose run --rm metahuman-converter metahuman-convert convert input/your-file.fbx --output output/your-file.glb

# Convert with validation disabled
docker-compose run --rm metahuman-converter metahuman-convert convert input/your-file.fbx --no-validate-first
```

## 📁 Directory Structure

```
kitr/
├── input/              # Place your FBX files here
│   ├── .gitkeep
│   └── input-file.fbx  # Example file included
├── output/             # Converted files appear here
│   └── .gitkeep
├── temp/               # Temporary processing files
│   └── .gitkeep
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Service orchestration
└── DOCKER_README.md    # This file
```

## 🔧 Advanced Usage

### Custom Docker Commands

**Interactive Development:**
```bash
# Start development container with bash
docker-compose run --rm metahuman-converter-dev bash

# Mount additional directories
docker run -it --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/your-custom-dir:/app/custom \
  metahuman-converter bash
```

**Production Usage:**
```bash
# Run without mounting source code (production mode)
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output:rw \
  metahuman-converter python example_usage.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INPUT_FILE` | `input-file.fbx` | Default input FBX file |
| `OUTPUT_FILE` | `output.glb` | Default output GLB file |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PYTHONPATH` | `/app` | Python module search path |

**Example:**
```bash
docker-compose run --rm -e LOG_LEVEL=DEBUG -e INPUT_FILE=my-metahuman.fbx metahuman-converter-convert
```

### Custom Docker Compose Override

Create a `docker-compose.override.yml` file for local customizations:

```yaml
version: '3.8'
services:
  metahuman-converter:
    environment:
      - LOG_LEVEL=DEBUG
    volumes:
      - ./my-custom-input:/app/input
      - ./my-custom-output:/app/output
```

## 🧰 Included Tools

The Docker image includes several tools for FBX processing:

### Python Libraries
- **pygltflib**: glTF/GLB file manipulation
- **Pillow**: Image processing for textures
- **numpy/scipy**: Mathematical operations
- **lxml**: XML processing for FBX metadata
- **click**: Command-line interface
- **rich**: Beautiful console output

### External Tools
- **FBX2glTF**: Facebook's FBX to glTF converter (when available)
- **gltf-transform**: glTF optimization and manipulation
- **Xvfb**: Virtual display for headless graphics operations

### FBX SDK Alternatives
Since the official Autodesk FBX SDK is complex to install, the Docker image includes:
- Community FBX parsers
- Alternative conversion pipelines
- Binary format readers for FBX files

## 🐛 Troubleshooting

### Common Issues

**1. Permission Denied Errors:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER input/ output/ temp/

# Or run with current user
docker-compose run --rm --user $(id -u):$(id -g) metahuman-converter
```

**2. File Not Found:**
```bash
# Make sure file is in the correct directory
ls -la input/
docker-compose run --rm metahuman-converter ls -la input/
```

**3. Build Errors:**
```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose build --no-cache metahuman-converter
```

**4. Memory Issues:**
```bash
# Increase Docker memory limit in Docker Desktop settings
# Or add memory limits to docker-compose.yml:
services:
  metahuman-converter:
    mem_limit: 4g
```

### Debug Mode

Run in debug mode for detailed logging:

```bash
# Enable debug logging
docker-compose run --rm -e LOG_LEVEL=DEBUG metahuman-converter-dev bash

# Inside container, run with debug:
python -c "
import logging
from metahuman_converter.logging_config import setup_logging
setup_logging(level=logging.DEBUG)
# Your debug code here
"
```

### Health Check

Verify the container is working correctly:

```bash
# Check health status
docker-compose ps

# Manual health check
docker-compose run --rm metahuman-converter python -c "
from metahuman_converter.validation import validate_fbx
print('Health check: OK')
"
```

## 🔄 Development Workflow

### 1. Development Setup
```bash
# Start development environment
docker-compose run --rm metahuman-converter-dev bash

# Inside container:
# - Edit files (changes reflected immediately due to volume mount)
# - Run tests: python -m pytest tests/
# - Test changes: python example_usage.py
```

### 2. Testing Changes
```bash
# Run specific tests
docker-compose run --rm metahuman-converter-test python -m pytest tests/test_validation.py::test_specific_function -v

# Run with coverage
docker-compose run --rm metahuman-converter-test python -m pytest --cov=metahuman_converter --cov-report=html
```

### 3. Building for Production
```bash
# Build optimized image
docker build --target production -t metahuman-converter:latest .

# Test production image
docker run --rm metahuman-converter:latest python -c "print('Production build: OK')"
```

## 📦 Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/docker.yml
name: Docker Build and Test
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker image
      run: docker-compose build metahuman-converter
    - name: Run tests
      run: docker-compose run --rm metahuman-converter-test
    - name: Validate example file
      run: docker-compose run --rm metahuman-converter python example_usage.py
```

### Batch Processing Script

```bash
#!/bin/bash
# batch_process.sh

INPUT_DIR="./batch_input"
OUTPUT_DIR="./batch_output"

# Create directories if they don't exist
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# Process all FBX files
for fbx_file in "$INPUT_DIR"/*.fbx; do
  if [ -f "$fbx_file" ]; then
    filename=$(basename "$fbx_file" .fbx)
    echo "Processing $filename..."
    
    INPUT_FILE="batch_input/$(basename "$fbx_file")" \
    OUTPUT_FILE="batch_output/${filename}.glb" \
    docker-compose run --rm metahuman-converter-convert
  fi
done

echo "Batch processing complete!"
```

## 🎯 Performance Tips

1. **Use bind mounts for large files** instead of copying into the container
2. **Enable BuildKit** for faster builds: `export DOCKER_BUILDKIT=1`
3. **Use multi-stage builds** for smaller production images
4. **Mount only necessary directories** to reduce I/O overhead
5. **Use Docker layer caching** in CI/CD pipelines

## 📄 License & Support

This Docker setup is part of the MetaHuman FBX to GLB Converter project. 

For issues specific to the Docker setup, please include:
- Docker version: `docker --version`
- Docker Compose version: `docker-compose --version`
- System information: `uname -a`
- Error logs from the container

---

**Happy Converting! 🎭→📦** 