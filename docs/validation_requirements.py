"""
Validation Requirements for MetaHuman FBX Files

This module defines the validation requirements for MetaHuman FBX files that will be
processed by the Azure pipeline. It includes expected morph target counts, required
bone structures, and validation functions.

Validation ensures:
- FBX contains expected 823 MetaHuman morph targets
- Required bones exist for head/eye animations (9 variations)
- Proper mesh structure and naming conventions
- Compatible format for Azure Cognitive Services processing

Used by step1_validation for pre-processing verification.
"""

from typing import List, Dict, Optional, TypedDict, Literal, Final, Union
from enum import Enum

# Type definitions for validation structures
class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationResult(TypedDict):
    """Type definition for validation result structure."""
    level: ValidationLevel
    message: str
    details: Optional[str]

class ValidationSummary(TypedDict):
    """Type definition for complete validation summary."""
    total_checks: int
    errors: int
    warnings: int
    info: int
    passed: bool
    results: List[ValidationResult]

BoneName = Literal[
    "head", "head_joint", "Head",
    "leftEye", "left_eye", "LeftEye",
    "rightEye", "right_eye", "RightEye"
]

MeshName = Literal["head_lod0_mesh", "teeth_lod0_mesh", "hair_lod0_mesh"]

class BoneRequirements(TypedDict):
    """Type definition for bone requirements structure."""
    required_bones: List[BoneName]
    optional_bones: List[str]
    bone_variations: int

class MorphTargetRequirements(TypedDict):
    """Type definition for morph target requirements structure."""
    expected_count: int
    required_prefixes: List[str]
    validation_patterns: List[str]

class MeshRequirements(TypedDict):
    """Type definition for mesh requirements structure."""
    required_meshes: List[MeshName]
    optional_meshes: List[str]

class ValidationRequirementsData(TypedDict):
    """Type definition for complete validation requirements structure."""
    description: str
    version: str
    morph_targets: MorphTargetRequirements
    bones: BoneRequirements
    meshes: MeshRequirements
    file_format_requirements: Dict[str, Union[str, bool, int]]

# Expected morph target count for MetaHuman FBX files
EXPECTED_MORPH_TARGET_COUNT: Final[int] = 823

# Required bones for head and eye animations - 9 variations total
REQUIRED_BONES: Final[List[BoneName]] = [
    # Head bone variations (3) - different naming conventions
    "head",            # Standard head bone
    "head_joint",      # Alternative head bone naming
    "Head",            # Capitalized variant

    # Left eye bone variations (3) - different naming conventions
    "leftEye",         # Standard left eye bone
    "left_eye",        # Underscore variant
    "LeftEye",         # Capitalized variant

    # Right eye bone variations (3) - different naming conventions
    "rightEye",        # Standard right eye bone
    "right_eye",       # Underscore variant
    "RightEye",        # Capitalized variant
]

# Optional bones that may be present but not required
OPTIONAL_BONES: Final[List[str]] = [
    "neck",            # Neck bone for additional head control
    "spine_03",        # Upper spine connection
    "jaw",             # Jaw bone for mouth animation
    "tongue",          # Tongue bone for tongue_out animation
    "leftEyelid",      # Left eyelid bone
    "rightEyelid",     # Right eyelid bone
]

# Required mesh prefixes for morph targets
REQUIRED_MESH_PREFIXES: Final[List[str]] = [
    "head_lod0_mesh__",    # Main facial mesh prefix - most morph targets use this
    "teeth_lod0_mesh__",   # Teeth mesh prefix - tongue_out uses this
]

# Optional mesh prefixes that may be present
OPTIONAL_MESH_PREFIXES: Final[List[str]] = [
    "hair_lod0_mesh__",    # Hair mesh prefix - rarely has morph targets
    "body_lod0_mesh__",    # Body mesh prefix - not used for facial animation
    "eyelashes_lod0_mesh__", # Eyelashes mesh prefix
]

# Validation patterns for morph target names
VALIDATION_PATTERNS: Final[List[str]] = [
    r"^head_lod0_mesh__\w+",           # Head mesh morphs
    r"^teeth_lod0_mesh__\w+",          # Teeth mesh morphs
    r"^\w+_[LR]$",                     # Side-specific morphs (_L, _R)
    r"^\w+_(left|right)$",             # Alternative side naming
    r"^(eye|jaw|mouth|brow|cheek|nose)_\w+", # Facial feature categories
]

# File format requirements
FILE_FORMAT_REQUIREMENTS: Final[Dict[str, Union[str, bool, int]]] = {
    "extension": ".fbx",
    "binary_format": True,
    "version_compatibility": "FBX 2020.0 or newer",
    "max_file_size_mb": 500,
    "requires_animations": False,
    "requires_textures": False,
    "requires_materials": False,
}

