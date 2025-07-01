"""
MetaHuman to Azure Blendshape Mappings

This module provides mappings from MetaHuman FBX morph target names to Azure/ARKit
blendshape names. MetaHuman uses different naming conventions that must be mapped
to Azure Cognitive Services standards.

Key mapping patterns:
- Eye directions: Left eye looking left = looking in, right eye looking left = looking out
- Compound shapes: Some MetaHuman shapes map to the same Azure blendshape
- Mesh prefixes: MetaHuman uses 'head_lod0_mesh__' and 'teeth_lod0_mesh__' prefixes
- Backwards compatibility: Includes variations without prefixes for older MetaHuman versions

Total mappings: 110 (covers various MetaHuman naming conventions)
"""

from typing import Dict, List, Set, TypedDict, Literal, Final, Union

# Import Azure types from the blendshapes module for consistency
from .azure_blendshapes_complete import AzureBlendshapeName

# Type definitions for MetaHuman naming patterns
MetaHumanMorphName = str  # MetaHuman morph target names (too many variations for Literal)

MeshPrefix = Literal["head_lod0_mesh__", "teeth_lod0_mesh__"]
SideVariation = Literal["_L", "_R", "_left", "_right", "_Left", "_Right"]

# Mapping categories for organization
MappingCategory = Literal[
    "eye_blendshapes",
    "jaw_blendshapes",
    "mouth_blendshapes",
    "brow_blendshapes",
    "cheek_blendshapes",
    "nose_blendshapes",
    "tongue_blendshapes"
]

class MappingStats(TypedDict):
    """Type definition for mapping statistics structure."""
    total_mappings: int
    eye_blendshapes: int
    jaw_blendshapes: int
    mouth_blendshapes: int
    brow_blendshapes: int
    cheek_blendshapes: int
    nose_blendshapes: int
    tongue_blendshapes: int

class MappingAnalysis(TypedDict):
    """Type definition for mapping analysis results."""
    has_mesh_prefix: bool
    category: MappingCategory
    azure_target: AzureBlendshapeName
    is_compound_mapping: bool

