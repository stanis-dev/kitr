#!/usr/bin/env python3
"""
Setup script for MetaHuman FBX to GLB Converter.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith("#") and "FBX" not in line
        ]

# Add runtime requirements that are Docker-compatible
requirements.extend([
    "numpy>=1.24.0",
    "scipy>=1.10.0", 
    "lxml>=4.9.0",
])

setup(
    name="metahuman-converter",
    version="0.1.0",
    description="Convert MetaHuman FBX files to optimized GLB for Babylon.js with Azure viseme support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="MetaHuman Converter Team",
    author_email="dev@metahuman-converter.com",
    url="https://github.com/metahuman/fbx-to-glb-converter",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "full": [
            "blender-bpy>=3.6.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "metahuman-convert=metahuman_converter.cli:main",
            "validate-fbx=metahuman_converter.validation:cli_validate",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="fbx glb metahuman babylon.js azure viseme 3d graphics converter",
    project_urls={
        "Bug Reports": "https://github.com/metahuman/fbx-to-glb-converter/issues",
        "Source": "https://github.com/metahuman/fbx-to-glb-converter",
        "Documentation": "https://metahuman-converter.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
) 