# Complete validation requirements data structure
VALIDATION_REQUIREMENTS: Final[ValidationRequirementsData] = {
    "description": "MetaHuman FBX validation requirements for Azure pipeline",
    "version": "1.0",
    "morph_targets": {
        "expected_count": EXPECTED_MORPH_TARGET_COUNT,
        "required_prefixes": REQUIRED_MESH_PREFIXES,
        "validation_patterns": VALIDATION_PATTERNS,
    },
    "bones": {
        "required_bones": REQUIRED_BONES,
        "optional_bones": OPTIONAL_BONES,
        "bone_variations": len(REQUIRED_BONES),
    },
    "meshes": {
        "required_meshes": ["head_lod0_mesh", "teeth_lod0_mesh"],
        "optional_meshes": ["hair_lod0_mesh"],
    },
    "file_format_requirements": FILE_FORMAT_REQUIREMENTS,
}

def validate_morph_target_count(actual_count: int) -> ValidationResult:
    """
    Validate morph target count against expected value.

    Args:
        actual_count: Actual number of morph targets found

    Returns:
        Validation result with level and message

    Example:
        >>> validate_morph_target_count(823)
        {'level': ValidationLevel.INFO, 'message': 'Morph target count is correct', 'details': '823 morph targets found'}
        >>> validate_morph_target_count(800)
        {'level': ValidationLevel.WARNING, 'message': 'Morph target count differs from expected', 'details': 'Found 800, expected 823'}
    """
    if actual_count == EXPECTED_MORPH_TARGET_COUNT:
        return {
            "level": ValidationLevel.INFO,
            "message": "Morph target count is correct",
            "details": f"{actual_count} morph targets found"
        }
    elif actual_count > EXPECTED_MORPH_TARGET_COUNT * 0.9:  # Within 90% tolerance
        return {
            "level": ValidationLevel.WARNING,
            "message": "Morph target count differs from expected",
            "details": f"Found {actual_count}, expected {EXPECTED_MORPH_TARGET_COUNT}"
        }
    else:
        return {
            "level": ValidationLevel.ERROR,
            "message": "Morph target count significantly below expected",
            "details": f"Found {actual_count}, expected {EXPECTED_MORPH_TARGET_COUNT}"
        }

def validate_bone_presence(bones_found: List[str]) -> List[ValidationResult]:
    """
    Validate presence of required bones.

    Args:
        bones_found: List of bone names found in FBX

    Returns:
        List of validation results for bone checks

    Example:
        >>> validate_bone_presence(['head', 'leftEye', 'rightEye'])
        [{'level': ValidationLevel.INFO, 'message': 'Required bones found', 'details': 'All critical bones present'}]
    """
    results: List[ValidationResult] = []
    bones_set = set(bones_found)

    # Check for head bone (at least one variant required)
    head_bones = {"head", "head_joint", "Head"}
    if not head_bones.intersection(bones_set):
        results.append({
            "level": ValidationLevel.ERROR,
            "message": "No head bone found",
            "details": f"Expected one of: {', '.join(head_bones)}"
        })

    # Check for left eye bone (at least one variant required)
    left_eye_bones = {"leftEye", "left_eye", "LeftEye"}
    if not left_eye_bones.intersection(bones_set):
        results.append({
            "level": ValidationLevel.ERROR,
            "message": "No left eye bone found",
            "details": f"Expected one of: {', '.join(left_eye_bones)}"
        })

    # Check for right eye bone (at least one variant required)
    right_eye_bones = {"rightEye", "right_eye", "RightEye"}
    if not right_eye_bones.intersection(bones_set):
        results.append({
            "level": ValidationLevel.ERROR,
            "message": "No right eye bone found",
            "details": f"Expected one of: {', '.join(right_eye_bones)}"
        })

    # If all required bone types found, add success result
    if (head_bones.intersection(bones_set) and
        left_eye_bones.intersection(bones_set) and
        right_eye_bones.intersection(bones_set)):
        results.append({
            "level": ValidationLevel.INFO,
            "message": "Required bones found",
            "details": "All critical bones present"
        })

    return results

def validate_mesh_prefix_coverage(morph_targets: List[str]) -> List[ValidationResult]:
    """
    Validate mesh prefix coverage in morph targets.

    Args:
        morph_targets: List of morph target names

    Returns:
        List of validation results for mesh prefix checks

    Example:
        >>> validate_mesh_prefix_coverage(['head_lod0_mesh__eye_blink_L', 'teeth_lod0_mesh__tongue_out'])
        [{'level': ValidationLevel.INFO, 'message': 'Good mesh prefix coverage', 'details': 'Found prefixed morphs: head_lod0_mesh__ (1), teeth_lod0_mesh__ (1)'}]
    """
    results: List[ValidationResult] = []
    prefix_counts: Dict[str, int] = {}

    # Count morph targets by prefix
    for target in morph_targets:
        for prefix in REQUIRED_MESH_PREFIXES + OPTIONAL_MESH_PREFIXES:
            if target.startswith(prefix):
                prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
                break

    # Check required prefixes
    missing_required: List[str] = []
    for prefix in REQUIRED_MESH_PREFIXES:
        if prefix not in prefix_counts:
            missing_required.append(prefix)

    if missing_required:
        results.append({
            "level": ValidationLevel.WARNING,
            "message": "Missing required mesh prefixes",
            "details": f"Missing: {', '.join(missing_required)}"
        })

    # Report coverage
    if prefix_counts:
        coverage_details = ", ".join([f"{prefix} ({count})" for prefix, count in prefix_counts.items()])
        results.append({
            "level": ValidationLevel.INFO,
            "message": "Good mesh prefix coverage",
            "details": f"Found prefixed morphs: {coverage_details}"
        })
    else:
        results.append({
            "level": ValidationLevel.WARNING,
            "message": "No mesh prefixes found",
            "details": "All morph targets appear to be unprefixed"
        })

    return results

