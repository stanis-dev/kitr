#!/usr/bin/env python3
"""
Step 1: Asset Duplicator

Copies MetaHuman project files to artifacts folder for processing.
Preserves original project by working on copies.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional
import datetime

from logger.core import get_logger

logger = get_logger(__name__)


class AssetDuplicator:
    """Handles MetaHuman project copying and preparation."""

    def __init__(self, source_project_path: str, artifacts_base_dir: str = "artifacts"):
        """
        Initialize the asset duplicator.

        Args:
            source_project_path: Path to the .uproject file
            artifacts_base_dir: Base directory for artifacts (relative to project root)
        """
        self.source_project_path = Path(source_project_path)
        self.source_project_dir = self.source_project_path.parent
        self.project_name = self.source_project_path.stem

        # Set up artifacts directory structure
        project_root = Path(__file__).parent.parent
        self.artifacts_base = project_root / artifacts_base_dir

        # Create timestamped copy directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.copy_dir = self.artifacts_base / f"{self.project_name}_{timestamp}"
        self.copied_project_path: Optional[Path] = None

    def create_project_copy(self) -> bool:
        """
        Copy the MetaHuman project to artifacts directory.

        Returns:
            True if copy successful, False otherwise
        """
        logger.info(f"📁 Copying project: {self.source_project_dir}")
        logger.info(f"   → Target directory: {self.copy_dir}")

        try:
            # Ensure artifacts directory exists
            self.artifacts_base.mkdir(exist_ok=True)

            # Validate source project exists
            if not self.source_project_path.exists():
                logger.error(f"Source project file not found: {self.source_project_path}")
                return False

            if not self.source_project_dir.exists():
                logger.error(f"Source project directory not found: {self.source_project_dir}")
                return False

            # Copy the entire project directory
            logger.info("🔄 Copying project files...")
            shutil.copytree(
                str(self.source_project_dir),
                str(self.copy_dir),
                dirs_exist_ok=False
            )

            # Set the copied project path
            self.copied_project_path = self.copy_dir / self.source_project_path.name

            logger.info(f"✅ Project copied successfully")
            logger.info(f"   Copied project file: {self.copied_project_path}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to copy project: {e}")
            return False

    def validate_copy(self) -> bool:
        """
        Validate the copied project structure.

        Returns:
            True if validation passes, False otherwise
        """
        logger.info("🔍 Validating copied project")

        try:
            if not self.copied_project_path or not self.copied_project_path.exists():
                logger.error("Copied project file not found")
                return False

                        # Check for essential directories/files
            expected_items = [
                "Content",
                "Config",
                self.source_project_path.name  # .uproject file
            ]

            missing_items: list[str] = []
            for item in expected_items:
                item_path = self.copy_dir / item
                if not item_path.exists():
                    missing_items.append(item)

            if missing_items:
                logger.error(f"Missing essential items in copy: {missing_items}")
                return False

            # Log copy statistics
            original_size = self._get_directory_size(self.source_project_dir)
            copy_size = self._get_directory_size(self.copy_dir)

            logger.info(f"📊 Copy validation:")
            logger.info(f"   Original size: {original_size / (1024*1024):.1f} MB")
            logger.info(f"   Copy size: {copy_size / (1024*1024):.1f} MB")
            logger.info(f"   Size match: {original_size == copy_size}")

            logger.info("✅ Copy validation passed")
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


def main():
    """Main entry point for Step 1: Asset Duplication."""
    logger.info("🎭 Step 1: Duplicate Project")
    logger.info("=" * 50)

    # Development path - will be parameterized in future
    development_project_path = "/Users/stanislav.samisko/Downloads/TestSofi/Metahumans5_6/Metahumans5_6.uproject"

    # TODO: Parse command line arguments
    # For now, use development path
    source_project_path = development_project_path

    duplicator = AssetDuplicator(source_project_path)

    # Execute duplication pipeline
    if not duplicator.create_project_copy():
        logger.error("❌ Project copy failed")
        sys.exit(1)

    if not duplicator.validate_copy():
        logger.error("❌ Copy validation failed")
        sys.exit(1)

    copied_path = duplicator.get_copied_project_path()
    logger.info("✅ Step 1 completed successfully")
    logger.info(f"   Copied project: {copied_path}")

    return str(copied_path)


if __name__ == "__main__":
    main()