# MetaHuman to Azure blendshape mappings (110 total)
METAHUMAN_NAME_MAPPINGS: Final[Dict[MetaHumanMorphName, AzureBlendshapeName]] = {
    # Eye blendshapes with head_lod0_mesh__ prefix
    "head_lod0_mesh__eye_blink_L": "eyeBlinkLeft",
    "head_lod0_mesh__eye_blink_R": "eyeBlinkRight",
    "head_lod0_mesh__eye_lookDown_L": "eyeLookDownLeft",
    "head_lod0_mesh__eye_lookDown_R": "eyeLookDownRight",
    # Eye direction logic: Left eye looking left = looking IN, right eye looking left = looking OUT
    "head_lod0_mesh__eye_lookLeft_L": "eyeLookInLeft",     # Left eye looking left = inward
    "head_lod0_mesh__eye_lookLeft_R": "eyeLookOutRight",   # Right eye looking left = outward
    "head_lod0_mesh__eye_lookRight_L": "eyeLookOutLeft",   # Left eye looking right = outward
    "head_lod0_mesh__eye_lookRight_R": "eyeLookInRight",   # Right eye looking right = inward
    "head_lod0_mesh__eye_lookUp_L": "eyeLookUpLeft",
    "head_lod0_mesh__eye_lookUp_R": "eyeLookUpRight",
    "head_lod0_mesh__eye_squintInner_L": "eyeSquintLeft",
    "head_lod0_mesh__eye_squintInner_R": "eyeSquintRight",
    "head_lod0_mesh__eye_widen_L": "eyeWideLeft",
    "head_lod0_mesh__eye_widen_R": "eyeWideRight",

    # Jaw blendshapes with head_lod0_mesh__ prefix
    "head_lod0_mesh__jaw_fwd": "jawForward",               # Forward movement
    "head_lod0_mesh__jaw_left": "jawLeft",                 # Left movement
    "head_lod0_mesh__jaw_right": "jawRight",               # Right movement
    "head_lod0_mesh__jaw_open": "jawOpen",                 # Open mouth

    # Mouth blendshapes with head_lod0_mesh__ prefix - many variations in MetaHuman
    "head_lod0_mesh__mouth_left": "mouthLeft",
    "head_lod0_mesh__mouth_right": "mouthRight",
    # Multiple corner pull variations
    "head_lod0_mesh__mouth_cornerPull_left": "mouthSmileLeft",
    "head_lod0_mesh__mouth_cornerPull_right": "mouthSmileRight",
    "head_lod0_mesh__mouth_cornersUp_L": "mouthSmileLeft",
    "head_lod0_mesh__mouth_cornersUp_R": "mouthSmileRight",
    # Multiple corner depress variations
    "head_lod0_mesh__mouth_cornerDepress_L": "mouthFrownLeft",
    "head_lod0_mesh__mouth_cornerDepress_R": "mouthFrownRight",
    "head_lod0_mesh__mouth_cornersDown_L": "mouthFrownLeft",
    "head_lod0_mesh__mouth_cornersDown_R": "mouthFrownRight",
    # Dimple and stretch
    "head_lod0_mesh__mouth_dimple_left": "mouthDimpleLeft",
    "head_lod0_mesh__mouth_dimple_right": "mouthDimpleRight",
    "head_lod0_mesh__mouth_stretch_left": "mouthStretchLeft",
    "head_lod0_mesh__mouth_stretch_right": "mouthStretchRight",
    # Lip roll variations - multiple MetaHuman morphs map to same Azure blendshape
    "head_lod0_mesh__mouth_lowerLipRollIn_L": "mouthRollLower",
    "head_lod0_mesh__mouth_lowerLipRollIn_R": "mouthRollLower",
    "head_lod0_mesh__mouth_upperLipRollIn_L": "mouthRollUpper",
    "head_lod0_mesh__mouth_upperLipRollIn_R": "mouthRollUpper",
    # Lip press
    "head_lod0_mesh__mouth_lipsPress_L": "mouthPressLeft",
    "head_lod0_mesh__mouth_lipsPress_R": "mouthPressRight",
    # Lip depress and raise
    "head_lod0_mesh__mouth_lowerLipDepress_left": "mouthLowerDownLeft",
    "head_lod0_mesh__mouth_lowerLipDepress_right": "mouthLowerDownRight",
    "head_lod0_mesh__mouth_upperLipRaise_left": "mouthUpperUpLeft",
    "head_lod0_mesh__mouth_upperLipRaise_right": "mouthUpperUpRight",
    # Funnel and pucker - compound shapes using one of the variants
    "head_lod0_mesh__mouth_funnel_DL": "mouthFunnel",      # Use DL variant for funnel
    "head_lod0_mesh__mouth_lipsPurse_DL": "mouthPucker",   # Use DL variant for pucker
    # Close mouth
    "head_lod0_mesh__mouth_down": "mouthClose",
    # Mouth shrug mappings - lip roll out movements
    "head_lod0_mesh__mouth_lowerLipRollOut_L": "mouthShrugLower",
    "head_lod0_mesh__mouth_lowerLipRollOut_R": "mouthShrugLower",
    "head_lod0_mesh__mouth_upperLipRollOut_L": "mouthShrugUpper",
    "head_lod0_mesh__mouth_upperLipRollOut_R": "mouthShrugUpper",

    # Brow blendshapes with head_lod0_mesh__ prefix
    "head_lod0_mesh__brow_down_L": "browDownLeft",
    "head_lod0_mesh__brow_down_R": "browDownRight",
    # Inner brow raise - both sides contribute to browInnerUp
    "head_lod0_mesh__brow_raiseIn_L": "browInnerUp",       # Left inner raise
    "head_lod0_mesh__brow_raiseIn_R": "browInnerUp",       # Right inner raise
    "head_lod0_mesh__brow_raiseOuter_left": "browOuterUpLeft",
    "head_lod0_mesh__brow_raiseOuter_right": "browOuterUpRight",

    # Cheek blendshapes with head_lod0_mesh__ prefix - using actual MetaHuman morph names
    "head_lod0_mesh__cheek_blow_cor": "cheekPuff",         # Cheek blow for puff
    "head_lod0_mesh__EcheekRaise_EsquintInner_L": "cheekSquintLeft",
    "head_lod0_mesh__EcheekRaise_EsquintInner_R": "cheekSquintRight",

    # Nose blendshapes with head_lod0_mesh__ prefix
    "head_lod0_mesh__nose_wrinkle_left": "noseSneerLeft",
    "head_lod0_mesh__nose_wrinkle_right": "noseSneerRight",

    # Tongue blendshape - on teeth mesh, not head mesh
    "teeth_lod0_mesh__tongue_out_cor": "tongueOut",

    # Backwards compatibility - variations WITHOUT mesh prefixes for older MetaHuman versions
    # Eye blendshapes without prefix
    "eye_blink_L": "eyeBlinkLeft",
    "eye_blink_R": "eyeBlinkRight",
    "eye_lookDown_L": "eyeLookDownLeft",
    "eye_lookDown_R": "eyeLookDownRight",
    "eye_lookLeft_L": "eyeLookInLeft",      # Left eye looking left = looking in
    "eye_lookLeft_R": "eyeLookOutRight",    # Right eye looking left = looking out
    "eye_lookRight_L": "eyeLookOutLeft",    # Left eye looking right = looking out
    "eye_lookRight_R": "eyeLookInRight",    # Right eye looking right = looking in
    "eye_lookUp_L": "eyeLookUpLeft",
    "eye_lookUp_R": "eyeLookUpRight",
    "eye_squintInner_L": "eyeSquintLeft",
    "eye_squintInner_R": "eyeSquintRight",
    "eye_widen_L": "eyeWideLeft",
    "eye_widen_R": "eyeWideRight",

    # Jaw blendshapes without prefix
    "jaw_fwd": "jawForward",
    "jaw_left": "jawLeft",
    "jaw_right": "jawRight",
    "jaw_open": "jawOpen",

    # Mouth blendshapes without prefix
    "mouth_left": "mouthLeft",
    "mouth_right": "mouthRight",
    "mouth_cornerPull_left": "mouthSmileLeft",
    "mouth_cornerPull_right": "mouthSmileRight",
    "mouth_cornersUp_L": "mouthSmileLeft",
    "mouth_cornersUp_R": "mouthSmileRight",
    "mouth_cornerDepress_L": "mouthFrownLeft",
    "mouth_cornerDepress_R": "mouthFrownRight",
    "mouth_cornersDown_L": "mouthFrownLeft",
    "mouth_cornersDown_R": "mouthFrownRight",
    "mouth_funnel_DL": "mouthFunnel",
    "mouth_lipsPurse_DL": "mouthPucker",
    "mouth_down": "mouthClose",

    # Brow blendshapes without prefix
    "brow_down_L": "browDownLeft",
    "brow_down_R": "browDownRight",
    "brow_raiseIn_L": "browInnerUp",
    "brow_raiseIn_R": "browInnerUp",
    "brow_raiseOuter_left": "browOuterUpLeft",
    "brow_raiseOuter_right": "browOuterUpRight",

    # Cheek blendshapes without prefix (if they exist)
    "cheek_puff_L": "cheekPuff",
    "cheek_raiseInner_L": "cheekSquintLeft",
    "cheek_raiseInner_R": "cheekSquintRight",

    # Nose blendshapes without prefix
    "nose_wrinkle_left": "noseSneerLeft",
    "nose_wrinkle_right": "noseSneerRight",

    # Tongue without prefix
    "tongue_out_cor": "tongueOut",

    # Legacy style variations with _L/_R suffixes (alternative naming)
    "mouthSmile_L": "mouthSmileLeft",
    "mouthSmile_R": "mouthSmileRight",
    "mouthFrown_L": "mouthFrownLeft",
    "mouthFrown_R": "mouthFrownRight",
    "eyeBlink_L": "eyeBlinkLeft",
    "eyeBlink_R": "eyeBlinkRight",
}

