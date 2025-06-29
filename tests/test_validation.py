"""
Tests for FBX validation functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from metahuman_converter.validation import (
    FBXValidator, 
    FBXValidationResult, 
    validate_fbx
)
from metahuman_converter.constants import AZURE_BLENDSHAPES


class TestFBXValidationResult:
    """Test the FBXValidationResult class."""
    
    def test_init_default_state(self):
        """Test that validation result initializes correctly."""
        result = FBXValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.found_blendshapes == []
        assert result.missing_blendshapes == []
        
    def test_add_error_marks_invalid(self):
        """Test that adding an error marks result as invalid."""
        result = FBXValidationResult()
        result.add_error("Test error")
        
        assert result.is_valid is False
        assert "Test error" in result.errors
        
    def test_add_warning_keeps_valid(self):
        """Test that adding a warning doesn't mark as invalid."""
        result = FBXValidationResult()
        result.add_warning("Test warning")
        
        assert result.is_valid is True
        assert "Test warning" in result.warnings


class TestFBXValidator:
    """Test the FBXValidator class."""
    
    def test_init_checks_fbx_sdk(self):
        """Test that validator checks for FBX SDK availability."""
        with patch('metahuman_converter.validation.fbx') as mock_fbx:
            validator = FBXValidator()
            assert validator.fbx_sdk_available is True
            
        # Test without FBX SDK
        with patch('metahuman_converter.validation.fbx', side_effect=ImportError):
            validator = FBXValidator()
            assert validator.fbx_sdk_available is False
            
    def test_validate_file_exists_missing_file(self, mock_logger):
        """Test validation of missing file."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Test with non-existent file
        fake_path = Path("/nonexistent/file.fbx")
        is_valid = validator._validate_file_exists(fake_path, result)
        
        assert is_valid is False
        assert result.is_valid is False
        assert any("not found" in error for error in result.errors)
        
    def test_validate_file_exists_wrong_extension(self, mock_fbx_file, mock_logger):
        """Test validation with wrong file extension."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Rename file to have wrong extension
        wrong_ext_file = mock_fbx_file.with_suffix('.obj')
        mock_fbx_file.rename(wrong_ext_file)
        
        is_valid = validator._validate_file_exists(wrong_ext_file, result)
        
        assert is_valid is True  # Still valid, just a warning
        assert any("expected '.fbx'" in warning for warning in result.warnings)
        
    def test_mock_validation_creates_realistic_data(self, mock_logger):
        """Test that mock validation creates realistic MetaHuman data."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        validator._mock_validation(result)
        
        # Should have found a good number of blendshapes
        assert len(result.found_blendshapes) >= 40  # Most ARKit shapes
        assert "eyeBlinkLeft" in result.found_blendshapes
        assert "jawOpen" in result.found_blendshapes
        
        # Should have typical skeleton bones
        assert len(result.found_bones) > 5
        assert any("head" in bone.lower() for bone in result.found_bones)
        assert any("eye" in bone.lower() for bone in result.found_bones)
        
        # Should have mesh info
        assert "Face" in result.mesh_info
        assert result.mesh_info["Face"]["vertices"] > 1000
        
    def test_analyze_blendshape_mapping_direct_matches(self, mock_logger):
        """Test blendshape mapping with direct matches."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Set up some found blendshapes that directly match Azure names
        result.found_blendshapes = [
            "eyeBlinkLeft", "eyeBlinkRight", "jawOpen", "mouthSmileLeft"
        ]
        
        validator._analyze_blendshape_mapping(result)
        
        # Should have 4 direct matches, 48 missing
        assert len(result.missing_blendshapes) == 52 - 4
        assert "eyeBlinkLeft" not in result.missing_blendshapes
        assert "tongueOut" in result.missing_blendshapes  # Should be missing
        
    def test_analyze_blendshape_mapping_with_variations(self, mock_logger):
        """Test blendshape mapping with MetaHuman naming variations."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Include some MetaHuman naming variations
        result.found_blendshapes = [
            "eyeBlinkLeft", "mouthSmile_L", "mouthSmile_R", "mouthFrown_L"
        ]
        
        validator._analyze_blendshape_mapping(result)
        
        # Should map variations correctly
        assert "mouthSmile_L" in result.blendshape_mapping
        assert result.blendshape_mapping["mouthSmile_L"] == "mouthSmileLeft"
        
        # Missing count should account for mapped variations
        expected_missing = 52 - 4  # 4 shapes found (including mapped ones)
        assert len(result.missing_blendshapes) == expected_missing
        
    def test_validate_completeness_good_case(self, mock_logger):
        """Test completeness validation with good data."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Set up a good scenario
        result.missing_blendshapes = []  # All blendshapes found
        result.found_bones = ["Head", "LeftEye", "RightEye"]
        result.mesh_info = {"Face": {"vertices": 15000}}
        
        validator._validate_completeness(result)
        
        # Should pass validation
        assert result.is_valid is True
        assert len(result.errors) == 0
        
    def test_validate_completeness_missing_blendshapes(self, mock_logger):
        """Test completeness validation with missing blendshapes."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Set up scenario with many missing blendshapes
        result.missing_blendshapes = ["tongueOut", "browInnerUp", "cheekPuff", 
                                     "noseSneerLeft", "noseSneerRight", "jawForward"]
        result.found_bones = ["Head", "LeftEye", "RightEye"] 
        result.mesh_info = {"Face": {"vertices": 15000}}
        
        validator._validate_completeness(result)
        
        # Should fail validation due to too many missing shapes
        assert result.is_valid is False
        assert any("Too many missing blendshapes" in error for error in result.errors)
        
    def test_validate_completeness_missing_bones(self, mock_logger):
        """Test completeness validation with missing bones."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Set up scenario with missing eye bones
        result.missing_blendshapes = []
        result.found_bones = ["Head", "Neck"]  # Missing eye bones
        result.mesh_info = {"Face": {"vertices": 15000}}
        
        validator._validate_completeness(result)
        
        # Should have warnings about missing bones
        assert any("Missing bone types" in warning for warning in result.warnings)
        
    def test_validate_completeness_low_vertex_count(self, mock_logger):
        """Test completeness validation with too few vertices."""
        validator = FBXValidator()
        result = FBXValidationResult()
        
        # Set up scenario with too few vertices
        result.missing_blendshapes = []
        result.found_bones = ["Head", "LeftEye", "RightEye"]
        result.mesh_info = {"Face": {"vertices": 500}}  # Too few
        
        validator._validate_completeness(result)
        
        # Should fail due to low vertex count
        assert result.is_valid is False
        assert any("Too few vertices" in error for error in result.errors)


