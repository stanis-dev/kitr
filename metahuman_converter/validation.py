"""
FBX validation module for MetaHuman conversion pipeline.

Provides validation functions to check FBX files for required blendshapes,
bones, and other properties needed for successful GLB conversion.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from .constants import ARKIT_BLENDSHAPES, REQUIRED_BONES, CORE_REQUIRED_BONES


# Configure module logger
logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Enumeration of validation result types."""
    PASS = "pass"
    WARNING = "warning" 
    FAIL = "fail"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during FBX validation."""
    level: ValidationResult
    message: str
    details: Optional[Dict] = None


@dataclass
class FBXValidationReport:
    """Complete validation report for an FBX file."""
    file_path: str
    overall_result: ValidationResult
    issues: List[ValidationIssue]
    found_blendshapes: Set[str]
    missing_blendshapes: Set[str]
    found_bones: Set[str] 
    missing_bones: Set[str]
    extra_blendshapes: Set[str]
    file_size_mb: float
    
    @property
    def is_valid(self) -> bool:
        """Returns True if validation passed or only has warnings."""
        return self.overall_result in [ValidationResult.PASS, ValidationResult.WARNING]
    
    @property
    def critical_issues(self) -> List[ValidationIssue]:
        """Returns only critical (FAIL level) issues."""
        return [issue for issue in self.issues if issue.level == ValidationResult.FAIL]


class FBXReader:
    """
    Placeholder FBX reader class.
    
    This will be replaced with actual FBX SDK integration later.
    For now, it simulates reading FBX files for testing purposes.
    """
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._validate_file()
    
    def _validate_file(self) -> None:
        """Validate that the file exists and is readable."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"FBX file not found: {self.file_path}")
        
        if not os.path.isfile(self.file_path):
            raise ValueError(f"Path is not a file: {self.file_path}")
        
        # Check file extension
        if not self.file_path.lower().endswith('.fbx'):
            logger.warning(f"File does not have .fbx extension: {self.file_path}")
    
    def get_blendshapes(self) -> Set[str]:
        """
        Get all blendshape names from the FBX file.
        
        Returns:
            Set of blendshape names found in the file.
        """
        # PLACEHOLDER IMPLEMENTATION
        # In real implementation, this would use FBX SDK to read morph targets
        logger.debug(f"Reading blendshapes from {self.file_path}")
        
        # Simulate different scenarios for testing
        filename = Path(self.file_path).stem.lower()
        
        if "complete" in filename:
            # Simulate a complete MetaHuman with all blendshapes
            return set(ARKIT_BLENDSHAPES)
        elif "missing" in filename:
            # Simulate missing some critical blendshapes
            return set(ARKIT_BLENDSHAPES[:-5])  # Missing last 5 blendshapes
        elif "extra" in filename:
            # Simulate extra non-ARKit blendshapes
            extra_shapes = {"customShape1", "customShape2", "oldBlendshape"}
            return set(ARKIT_BLENDSHAPES).union(extra_shapes)
        elif "minimal" in filename:
            # Simulate minimal set for testing
            return {"mouthOpen", "mouthClose", "mouthSmileLeft", "mouthSmileRight"}
        else:
            # Default: most ARKit blendshapes present
            return set(ARKIT_BLENDSHAPES[:-2])  # Missing last 2
    
    def get_bones(self) -> Set[str]:
        """
        Get all bone names from the FBX skeleton.
        
        Returns:
            Set of bone names found in the skeleton.
        """
        # PLACEHOLDER IMPLEMENTATION  
        # In real implementation, this would traverse the FBX scene hierarchy
        logger.debug(f"Reading bones from {self.file_path}")
        
        filename = Path(self.file_path).stem.lower()
        
        if "complete" in filename:
            # Simulate complete MetaHuman skeleton
            return set(REQUIRED_BONES)
        elif "noskeleton" in filename:
            # Simulate FBX with no skeleton
            return set()
        elif "minimal" in filename:
            # Simulate minimal skeleton
            return set(CORE_REQUIRED_BONES)
        else:
            # Default: most bones present but missing some optional ones
            return set(REQUIRED_BONES[:-3])  # Missing last 3 optional bones
    
    def get_file_info(self) -> Dict:
        """Get basic file information."""
        stat = os.stat(self.file_path)
        return {
            "size_bytes": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "last_modified": stat.st_mtime
        }


