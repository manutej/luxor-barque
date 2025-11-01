"""Core PDF generation engine for BARQUE"""

import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

from .config import BarqueConfig
from .themes import ThemeProcessor
from .metadata import MetadataExtractor


@dataclass
class GenerationResult:
    """Result of PDF generation"""
    success: bool
    files: List[str]
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PDFGenerator:
    """Core PDF generation orchestrator"""

    def __init__(self, config: Optional[BarqueConfig] = None):
        self.config = config or BarqueConfig()
        self.theme_processor = ThemeProcessor(self.config)
        self.metadata_extractor = MetadataExtractor()

        # Setup directories
        self.output_dir = self.config.output_dir
        self.temp_dir = self.output_dir / ".temp"
        self.metadata_dir = self.output_dir / "metadata"

        self._init_directories()

    def _init_directories(self) -> None:
        """Initialize output directories"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        if self.config.organize_by_theme:
            (self.output_dir / "light").mkdir(parents=True, exist_ok=True)
            (self.output_dir / "dark").mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        input_file: Path,
        theme: str = "both",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """
        Generate PDF from markdown file

        Args:
            input_file: Path to markdown file
            theme: Theme selection ('light', 'dark', or 'both')
            output_dir: Optional custom output directory

        Returns:
            GenerationResult with success status and generated files
        """
        try:
            output = output_dir or self.output_dir
            files = []

            # Extract metadata
            metadata = self.metadata_extractor.extract(input_file)

            # Generate CSS for themes
            self._generate_theme_css()

            # Generate light theme if requested
            if theme in ["light", "both"]:
                light_pdf = self._generate_theme_pdf(input_file, "light", output)
                if light_pdf:
                    files.append(str(light_pdf))

            # Generate dark theme if requested
            if theme in ["dark", "both"]:
                dark_pdf = self._generate_theme_pdf(input_file, "dark", output)
                if dark_pdf:
                    files.append(str(dark_pdf))

            # Save metadata
            metadata["pdf_files"] = {
                "light": f"light/{input_file.stem}-light.pdf" if theme in ["light", "both"] else None,
                "dark": f"dark/{input_file.stem}-dark.pdf" if theme in ["dark", "both"] else None,
            }

            metadata_file = self.metadata_dir / f"{input_file.stem}.json"
            self.metadata_extractor.save_metadata(metadata, metadata_file)

            return GenerationResult(
                success=True,
                files=files,
                metadata=metadata
            )

        except Exception as e:
            return GenerationResult(
                success=False,
                files=[],
                error=str(e)
            )

    def batch_generate(
        self,
        input_dir: Path,
        theme: str = "both",
        output_dir: Optional[Path] = None,
        workers: Optional[int] = None,
        pattern: str = "**/*.md",
    ) -> List[GenerationResult]:
        """
        Generate PDFs for all markdown files in directory

        Args:
            input_dir: Directory containing markdown files
            theme: Theme selection
            output_dir: Optional custom output directory
            workers: Number of parallel workers (default from config)
            pattern: Glob pattern for matching files (default: **/*.md)

        Returns:
            List of GenerationResults
        """
        md_files = list(input_dir.glob(pattern))
        workers = workers or self.config.workers
        results = []

        if workers == 1:
            # Sequential processing
            for md_file in md_files:
                result = self.generate(md_file, theme, output_dir)
                results.append(result)
        else:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future_to_file = {
                    executor.submit(self.generate, md_file, theme, output_dir): md_file
                    for md_file in md_files
                }

                for future in as_completed(future_to_file):
                    result = future.result()
                    results.append(result)

        return results

    def _generate_theme_css(self) -> None:
        """Generate CSS files for both themes"""
        self.theme_processor.save_theme_css("light", self.temp_dir)
        self.theme_processor.save_theme_css("dark", self.temp_dir)

    def _generate_theme_pdf(
        self,
        input_file: Path,
        theme: str,
        output_dir: Path
    ) -> Optional[Path]:
        """Generate PDF with specific theme"""
        try:
            # Determine output location
            if self.config.organize_by_theme:
                pdf_output_dir = output_dir / theme
            else:
                pdf_output_dir = output_dir

            pdf_output_dir.mkdir(parents=True, exist_ok=True)
            output_pdf = pdf_output_dir / f"{input_file.stem}-{theme}.pdf"

            # Get CSS file
            css_file = self.temp_dir / f"{theme}-theme.css"

            # Build pandoc command
            cmd = self._build_pandoc_command(input_file, output_pdf, css_file)

            # Execute pandoc
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            return output_pdf

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            print(f"Error generating {theme} PDF for {input_file.name}: {error_msg}")
            return None

        except Exception as e:
            print(f"Unexpected error generating {theme} PDF: {e}")
            return None

    def _build_pandoc_command(
        self,
        input_file: Path,
        output_pdf: Path,
        css_file: Path
    ) -> List[str]:
        """Build pandoc command with all options"""
        cmd = [
            "pandoc",
            str(input_file),
            "--from", "markdown",
            "--to", "html5",
            "--standalone",
            "--embed-resources",
            "--css", str(css_file),
            "--toc",  # Table of contents
            "--toc-depth", "3",
            "--number-sections",
            f"--metadata=title:{input_file.stem}",
            "--pdf-engine", "weasyprint",
        ]

        # Add MathJax support if enabled
        if self.config.math_enabled:
            cmd.extend([
                "--mathjax",
                "--mathml",
            ])

        # Output file
        cmd.extend(["--output", str(output_pdf)])

        return cmd

    def generate_index(self) -> Path:
        """Generate comprehensive index document"""
        index_file = self.output_dir / "INDEX.md"

        # Collect all metadata files
        metadata_files = sorted(
            self.metadata_dir.glob("*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )

        if not metadata_files:
            index_file.write_text("# PDF Documentation Index\n\nNo documents generated yet.")
            return index_file

        # Calculate statistics
        total_docs = len(metadata_files)
        total_size = 0
        total_words = 0

        for meta_file in metadata_files:
            metadata = self.metadata_extractor.load_metadata(meta_file)
            total_size += metadata.get("file_size", 0)
            total_words += metadata.get("word_count", 0)

        # Build index content
        content = f"""# PDF Documentation Index

**Generated:** {self._get_timestamp()}
**Project:** {self.config.project_name}

## 📊 Statistics

- **Total Documents**: {total_docs}
- **Total Words**: {total_words:,}
- **Total Size**: {MetadataExtractor.format_bytes(total_size)}

## 🎨 Themes

### Light Mode
Browse [Light Theme PDFs](light/)
- Clean, bright interface
- Perfect for printing
- Easy on the eyes in well-lit environments

### Dark Mode
Browse [Dark Theme PDFs](dark/)
- Reduced eye strain
- Modern dark aesthetic
- Great for screen reading

## 📚 All Documents

"""

        # Add document entries
        for meta_file in metadata_files:
            metadata = self.metadata_extractor.load_metadata(meta_file)
            title = metadata.get("title", metadata["name"])
            word_count = metadata.get("word_count", 0)
            section_count = metadata.get("section_count", 0)
            modified = metadata.get("modified", "")[:10]
            has_math = metadata.get("has_math", False)

            math_indicator = " 📐" if has_math else ""

            content += f"""
### {title}{math_indicator}
- **Words**: {word_count:,}
- **Sections**: {section_count}
- **Modified**: {modified}
- **Files**:
  - [Light Theme](light/{metadata['name']}-light.pdf)
  - [Dark Theme](dark/{metadata['name']}-dark.pdf)
"""

        # Add footer
        content += """

## 📖 Legend

| Symbol | Meaning |
|--------|---------|
| 📐 | Contains mathematical formulas |
| Words | Total word count in document |
| Sections | Number of headings/sections |
| Modified | Last modification date |

---

*Generated by BARQUE v2.0.0*
"""

        index_file.write_text(content, encoding='utf-8')
        return index_file

    @staticmethod
    def _get_timestamp() -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
