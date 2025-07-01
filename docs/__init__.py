"""
Documentation modules for MetaHuman to Azure pipeline.

This package contains the single source of truth for all Azure blendshapes,
MetaHuman mappings, and validation requirements with full type safety.

Modules:
- azure_blendshapes_complete: Azure parameters with type safety
- metahuman_to_azure_mappings: MetaHuman→Azure mappings with utilities
- validation_requirements: Validation specs with validation functions
"""

# Re-export key types and constants for easy access
from .azure_blendshapes_complete import (
    FACIAL_BLENDSHAPES,
    ROTATION_PARAMETERS,
    TOTAL_PARAMETERS,
    AzureBlendshapeName,
    AzureRotationName,
    AzureParameterName,
    get_blendshape_by_index,
    get_blendshape_index,
    is_rotation_parameter,
    is_facial_blendshape,
    get_blendshape_category,
    AZURE_BLENDSHAPES_DATA
)

from .metahuman_to_azure_mappings import (
    METAHUMAN_NAME_MAPPINGS,
    MetaHumanMorphName,
    MappingCategory,
    get_azure_name,
    get_metahuman_names,
    has_mesh_prefix,
    get_mesh_prefix,
    get_unique_azure_mappings,
    is_compound_mapping,
    analyze_mapping,
    get_mappings_by_category,
    MAPPING_STATS
)

from .validation_requirements import (
    EXPECTED_MORPH_TARGET_COUNT,
    REQUIRED_BONES,
    OPTIONAL_BONES,
    REQUIRED_MESH_PREFIXES,
    ValidationLevel,
    ValidationResult,
    ValidationSummary,
    BoneName,
    MeshName,
    validate_morph_target_count,
    validate_bone_presence,
    validate_mesh_prefix_coverage,
    validate_naming_patterns,
    validate_file_requirements,
    run_complete_validation,
    VALIDATION_REQUIREMENTS
)

__all__ = [
    # Azure blendshapes
    'FACIAL_BLENDSHAPES',
    'ROTATION_PARAMETERS',
    'TOTAL_PARAMETERS',
    'AzureBlendshapeName',
    'AzureRotationName',
    'AzureParameterName',
    'get_blendshape_by_index',
    'get_blendshape_index',
    'is_rotation_parameter',
    'is_facial_blendshape',
    'get_blendshape_category',
    'AZURE_BLENDSHAPES_DATA',

    # MetaHuman mappings
    'METAHUMAN_NAME_MAPPINGS',
    'MetaHumanMorphName',
    'MappingCategory',
    'get_azure_name',
    'get_metahuman_names',
    'has_mesh_prefix',
    'get_mesh_prefix',
    'get_unique_azure_mappings',
    'is_compound_mapping',
    'analyze_mapping',
    'get_mappings_by_category',
    'MAPPING_STATS',

    # Validation requirements
    'EXPECTED_MORPH_TARGET_COUNT',
    'REQUIRED_BONES',
    'OPTIONAL_BONES',
    'REQUIRED_MESH_PREFIXES',
    'ValidationLevel',
    'ValidationResult',
    'ValidationSummary',
    'BoneName',
    'MeshName',
    'validate_morph_target_count',
    'validate_bone_presence',
    'validate_mesh_prefix_coverage',
    'validate_naming_patterns',
    'validate_file_requirements',
    'run_complete_validation',
    'VALIDATION_REQUIREMENTS'
]
