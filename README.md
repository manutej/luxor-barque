# BARQUE

**Beautiful Automated Report and Query Universal Engine**

Multi-modal document orchestration engine with dual-theme PDF generation, mathematical formula support, and beautiful formatting.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/luxor/barque)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Features

✨ **Dual-Theme Support** - Automatic light and dark mode PDFs from single source
📐 **Mathematical Formulas** - Perfect LaTeX/MathJax rendering in PDFs
🎨 **Beautiful Styling** - Professional typography and layout
⚡ **Batch Processing** - Process hundreds of documents in parallel
📧 **Email Delivery** - Send generated PDFs via email (Resend/SMTP)
🔧 **Highly Configurable** - YAML-based themes and configuration
📦 **Zero Config** - Works out of the box with sensible defaults
🚀 **Fast** - Optimized for large document collections
📊 **Metadata Management** - Extract and organize document metadata
🔌 **Microservice Ready** - Easy integration with LUMOS, LUMINA, and other systems

---

## Quick Start

### Email Setup (2 Minutes)

To use email features, configure your Resend API key:

```bash
# 1. Initialize user config
barque user-config init

# 2. Set your Resend API key (get free key from https://resend.com)
barque user-config set email.resend_api_key re_your_api_key_here

# 3. Set default sender email
barque user-config set email.from noreply@your-domain.com

# 4. Test email delivery
barque send README.md --to your-email@example.com
```