class TestValidateFbxFunction:
    """Test the convenience validate_fbx function."""
    
    @patch('metahuman_converter.validation.FBXValidator')
    def test_validate_fbx_calls_validator(self, mock_validator_class, mock_logger):
        """Test that validate_fbx function creates validator and calls it."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_validator.validate_fbx.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        test_path = Path("/test/file.fbx")
        result = validate_fbx(test_path)
        
        # Should create validator and call validate_fbx
        mock_validator_class.assert_called_once()
        mock_validator.validate_fbx.assert_called_once_with(test_path)
        assert result == mock_result


class TestIntegration:
    """Integration tests for the validation module."""
    
    def test_end_to_end_validation_mock(self, mock_fbx_file, mock_logger):
        """Test end-to-end validation using mock data."""
        # This test uses the mock validation path since we don't have real FBX SDK
        with patch('metahuman_converter.validation.fbx', side_effect=ImportError):
            result = validate_fbx(mock_fbx_file)
            
        # Should complete successfully with mock data
        assert isinstance(result, FBXValidationResult)
        assert len(result.found_blendshapes) > 40  # Mock should find most shapes
        assert len(result.found_bones) > 5
        
        # Should have reasonable validation results
        # (Most shapes found, few missing, so should be valid or have minor warnings)
        missing_count = len(result.missing_blendshapes)
        if missing_count <= 5:
            assert result.is_valid is True or len(result.warnings) > 0
        else:
            # If many missing, should be invalid
            assert result.is_valid is False