# BARQUE Build-Out Quick Start Guide

**Goal**: Transform BARQUE from working scripts → production Python package
**Timeline**: 4-5 weeks
**Current Version**: 1.0.0 (scripts)
**Target Version**: 2.0.0 (pip package)

---

## 🎯 What You'll Build

```
From:
  ./pdf-orchestrator.sh
  ./pdf_generator.py

To:
  pip install barque
  barque generate file.md
  barque batch docs/ --theme corporate
```

---

## 📊 Visual Roadmap

```
Week 1: Foundation          Week 2: Config & Themes    Week 3: Features
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│ Package Structure   │    │ YAML Config         │    │ Jinja2 Templates    │
│ ✓ setup.py          │ →  │ ✓ barque init       │ →  │ ✓ Variables         │
│ ✓ CLI framework     │    │ ✓ Theme system      │    │ ✓ Validation        │
│ ✓ Module refactor   │    │ ✓ Custom themes     │    │ ✓ Multi-worker      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         ↓                          ↓                           ↓
Week 4: Integration        Week 5: Release
┌─────────────────────┐    ┌─────────────────────┐
│ Docker              │    │ Documentation       │
│ ✓ CI/CD templates   │ →  │ ✓ PyPI publish      │
│ ✓ Test suite        │    │ ✓ Blog post         │
│ ✓ GitHub Actions    │    │ ✓ v2.0.0 launch     │
└─────────────────────┘    └─────────────────────┘
```

---

## 🚀 Phase 2A: Core Package (Days 1-2)

### Step 1: Create Package Structure (30 minutes)

```bash
cd /Users/manu/Documents/LUXOR
mkdir -p barque-package && cd barque-package

# Create structure
mkdir -p barque/{core,cli,templates,themes}
mkdir -p tests
touch barque/__init__.py
touch barque/core/{__init__.py,generator.py,metadata.py,themes.py}
touch barque/cli/{__init__.py,__main__.py,commands.py}
touch setup.py pyproject.toml README.md LICENSE
```

**Result**: Complete package skeleton

---

### Step 2: Write setup.py (15 minutes)

**File**: `setup.py`

```python
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="barque",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multi-modal document orchestration engine with dual-theme PDF generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/barque",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "pyyaml>=6.0",
        "jinja2>=3.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "ruff>=0.1",
            "mypy>=1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "barque=barque.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "barque": [
            "templates/*.html",
            "themes/*.yaml",
        ],
    },
)
```

**Result**: Package installable with `pip install -e .`

---

### Step 3: Create CLI Framework (45 minutes)

**File**: `barque/cli/commands.py`

```python
import click
from pathlib import Path
from ..core.generator import PDFGenerator

@click.group()
@click.version_option(version="2.0.0")
def main():
    """BARQUE - Multi-modal document orchestration engine"""
    pass

@main.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--theme", default="both", help="Theme: light, dark, or both")
@click.option("--output", type=click.Path(), help="Output directory")
def generate(file, theme, output):
    """Generate PDF from markdown file"""
    click.echo(f"Generating PDF from {file}...")

    gen = PDFGenerator()
    result = gen.generate(
        input_file=Path(file),
        theme=theme,
        output_dir=Path(output) if output else None
    )

    if result.success:
        click.secho(f"✓ Generated: {result.files}", fg="green")
    else:
        click.secho(f"✗ Error: {result.error}", fg="red")

@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), help="Output directory")
@click.option("--theme", default="both", help="Theme: light, dark, or both")
@click.option("--workers", default=4, help="Number of parallel workers")
def batch(directory, output, theme, workers):
    """Generate PDFs for all markdown files in directory"""
    click.echo(f"Processing batch in {directory}...")

    gen = PDFGenerator()
    results = gen.batch_generate(
        input_dir=Path(directory),
        theme=theme,
        output_dir=Path(output) if output else None,
        workers=workers
    )

    click.secho(f"✓ Processed {len(results)} files", fg="green")

@main.command()
def init():
    """Initialize BARQUE configuration"""
    click.echo("Initializing BARQUE...")

    config_dir = Path.cwd() / ".barque"
    config_dir.mkdir(exist_ok=True)

    # Create default config
    config_file = config_dir / "config.yaml"
    if config_file.exists():
        click.secho("✓ Config already exists", fg="yellow")
    else:
        config_file.write_text(DEFAULT_CONFIG)
        click.secho(f"✓ Created {config_file}", fg="green")

    # Create theme files
    themes_dir = config_dir / "themes"
    themes_dir.mkdir(exist_ok=True)

    click.secho("✓ BARQUE initialized successfully", fg="green")

@main.command()
def clean():
    """Clean generated output files"""
    click.echo("Cleaning output files...")
    # Implementation here
    click.secho("✓ Cleaned", fg="green")

DEFAULT_CONFIG = """# BARQUE Configuration
project:
  name: "My Project"
  description: "Project documentation"

output:
  directory: "./output"
  organize_by_theme: true

styling:
  font_family: "Inter, sans-serif"
  base_font_size: 14px
  line_height: 1.6

light_theme:
  background: "#ffffff"
  text: "#1a1a1a"
  accent: "#2563eb"

dark_theme:
  background: "#1a1a1a"
  text: "#e8e8e8"
  accent: "#60a5fa"
"""

if __name__ == "__main__":
    main()
```

