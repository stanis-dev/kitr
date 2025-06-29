"""
Pytest configuration and shared fixtures for MetaHuman converter tests.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from metahuman_converter.validation import FBXValidationResult


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_fbx_file(temp_dir):
    """Create a mock FBX file for testing."""
    fbx_path = temp_dir / "test_metahuman.fbx"
    # Create a dummy file to simulate an FBX
    fbx_path.write_bytes(b"FBX mock file content")
    return fbx_path


@pytest.fixture
def sample_validation_result():
    """Create a sample validation result for testing."""
    result = FBXValidationResult()
    result.found_blendshapes = [
        "eyeBlinkLeft", "eyeBlinkRight", "jawOpen", "mouthSmileLeft", 
        "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight"
    ]
    result.found_bones = ["Head", "LeftEye", "RightEye", "Neck_01"]
    result.mesh_info = {
        "Face": {"vertices": 15420, "polygons": 30240}
    }
    return result


@pytest.fixture
def mock_fbx_sdk():
    """Mock the FBX SDK for testing without requiring actual installation."""
    with patch('metahuman_converter.validation.fbx') as mock_fbx:
        # Mock FBX SDK classes and methods
        mock_manager = Mock()
        mock_scene = Mock()
        mock_importer = Mock()
        
        mock_fbx.FbxManager.Create.return_value = mock_manager
        mock_fbx.FbxScene.Create.return_value = mock_scene
        mock_fbx.FbxImporter.Create.return_value = mock_importer
        
        # Mock successful import
        mock_importer.Initialize.return_value = True
        mock_importer.Import.return_value = True
        
        yield mock_fbx


@pytest.fixture
def mock_logger():
    """Mock the logger to avoid rich dependency in tests."""
    with patch('metahuman_converter.validation.logger') as mock_log:
        yield mock_log