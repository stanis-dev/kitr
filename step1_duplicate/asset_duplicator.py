#!/usr/bin/env python3
"""
Step 1: MetaHuman Project Validation & Asset Preparation

Validation and preparation of MetaHuman projects for FBX to GLB conversion pipeline.
This step uses the 10-step validation roadmap to ensure project readiness.
"""

from typing import Optional
from logger.core import get_logger

logger = get_logger(__name__)


def main(metahuman_project_path: Optional[str] = None) -> Optional[str]:
    """
    Main entry point for Step 1: MetaHuman Project Validation.

    This step performs the complete 10-step validation roadmap:
    1.1 Locate Project
    1.2 Read Engine Version
    1.3 Check MetaHuman Plugins
    1.4 Open Project Headless
    1.5 Enumerate MetaHumans
    1.6 Quick-Health Check
    1.7 Artist-Facing Readiness Report
    1.8 Duplicate Working Copy
    1.9 Lock Original
    1.10 Emit Step-1 Checkpoint

    Args:
        metahuman_project_path: Path to .uproject file. If None, uses default test project.

    Returns:
        Project path if validation succeeds, None if it fails
    """
    from step1_duplicate.project_validator import ProjectValidator

    # Determine project path
    if metahuman_project_path:
        project_path = metahuman_project_path
    else:
        # Use default test project path
        default_project = "/Users/stanislav.samisko/Downloads/TestSofi/Metahumans5_6/Metahumans5_6.uproject"
        project_path = default_project

    # Execute validation (the only validation path)
    validator = ProjectValidator()

    try:
        checkpoint = validator.execute_validation(project_path)

        if checkpoint.success:
            logger.info("✅ Step 1 completed successfully")

            # Return the project path for pipeline continuation
            return checkpoint.project_path

        else:
            logger.error("❌ Step 1 validation failed")
            logger.error(f"🚫 Error: {checkpoint.error}")
            return None

    except Exception as e:
        logger.error(f"❌ Step 1 validation exception: {e}")
        return None


if __name__ == "__main__":
    main()
