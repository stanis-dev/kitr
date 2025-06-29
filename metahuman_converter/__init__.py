"""
MetaHuman FBX to GLB Conversion Pipeline

A tool for converting MetaHuman FBX files to optimized GLB format
for Babylon.js with Azure Cognitive Services viseme blendshape support.
"""

__version__ = "0.1.0"
__author__ = "MetaHuman Converter Team"
__description__ = "MetaHuman FBX to GLB conversion pipeline"

from .validation import validate_fbx
from .constants import ARKIT_BLENDSHAPES, REQUIRED_BONES

__all__ = [
    "validate_fbx",
    "ARKIT_BLENDSHAPES", 
    "REQUIRED_BONES"
]