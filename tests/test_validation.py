"""
Unit tests for FBX validation functionality.

Tests cover various scenarios including complete files, missing blendshapes,
missing bones, and error conditions.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from metahuman_converter.validation import (
    validate_fbx,
    FBXValidationReport,
    ValidationResult,
    ValidationIssue,
    FBXReader
)
from metahuman_converter.constants import ARKIT_BLENDSHAPES, CORE_REQUIRED_BONES


class TestFBXReader:
    """Test cases for the FBXReader placeholder class."""
    
    def test_fbx_reader_file_not_found(self):
        """Test FBXReader raises FileNotFoundError for non-existent files."""
        with pytest.raises(FileNotFoundError, match="FBX file not found"):
            FBXReader("non_existent_file.fbx")
    
    def test_fbx_reader_directory_path(self):
        """Test FBXReader raises ValueError for directory paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="Path is not a file"):
                FBXReader(temp_dir)
    
    def test_fbx_reader_complete_scenario(self):
        """Test FBXReader with complete MetaHuman scenario."""
        with tempfile.NamedTemporaryFile(suffix="_complete.fbx", delete=False) as tmp:
            try:
                reader = FBXReader(tmp.name)
                blendshapes = reader.get_blendshapes()
                bones = reader.get_bones()
                
                assert blendshapes == set(ARKIT_BLENDSHAPES)
                assert len(bones) > 0
                assert "root" in bones
                assert "head" in bones
            finally:
                os.unlink(tmp.name)
    
    def test_fbx_reader_missing_scenario(self):
        """Test FBXReader with missing blendshapes scenario."""
        with tempfile.NamedTemporaryFile(suffix="_missing.fbx", delete=False) as tmp:
            try:
                reader = FBXReader(tmp.name)
                blendshapes = reader.get_blendshapes()
                
                # Should be missing last 5 blendshapes
                expected = set(ARKIT_BLENDSHAPES[:-5])
                assert blendshapes == expected
                assert len(blendshapes) == len(ARKIT_BLENDSHAPES) - 5
            finally:
                os.unlink(tmp.name)
    
    def test_fbx_reader_extra_scenario(self):
        """Test FBXReader with extra blendshapes scenario."""
        with tempfile.NamedTemporaryFile(suffix="_extra.fbx", delete=False) as tmp:
            try:
                reader = FBXReader(tmp.name)
                blendshapes = reader.get_blendshapes()
                
                # Should have all ARKit + extra shapes
                assert all(shape in blendshapes for shape in ARKIT_BLENDSHAPES)
                assert "customShape1" in blendshapes
                assert "customShape2" in blendshapes
                assert len(blendshapes) > len(ARKIT_BLENDSHAPES)
            finally:
                os.unlink(tmp.name)
    
    def test_fbx_reader_no_skeleton_scenario(self):
        """Test FBXReader with no skeleton scenario."""
        with tempfile.NamedTemporaryFile(suffix="_noskeleton.fbx", delete=False) as tmp:
            try:
                reader = FBXReader(tmp.name)
                bones = reader.get_bones()
                
                assert len(bones) == 0
            finally:
                os.unlink(tmp.name)
    
    def test_fbx_reader_file_info(self):
        """Test FBXReader file info functionality."""
        with tempfile.NamedTemporaryFile(suffix=".fbx", delete=False) as tmp:
            # Write some data to create a file with size
            tmp.write(b"test data for file size")
            tmp.flush()
            
            try:
                reader = FBXReader(tmp.name)
                file_info = reader.get_file_info()
                
                assert "size_bytes" in file_info
                assert "size_mb" in file_info
                assert "last_modified" in file_info
                assert file_info["size_bytes"] > 0
                assert file_info["size_mb"] > 0
            finally:
                os.unlink(tmp.name)


