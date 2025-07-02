"""
Constants for MetaHuman FBX validation.
All documentation and knowledge is maintained in the docs/ folder as the single source of truth.
See docs/ Python modules for complete technical documentation with full IDE support.

For full type-safe access to all functions and types, import directly from docs package:
- from docs import ...
"""

import sys
from pathlib import Path
from typing import List

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Direct imports from docs package for better type inference
from docs import (
    FACIAL_BLENDSHAPES,
    ROTATION_PARAMETERS,
    TOTAL_PARAMETERS,
    METAHUMAN_NAME_MAPPINGS,
    EXPECTED_MORPH_TARGET_COUNT,
    REQUIRED_BONES,
    AzureBlendshapeName,
    AzureRotationName,
    BoneName
)

# Backwards compatibility aliases with proper typing
AZURE_BLENDSHAPES: List[AzureBlendshapeName] = FACIAL_BLENDSHAPES
AZURE_ROTATIONS: List[AzureRotationName] = ROTATION_PARAMETERS
TOTAL_AZURE_PARAMETERS: int = TOTAL_PARAMETERS

# Updated validation constants with new names for backwards compatibility
EXPECTED_INPUT_BLENDSHAPE_COUNT: int = EXPECTED_MORPH_TARGET_COUNT
ALL_REQUIRED_BONES: List[BoneName] = REQUIRED_BONES

# Export list for clean imports
__all__ = [
    # Azure parameters
    'AZURE_BLENDSHAPES',
    'AZURE_ROTATIONS',
    'TOTAL_AZURE_PARAMETERS',
    'FACIAL_BLENDSHAPES',
    'ROTATION_PARAMETERS',
    'TOTAL_PARAMETERS',

    # MetaHuman mappings
    'METAHUMAN_NAME_MAPPINGS',

    # Validation constants
    'EXPECTED_INPUT_BLENDSHAPE_COUNT',
    'EXPECTED_MORPH_TARGET_COUNT',
    'ALL_REQUIRED_BONES',
    'REQUIRED_BONES',

    # Type aliases
    'AzureBlendshapeName',
    'AzureRotationName',
    'BoneName'
]
