"""
MetaHuman to Babylon.js Avatar Converter

A robust CLI pipeline to convert MetaHuman-exported avatars (FBX format, LOD0) 
into optimized GLB files ready for Babylon.js with Azure viseme blendshapes.
"""

__version__ = "0.1.0"
__author__ = "MetaHuman Converter Team"

from .validation import validate_fbx
from .constants import AZURE_BLENDSHAPES

__all__ = ["validate_fbx", "AZURE_BLENDSHAPES"]