def validate_fbx(
    file_path: str,
    required_blendshapes: Optional[List[str]] = None,
    required_bones: Optional[List[str]] = None,
    allow_extra_blendshapes: bool = True,
    strict_mode: bool = False
) -> FBXValidationReport:
    """
    Validate an FBX file for MetaHuman to GLB conversion.
    
    Args:
        file_path: Path to the FBX file to validate
        required_blendshapes: List of required blendshape names (defaults to ARKit set)
        required_bones: List of required bone names (defaults to MetaHuman set)
        allow_extra_blendshapes: Whether to allow non-ARKit blendshapes
        strict_mode: If True, treats warnings as failures
    
    Returns:
        FBXValidationReport with validation results
        
    Raises:
        FileNotFoundError: If the FBX file doesn't exist
        ValueError: If the file path is invalid
    """
    logger.info(f"Starting FBX validation for: {file_path}")
    
    # Use defaults if not provided
    if required_blendshapes is None:
        required_blendshapes = ARKIT_BLENDSHAPES
    if required_bones is None:
        required_bones = CORE_REQUIRED_BONES if not strict_mode else REQUIRED_BONES
    
    issues = []
    overall_result = ValidationResult.PASS
    
    try:
        # Initialize FBX reader
        fbx_reader = FBXReader(file_path)
        file_info = fbx_reader.get_file_info()
        
        # Get blendshapes and bones from FBX
        found_blendshapes = fbx_reader.get_blendshapes()
        found_bones = fbx_reader.get_bones()
        
        logger.debug(f"Found {len(found_blendshapes)} blendshapes")
        logger.debug(f"Found {len(found_bones)} bones")
        
        # Validate blendshapes
        required_blendshapes_set = set(required_blendshapes)
        missing_blendshapes = required_blendshapes_set - found_blendshapes
        extra_blendshapes = found_blendshapes - required_blendshapes_set
        
        # Check for missing critical blendshapes
        if missing_blendshapes:
            level = ValidationResult.FAIL
            message = f"Missing {len(missing_blendshapes)} required blendshapes"
            issues.append(ValidationIssue(
                level=level,
                message=message,
                details={"missing_blendshapes": list(missing_blendshapes)}
            ))
            overall_result = ValidationResult.FAIL
            logger.error(f"{message}: {list(missing_blendshapes)}")
        
        # Check for extra blendshapes
        if extra_blendshapes and not allow_extra_blendshapes:
            level = ValidationResult.WARNING if not strict_mode else ValidationResult.FAIL
            message = f"Found {len(extra_blendshapes)} non-ARKit blendshapes"
            issues.append(ValidationIssue(
                level=level,
                message=message,
                details={"extra_blendshapes": list(extra_blendshapes)}
            ))
            if level == ValidationResult.FAIL:
                overall_result = ValidationResult.FAIL
            elif overall_result == ValidationResult.PASS:
                overall_result = ValidationResult.WARNING
            logger.warning(f"{message}: {list(extra_blendshapes)}")
        
        # Validate bones
        required_bones_set = set(required_bones)
        missing_bones = required_bones_set - found_bones
        
        if missing_bones:
            level = ValidationResult.FAIL
            message = f"Missing {len(missing_bones)} required bones"
            issues.append(ValidationIssue(
                level=level,
                message=message, 
                details={"missing_bones": list(missing_bones)}
            ))
            overall_result = ValidationResult.FAIL
            logger.error(f"{message}: {list(missing_bones)}")
        
        # Check file size (warn if very large)
        size_mb = file_info["size_mb"]
        if size_mb > 500:  # Warn if larger than 500MB
            level = ValidationResult.WARNING
            message = f"Large file size: {size_mb:.1f}MB"
            issues.append(ValidationIssue(
                level=level,
                message=message,
                details={"size_mb": size_mb}
            ))
            if overall_result == ValidationResult.PASS:
                overall_result = ValidationResult.WARNING
            logger.warning(message)
        
        # Log success cases
        if not issues:
            logger.info("FBX validation passed with no issues")
        elif overall_result == ValidationResult.WARNING:
            logger.info("FBX validation passed with warnings")
            
        # Create and return report
        report = FBXValidationReport(
            file_path=file_path,
            overall_result=overall_result,
            issues=issues,
            found_blendshapes=found_blendshapes,
            missing_blendshapes=missing_blendshapes,
            found_bones=found_bones,
            missing_bones=missing_bones,
            extra_blendshapes=extra_blendshapes,
            file_size_mb=size_mb
        )
        
        logger.info(f"FBX validation completed: {overall_result.value}")
        return report
        
    except Exception as e:
        logger.error(f"FBX validation failed with exception: {e}")
        raise