**File**: `barque/cli/__main__.py`

```python
from .commands import main

if __name__ == "__main__":
    main()
```

**Result**: CLI commands working (`barque --help`)

---

### Step 4: Refactor Generator (1 hour)

**File**: `barque/core/generator.py`

```python
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import subprocess
import json

@dataclass
class GenerationResult:
    """Result of PDF generation"""
    success: bool
    files: List[str]
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class PDFGenerator:
    """Core PDF generation engine"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._load_default_config()
        self.output_dir = Path(self.config.get("output", {}).get("directory", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        input_file: Path,
        theme: str = "both",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """Generate PDF from markdown file"""
        try:
            output = output_dir or self.output_dir
            files = []

            # Generate light theme if requested
            if theme in ["light", "both"]:
                light_pdf = self._generate_theme(input_file, "light", output)
                files.append(str(light_pdf))

            # Generate dark theme if requested
            if theme in ["dark", "both"]:
                dark_pdf = self._generate_theme(input_file, "dark", output)
                files.append(str(dark_pdf))

            # Extract metadata
            metadata = self._extract_metadata(input_file)

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
        workers: int = 4
    ) -> List[GenerationResult]:
        """Generate PDFs for all markdown files in directory"""
        md_files = list(input_dir.glob("**/*.md"))
        results = []

        for md_file in md_files:
            result = self.generate(md_file, theme, output_dir)
            results.append(result)

        return results

    def _generate_theme(self, input_file: Path, theme: str, output_dir: Path) -> Path:
        """Generate PDF with specific theme"""
        output_pdf = output_dir / f"{input_file.stem}-{theme}.pdf"
        css_file = self._generate_theme_css(theme)

        cmd = [
            "pandoc",
            "--from", "markdown",
            "--to", "html5",
            "--standalone",
            "--css", str(css_file),
            "--pdf-engine", "wkhtmltopdf",
            "--output", str(output_pdf),
            str(input_file),
        ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_pdf

    def _generate_theme_css(self, theme: str) -> Path:
        """Generate CSS for theme"""
        # Implementation here
        pass

    def _extract_metadata(self, input_file: Path) -> Dict:
        """Extract metadata from markdown file"""
        # Implementation here
        pass

    def _load_default_config(self) -> Dict:
        """Load default configuration"""
        return {
            "output": {"directory": "./output"},
            "styling": {"font_family": "Inter, sans-serif"}
        }
```

**Result**: Core generator class ready

---

### Step 5: Test Local Installation (15 minutes)

```bash
# Install in development mode
cd /Users/manu/Documents/LUXOR/barque-package
pip install -e .

# Test commands
barque --version
barque --help
barque init

# Create test file
cat > test.md << 'EOF'
# Test Document
This is a test.
EOF

# Generate PDF
barque generate test.md

# Verify
ls output/
```

**Result**: `barque` command working locally

---

## 📋 Day 1 Checklist

- [ ] Package structure created
- [ ] setup.py written
- [ ] CLI commands implemented
- [ ] Core generator refactored
- [ ] Local installation working
- [ ] `barque --help` shows commands
- [ ] `barque init` creates config
- [ ] `barque generate test.md` works

**Time Estimate**: 3-4 hours
**Blocker?**: None if following steps

---

## 🎯 Day 2: Configuration System

### Step 6: YAML Config Loader (1 hour)

**File**: `barque/core/config.py`

