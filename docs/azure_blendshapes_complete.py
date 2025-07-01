"""
Azure Cognitive Services Blendshapes and Parameters Reference

This module defines the complete set of 52 Azure ARKit-compatible facial blendshapes
and 3 rotation parameters required for Azure Cognitive Services integration.

Azure Cognitive Services expects exactly these parameters for 3D viseme output:
- 52 facial blendshapes (indices 0-51)
- 3 rotation parameters (indices 52-54)
- Total: 55 parameters

Reference: https://docs.microsoft.com/azure/cognitive-services/speech-service/how-to-speech-synthesis-viseme
"""

from typing import List, TypedDict, Literal, Final, Union

# Type definitions for better type safety
AzureBlendshapeName = Literal[
    # Eye blendshapes (14)
    "eyeBlinkLeft", "eyeBlinkRight", "eyeLookDownLeft", "eyeLookDownRight",
    "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
    "eyeLookUpLeft", "eyeLookUpRight", "eyeSquintLeft", "eyeSquintRight",
    "eyeWideLeft", "eyeWideRight",
    # Jaw blendshapes (4)
    "jawForward", "jawLeft", "jawRight", "jawOpen",
    # Mouth blendshapes (24)
    "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft", "mouthRight",
    "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
    "mouthDimpleLeft", "mouthDimpleRight", "mouthStretchLeft", "mouthStretchRight",
    "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper",
    "mouthPressLeft", "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight",
    "mouthUpperUpLeft", "mouthUpperUpRight", "tongueOut",
    # Brow blendshapes (5)
    "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft", "browOuterUpRight",
    # Cheek blendshapes (3)
    "cheekPuff", "cheekSquintLeft", "cheekSquintRight",
    # Nose blendshapes (2)
    "noseSneerLeft", "noseSneerRight"
]

AzureRotationName = Literal["headRoll", "leftEyeRoll", "rightEyeRoll"]
AzureParameterName = Union[AzureBlendshapeName, AzureRotationName]

# For practical typing, use int with range validation in functions
BlendshapeIndex = int  # 0-54, validated at runtime

class ParameterBreakdown(TypedDict):
    """Type definition for parameter breakdown structure."""
    facial_blendshapes: int
    rotation_parameters: int

class BlendshapeCategories(TypedDict):
    """Type definition for blendshape categories structure."""
    eye_blendshapes: int
    jaw_blendshapes: int
    mouth_blendshapes: int
    brow_blendshapes: int
    cheek_blendshapes: int
    nose_blendshapes: int

class AzureBlendshapesData(TypedDict):
    """Type definition for complete Azure blendshapes data structure."""
    description: str
    version: str
    facial_blendshapes: List[AzureBlendshapeName]
    rotation_parameters: List[AzureRotationName]
    total_parameters: int
    parameter_breakdown: ParameterBreakdown
    categories: BlendshapeCategories

# Azure ARKit-compatible facial blendshapes (52 total)
FACIAL_BLENDSHAPES: Final[List[AzureBlendshapeName]] = [
    # Eye blendshapes (14) - Control eye movement, blinking, squinting, and widening
    "eyeBlinkLeft",        # Left eye blink
    "eyeBlinkRight",       # Right eye blink
    "eyeLookDownLeft",     # Left eye look down
    "eyeLookDownRight",    # Right eye look down
    "eyeLookInLeft",       # Left eye look inward (toward nose)
    "eyeLookInRight",      # Right eye look inward (toward nose)
    "eyeLookOutLeft",      # Left eye look outward (away from nose)
    "eyeLookOutRight",     # Right eye look outward (away from nose)
    "eyeLookUpLeft",       # Left eye look up
    "eyeLookUpRight",      # Right eye look up
    "eyeSquintLeft",       # Left eye squint
    "eyeSquintRight",      # Right eye squint
    "eyeWideLeft",         # Left eye wide open
    "eyeWideRight",        # Right eye wide open

    # Jaw blendshapes (4) - Control jaw movement and positioning
    "jawForward",          # Jaw push forward
    "jawLeft",             # Jaw move left
    "jawRight",            # Jaw move right
    "jawOpen",             # Jaw open (mouth open)

    # Mouth blendshapes (24) - Control mouth shape, lip movement, and expressions
    "mouthClose",          # Mouth close tightly
    "mouthFunnel",         # Mouth funnel shape (like "ooo")
    "mouthPucker",         # Mouth pucker (kiss shape)
    "mouthLeft",           # Mouth move left
    "mouthRight",          # Mouth move right
    "mouthSmileLeft",      # Left side smile
    "mouthSmileRight",     # Right side smile
    "mouthFrownLeft",      # Left side frown
    "mouthFrownRight",     # Right side frown
    "mouthDimpleLeft",     # Left dimple
    "mouthDimpleRight",    # Right dimple
    "mouthStretchLeft",    # Left mouth stretch
    "mouthStretchRight",   # Right mouth stretch
    "mouthRollLower",      # Lower lip roll inward
    "mouthRollUpper",      # Upper lip roll inward
    "mouthShrugLower",     # Lower lip shrug
    "mouthShrugUpper",     # Upper lip shrug
    "mouthPressLeft",      # Left lip press
    "mouthPressRight",     # Right lip press
    "mouthLowerDownLeft",  # Left lower lip down
    "mouthLowerDownRight", # Right lower lip down
    "mouthUpperUpLeft",    # Left upper lip up
    "mouthUpperUpRight",   # Right upper lip up
    "tongueOut",           # Tongue out

    # Brow blendshapes (5) - Control eyebrow movement and positioning
    "browDownLeft",        # Left brow down
    "browDownRight",       # Right brow down
    "browInnerUp",         # Inner brow up (both sides)
    "browOuterUpLeft",     # Left outer brow up
    "browOuterUpRight",    # Right outer brow up

    # Cheek blendshapes (3) - Control cheek movement and puffing
    "cheekPuff",           # Cheek puff (both sides)
    "cheekSquintLeft",     # Left cheek squint
    "cheekSquintRight",    # Right cheek squint

    # Nose blendshapes (2) - Control nose movement and sneering
    "noseSneerLeft",       # Left nose sneer
    "noseSneerRight",      # Right nose sneer
]

