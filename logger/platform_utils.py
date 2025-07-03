"""
Windows-only platform utilities for WSL2 compatibility.

This module provides Windows-specific path configuration with WSL2 support.
All paths are configurable via parameters with sensible defaults.
"""

from pathlib import Path
from typing import Optional

from config import (
    DEFAULT_UE_PATH, DEFAULT_BLENDER_PATH, DEFAULT_PROJECT_PATH,
    to_windows_path, to_wsl_path
)


def get_windows_path(wsl_path: str) -> str:
    """
    Convert WSL path to Windows path for WSL2 compatibility.

    Args:
        wsl_path: Path in WSL format (e.g., /mnt/f/Games/Fortnite/UE_5.6)

    Returns:
        Windows path format (e.g., F:/Games/Fortnite/UE_5.6)
    """
    return to_windows_path(wsl_path)


def get_wsl_path(windows_path: str) -> str:
    """
    Convert Windows path to WSL path for WSL2 compatibility.

    Args:
        windows_path: Path in Windows format (e.g., F:/Games/Fortnite/UE_5.6)

    Returns:
        WSL path format (e.g., /mnt/f/Games/Fortnite/UE_5.6)
    """
    return to_wsl_path(windows_path)


def validate_windows_path(path: str) -> bool:
    """
    Validate that a path is accessible from WSL2.

    Args:
        path: Path to validate

    Returns:
        True if path is valid and accessible
    """
    try:
        # Convert to Windows path if needed
        windows_path = get_windows_path(path)
        return Path(windows_path).exists()
    except Exception:
        return False


def get_default_unreal_engine_path() -> str:
    """
    Get default Unreal Engine path for Windows/WSL2.

    Returns:
        Default UE path from config
    """
    return DEFAULT_UE_PATH


def get_default_blender_path() -> str:
    """
    Get default Blender path for Windows/WSL2.

    Returns:
        Default Blender path from config
    """
    return DEFAULT_BLENDER_PATH


def get_default_project_path() -> str:
    """
    Get default project path for Windows/WSL2.

    Returns:
        Default project path from config
    """
    return DEFAULT_PROJECT_PATH


def find_executable_in_paths(paths: list[str]) -> Optional[str]:
    """
    Find the first existing executable from a list of paths.

    Args:
        paths: List of potential executable paths

    Returns:
        First existing executable path, or None if none found
    """
    for path in paths:
        windows_path = get_windows_path(path)
        if Path(windows_path).exists():
            return path
    return None
