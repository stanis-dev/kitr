#!/usr/bin/env python3
"""
Step 1: Asset Duplicator

Scans MetaHuman project for available characters, allows selection,
and copies only the selected MetaHuman for processing.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
import datetime
import json

from logger.core import get_logger

logger = get_logger(__name__)


class MetaHumanScanner:
    """Scans and identifies MetaHuman characters in a project."""

    def __init__(self, project_path: str):
        """
        Initialize the MetaHuman scanner.

        Args:
            project_path: Path to the .uproject file
        """
        self.project_path = Path(project_path)
        self.project_dir = self.project_path.parent
        self.content_dir = self.project_dir / "Content"
        self.metahumans_dir = self.content_dir / "MetaHumans"

    def scan_available_metahumans(self) -> List[Dict[str, Any]]:
        """
        Scan the project for available MetaHuman characters.

        Returns:
            List of MetaHuman character information
        """
        logger.info("🔍 Scanning for available MetaHuman characters")

        metahumans: List[Dict[str, Any]] = []

        try:
            if not self.content_dir.exists():
                logger.warning(f"Content directory not found: {self.content_dir}")
                return metahumans

            # Method 1: Check MetaHumans directory
            if self.metahumans_dir.exists():
                logger.info(f"   📁 Found MetaHumans directory: {self.metahumans_dir}")

                for character_dir in self.metahumans_dir.iterdir():
                    if character_dir.is_dir() and not character_dir.name.startswith('.'):
                        character_info = self._analyze_character_directory(character_dir)
                        if character_info:
                            metahumans.append(character_info)

            # Method 2: Scan for Blueprint assets (BP_<character>)
            blueprint_characters = self._scan_blueprint_characters()
            for bp_char in blueprint_characters:
                # Avoid duplicates
                if not any(mh['name'].lower() == bp_char['name'].lower() for mh in metahumans):
                    metahumans.append(bp_char)

            # Method 3: Scan Content root for character assets
            content_characters = self._scan_content_characters()
            for content_char in content_characters:
                if not any(mh['name'].lower() == content_char['name'].lower() for mh in metahumans):
                    metahumans.append(content_char)

            logger.info(f"   ✅ Found {len(metahumans)} MetaHuman character(s)")

            return metahumans

        except Exception as e:
            logger.error(f"❌ Failed to scan MetaHumans: {e}")
            return metahumans

    def _analyze_character_directory(self, character_dir: Path) -> Optional[Dict[str, Any]]:
        """Analyze a character directory to extract information."""
        try:
            character_name = character_dir.name

            # Look for common MetaHuman files
            mesh_files = list(character_dir.rglob("*.uasset"))
            blueprint_files = list(character_dir.rglob("BP_*.uasset"))

            if mesh_files or blueprint_files:
                return {
                    "name": character_name,
                    "type": "MetaHuman Directory",
                    "path": str(character_dir),
                    "assets_count": len(mesh_files) + len(blueprint_files),
                    "source": "MetaHumans folder"
                }

        except Exception as e:
            logger.warning(f"Error analyzing character directory {character_dir}: {e}")

        return None

    def _scan_blueprint_characters(self) -> List[Dict[str, Any]]:
        """Scan for Blueprint character assets (BP_<name>.uasset)."""
        blueprints: List[Dict[str, Any]] = []

        try:
            # Search for BP_*.uasset files
            bp_pattern = "BP_*.uasset"
            bp_files = list(self.content_dir.rglob(bp_pattern))

            for bp_file in bp_files:
                bp_name = bp_file.stem  # Remove .uasset extension
                if bp_name.startswith("BP_") and len(bp_name) > 3:
                    character_name = bp_name[3:]  # Remove "BP_" prefix

                    # Skip common non-character blueprints
                    if character_name.lower() not in ['face_postprocess', 'body_postprocess',
                                                     'clothing_postprocess', 'mh_livelink']:
                        blueprints.append({
                            "name": character_name,
                            "type": "Blueprint Asset",
                            "path": str(bp_file.parent),
                            "blueprint_file": str(bp_file),
                            "source": "Blueprint scan"
                        })

        except Exception as e:
            logger.warning(f"Error scanning blueprints: {e}")

        return blueprints

    def _scan_content_characters(self) -> List[Dict[str, Any]]:
        """Scan Content directory for character-related folders."""
        characters: List[Dict[str, Any]] = []

        try:
            # Look for common character directory patterns
            for item in self.content_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check if directory contains character-like assets
                    if self._looks_like_character_directory(item):
                        characters.append({
                            "name": item.name,
                            "type": "Content Directory",
                            "path": str(item),
                            "source": "Content scan"
                        })

        except Exception as e:
            logger.warning(f"Error scanning content directories: {e}")

        return characters

    def _looks_like_character_directory(self, directory: Path) -> bool:
        """Check if a directory looks like it contains character assets."""
        try:
            # Look for mesh, animation, or blueprint files
            asset_extensions = [".uasset", ".umap"]
            character_indicators = ["mesh", "skeleton", "anim", "bp_", "character"]

            for file_path in directory.rglob("*"):
                if file_path.suffix.lower() in asset_extensions:
                    file_name_lower = file_path.name.lower()
                    if any(indicator in file_name_lower for indicator in character_indicators):
                        return True

        except Exception:
            pass

        return False


class AssetDuplicator:
    """Handles selective MetaHuman character copying and preparation."""

    def __init__(self, source_project_path: str, selected_character: str, artifacts_base_dir: str = "artifacts"):
        """
        Initialize the asset duplicator for a specific character.

        Args:
            source_project_path: Path to the .uproject file
            selected_character: Name of the selected MetaHuman character
            artifacts_base_dir: Base directory for artifacts
        """
        self.source_project_path = Path(source_project_path)
        self.source_project_dir = self.source_project_path.parent
        self.project_name = self.source_project_path.stem
        self.selected_character = selected_character

        # Set up artifacts directory structure
        project_root = Path(__file__).parent.parent
        self.artifacts_base = project_root / artifacts_base_dir

        # Create timestamped copy directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.copy_dir = self.artifacts_base / f"{self.project_name}_{self.selected_character}_{timestamp}"
        self.copied_project_path: Optional[Path] = None

    def create_character_copy(self) -> bool:
        """
        Copy the selected MetaHuman character and necessary project files.

        Returns:
            True if copy successful, False otherwise
        """
        logger.info(f"📁 Copying MetaHuman character: {self.selected_character}")
        logger.info(f"   Source project: {self.source_project_dir}")
        logger.info(f"   → Target directory: {self.copy_dir}")

        try:
            # Ensure artifacts directory exists
            self.artifacts_base.mkdir(exist_ok=True)

            # Validate source project exists
            if not self.source_project_path.exists():
                logger.error(f"Source project file not found: {self.source_project_path}")
                return False

            # Create target directory structure
            self.copy_dir.mkdir(parents=True, exist_ok=True)

            logger.info("🔄 Copying project structure...")

            # 1. Copy essential project files
            self._copy_essential_project_files()

            # 2. Copy selected character assets
            self._copy_character_assets()

            # 3. Copy shared/common assets
            self._copy_shared_assets()

            # 4. Create character selection manifest
            self._create_character_manifest()

            # Set the copied project path
            self.copied_project_path = self.copy_dir / self.source_project_path.name

            logger.info(f"✅ Character copy completed successfully")
            logger.info(f"   Selected character: {self.selected_character}")
            logger.info(f"   Copied project file: {self.copied_project_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to copy character: {e}")
            return False

    def _copy_essential_project_files(self) -> None:
        """Copy essential project files (.uproject, Config, etc.)."""
        logger.info("   📋 Copying essential project files...")

        # Copy .uproject file
        if self.source_project_path.exists():
            shutil.copy2(self.source_project_path, self.copy_dir)

        # Copy Config directory (project settings)
        config_src = self.source_project_dir / "Config"
        if config_src.exists():
            config_dst = self.copy_dir / "Config"
            shutil.copytree(config_src, config_dst)

        # Copy Plugins directory if it exists
        plugins_src = self.source_project_dir / "Plugins"
        if plugins_src.exists():
            plugins_dst = self.copy_dir / "Plugins"
            shutil.copytree(plugins_src, plugins_dst)

        logger.info("   ✅ Essential files copied")

    def _copy_character_assets(self) -> None:
        """Copy the selected character's assets."""
        logger.info(f"   🎭 Copying character assets for: {self.selected_character}")

        content_src = self.source_project_dir / "Content"
        content_dst = self.copy_dir / "Content"
        content_dst.mkdir(exist_ok=True)

        # Copy MetaHumans directory if character is there
        metahumans_src = content_src / "MetaHumans"
        if metahumans_src.exists():
            character_dir = metahumans_src / self.selected_character
            if character_dir.exists():
                metahumans_dst = content_dst / "MetaHumans"
                metahumans_dst.mkdir(exist_ok=True)
                shutil.copytree(character_dir, metahumans_dst / self.selected_character)
                logger.info(f"     ✅ Copied MetaHumans/{self.selected_character}")

        # Copy character blueprints (BP_<character>.uasset)
        bp_pattern = f"BP_{self.selected_character}.*"
        for bp_file in content_src.rglob(bp_pattern):
            if bp_file.is_file():
                relative_path = bp_file.relative_to(content_src)
                bp_dst = content_dst / relative_path
                bp_dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(bp_file, bp_dst)
                logger.info(f"     ✅ Copied blueprint: {relative_path}")

        # Copy character-specific directories in Content
        character_content_dir = content_src / self.selected_character
        if character_content_dir.exists():
            shutil.copytree(character_content_dir, content_dst / self.selected_character)
            logger.info(f"     ✅ Copied Content/{self.selected_character}")

        logger.info("   ✅ Character assets copied")

    def _copy_shared_assets(self) -> None:
        """Copy shared/common assets needed for MetaHuman functionality."""
        logger.info("   🔗 Copying shared MetaHuman assets...")

        content_src = self.source_project_dir / "Content"
        content_dst = self.copy_dir / "Content"

        # Copy common MetaHuman assets
        shared_patterns = [
            "ABP_*_PostProcess*",  # Animation blueprints
            "ABP_MH_LiveLink*",    # LiveLink assets
            "*MetaHuman*",         # Any other MetaHuman-related files
            "Common*",             # Common assets
            "Shared*"              # Shared assets
        ]

        for pattern in shared_patterns:
            for asset_file in content_src.rglob(pattern):
                if asset_file.is_file() and not self._is_character_specific_file(asset_file):
                    relative_path = asset_file.relative_to(content_src)
                    asset_dst = content_dst / relative_path
                    asset_dst.parent.mkdir(parents=True, exist_ok=True)

                    if not asset_dst.exists():  # Avoid duplicates
                        shutil.copy2(asset_file, asset_dst)

        logger.info("   ✅ Shared assets copied")

    def _is_character_specific_file(self, file_path: Path) -> bool:
        """Check if a file is specific to a different character."""
        file_name = file_path.name.lower()

        # Skip files that belong to other characters
        other_character_indicators = [
            f"bp_{char}" for char in ["bob", "charlie", "david", "eve", "frank", "grace"]
            if char != self.selected_character.lower()
        ]

        return any(indicator in file_name for indicator in other_character_indicators)

    def _create_character_manifest(self) -> None:
        """Create a manifest file documenting the character selection."""
        manifest = {
            "selection_timestamp": datetime.datetime.now().isoformat(),
            "source_project": str(self.source_project_path),
            "selected_character": self.selected_character,
            "copy_directory": str(self.copy_dir),
            "project_name": self.project_name,
            "copy_type": "selective_character",
            "notes": f"Copied only {self.selected_character} character and shared assets"
        }

        manifest_path = self.copy_dir / "character_selection_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"   📄 Created character manifest: {manifest_path}")

    def validate_copy(self) -> bool:
        """
        Validate the copied character assets.

        Returns:
            True if validation passes, False otherwise
        """
        logger.info("🔍 Validating character copy")

        try:
            if not self.copied_project_path or not self.copied_project_path.exists():
                logger.error("Copied project file not found")
                return False

            # Check for essential files
            essential_files = [
                self.source_project_path.name,  # .uproject file
                "character_selection_manifest.json"
            ]

            essential_dirs = [
                "Config",
                "Content"
            ]

            missing_items: List[str] = []

            for file_name in essential_files:
                if not (self.copy_dir / file_name).exists():
                    missing_items.append(file_name)

            for dir_name in essential_dirs:
                if not (self.copy_dir / dir_name).exists():
                    missing_items.append(f"{dir_name}/")

            if missing_items:
                logger.error(f"Missing essential items in copy: {missing_items}")
                return False

            # Check for character assets
            content_dir = self.copy_dir / "Content"
            character_assets_found = False

            # Check MetaHumans directory
            metahuman_char_dir = content_dir / "MetaHumans" / self.selected_character
            if metahuman_char_dir.exists():
                character_assets_found = True
                logger.info(f"   ✅ Found MetaHuman character directory")

            # Check for character blueprints
            bp_files = list(content_dir.rglob(f"BP_{self.selected_character}.*"))
            if bp_files:
                character_assets_found = True
                logger.info(f"   ✅ Found {len(bp_files)} character blueprint(s)")

            if not character_assets_found:
                logger.warning(f"No character assets found for '{self.selected_character}'")

            # Log copy statistics
            original_size = self._get_directory_size(self.source_project_dir)
            copy_size = self._get_directory_size(self.copy_dir)

            logger.info(f"📊 Character copy validation:")
            logger.info(f"   Selected character: {self.selected_character}")
            logger.info(f"   Original project size: {original_size / (1024*1024):.1f} MB")
            logger.info(f"   Character copy size: {copy_size / (1024*1024):.1f} MB")
            logger.info(f"   Size reduction: {((original_size - copy_size) / original_size * 100):.1f}%")

            logger.info("✅ Character copy validation passed")
            return True

        except Exception as e:
            logger.error(f"❌ Copy validation failed: {e}")
            return False

    def _get_directory_size(self, directory: Path) -> int:
        """Get total size of directory in bytes."""
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    if file_path.exists():
                        total_size += file_path.stat().st_size
        except Exception as e:
            logger.warning(f"Error calculating directory size: {e}")
        return total_size

    def get_copied_project_path(self) -> Optional[Path]:
        """Get path to the copied project file."""
        return self.copied_project_path


