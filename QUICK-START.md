# BARQUE Quick Start Guide

**Version**: 2.0.0
**Status**: Production Ready ✅

---

## Installation

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/BARQUE
source venv/bin/activate
pip install -e .
```

## Shell Alias Setup

```bash
./setup-barque-alias.sh
source ~/.zshrc
```

## Verify Installation

```bash
barque --version    # Should show: barque, version 2.0.0
barque --help       # Show all commands
```

---

## Common Commands

### Initialize Project
```bash
cd your-project
barque init        # Creates .barque/config.yaml
```

### Generate Single PDF
```bash
# Both themes (default)
barque generate document.md

# Light theme only
barque generate document.md --theme light

# Dark theme only
barque generate document.md --theme dark

# Custom output directory
barque generate document.md --output pdfs/
```

### Batch Processing
```bash
# Process all .md files in directory
barque batch docs/

# With custom settings
barque batch docs/ --workers 8 --theme both --output pdfs/

# Show progress
barque batch docs/ --workers 4
```

### Configuration
```bash
# Show current configuration
barque config --show

# Validate configuration
barque config --validate
```

### Cleanup
```bash
# Remove generated PDFs
barque clean

# Remove everything including cache
barque clean --all
```

---

## Example Workflow

```bash
# 1. Initialize BARQUE
cd ~/Documents/my-docs
barque init

# 2. Generate PDFs
barque batch ./ --workers 4

# 3. Check output
ls output/light/    # Light theme PDFs
ls output/dark/     # Dark theme PDFs
cat output/INDEX.md # Generated index
```

---

## Mathematical Formulas

BARQUE supports LaTeX math:

```markdown
Inline math: $E = mc^2$

Display math:
$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$
```

---

## Configuration

Edit `.barque/config.yaml`:

```yaml
project:
  name: "My Project"

output:
  directory: "./output"
  organize_by_theme: true

light_theme:
  background: "#ffffff"
  text: "#1a1a1a"
  accent: "#2563eb"

dark_theme:
  background: "#1a1a1a"
  text: "#e8e8e8"
  accent: "#60a5fa"

math:
  enabled: true
  engine: "mathjax"

processing:
  workers: 4
```

---

## Output Structure

```
output/
├── light/              # Light theme PDFs
├── dark/               # Dark theme PDFs
├── metadata/           # Document metadata (JSON)
├── INDEX.md            # Generated index
└── .temp/              # Temporary files
```

---

## Tips & Tricks

### 1. Use Custom Themes
Edit theme colors in `.barque/config.yaml`

### 2. Parallel Processing
Use `--workers 8` for faster batch processing

### 3. Check Configuration
Run `barque config --validate` before generating

### 4. Organize Output
Use `organize_by_theme: true` to separate light/dark PDFs

### 5. Mathematical Documents
Set `math.enabled: true` for documents with formulas

---

## Troubleshooting

### Issue: Command not found
```bash
source ~/.zshrc
# or
source venv/bin/activate
```

### Issue: Configuration errors
```bash
barque config --validate
```

### Issue: PDF generation fails
```bash
# Check pandoc is installed
which pandoc

# Check WeasyPrint is installed
source venv/bin/activate
python -c "import weasyprint"
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `barque init` | Initialize configuration |
| `barque generate <file>` | Generate PDF from markdown |
| `barque batch <dir>` | Process directory |
| `barque config --show` | Show configuration |
| `barque config --validate` | Validate configuration |
| `barque clean` | Remove generated files |
| `barque --version` | Show version |
| `barque --help` | Show help |

---

## Examples

### Example 1: Quick PDF
```bash
barque generate README.md
```

### Example 2: Batch with Custom Output
```bash
barque batch docs/ --output ~/PDFs/my-docs
```

### Example 3: Light Theme Only
```bash
barque batch docs/ --theme light --workers 8
```

### Example 4: Dark Theme with Custom Config
```bash
barque generate doc.md --theme dark --config custom-config.yaml
```

---

## Resources

- **Full Documentation**: README.md
- **Implementation Details**: IMPLEMENTATION-COMPLETE.md
- **Project Status**: BARQUE-PROJECT-STATUS.md
- **Test Outputs**:
  - `/Users/manu/Documents/LUXOR/PROJECTS/BARQUE/sample-output/`
  - `/Users/manu/Documents/LUXOR/PROJECTS/BARQUE/batch-output/`

---

**Ready to use BARQUE? Start with `barque init`!** 🚀
