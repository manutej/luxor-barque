"""Metadata extraction and management for BARQUE"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import yaml


class MetadataExtractor:
    """Extract and manage document metadata"""

    def __init__(self):
        pass

    def extract(self, md_file: Path) -> Dict[str, Any]:
        """Extract metadata from markdown file"""
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata = {}

        # Try to extract YAML frontmatter
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            metadata.update(frontmatter)

        # Extract title (from frontmatter or first h1)
        if 'title' not in metadata:
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            metadata['title'] = title_match.group(1) if title_match else md_file.stem

        # Count content elements
        metadata.update({
            'name': md_file.stem,
            'file': str(md_file),
            'file_size': md_file.stat().st_size,
            'line_count': len(content.split('\n')),
            'word_count': len(content.split()),
            'section_count': len(re.findall(r'^#+\s+', content, re.MULTILINE)),
            'code_blocks': len(re.findall(r'```', content)) // 2,
            'links': len(re.findall(r'\[.+?\]\(.+?\)', content)),
            'images': len(re.findall(r'!\[.*?\]\(.+?\)', content)),
        })

        # Detect mathematical content
        metadata['has_math'] = self._detect_math(content)

        # Get file timestamps
        stat = md_file.stat()
        metadata.update({
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        })

        # Extract first 200 characters as summary
        clean_content = self._strip_frontmatter(content)
        summary_text = clean_content[:200].replace('\n', ' ').strip()
        metadata['summary'] = summary_text

        # Set default themes
        metadata['themes'] = ['light', 'dark']

        return metadata

    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from document"""
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if match:
            yaml_content = match.group(1)
            try:
                return yaml.safe_load(yaml_content)
            except yaml.YAMLError:
                return None
        return None

    def _strip_frontmatter(self, content: str) -> str:
        """Remove frontmatter from content"""
        frontmatter_pattern = r'^---\s*\n.*?\n---\s*\n'
        return re.sub(frontmatter_pattern, '', content, count=1, flags=re.DOTALL)

    def _detect_math(self, content: str) -> bool:
        """Detect if document contains mathematical formulas"""
        # Check for LaTeX delimiters
        latex_patterns = [
            r'\$\$.*?\$\$',  # Display math
            r'\$[^$]+\$',    # Inline math
            r'\\begin\{equation\}',
            r'\\begin\{align\}',
            r'\\[.*?\\]',    # LaTeX display mode
        ]

        for pattern in latex_patterns:
            if re.search(pattern, content, re.DOTALL):
                return True

        return False

    def save_metadata(self, metadata: Dict[str, Any], output_file: Path) -> None:
        """Save metadata to JSON file"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert any date objects to strings
        serializable_metadata = self._make_json_serializable(metadata)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_metadata, f, indent=2, ensure_ascii=False)

    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'isoformat'):  # date, time objects
            return obj.isoformat()
        else:
            return obj

    def load_metadata(self, metadata_file: Path) -> Dict[str, Any]:
        """Load metadata from JSON file"""
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def format_bytes(bytes_size: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} PB"
