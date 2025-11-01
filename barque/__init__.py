"""
BARQUE - Beautiful Automated Report and Query Universal Engine

Multi-modal document orchestration with dual-theme PDF generation.
"""

__version__ = "2.0.0"
__author__ = "LUXOR Systems"
__license__ = "MIT"

from .core.generator import PDFGenerator, GenerationResult
from .core.config import BarqueConfig
from .core.themes import ThemeProcessor
from .core.metadata import MetadataExtractor

__all__ = [
    "PDFGenerator",
    "GenerationResult",
    "BarqueConfig",
    "ThemeProcessor",
    "MetadataExtractor",
]