**Note**: Free Resend accounts can only send to your verified email (the one you signed up with). To send to any recipient, verify a domain at [resend.com/domains](https://resend.com/domains).

📖 **[EMAIL-SETUP.md](EMAIL-SETUP.md)** - Complete setup guide
📖 **[CLI-CHEATSHEET.md](CLI-CHEATSHEET.md)** - Quick command reference

### Installation

**From Source** (Currently):

```bash
git clone https://github.com/manutej/luxor-barque.git
cd luxor-barque
pip install -e .
```

**Note**: BARQUE is not yet published to PyPI. Coming soon!

### Basic Usage

```bash
# Initialize BARQUE in your project
barque init

# Generate PDF from single markdown file
barque generate document.md

# Generate both light and dark themes
barque generate document.md --theme both

# Generate and send via email
barque send report.md --to boss@company.com

# Process entire directory
barque batch docs/ --output pdfs/

# Send existing PDF file
barque email report.pdf --to client@example.com --subject "Monthly Report"
```

### Example Document

Create `example.md`:

```markdown
---
title: "My Document"
author: "Your Name"
date: 2025-01-01
---

# Introduction

This is a document with **mathematical formulas**:

$$
E = mc^2
$$

Inline math: $x^2 + y^2 = z^2$

## Features

- Light and dark themes
- Beautiful typography
- Code syntax highlighting
```

Generate PDF:

```bash
barque generate example.md
```

Output:
- `example-light.pdf` - Light theme version
- `example-dark.pdf` - Dark theme version

---

## CLI Commands

### `barque init`

Initialize BARQUE configuration in current directory.

```bash
barque init
```

Creates `.barque/config.yaml` with default settings and theme files.

### `barque generate <file>`

Generate PDF from markdown file.

```bash
barque generate document.md                    # Both themes
barque generate document.md --theme light      # Light only
barque generate document.md --theme dark       # Dark only
barque generate document.md --output pdfs/     # Custom output
```

**Options:**
- `--theme` - Theme selection: `light`, `dark`, or `both` (default: `both`)
- `--output` - Output directory (default: `./output`)
- `--config` - Custom config file path

### `barque batch <directory>`

Process all markdown files in directory.

```bash
barque batch docs/                             # Process all .md files
barque batch docs/ --theme light               # Light theme only
barque batch docs/ --workers 8                 # Parallel processing
barque batch docs/ --output pdfs/ --recursive  # Recursive processing
```

**Options:**
- `--theme` - Theme selection: `light`, `dark`, or `both`
- `--output` - Output directory
- `--workers` - Number of parallel workers (default: 4)
- `--recursive` - Process subdirectories

### `barque clean`

Remove generated output files.

```bash
barque clean              # Clean output directory
barque clean --all        # Clean output and cache
```

### `barque config`

Manage configuration.

```bash
barque config --show      # Show current configuration
barque config --validate  # Validate configuration
barque config --reset     # Reset to defaults
```

### `barque send <file>`

Generate PDF and send via email (convenience command).

**Prerequisites**: Configure email settings with `barque user-config` ([setup guide](EMAIL-SETUP.md))

```bash
# Quick setup
barque user-config set email.resend_api_key re_your_key
barque user-config set email.from noreply@your-domain.com

# Generate PDF and send
barque send report.md --to user@example.com

# With options
barque send doc.md --to user@example.com --theme light            # Light theme only
barque send report.md --to team@company.com --subject "Q4 Report" # Custom subject
barque send file.md --to user@example.com --from custom@email.com # Override sender
```

**Options:**
- `--to` - Recipient email (required, can specify multiple times)
- `--subject` - Email subject (default: auto-generated from filename)
- `--from` - Sender email address (default: from config or env)
- `--theme` - PDF theme: `light`, `dark`, or `both` (default: `both`)
- `--provider` - Email provider: `resend` or `smtp` (default: `resend`)
- `--body` - Custom email body text
- `--email-config` - Path to email config file (optional)

### `barque email <files...>`

Send existing files via email.

**Prerequisites**: Configure email settings with `barque user-config` ([setup guide](EMAIL-SETUP.md))

```bash
# Quick setup
barque user-config set email.resend_api_key re_your_key

# Send single file
barque email report.pdf --to user@example.com --subject "Report"

# Multiple files
barque email doc1.pdf doc2.pdf --to team@company.com --subject "Documents"

# With CC/BCC
barque email file.pdf \
  --to user@example.com \
  --cc manager@company.com \
  --bcc archive@company.com \
  --subject "Important File"
```

### `barque user-config`

Manage user-level configuration (API keys, email settings).

```bash
# Initialize user config
barque user-config init

# Set Resend API key
barque user-config set email.resend_api_key re_your_key

# Set default sender email
barque user-config set email.from noreply@your-domain.com

# View all settings
barque user-config show

# Get specific value
barque user-config get email.from

# Show config file location
barque user-config path
```

**Available Settings:**
- `email.resend_api_key` - Resend API key
- `email.from` - Default sender email
- `email.signature` - Email signature
- `smtp.host` - SMTP server (alternative to Resend)
- `smtp.port` - SMTP port
- `smtp.username` - SMTP username
- `smtp.password` - SMTP password
- `preferences.theme` - Default theme (light/dark/both)
- `preferences.output` - Default output directory
```

**Options:**
- `--to` - Recipient email (required, can specify multiple times)
- `--subject` - Email subject (required)
- `--from` - Sender email address (default: from config or env)
- `--cc` - CC recipient (can specify multiple times)
- `--bcc` - BCC recipient (can specify multiple times)
- `--body` - Custom email body text
- `--provider` - Email provider: `resend` or `smtp` (default: `resend`)
- `--email-config` - Path to email config file (optional)

---

## Email Documentation

📖 **[EMAIL-SETUP.md](EMAIL-SETUP.md)** - 5-minute setup guide (start here!)
📖 **[EMAIL-GUIDE.md](EMAIL-GUIDE.md)** - Complete email feature documentation
📖 **[CONFIGURATION-GUIDE.md](CONFIGURATION-GUIDE.md)** - Advanced configuration

---

## Configuration

BARQUE uses `.barque/config.yaml` for configuration:

```yaml
# Project Information
project:
  name: "My Project"
  description: "Project documentation"
  author: "Your Name"

# Output Settings
output:
  directory: "./output"
  organize_by_theme: true
  create_index: true

# Styling
styling:
  font_family: "Inter, -apple-system, sans-serif"
  base_font_size: "14px"
  line_height: 1.6
  max_width: "900px"

# Light Theme
light_theme:
  background: "#ffffff"
  text: "#1a1a1a"
  accent: "#2563eb"
  code_bg: "#f0f0f0"
  border: "#e0e0e0"

# Dark Theme
dark_theme:
  background: "#1a1a1a"
  text: "#e8e8e8"
  accent: "#60a5fa"
  code_bg: "#2d2d2d"
  border: "#3d3d3d"

# Mathematical Formulas
math:
  enabled: true
  engine: "mathjax"  # or "katex"
  inline_delimiter: "$"
  display_delimiter: "$$"

# Processing
processing:
  workers: 4
  cache_enabled: true
  incremental_build: false
```

---

## Mathematical Formulas

BARQUE supports beautiful mathematical formulas using LaTeX syntax:

### Inline Math

```markdown
The equation $E = mc^2$ is famous.
```

### Display Math

```markdown
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

### Complex Equations

```markdown
$$
\frac{\partial f}{\partial x} = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}
$$
```

All formulas render perfectly in both light and dark themes!

---

## Custom Themes

Create custom theme in `.barque/themes/corporate.yaml`:

```yaml
name: corporate
description: Corporate brand theme

colors:
  background: "#f8f9fa"
  text: "#212529"
  accent: "#0066cc"
  code_bg: "#e9ecef"

fonts:
  heading: "Montserrat, sans-serif"
  body: "Open Sans, sans-serif"
  code: "JetBrains Mono, monospace"

styling:
  border_radius: "8px"
  shadow: "0 2px 8px rgba(0,0,0,0.1)"
```

Use custom theme:

```bash
barque generate doc.md --theme corporate
```

---

## Advanced Usage

### Python API

```python
from barque import PDFGenerator, BarqueConfig

# Load configuration
config = BarqueConfig.load(".barque/config.yaml")

# Create generator
generator = PDFGenerator(config)

# Generate PDF
result = generator.generate(
    input_file="document.md",
    theme="both",
    output_dir="pdfs/"
)

if result.success:
    print(f"Generated: {result.files}")
else:
    print(f"Error: {result.error}")

# Batch processing
results = generator.batch_generate(
    input_dir="docs/",
    theme="both",
    workers=8
)
```

### Custom Templates

Create custom Jinja2 template in `.barque/templates/custom.j2`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ metadata.title }}</title>
    <style>
        {{ theme_css }}
    </style>
