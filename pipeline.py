#!/usr/bin/env python3
"""
MetaHuman FBX to GLB Pipeline - Single Entry Point

Orchestrates the complete pipeline from MetaHuman FBX validation through final GLB optimization.
Follows file immutability principle - each step produces new output files.
"""

import sys
import subprocess
import time
from pathlib import Path
import logging

def setup_logging():
    """Setup basic logging for pipeline"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def run_step(step_name: str, script_path: str, description: str) -> bool:
    """
    Run a single pipeline step and return success status.

    Args:
        step_name: Display name for the step (e.g., "Step 1")
        script_path: Path to the Python script to execute
        description: Brief description of what the step does

    Returns:
        True if step succeeded, False if it failed
    """
    print(f"\n🚀 {step_name}: {description}")
    print("=" * 60)

    start_time = time.time()

    try:
        # Run the step script
        subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False,  # Let output stream to console
            text=True
        )

        elapsed = time.time() - start_time
        print(f"✅ {step_name} completed successfully in {elapsed:.1f}s")
        return True

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        print(f"❌ {step_name} failed after {elapsed:.1f}s (exit code: {e.returncode})")
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ {step_name} failed after {elapsed:.1f}s: {e}")
        return False


def check_prerequisites() -> bool:
    """Check that all prerequisites are met before starting pipeline."""
    print("🔍 Checking prerequisites...")

    # Check input file exists
    input_file = Path("input-file.fbx")
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        print("   Please ensure input-file.fbx is present in the current directory")
        return False

    print(f"✅ Input file found: {input_file} ({input_file.stat().st_size / (1024*1024):.1f}MB)")

    # Check step scripts exist
    required_scripts = [
        "step1_validation/validate.py",
        "step2_morphs/azure_processor.py",
        "step3_glb/simple_converter.py",
        "step4_render/glb_animator.py"
    ]

    for script in required_scripts:
        if not Path(script).exists():
            print(f"❌ Required script not found: {script}")
            return False

    print("✅ All required step scripts found")

    # Check Blender availability (required for processing)
    try:
        result = subprocess.run(
            ["blender", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            blender_version = result.stdout.split()[1]
            print(f"✅ Blender available: {blender_version}")
        else:
            print("❌ Blender not accessible")
            return False
    except Exception:
        print("❌ Blender not found or not accessible")
        print("   Please install Blender and ensure it's in your PATH")
        return False

    return True


def show_pipeline_summary():
    """Display the complete pipeline flow and file outputs."""
    print("\n📋 MetaHuman FBX to GLB Pipeline Overview")
    print("=" * 60)
    print("Input:  input-file.fbx (MetaHuman export)")
    print("├─ Step 1: FBX Validation")
    print("│   └─ Output: validation report only")
    print("├─ Step 2: Azure FBX Optimization")
    print("│   └─ Output: azure_optimized.fbx")
    print("├─ Step 3: FBX to GLB Conversion")
    print("│   └─ Output: step3_glb/azure_optimized_web.glb")
    print("├─ Step 4: GLB Animation Validation")
    print("│   └─ Output: step4_render/output/animation_validation_report.json + rendered frames")
    print("├─ Step 5: GLB Optimization [NOT IMPLEMENTED]")
    print("│   └─ Output: step5_optimize/optimized.glb")
    print("├─ Step 6: Texture Optimization [NOT IMPLEMENTED]")
    print("│   └─ Output: step6_textures/output-step6-optimized.glb")
    print("└─ Step 7: Final Validation [NOT IMPLEMENTED]")
    print("    └─ Output: step7_final/output-final-avatar.glb")
    print("\n🔒 File Immutability: Original input-file.fbx is never modified")


def show_final_summary(steps_completed: int, total_time: float):
    """Show final pipeline execution summary."""
    print("\n" + "=" * 60)
    print("🏁 PIPELINE EXECUTION SUMMARY")
    print("=" * 60)

    # Show file status
    input_file = Path("input-file.fbx")
    if input_file.exists():
        print(f"📁 Input: {input_file.name} ({input_file.stat().st_size / (1024*1024):.1f}MB) - PRESERVED")

    output_files = [
        "azure_optimized.fbx",
        "step3_glb/azure_optimized_web.glb",
        "step4_render/output/animation_validation_report.json",
        "step5_optimize/optimized.glb",
        "step6_textures/output-step6-optimized.glb",
        "step7_final/output-final-avatar.glb"
    ]

    for i, output_file in enumerate(output_files, 2):
        file_path = Path(output_file)
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024*1024)
            print(f"📁 Step {i}: {file_path.name} ({size_mb:.1f}MB) - CREATED")
        elif i <= steps_completed:
            print(f"❌ Step {i}: {output_file} - MISSING (step may have failed)")

    print(f"\n⏱️  Total execution time: {total_time:.1f}s")
    print(f"📊 Steps completed: {steps_completed}/7")

    if steps_completed == 4:  # All currently implemented steps
        print("✅ All implemented steps completed successfully!")
    elif steps_completed < 4:
        print("❌ Pipeline failed - not all steps completed")

    print("\n🔒 File immutability maintained - original input preserved")


def main():
    """Main pipeline orchestrator."""
    setup_logging()

    print("🎭 MetaHuman FBX to GLB Pipeline")
    print("=" * 60)
    print("Single entry point for complete avatar processing")
    print("Processes MetaHuman FBX → Optimized GLB for Babylon.js + Azure visemes")

    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Pipeline cannot continue.")
        sys.exit(1)

    # Show pipeline overview
    show_pipeline_summary()

    # Start pipeline execution
    print("\n🚀 STARTING PIPELINE EXECUTION")
    print("=" * 60)

    pipeline_start = time.time()
    steps_completed = 0

    # Define pipeline steps
    pipeline_steps = [
        ("Step 1", "step1_validation/validate.py", "FBX Validation & Azure Blendshape Check"),
        ("Step 2", "step2_morphs/azure_processor.py", "Azure FBX Optimization"),
        ("Step 3", "step3_glb/simple_converter.py", "FBX to GLB Conversion"),
        ("Step 4", "step4_render/glb_animator.py", "GLB Animation Validation"),
        # Future steps will be added here as they're implemented
        # ("Step 5", "step5_optimize.py", "GLB Optimization & Compression"),
        # ("Step 6", "step6_textures.py", "Texture Resolution Optimization"),
        # ("Step 7", "step7_final.py", "Final Validation & Browser Compatibility"),
    ]

    # Execute each step
    for step_name, script_path, description in pipeline_steps:
        if not Path(script_path).exists():
            print(f"\n⏭️  {step_name}: {description}")
            print(f"   Script {script_path} not implemented yet - skipping")
            continue

        success = run_step(step_name, script_path, description)

        if success:
            steps_completed += 1
        else:
            print(f"\n💥 Pipeline failed at {step_name}")
            print("   Fix the error and restart the pipeline")
            break

    # Show final summary
    total_time = time.time() - pipeline_start
    show_final_summary(steps_completed, total_time)

    # Exit with appropriate code
    if steps_completed < len([s for s in pipeline_steps if Path(s[1]).exists()]):
        sys.exit(1)
    else:
        print("\n🎉 Pipeline completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