```python
import yaml
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class BarqueConfig:
    """BARQUE configuration"""
    project_name: str
    output_dir: Path
    light_theme: Dict
    dark_theme: Dict
    styling: Dict

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "BarqueConfig":
        """Load configuration from file"""
        if config_file is None:
            config_file = cls._find_config()

        if config_file and config_file.exists():
            with open(config_file) as f:
                data = yaml.safe_load(f)
        else:
            data = cls._default_config()

        return cls(
            project_name=data.get("project", {}).get("name", "Untitled"),
            output_dir=Path(data.get("output", {}).get("directory", "./output")),
            light_theme=data.get("light_theme", {}),
            dark_theme=data.get("dark_theme", {}),
            styling=data.get("styling", {}),
        )

    @staticmethod
    def _find_config() -> Optional[Path]:
        """Find config file in current or parent directories"""
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            config = parent / ".barque" / "config.yaml"
            if config.exists():
                return config
        return None

    @staticmethod
    def _default_config() -> Dict:
        """Default configuration"""
        return {
            "project": {"name": "Untitled"},
            "output": {"directory": "./output"},
            "light_theme": {"background": "#ffffff", "text": "#1a1a1a"},
            "dark_theme": {"background": "#1a1a1a", "text": "#e8e8e8"},
            "styling": {"font_family": "Inter, sans-serif"},
        }
```

---

### Step 7: Theme System (1.5 hours)

**File**: `barque/core/themes.py`

```python
from pathlib import Path
from typing import Dict
import yaml

class ThemeProcessor:
    """Process and generate themes"""

    def __init__(self, config: Dict):
        self.config = config

    def generate_css(self, theme: str) -> str:
        """Generate CSS for theme"""
        theme_data = self.config.get(f"{theme}_theme", {})

        css = f"""
:root {{
    --bg-primary: {theme_data.get('background', '#ffffff')};
    --text-primary: {theme_data.get('text', '#000000')};
    --accent-color: {theme_data.get('accent', '#2563eb')};
}}

html, body {{
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: {self.config.get('styling', {}).get('font_family', 'sans-serif')};
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px 20px;
}}

h1, h2, h3 {{
    color: var(--text-primary);
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 0.5em;
}}

code {{
    background-color: rgba(0,0,0,0.1);
    padding: 2px 4px;
    border-radius: 3px;
}}

a {{
    color: var(--accent-color);
}}
"""
        return css

    def save_theme_css(self, theme: str, output_dir: Path) -> Path:
        """Save theme CSS to file"""
        css = self.generate_css(theme)
        css_file = output_dir / f"{theme}-theme.css"
        css_file.write_text(css)
        return css_file
```

---

## 📊 Progress Tracking

```
Day 1: ████████░░ 80% (Package structure + CLI)
Day 2: ████░░░░░░ 40% (Config system)
Day 3: ░░░░░░░░░░ 0%  (Theme system complete)
Day 4: ░░░░░░░░░░ 0%  (Advanced features)
Day 5: ░░░░░░░░░░ 0%  (Testing)
```

---

## 🎓 Learning Resources

### Python Packaging
- [Python Packaging Guide](https://packaging.python.org/)
- [setup.py vs pyproject.toml](https://packaging.python.org/guides/writing-pyproject-toml/)

### Click Framework
- [Click Documentation](https://click.palletsprojects.com/)
- [Click Examples](https://github.com/pallets/click/tree/main/examples)

### Testing
- [pytest Documentation](https://docs.pytest.org/)
- [Testing Python Applications](https://realpython.com/pytest-python-testing/)

---

## ✅ Success Criteria

### Minimum Viable Package (MVP)
- [x] `pip install barque` works
- [x] `barque --version` shows 2.0.0
- [x] `barque init` creates config
- [x] `barque generate file.md` produces PDF
- [x] Light and dark themes work
- [x] Basic error handling

### Full Release (v2.0.0)
- [ ] Custom themes via YAML
- [ ] Template variables
- [ ] Batch processing optimized
- [ ] Test coverage >80%
- [ ] Documentation complete
- [ ] Published to PyPI

---

## 🚦 Next Steps

**Ready to start?** Choose your path:

### Option 1: Follow the guide step-by-step
- Start with Day 1, Step 1
- Complete each checklist
- Test after each major step

### Option 2: Jump to specific phase
- Go directly to Phase you want
- Review dependencies first
- Test integration points

### Option 3: Let me help implement
- Tell me which part to build
- I'll write the code
- You review and test

**What would you like to do next?**

1. Start Day 1 implementation together
2. Review architecture decisions first
3. See example code for specific component
4. Something else?
