"""
Windows-only configuration for the MetaHuman pipeline.

This module contains all Windows-specific paths and settings
for WSL2 compatibility. All paths use F: drive by default.
"""

# Unreal Engine paths
DEFAULT_UE_PATH = "F:/Games/Fortnite/UE_5.6"
DEFAULT_UE_ENGINE_PATH = f"{DEFAULT_UE_PATH}/Engine"

# Blender paths
DEFAULT_BLENDER_PATH = "F:/Program Files/Blender Foundation/Blender 4.0/blender.exe"
ALTERNATIVE_BLENDER_PATHS = [
    "F:/Program Files/Blender Foundation/Blender 3.6/blender.exe",
    "F:/Program Files/Blender Foundation/Blender 3.5/blender.exe",
    "F:/Program Files/Blender Foundation/Blender 3.4/blender.exe"
]

# Project paths
DEFAULT_PROJECT_PATH = "F:/Users/stan/Downloads/TestSofi/Metahumans5_6/Metahumans5_6.uproject"

# Artifacts and output paths
DEFAULT_ARTIFACTS_DIR = "artifacts"
DEFAULT_OUTPUT_DIR = "output"

# WSL2 path conversion helpers
def to_wsl_path(windows_path: str) -> str:
    """Convert Windows path to WSL path."""
    if ':' in windows_path:
        drive_letter = windows_path[0].lower()
        return f"/mnt/{drive_letter}/{windows_path[3:]}"
    return windows_path

def to_windows_path(wsl_path: str) -> str:
    """Convert WSL path to Windows path."""
    if wsl_path.startswith('/mnt/'):
        drive_letter = wsl_path[5].upper()
        return f"{drive_letter}:/{wsl_path[7:]}"
    return wsl_path
