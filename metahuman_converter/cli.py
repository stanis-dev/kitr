#!/usr/bin/env python3
"""
Command Line Interface for MetaHuman FBX to GLB Converter.
"""

import sys
import logging
import click
from pathlib import Path
from typing import Optional

from .validation import validate_fbx
from .logging_config import setup_logging, logger


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(verbose: bool, debug: bool):
    """MetaHuman FBX to GLB Converter CLI."""
    if debug:
        log_level = logging.DEBUG
    elif verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    setup_logging(level=log_level)
    

@main.command()
@click.argument('fbx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output directory (default: ./output)')
def validate(fbx_file: Path, output: Optional[Path]):
    """Validate an FBX file for MetaHuman conversion compatibility."""
    logger.step_start("CLI Validation", f"Validating {fbx_file.name}")
    
    try:
        result = validate_fbx(fbx_file)
        
        # Display results
        click.echo(f"\n📊 Validation Results for {fbx_file.name}:")
        
        if result.is_valid:
            click.echo(click.style("✅ VALID", fg='green', bold=True))
        else:
            click.echo(click.style("❌ INVALID", fg='red', bold=True))
            
        click.echo(f"   📁 File size: {fbx_file.stat().st_size / (1024*1024):.1f}MB")
        click.echo(f"   🎭 Blendshapes: {len(result.found_blendshapes)}/52 required")
        click.echo(f"   🦴 Bones: {len(result.found_bones)} found")
        click.echo(f"   ❌ Errors: {len(result.errors)}")
        click.echo(f"   ⚠️  Warnings: {len(result.warnings)}")
        
        if result.errors:
            click.echo(f"\n❌ Errors:")
            for error in result.errors:
                click.echo(f"   - {error}")
                
        if result.warnings:
            click.echo(f"\n⚠️  Warnings:")
            for warning in result.warnings:
                click.echo(f"   - {warning}")
                
        if result.missing_blendshapes:
            click.echo(f"\n🔍 Missing Blendshapes ({len(result.missing_blendshapes)}):")
            for missing in result.missing_blendshapes[:10]:
                click.echo(f"   - {missing}")
            if len(result.missing_blendshapes) > 10:
                click.echo(f"   ... and {len(result.missing_blendshapes) - 10} more")
                
        # Save detailed report if output specified
        if output:
            output.mkdir(parents=True, exist_ok=True)
            report_file = output / f"{fbx_file.stem}_validation_report.json"
            
            import json
            report_data = {
                "file": str(fbx_file),
                "valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings,
                "found_blendshapes": result.found_blendshapes,
                "missing_blendshapes": result.missing_blendshapes,
                "found_bones": result.found_bones,
                "missing_bones": result.missing_bones,
                "mesh_info": result.mesh_info,
                "material_info": result.material_info,
                "blendshape_mapping": result.blendshape_mapping
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            
            click.echo(f"\n📄 Detailed report saved to: {report_file}")
        
        # Exit with appropriate code
        sys.exit(0 if result.is_valid else 1)
        
    except Exception as e:
        logger.logger.error(f"Validation failed: {e}")
        click.echo(click.style(f"❌ Validation failed: {e}", fg='red'))
        sys.exit(1)


@main.command()
@click.argument('fbx_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output GLB file (default: same name with .glb extension)')
@click.option('--validate-first', is_flag=True, default=True,
              help='Validate FBX before conversion (default: True)')
def convert(fbx_file: Path, output: Optional[Path], validate_first: bool):
    """Convert an FBX file to GLB format."""
    logger.step_start("CLI Conversion", f"Converting {fbx_file.name}")
    
    # Set default output path
    if not output:
        output = Path("./output") / f"{fbx_file.stem}.glb"
    
    output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Validate if requested
        if validate_first:
            click.echo("🔍 Validating FBX file...")
            result = validate_fbx(fbx_file)
            
            if not result.is_valid:
                click.echo(click.style("❌ Validation failed. Use --no-validate-first to skip validation.", fg='red'))
                for error in result.errors:
                    click.echo(f"   - {error}")
                sys.exit(1)
            else:
                click.echo(click.style("✅ Validation passed", fg='green'))
        
        # TODO: Implement actual conversion steps
        click.echo("🚧 Conversion pipeline not yet fully implemented.")
        click.echo("Current status:")
        click.echo("   ✅ Step 1: FBX Validation")
        click.echo("   🚧 Step 2: Blendshape Processing")
        click.echo("   🚧 Step 3: Skeleton Optimization")
        click.echo("   🚧 Step 4: FBX to glTF Conversion")
        click.echo("   🚧 Step 5: Texture Optimization")
        click.echo("   🚧 Step 6: Final Validation")
        
        click.echo(f"\n✅ Validation completed. GLB conversion will be available in future versions.")
        
    except Exception as e:
        logger.logger.error(f"Conversion failed: {e}")
        click.echo(click.style(f"❌ Conversion failed: {e}", fg='red'))
        sys.exit(1)


@main.command()
@click.option('--input-dir', '-i', type=click.Path(path_type=Path), default=Path('./input'),
              help='Input directory containing FBX files')
@click.option('--output-dir', '-o', type=click.Path(path_type=Path), default=Path('./output'),
              help='Output directory for GLB files')
def batch(input_dir: Path, output_dir: Path):
    """Process multiple FBX files in batch mode."""
    logger.step_start("CLI Batch Processing", f"Processing files in {input_dir}")
    
    if not input_dir.exists():
        click.echo(click.style(f"❌ Input directory not found: {input_dir}", fg='red'))
        sys.exit(1)
    
    # Find all FBX files
    fbx_files = list(input_dir.glob("*.fbx")) + list(input_dir.glob("*.FBX"))
    
    if not fbx_files:
        click.echo(click.style(f"❌ No FBX files found in {input_dir}", fg='yellow'))
        sys.exit(0)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"🔍 Found {len(fbx_files)} FBX files to process...")
    
    results = []
    for fbx_file in fbx_files:
        click.echo(f"\n📁 Processing: {fbx_file.name}")
        
        try:
            result = validate_fbx(fbx_file)
            results.append({
                'file': fbx_file.name,
                'valid': result.is_valid,
                'errors': len(result.errors),
                'warnings': len(result.warnings),
                'blendshapes': len(result.found_blendshapes),
                'bones': len(result.found_bones)
            })
            
            status = "✅ VALID" if result.is_valid else "❌ INVALID"
            click.echo(f"   {status} - {len(result.found_blendshapes)}/52 blendshapes, {len(result.found_bones)} bones")
            
        except Exception as e:
            results.append({
                'file': fbx_file.name,
                'valid': False,
                'error': str(e)
            })
            click.echo(f"   ❌ ERROR: {e}")
    
    # Summary
    valid_count = sum(1 for r in results if r.get('valid', False))
    click.echo(f"\n📊 Batch Processing Summary:")
    click.echo(f"   📁 Total files: {len(fbx_files)}")
    click.echo(f"   ✅ Valid: {valid_count}")
    click.echo(f"   ❌ Invalid: {len(fbx_files) - valid_count}")
    
    # Save batch report
    report_file = output_dir / "batch_validation_report.json"
    import json
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    click.echo(f"   📄 Report saved to: {report_file}")


def cli_validate():
    """Entry point for validate-fbx command."""
    # This allows the validate command to be used as a standalone CLI tool
    import sys
    if len(sys.argv) < 2:
        click.echo("Usage: validate-fbx <fbx_file>")
        sys.exit(1)
    
    fbx_file = Path(sys.argv[1])
    if not fbx_file.exists():
        click.echo(f"❌ File not found: {fbx_file}")
        sys.exit(1)
    
    # Use the validate command logic
    setup_logging()
    try:
        result = validate_fbx(fbx_file)
        print(f"Valid: {result.is_valid}")
        print(f"Blendshapes: {len(result.found_blendshapes)}/52")
        print(f"Bones: {len(result.found_bones)}")
        sys.exit(0 if result.is_valid else 1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 