# Azure rotation parameters (3 total) - indices 52-54
ROTATION_PARAMETERS: Final[List[AzureRotationName]] = [
    "headRoll",            # Head rotation around forward axis (index 52)
    "leftEyeRoll",         # Left eye rotation (index 53)
    "rightEyeRoll",        # Right eye rotation (index 54)
]

# Total number of parameters Azure outputs
TOTAL_PARAMETERS: Final[int] = len(FACIAL_BLENDSHAPES) + len(ROTATION_PARAMETERS)  # 55

# Structured data for programmatic access
AZURE_BLENDSHAPES_DATA: Final[AzureBlendshapesData] = {
    "description": "Complete Azure Cognitive Services blendshapes and parameters",
    "version": "1.0",
    "facial_blendshapes": FACIAL_BLENDSHAPES,
    "rotation_parameters": ROTATION_PARAMETERS,
    "total_parameters": TOTAL_PARAMETERS,
    "parameter_breakdown": {
        "facial_blendshapes": len(FACIAL_BLENDSHAPES),
        "rotation_parameters": len(ROTATION_PARAMETERS)
    },
    "categories": {
        "eye_blendshapes": 14,
        "jaw_blendshapes": 4,
        "mouth_blendshapes": 24,
        "brow_blendshapes": 5,
        "cheek_blendshapes": 3,
        "nose_blendshapes": 2
    }
}

def get_blendshape_by_index(index: BlendshapeIndex) -> AzureParameterName:
    """
    Get Azure blendshape name by index.

    Args:
        index: Parameter index (0-54)

    Returns:
        Blendshape or rotation parameter name

    Raises:
        IndexError: If index is out of range

    Example:
        >>> get_blendshape_by_index(0)
        'eyeBlinkLeft'
        >>> get_blendshape_by_index(52)
        'headRoll'
    """
    if index < 0 or index >= TOTAL_PARAMETERS:
        raise IndexError(f"Index {index} out of range (0-{TOTAL_PARAMETERS-1})")

    if index < len(FACIAL_BLENDSHAPES):
        return FACIAL_BLENDSHAPES[index]
    else:
        return ROTATION_PARAMETERS[index - len(FACIAL_BLENDSHAPES)]

def get_blendshape_index(name: AzureParameterName) -> BlendshapeIndex:
    """
    Get Azure parameter index by name.

    Args:
        name: Blendshape or rotation parameter name

    Returns:
        Parameter index (0-54)

    Raises:
        ValueError: If name is not found

    Example:
        >>> get_blendshape_index('eyeBlinkLeft')
        0
        >>> get_blendshape_index('headRoll')
        52
    """
    if name in FACIAL_BLENDSHAPES:
        return FACIAL_BLENDSHAPES.index(name)
    elif name in ROTATION_PARAMETERS:
        return len(FACIAL_BLENDSHAPES) + ROTATION_PARAMETERS.index(name)
    else:
        raise ValueError(f"Blendshape '{name}' not found in Azure parameters")

def is_rotation_parameter(name: AzureParameterName) -> bool:
    """
    Check if parameter is a rotation parameter.

    Args:
        name: Parameter name

    Returns:
        True if rotation parameter, False if facial blendshape

    Example:
        >>> is_rotation_parameter('headRoll')
        True
        >>> is_rotation_parameter('eyeBlinkLeft')
        False
    """
    return name in ROTATION_PARAMETERS

def is_facial_blendshape(name: AzureParameterName) -> bool:
    """
    Check if parameter is a facial blendshape.

    Args:
        name: Parameter name

    Returns:
        True if facial blendshape, False if rotation parameter

    Example:
        >>> is_facial_blendshape('eyeBlinkLeft')
        True
        >>> is_facial_blendshape('headRoll')
        False
    """
    return name in FACIAL_BLENDSHAPES

def get_blendshape_category(name: AzureBlendshapeName) -> Literal["eye", "jaw", "mouth", "brow", "cheek", "nose"]:
    """
    Get the category of an Azure blendshape.

    Args:
        name: Azure blendshape name

    Returns:
        Category name

    Raises:
        ValueError: If name is not a facial blendshape

    Example:
        >>> get_blendshape_category('eyeBlinkLeft')
        'eye'
        >>> get_blendshape_category('jawOpen')
        'jaw'
    """
    if name.startswith('eye'):
        return "eye"
    elif name.startswith('jaw'):
        return "jaw"
    elif name.startswith('mouth') or name == 'tongueOut':
        return "mouth"
    elif name.startswith('brow'):
        return "brow"
    elif name.startswith('cheek'):
        return "cheek"
    elif name.startswith('nose'):
        return "nose"
    else:
        raise ValueError(f"Unknown blendshape category for '{name}'")