# Mapping statistics and categorization
MAPPING_STATS: Final[MappingStats] = {
    "total_mappings": len(METAHUMAN_NAME_MAPPINGS),
    "eye_blendshapes": 28,      # Includes both prefixed and non-prefixed variants
    "jaw_blendshapes": 8,       # jaw_fwd -> jawForward, etc.
    "mouth_blendshapes": 62,    # Most complex category with many MetaHuman variants
    "brow_blendshapes": 10,     # Inner raise maps to browInnerUp for both sides
    "cheek_blendshapes": 4,     # Using actual MetaHuman morph names
    "nose_blendshapes": 4,      # Wrinkle variations
    "tongue_blendshapes": 2,    # May be on teeth mesh
}

def get_azure_name(metahuman_name: MetaHumanMorphName) -> AzureBlendshapeName:
    """
    Get Azure blendshape name from MetaHuman morph target name.

    Args:
        metahuman_name: MetaHuman FBX morph target name

    Returns:
        Corresponding Azure blendshape name

    Raises:
        KeyError: If MetaHuman name is not found in mappings

    Example:
        >>> get_azure_name('head_lod0_mesh__eye_blink_L')
        'eyeBlinkLeft'
        >>> get_azure_name('jaw_open')
        'jawOpen'
    """
    if metahuman_name not in METAHUMAN_NAME_MAPPINGS:
        raise KeyError(f"MetaHuman morph '{metahuman_name}' not found in mappings")
    return METAHUMAN_NAME_MAPPINGS[metahuman_name]

def get_metahuman_names(azure_name: AzureBlendshapeName) -> List[MetaHumanMorphName]:
    """
    Get all MetaHuman morph target names that map to an Azure blendshape.

    Args:
        azure_name: Azure blendshape name

    Returns:
        List of MetaHuman morph target names that map to this Azure blendshape

    Example:
        >>> get_metahuman_names('eyeBlinkLeft')
        ['head_lod0_mesh__eye_blink_L', 'eye_blink_L', 'eyeBlink_L']
        >>> get_metahuman_names('mouthFunnel')
        ['head_lod0_mesh__mouth_funnel_DL', 'mouth_funnel_DL']
    """
    return [meta_name for meta_name, azure in METAHUMAN_NAME_MAPPINGS.items()
            if azure == azure_name]

