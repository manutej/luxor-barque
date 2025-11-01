#!/usr/bin/env python3
"""
BARQUE - Beautiful Automated Report and Query Universal Engine
Multi-modal document orchestration with dual-theme PDF generation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="barque",
    version="2.0.0",
    author="LUXOR Systems",
    author_email="dev@luxor.systems",
    description="Multi-modal document orchestration engine with dual-theme PDF generation and mathematical formula support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luxor/barque",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "pyyaml>=6.0",
        "jinja2>=3.1",
        "markdown>=3.4",
        "pygments>=2.14",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "ruff>=0.1",
            "mypy>=1.0",
        ],
        "all": [
            "weasyprint>=58.0",  # For advanced PDF rendering
            "pillow>=9.0",       # For image processing
        ]
    },
    entry_points={
        "console_scripts": [
            "barque=barque.cli.commands:main",
        ],
    },
    include_package_data=True,
    package_data={
        "barque": [
            "templates/*.html",
            "templates/*.j2",
            "themes/*.yaml",
            "themes/*.css",
        ],
    },
    project_urls={
        "Documentation": "https://barque.readthedocs.io",
        "Source": "https://github.com/luxor/barque",
        "Tracker": "https://github.com/luxor/barque/issues",
    },
)
