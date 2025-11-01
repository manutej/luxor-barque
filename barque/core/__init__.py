"""Core BARQUE modules"""

from .generator import PDFGenerator, GenerationResult
from .config import BarqueConfig
from .themes import ThemeProcessor
from .metadata import MetadataExtractor

__all__ = [
    "PDFGenerator",
    "GenerationResult",
    "BarqueConfig",
    "ThemeProcessor",
    "MetadataExtractor",
]