def select_metahuman_character(available_characters: List[Dict[str, Any]], default_character: str = "ada") -> str:
    """
    Allow user to select a MetaHuman character from available options.

    Args:
        available_characters: List of available character information
        default_character: Default character name if no input provided

    Returns:
        Selected character name
    """
    logger.info("🎭 Available MetaHuman Characters:")
    logger.info("-" * 40)

    if not available_characters:
        logger.warning("No MetaHuman characters found in project")
        logger.info(f"Using default character: {default_character}")
        return default_character

    # Display available characters
    for i, character in enumerate(available_characters, 1):
        logger.info(f"   {i}. {character['name']} ({character['type']})")
        if character.get('source'):
            logger.info(f"      Source: {character['source']}")

    logger.info("")
    logger.info(f"Default: {default_character}")
    logger.info("")

    # Check if default character is available
    available_names = [char['name'].lower() for char in available_characters]
    default_available = default_character.lower() in available_names

    # For automation, return default if available
    if default_available:
        logger.info(f"🎯 Using default character: {default_character}")
        return default_character
    else:
        # If default not available, use first available character
        if available_characters:
            selected = available_characters[0]['name']
            logger.info(f"🎯 Default '{default_character}' not found, using: {selected}")
            return selected
        else:
            logger.info(f"🎯 No characters found, using default: {default_character}")
            return default_character


