#!/bin/bash
# Docker Test Script for MetaHuman FBX to GLB Converter
# This script demonstrates the complete Docker setup

set -e  # Exit on any error

echo "🐳 MetaHuman FBX to GLB Converter - Docker Test"
echo "================================================"

# Build the image
echo "📦 Building Docker image..."
docker-compose build metahuman-converter

# Test 1: Basic validation
echo ""
echo "🔍 Test 1: Basic FBX Validation"
echo "--------------------------------"
docker-compose run --rm metahuman-converter python -c "
from pathlib import Path
from metahuman_converter.validation import validate_fbx
from metahuman_converter.logging_config import setup_logging
setup_logging()
result = validate_fbx(Path('input/input-file.fbx'))
print(f'Validation Status: {\"✅ PASSED\" if result.is_valid else \"❌ FAILED\"}')
print(f'Blendshapes Found: {len(result.found_blendshapes)}/52')
print(f'Bones Found: {len(result.found_bones)}')
"

# Test 2: CLI validation
echo ""
echo "🖥️  Test 2: CLI Validation"
echo "-------------------------"
docker-compose run --rm metahuman-converter metahuman-convert validate input/input-file.fbx

# Test 3: Example usage script
echo ""
echo "📄 Test 3: Example Usage Script"
echo "-------------------------------"
docker-compose run --rm metahuman-converter python example_usage.py

# Test 4: Development environment
echo ""
echo "🛠️  Test 4: Development Environment"
echo "----------------------------------"
docker-compose run --rm metahuman-converter-dev python -c "
print('Development environment ready!')
print('Available commands:')
print('  - python example_usage.py')
print('  - metahuman-convert validate <file>')
print('  - python -m pytest tests/')
print('Environment variables:')
import os
print(f'  PYTHONPATH: {os.getenv(\"PYTHONPATH\")}')
print(f'  LOG_LEVEL: {os.getenv(\"LOG_LEVEL\")}')
"

echo ""
echo "✅ All Docker tests completed successfully!"
echo ""
echo "📚 Usage Examples:"
echo "  # Validate a custom FBX file:"
echo "  cp your-file.fbx input/"
echo "  docker-compose run --rm metahuman-converter metahuman-convert validate input/your-file.fbx"
echo ""
echo "  # Interactive development:"
echo "  docker-compose run --rm metahuman-converter-dev bash"
echo ""
echo "  # Batch processing:"
echo "  docker-compose run --rm metahuman-converter metahuman-convert batch"
echo ""
echo "�� Happy Converting!" 