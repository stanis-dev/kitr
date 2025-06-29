"""
MetaHuman FBX Validator

Simple Blender-based validation tool for MetaHuman FBX files.
Validates Azure-compatible facial blendshapes.
"""

__version__ = "1.0.0"
__author__ = "MetaHuman Validator"

# Core validation functionality
from .validation import validate_fbx
from .constants import AZURE_BLENDSHAPES

__all__ = ["validate_fbx", "AZURE_BLENDSHAPES"]