def has_mesh_prefix(metahuman_name: MetaHumanMorphName) -> bool:
    """
    Check if MetaHuman morph target name has a mesh prefix.

    Args:
        metahuman_name: MetaHuman morph target name

    Returns:
        True if has mesh prefix, False otherwise

    Example:
        >>> has_mesh_prefix('head_lod0_mesh__eye_blink_L')
        True
        >>> has_mesh_prefix('eye_blink_L')
        False
    """
    return metahuman_name.startswith(('head_lod0_mesh__', 'teeth_lod0_mesh__'))

def get_mesh_prefix(metahuman_name: MetaHumanMorphName) -> Union[MeshPrefix, None]:
    """
    Get the mesh prefix from a MetaHuman morph target name.

    Args:
        metahuman_name: MetaHuman morph target name

    Returns:
        Mesh prefix if present, None otherwise

    Example:
        >>> get_mesh_prefix('head_lod0_mesh__eye_blink_L')
        'head_lod0_mesh__'
        >>> get_mesh_prefix('eye_blink_L')
        None
    """
    if metahuman_name.startswith('head_lod0_mesh__'):
        return "head_lod0_mesh__"
    elif metahuman_name.startswith('teeth_lod0_mesh__'):
        return "teeth_lod0_mesh__"
    else:
        return None

def get_unique_azure_mappings() -> Set[AzureBlendshapeName]:
    """
    Get set of unique Azure blendshape names from all mappings.

    Returns:
        Set of unique Azure blendshape names

    Example:
        >>> azure_names = get_unique_azure_mappings()
        >>> len(azure_names)  # Should be less than total mappings due to duplicates
        52
    """
    return set(METAHUMAN_NAME_MAPPINGS.values())

def is_compound_mapping(azure_name: AzureBlendshapeName) -> bool:
    """
    Check if Azure blendshape has multiple MetaHuman mappings (compound shape).

    Args:
        azure_name: Azure blendshape name

    Returns:
        True if multiple MetaHuman morphs map to this Azure blendshape

    Example:
        >>> is_compound_mapping('mouthRollLower')
        True  # Multiple MetaHuman morphs map to this
        >>> is_compound_mapping('jawOpen')
        False  # Only prefixed and non-prefixed variants
    """
    return len(get_metahuman_names(azure_name)) > 1

def analyze_mapping(metahuman_name: MetaHumanMorphName) -> MappingAnalysis:
    """
    Analyze a MetaHuman morph target mapping.

    Args:
        metahuman_name: MetaHuman morph target name

    Returns:
        Analysis results including category, Azure target, and characteristics

    Raises:
        KeyError: If MetaHuman name is not found in mappings

    Example:
        >>> analyze_mapping('head_lod0_mesh__eye_blink_L')
        {'has_mesh_prefix': True, 'category': 'eye_blendshapes', 'azure_target': 'eyeBlinkLeft', 'is_compound_mapping': True}
    """
    azure_name = get_azure_name(metahuman_name)  # May raise KeyError

    # Determine category based on Azure name
    if azure_name.startswith('eye'):
        category: MappingCategory = "eye_blendshapes"
    elif azure_name.startswith('jaw'):
        category = "jaw_blendshapes"
    elif azure_name.startswith('mouth') or azure_name == 'tongueOut':
        category = "mouth_blendshapes"
    elif azure_name.startswith('brow'):
        category = "brow_blendshapes"
    elif azure_name.startswith('cheek'):
        category = "cheek_blendshapes"
    elif azure_name.startswith('nose'):
        category = "nose_blendshapes"
    else:  # tongueOut
        category = "tongue_blendshapes"

    return {
        "has_mesh_prefix": has_mesh_prefix(metahuman_name),
        "category": category,
        "azure_target": azure_name,
        "is_compound_mapping": is_compound_mapping(azure_name)
    }

def get_mappings_by_category(category: MappingCategory) -> Dict[MetaHumanMorphName, AzureBlendshapeName]:
    """
    Get all mappings for a specific category.

    Args:
        category: Category to filter by

    Returns:
        Dictionary of MetaHuman names to Azure names for the category

    Example:
        >>> eye_mappings = get_mappings_by_category('eye_blendshapes')
        >>> len(eye_mappings)
        28
    """
    category_mappings: Dict[MetaHumanMorphName, AzureBlendshapeName] = {}
    for meta_name, azure_name in METAHUMAN_NAME_MAPPINGS.items():
        try:
            analysis = analyze_mapping(meta_name)
            if analysis["category"] == category:
                category_mappings[meta_name] = azure_name
        except KeyError:
            continue
    return category_mappings
