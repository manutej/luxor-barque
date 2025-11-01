"""Configuration management for BARQUE"""

import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, field


@dataclass
class BarqueConfig:
    """BARQUE configuration"""

    # Project information
    project_name: str = "Untitled"
    project_description: str = ""
    project_author: str = ""

    # Output settings
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    organize_by_theme: bool = True
    create_index: bool = True

    # Styling
    font_family: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    base_font_size: str = "14px"
    line_height: float = 1.6
    max_width: str = "900px"

    # Light theme colors
    light_theme: Dict[str, str] = field(default_factory=lambda: {
        "background": "#ffffff",
        "text": "#1a1a1a",
        "accent": "#2563eb",
        "code_bg": "#f0f0f0",
        "border": "#e0e0e0",
    })

    # Dark theme colors
    dark_theme: Dict[str, str] = field(default_factory=lambda: {
        "background": "#1a1a1a",
        "text": "#e8e8e8",
        "accent": "#60a5fa",
        "code_bg": "#2d2d2d",
        "border": "#3d3d3d",
    })

    # Mathematical formulas
    math_enabled: bool = True
    math_engine: str = "mathjax"
    math_inline_delimiter: str = "$"
    math_display_delimiter: str = "$$"

    # Processing
    workers: int = 4
    cache_enabled: bool = True
    incremental_build: bool = False

    @classmethod
    def load(cls, config_file: Optional[Path] = None) -> "BarqueConfig":
        """Load configuration from file or find in parent directories"""
        if config_file is None:
            config_file = cls._find_config()

        if config_file and config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "BarqueConfig":
        """Create config from dictionary"""
        project = data.get("project", {})
        output = data.get("output", {})
        styling = data.get("styling", {})
        math = data.get("math", {})
        processing = data.get("processing", {})

        # Default themes
        default_light = {
            "background": "#ffffff",
            "text": "#1a1a1a",
            "accent": "#2563eb",
            "code_bg": "#f0f0f0",
            "border": "#e0e0e0",
        }
        default_dark = {
            "background": "#1a1a1a",
            "text": "#e8e8e8",
            "accent": "#60a5fa",
            "code_bg": "#2d2d2d",
            "border": "#3d3d3d",
        }

        return cls(
            # Project
            project_name=project.get("name", "Untitled"),
            project_description=project.get("description", ""),
            project_author=project.get("author", ""),
            # Output
            output_dir=Path(output.get("directory", "./output")),
            organize_by_theme=output.get("organize_by_theme", True),
            create_index=output.get("create_index", True),
            # Styling
            font_family=styling.get("font_family", "Inter, sans-serif"),
            base_font_size=styling.get("base_font_size", "14px"),
            line_height=styling.get("line_height", 1.6),
            max_width=styling.get("max_width", "900px"),
            # Themes
            light_theme=data.get("light_theme", default_light),
            dark_theme=data.get("dark_theme", default_dark),
            # Math
            math_enabled=math.get("enabled", True),
            math_engine=math.get("engine", "mathjax"),
            math_inline_delimiter=math.get("inline_delimiter", "$"),
            math_display_delimiter=math.get("display_delimiter", "$$"),
            # Processing
            workers=processing.get("workers", 4),
            cache_enabled=processing.get("cache_enabled", True),
            incremental_build=processing.get("incremental_build", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "project": {
                "name": self.project_name,
                "description": self.project_description,
                "author": self.project_author,
            },
            "output": {
                "directory": str(self.output_dir),
                "organize_by_theme": self.organize_by_theme,
                "create_index": self.create_index,
            },
            "styling": {
                "font_family": self.font_family,
                "base_font_size": self.base_font_size,
                "line_height": self.line_height,
                "max_width": self.max_width,
            },
            "light_theme": self.light_theme,
            "dark_theme": self.dark_theme,
            "math": {
                "enabled": self.math_enabled,
                "engine": self.math_engine,
                "inline_delimiter": self.math_inline_delimiter,
                "display_delimiter": self.math_display_delimiter,
            },
            "processing": {
                "workers": self.workers,
                "cache_enabled": self.cache_enabled,
                "incremental_build": self.incremental_build,
            },
        }

    def save(self, config_file: Path) -> None:
        """Save configuration to file"""
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

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
    def get_default_config_content() -> str:
        """Get default configuration as YAML string"""
        default_config = BarqueConfig()
        return yaml.dump(
            default_config.to_dict(),
            default_flow_style=False,
            sort_keys=False
        )

    def validate(self) -> tuple[bool, list[str]]:
        """Validate configuration"""
        errors = []

        # Validate paths
        if not self.output_dir:
            errors.append("Output directory not specified")

        # Validate math engine
        if self.math_engine not in ["mathjax", "katex", "latex"]:
            errors.append(f"Invalid math engine: {self.math_engine}")

        # Validate workers
        if self.workers < 1:
            errors.append(f"Workers must be >= 1, got {self.workers}")

        # Validate themes
        required_theme_keys = ["background", "text", "accent"]
        for theme_name, theme_data in [("light", self.light_theme), ("dark", self.dark_theme)]:
            for key in required_theme_keys:
                if key not in theme_data:
                    errors.append(f"Missing key '{key}' in {theme_name}_theme")

        return (len(errors) == 0, errors)
