"""
Pytest configuration and fixtures for MetaHuman converter tests.
"""

import logging
import pytest


@pytest.fixture(autouse=True)
def configure_logging():
    """Configure logging for tests."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set specific loggers to appropriate levels for testing
    logging.getLogger('metahuman_converter').setLevel(logging.DEBUG)


@pytest.fixture
def sample_arkit_blendshapes():
    """Fixture providing a sample set of ARKit blendshapes for testing."""
    return [
        "eyeBlinkLeft", "eyeBlinkRight",
        "mouthOpen", "mouthClose",
        "mouthSmileLeft", "mouthSmileRight"
    ]


@pytest.fixture
def sample_bones():
    """Fixture providing a sample set of bones for testing."""
    return [
        "root", "pelvis", "spine_01", "head",
        "FACIAL_C_FacialRoot", "FACIAL_C_Jaw"
    ]