</head>
<body>
    <header>
        <h1>{{ metadata.title }}</h1>
        <p>By {{ metadata.author }} - {{ metadata.date }}</p>
    </header>
    <main>
        {{ content | safe }}
    </main>
</body>
</html>
```

---

## Requirements

### System Dependencies

- **Python 3.8+**
- **pandoc** - Document converter
- **wkhtmltopdf** - PDF renderer (or WeasyPrint)

### Installation

**macOS:**
```bash
brew install pandoc wkhtmltopdf
```

**Ubuntu/Debian:**
```bash
sudo apt-get install pandoc wkhtmltopdf
```

**Windows:**
Download installers from:
- [Pandoc](https://pandoc.org/installing.html)
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

---

## Comparison with Alternatives

| Feature | BARQUE | Pandoc | LaTeX | Sphinx |
|---------|--------|--------|-------|--------|
| Dual Themes | ✅ | ❌ | ❌ | ⚠️ |
| Math Support | ✅ | ✅ | ✅ | ✅ |
| Easy Setup | ✅ | ✅ | ❌ | ⚠️ |
| Batch Processing | ✅ | ⚠️ | ❌ | ✅ |
| Custom Themes | ✅ | ❌ | ⚠️ | ✅ |
| Markdown-First | ✅ | ✅ | ❌ | ⚠️ |
| Zero Config | ✅ | ✅ | ❌ | ❌ |

---

## Examples

### Scientific Paper

```markdown
---
title: "Quantum Computing Overview"
author: "Dr. Smith"
date: 2025-01-01
---

# Abstract

Quantum computing leverages quantum mechanics...

# Introduction

The wave function $|\psi\rangle$ satisfies:

$$
i\hbar\frac{\partial}{\partial t}|\psi\rangle = \hat{H}|\psi\rangle
$$

# Results

...
```

### Technical Documentation

```markdown
---
title: "API Reference"
version: "2.0.0"
---

# Authentication

API uses OAuth 2.0:

```python
import requests
response = requests.get(
    "https://api.example.com/data",
    headers={"Authorization": f"Bearer {token}"}
)
`` `

# Endpoints

...
```

---

## Performance

Benchmark results (100 documents, avg 5000 words each):

| Operation | Time | Throughput |
|-----------|------|------------|
| Single PDF | 2.3s | - |
| Batch (1 worker) | 4min 12s | 0.4 docs/s |
| Batch (4 workers) | 1min 18s | 1.3 docs/s |
| Batch (8 workers) | 42s | 2.4 docs/s |

---

## Troubleshooting

### PDFs not generating

Check system dependencies:
```bash
which pandoc wkhtmltopdf
```

### Math formulas not rendering

Ensure MathJax is enabled in config:
```yaml
math:
  enabled: true
  engine: "mathjax"
```

### Theme not applying

Validate configuration:
```bash
barque config --validate
```

---

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Citation

If you use BARQUE in research, please cite:

```bibtex
@software{barque2025,
  title = {BARQUE: Multi-modal Document Orchestration Engine},
  author = {LUXOR Systems},
  year = {2025},
  url = {https://github.com/luxor/barque}
}
```

---

## Support

- 📖 [Documentation](https://barque.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/luxor/barque/issues)
- 💬 [Discussions](https://github.com/luxor/barque/discussions)

---

**Made with ❤️ by LUXOR Systems**
