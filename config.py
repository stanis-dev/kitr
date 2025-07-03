"""
MetaHuman pipeline configuration.

This module contains all paths and settings for the MetaHuman pipeline.
"""

# Unreal Engine path
DEFAULT_UE_PATH = "F:/Games/Fortnite/UE_5.6"
DEFAULT_UE_ENGINE_PATH = f"{DEFAULT_UE_PATH}/Engine"

# Blender path
DEFAULT_BLENDER_PATH = "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"

# Project path
DEFAULT_PROJECT_PATH = "C:/Users/stani/Documents/Unreal Projects/MhExporter/MhExporter.uproject"

# Artifacts and output path
DEFAULT_ARTIFACTS_DIR = "artifacts"

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