def main(metahuman_project_path: Optional[str] = None) -> Optional[str]:
    """Main entry point for Step 1: Asset Duplication with Character Selection."""
    logger.info("🎭 Step 1: Duplicate & Prepare MetaHuman Character")
    logger.info("=" * 60)

    # Use provided path or default development path
    if metahuman_project_path:
        source_project_path = metahuman_project_path
    else:
        source_project_path = "/Users/stanislav.samisko/Downloads/TestSofi/Metahumans5_6/Metahumans5_6.uproject"

    logger.info(f"📁 Source project: {source_project_path}")

    # Step 1: Scan for available MetaHuman characters
    scanner = MetaHumanScanner(source_project_path)
    available_characters = scanner.scan_available_metahumans()

    # Step 2: Select character (with 'ada' as default)
    selected_character = select_metahuman_character(available_characters, default_character="ada")

    # Step 3: Copy selected character
    logger.info("")
    logger.info(f"🎯 Processing character: {selected_character}")
    logger.info("-" * 40)

    duplicator = AssetDuplicator(source_project_path, selected_character)

    # Execute character duplication pipeline
    if not duplicator.create_character_copy():
        logger.error("❌ Character copy failed")
        return None

    if not duplicator.validate_copy():
        logger.error("❌ Copy validation failed")
        return None

    copied_path = duplicator.get_copied_project_path()
    logger.info("✅ Step 1 completed successfully")
    logger.info(f"   Selected character: {selected_character}")
    logger.info(f"   Copied project: {copied_path}")

    return str(copied_path) if copied_path else None


if __name__ == "__main__":
    main()
