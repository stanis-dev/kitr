#!/usr/bin/env python3
"""
Step 1 Validation Models

Data structures and models for the Step 1 validation plan.
Each model represents the output of a specific validation task.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Generic, TypeVar
import json


@dataclass
class ProjectPathInfo:
    """Output of sub-task 1.1: Locate Project"""
    exists: bool
    abs_root: Optional[Path]
    error: str

    def is_valid(self) -> bool:
        """Check if project path is valid for pipeline"""
        return self.exists and self.abs_root is not None and not self.error


@dataclass
class PluginStatus:
    """Plugin status for MetaHuman validation"""
    name: str
    enabled: bool
    version: Optional[str] = None


@dataclass
class MetaHumanHealthReport:
    """Output of sub-task 1.6: Quick-Health Check"""
    asset_path: str
    character_name: str
    has_LOD0: bool
    morph_count: int
    head_bone_ok: bool
    eye_bone_ok: bool
    error: str = ""

    def is_healthy(self) -> bool:
        """Check if MetaHuman passes health check"""
        return (
            self.has_LOD0 and
            self.morph_count >= 700 and  # Pre-prune requirement
            self.head_bone_ok and
            self.eye_bone_ok and
            not self.error
        )

    def get_issues(self) -> List[str]:
        """Get list of health issues"""
        issues: list[str] = []
        if not self.has_LOD0:
            issues.append("No LOD0")
        if self.morph_count < 700:
            issues.append(f"Insufficient morphs ({self.morph_count}/700)")
        if not self.head_bone_ok:
            issues.append("Missing head bones")
        if not self.eye_bone_ok:
            issues.append("Missing eye bones")
        if self.error:
            issues.append(f"Error: {self.error}")
        return issues


@dataclass
class SessionToken:
    """Output of sub-task 1.4: Open Project Headless"""
    process_id: Optional[int]
    session_active: bool
    project_path: str
    error: str = ""

    def is_active(self) -> bool:
        """Check if UE session is active"""
        return self.session_active and self.process_id is not None


@dataclass
class MetaHumanAsset:
    """MetaHuman asset information"""
    asset_path: str
    character_name: str
    asset_class: str
    package_path: str


@dataclass
class Step1Checkpoint:
    """Output of sub-task 1.10: Emit Step-1 Checkpoint"""
    success: bool
    project_path: str
    engine_version: str
    plugins: List[PluginStatus]
    metahumans: List[MetaHumanHealthReport]
    healthy_characters: List[str]
    temp_asset_paths: List[str]
    readiness_report: str
    error: str = ""
    timestamp: str = ""

    def to_json(self) -> str:
        """Serialize checkpoint to JSON"""
        return json.dumps({
            "success": self.success,
            "project_path": self.project_path,
            "engine_version": self.engine_version,
            "plugins": [{"name": p.name, "enabled": p.enabled, "version": p.version} for p in self.plugins],
            "metahumans": [
                {
                    "asset_path": mh.asset_path,
                    "character_name": mh.character_name,
                    "healthy": mh.is_healthy(),
                    "issues": mh.get_issues(),
                    "morph_count": mh.morph_count
                } for mh in self.metahumans
            ],
            "healthy_characters": self.healthy_characters,
            "temp_asset_paths": self.temp_asset_paths,
            "error": self.error,
            "timestamp": self.timestamp
        }, indent=2)


T = TypeVar('T')

class ValidationResult(Generic[T]):
    """Generic validation result for sub-tasks"""

    def __init__(self, success: bool, data: Optional[T] = None, error: str = ""):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def success_result(cls, data: T) -> 'ValidationResult[T]':
        """Create successful validation result"""
        return cls(True, data)

    @classmethod
    def failure_result(cls, error: str) -> 'ValidationResult[T]':
        """Create failed validation result"""
        return cls(False, error=error)


class EngineVersion:
    """Engine version handling"""

    def __init__(self, major: int, minor: int, patch: int = 0):
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def is_supported(self) -> bool:
        """Check if engine version is supported (5.6.x)"""
        return self.major == 5 and self.minor == 6

    @classmethod
    def from_string(cls, version_str: str) -> 'EngineVersion':
        """Parse version string like '5.6.0' or '5.6'"""
        parts = version_str.split('.')
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return cls(major, minor, patch)


# Required MetaHuman plugins for validation (UE 5.6 structure)
REQUIRED_METAHUMAN_PLUGINS = [
    "MetaHumanCharacter",  # Core MetaHuman character system
    "MetaHumanSDK",        # MetaHuman SDK for export/import
    "MetaHumanCoreTech"    # Core technology library (actual file name)
]

# Minimum requirements for healthy MetaHuman
MIN_MORPH_COUNT = 700  # Pre-prune requirement
REQUIRED_BONES = ["head", "eye_l", "eye_r"]

# UE5.6 specific paths and commands
UE_PYTHON_COMMANDS = {
    "get_plugins": "GetPlugins",
    "project_ping": "ProjectPing.py",
    "asset_registry": "unreal.AssetRegistryHelpers.get_asset_registry()"
}