def validate_naming_patterns(morph_targets: List[str]) -> ValidationResult:
    """
    Validate morph target naming patterns.

    Args:
        morph_targets: List of morph target names

    Returns:
        Validation result for naming pattern compliance

    Example:
        >>> validate_naming_patterns(['head_lod0_mesh__eye_blink_L', 'mouth_smile_R'])
        {'level': ValidationLevel.INFO, 'message': 'Good naming pattern compliance', 'details': '100% of morph targets follow expected patterns'}
    """
    import re

    pattern_matches = 0
    for target in morph_targets:
        for pattern in VALIDATION_PATTERNS:
            if re.match(pattern, target):
                pattern_matches += 1
                break

    compliance_rate = (pattern_matches / len(morph_targets)) * 100 if morph_targets else 0

    if compliance_rate >= 90:
        return {
            "level": ValidationLevel.INFO,
            "message": "Good naming pattern compliance",
            "details": f"{compliance_rate:.0f}% of morph targets follow expected patterns"
        }
    elif compliance_rate >= 70:
        return {
            "level": ValidationLevel.WARNING,
            "message": "Moderate naming pattern compliance",
            "details": f"{compliance_rate:.0f}% of morph targets follow expected patterns"
        }
    else:
        return {
            "level": ValidationLevel.ERROR,
            "message": "Poor naming pattern compliance",
            "details": f"Only {compliance_rate:.0f}% of morph targets follow expected patterns"
        }

def validate_file_requirements(file_path: str, file_size_mb: float) -> List[ValidationResult]:
    """
    Validate file format requirements.

    Args:
        file_path: Path to the FBX file
        file_size_mb: File size in megabytes

    Returns:
        List of validation results for file requirements

    Example:
        >>> validate_file_requirements('model.fbx', 50.5)
        [{'level': ValidationLevel.INFO, 'message': 'File extension is correct', 'details': '.fbx extension found'}]
    """
    results: List[ValidationResult] = []

    # Check file extension
    if file_path.lower().endswith('.fbx'):
        results.append({
            "level": ValidationLevel.INFO,
            "message": "File extension is correct",
            "details": ".fbx extension found"
        })
    else:
        results.append({
            "level": ValidationLevel.ERROR,
            "message": "Incorrect file extension",
            "details": f"Expected .fbx, got {file_path.split('.')[-1] if '.' in file_path else 'no extension'}"
        })

    # Check file size
    max_size = FILE_FORMAT_REQUIREMENTS["max_file_size_mb"]
    if isinstance(max_size, int) and file_size_mb <= max_size:
        results.append({
            "level": ValidationLevel.INFO,
            "message": "File size is acceptable",
            "details": f"{file_size_mb:.1f}MB (max {max_size}MB)"
        })
    elif isinstance(max_size, int):
        results.append({
            "level": ValidationLevel.WARNING,
            "message": "File size exceeds recommendation",
            "details": f"{file_size_mb:.1f}MB exceeds {max_size}MB"
        })

    return results

def run_complete_validation(
    morph_targets: List[str],
    bones: List[str],
    file_path: str,
    file_size_mb: float
) -> ValidationSummary:
    """
    Run complete validation suite on FBX data.

    Args:
        morph_targets: List of morph target names
        bones: List of bone names
        file_path: Path to the FBX file
        file_size_mb: File size in megabytes

    Returns:
        Complete validation summary with all results

    Example:
        >>> summary = run_complete_validation(['morph1', 'morph2'], ['head'], 'test.fbx', 10.0)
        >>> summary['passed']
        False
    """
    all_results: List[ValidationResult] = []

    # Run all validation checks
    all_results.append(validate_morph_target_count(len(morph_targets)))
    all_results.extend(validate_bone_presence(bones))
    all_results.extend(validate_mesh_prefix_coverage(morph_targets))
    all_results.append(validate_naming_patterns(morph_targets))
    all_results.extend(validate_file_requirements(file_path, file_size_mb))

    # Count results by level
    error_count = sum(1 for r in all_results if r["level"] == ValidationLevel.ERROR)
    warning_count = sum(1 for r in all_results if r["level"] == ValidationLevel.WARNING)
    info_count = sum(1 for r in all_results if r["level"] == ValidationLevel.INFO)

    return {
        "total_checks": len(all_results),
        "errors": error_count,
        "warnings": warning_count,
        "info": info_count,
        "passed": error_count == 0,  # Pass if no errors (warnings are acceptable)
        "results": all_results
    }