class TestValidateFBX:
    """Test cases for the validate_fbx function."""
    
    def test_validate_fbx_complete_success(self):
        """Test validation of a complete, valid FBX file."""
        with tempfile.NamedTemporaryFile(suffix="_complete.fbx", delete=False) as tmp:
            try:
                report = validate_fbx(tmp.name)
                
                assert report.overall_result == ValidationResult.PASS
                assert report.is_valid
                assert len(report.issues) == 0
                assert len(report.missing_blendshapes) == 0
                assert len(report.missing_bones) == 0
                assert report.found_blendshapes == set(ARKIT_BLENDSHAPES)
                assert len(report.critical_issues) == 0
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_missing_blendshapes(self):
        """Test validation with missing required blendshapes."""
        with tempfile.NamedTemporaryFile(suffix="_missing.fbx", delete=False) as tmp:
            try:
                report = validate_fbx(tmp.name)
                
                assert report.overall_result == ValidationResult.FAIL
                assert not report.is_valid
                assert len(report.issues) > 0
                assert len(report.missing_blendshapes) == 5  # Missing last 5
                assert len(report.critical_issues) > 0
                
                # Check that the issue details are present
                blendshape_issue = next(
                    (issue for issue in report.issues 
                     if "blendshapes" in issue.message), None
                )
                assert blendshape_issue is not None
                assert blendshape_issue.level == ValidationResult.FAIL
                assert blendshape_issue.details is not None
                assert "missing_blendshapes" in blendshape_issue.details
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_missing_bones(self):
        """Test validation with missing required bones."""
        with tempfile.NamedTemporaryFile(suffix="_noskeleton.fbx", delete=False) as tmp:
            try:
                report = validate_fbx(tmp.name)
                
                assert report.overall_result == ValidationResult.FAIL
                assert not report.is_valid
                assert len(report.missing_bones) == len(CORE_REQUIRED_BONES)
                
                # Check for bone-related issues
                bone_issue = next(
                    (issue for issue in report.issues 
                     if "bones" in issue.message), None
                )
                assert bone_issue is not None
                assert bone_issue.level == ValidationResult.FAIL
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_extra_blendshapes_allowed(self):
        """Test validation with extra blendshapes when allowed."""
        with tempfile.NamedTemporaryFile(suffix="_extra.fbx", delete=False) as tmp:
            try:
                report = validate_fbx(tmp.name, allow_extra_blendshapes=True)
                
                assert report.overall_result == ValidationResult.PASS
                assert report.is_valid
                assert len(report.extra_blendshapes) > 0
                assert "customShape1" in report.extra_blendshapes
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_extra_blendshapes_warning(self):
        """Test validation with extra blendshapes generating warning."""
        with tempfile.NamedTemporaryFile(suffix="_extra.fbx", delete=False) as tmp:
            try:
                report = validate_fbx(tmp.name, allow_extra_blendshapes=False)
                
                assert report.overall_result == ValidationResult.WARNING
                assert report.is_valid  # Warnings still allow validity
                assert len(report.extra_blendshapes) > 0
                
                # Check for warning issue
                extra_issue = next(
                    (issue for issue in report.issues 
                     if "non-ARKit" in issue.message), None
                )
                assert extra_issue is not None
                assert extra_issue.level == ValidationResult.WARNING
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_strict_mode(self):
        """Test validation in strict mode."""
        with tempfile.NamedTemporaryFile(suffix="_extra.fbx", delete=False) as tmp:
            try:
                report = validate_fbx(
                    tmp.name, 
                    allow_extra_blendshapes=False, 
                    strict_mode=True
                )
                
                assert report.overall_result == ValidationResult.FAIL
                assert not report.is_valid
                
                # In strict mode, extra blendshapes should be FAIL level
                extra_issue = next(
                    (issue for issue in report.issues 
                     if "non-ARKit" in issue.message), None
                )
                assert extra_issue is not None
                assert extra_issue.level == ValidationResult.FAIL
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_custom_requirements(self):
        """Test validation with custom blendshape and bone requirements."""
        with tempfile.NamedTemporaryFile(suffix="_minimal.fbx", delete=False) as tmp:
            try:
                custom_blendshapes = ["mouthOpen", "mouthClose"]
                custom_bones = ["root", "head"]
                
                report = validate_fbx(
                    tmp.name,
                    required_blendshapes=custom_blendshapes,
                    required_bones=custom_bones
                )
                
                assert report.overall_result == ValidationResult.PASS
                assert report.is_valid
                assert len(report.missing_blendshapes) == 0
                assert len(report.missing_bones) == 0
            finally:
                os.unlink(tmp.name)
    
    def test_validate_fbx_file_not_found(self):
        """Test validation with non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_fbx("non_existent_file.fbx")
    
    @patch('metahuman_converter.validation.FBXReader')
    def test_validate_fbx_large_file_warning(self, mock_fbx_reader):
        """Test validation generates warning for large files."""
        # Mock a large file (600MB)
        mock_reader_instance = MagicMock()
        mock_reader_instance.get_blendshapes.return_value = set(ARKIT_BLENDSHAPES)
        mock_reader_instance.get_bones.return_value = set(CORE_REQUIRED_BONES)
        mock_reader_instance.get_file_info.return_value = {
            "size_bytes": 600 * 1024 * 1024,
            "size_mb": 600.0,
            "last_modified": 1234567890
        }
        mock_fbx_reader.return_value = mock_reader_instance
        
        report = validate_fbx("large_file.fbx")
        
        assert report.overall_result == ValidationResult.WARNING
        assert report.is_valid
        assert report.file_size_mb == 600.0
        
        # Check for size warning
        size_issue = next(
            (issue for issue in report.issues 
             if "Large file size" in issue.message), None
        )
        assert size_issue is not None
        assert size_issue.level == ValidationResult.WARNING


class TestValidationDataStructures:
    """Test cases for validation data structures."""
    
    def test_validation_issue_creation(self):
        """Test ValidationIssue creation and properties."""
        issue = ValidationIssue(
            level=ValidationResult.FAIL,
            message="Test issue",
            details={"test": "data"}
        )
        
        assert issue.level == ValidationResult.FAIL
        assert issue.message == "Test issue"
        assert issue.details == {"test": "data"}
    
    def test_fbx_validation_report_properties(self):
        """Test FBXValidationReport properties and methods."""
        report = FBXValidationReport(
            file_path="test.fbx",
            overall_result=ValidationResult.WARNING,
            issues=[
                ValidationIssue(ValidationResult.WARNING, "Warning 1"),
                ValidationIssue(ValidationResult.FAIL, "Error 1"),
                ValidationIssue(ValidationResult.WARNING, "Warning 2")
            ],
            found_blendshapes={"shape1", "shape2"},
            missing_blendshapes={"shape3"},
            found_bones={"bone1", "bone2"},
            missing_bones={"bone3"},
            extra_blendshapes={"extra1"},
            file_size_mb=50.0
        )
        
        assert report.is_valid  # WARNING is still valid
        assert len(report.critical_issues) == 1
        assert report.critical_issues[0].level == ValidationResult.FAIL
        
        # Test with FAIL result
        report.overall_result = ValidationResult.FAIL
        assert not report.is_valid
    
    def test_validation_result_enum(self):
        """Test ValidationResult enum values."""
        assert ValidationResult.PASS.value == "pass"
        assert ValidationResult.WARNING.value == "warning"
        assert ValidationResult.FAIL.value == "fail"


if __name__ == "__main__":
    pytest.main([__file__])