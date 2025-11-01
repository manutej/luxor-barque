# BARQUE Testing Guide

**Quick Reference for Testing BARQUE v2.0.0**

---

## ✅ Alias Status

**YES** - The alias is configured in `~/.zshrc`:

```bash
alias barque='/Users/manu/Documents/LUXOR/PROJECTS/BARQUE/venv/bin/barque'
```

### Activate Alias

```bash
source ~/.zshrc
```

---

## ✅ Help System

**YES** - BARQUE has comprehensive `--help`:

```bash
# General help
barque --help

# Command-specific help
barque generate --help
barque batch --help
barque config --help
barque clean --help
```

---

## 🎯 Quick Start (30 seconds)

### 1. Activate Alias
```bash
source ~/.zshrc
```

### 2. Verify Installation
```bash
barque --version    # Should show: barque, version 2.0.0
```

### 3. Test with Demo
```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/BARQUE
barque generate /Users/manu/Documents/LUXOR/docs/organization/research/MARS-MERCURIO-ANALYSIS-SUMMARY.md
```

### 4. View Output
```bash
open output/light/*.pdf
open output/dark/*.pdf
```

**Expected Result:**
- ✅ 2 PDFs generated (light + dark)
- ✅ ~163KB each
- ✅ 1,805 words, 42 sections
- ✅ Mathematical formulas rendered 📐

---

## 🧪 Test Files (Proven to Work)

### Small File (13KB) - Good for Quick Tests
```bash
/Users/manu/Documents/LUXOR/docs/organization/research/MARS-MERCURIO-ANALYSIS-SUMMARY.md
```

### Medium File (16KB)
```bash
/Users/manu/Documents/LUXOR/docs/CATEGORY_A_COMPLETE_GUIDE.md
```

### Large File (33KB)
```bash
/Users/manu/Documents/LUXOR/docs/MARS_MERCURIO_FRAMEWORK.md
```

### Extra Large File (44KB)
```bash
/Users/manu/Documents/LUXOR/docs/hekat-dsl/CATEGORICAL_META_PROMPTING_SYNTHESIS.md
```

### Batch Directory (8 files - Proven ✅)
```bash
/Users/manu/Documents/LUXOR/docs/hekat-dsl/research
```

---

## 🚀 Test Scripts

### Quick Test (Automated - 3 Examples)

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/BARQUE
./quick-test.sh
```

**What it does:**
1. Single file with both themes
2. Batch processing (MARS docs)
3. Large file (44KB)

**Time:** ~30 seconds

### Comprehensive Test Suite (7 Tests)

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/BARQUE
./test-barque.sh
```

**What it does:**
1. Single file - light theme only
2. Single file - dark theme only
3. Single file - both themes
4. Batch - MARS docs
5. Batch - HEKAT research
6. Batch - Organization docs
7. Configuration management

**Time:** ~2 minutes

---

## 📋 Common Commands

### Generate PDFs

```bash
# Single file - both themes (default)
barque generate file.md

# Single file - light only
barque generate file.md --theme light

# Single file - dark only
barque generate file.md --theme dark

# Custom output directory
barque generate file.md --output ~/PDFs/
```

### Batch Processing

```bash
# Process directory - both themes
barque batch docs/

# Fast processing with 8 workers
barque batch docs/ --workers 8

# Light theme only (for printing)
barque batch docs/ --theme light

# Custom output
barque batch docs/ --output ~/PDFs/project
```

### Configuration

```bash
# Initialize in project
barque init

# Show configuration
barque config --show

# Validate configuration
barque config --validate
```

### Cleanup

```bash
# Clean generated PDFs
barque clean

# Clean everything including cache
barque clean --all
```

---

## 🎬 Example Workflows

### Workflow 1: Generate PDFs for MARS Documentation

```bash
source ~/.zshrc
barque batch ~/Documents/LUXOR/docs/mars --output ~/PDFs/mars
open ~/PDFs/mars/INDEX.md
```

### Workflow 2: Generate PDFs for HEKAT Research

```bash
barque batch ~/Documents/LUXOR/docs/hekat-dsl/research --output ~/PDFs/hekat
ls ~/PDFs/hekat/light/
ls ~/PDFs/hekat/dark/
```

### Workflow 3: Single Important Document

```bash
barque generate ~/Documents/LUXOR/docs/CATEGORY_A_COMPLETE_GUIDE.md
open output/light/*.pdf
```

---

## 📊 Test Results

### Demo Test (Just Completed ✅)

```bash
File: MARS-MERCURIO-ANALYSIS-SUMMARY.md
Size: 13KB (1,805 words)
Result: SUCCESS ✅

Generated:
  ✓ light PDF: 163KB
  ✓ dark PDF: 163KB
  ✓ Mathematical formulas: Rendered correctly 📐
  ✓ Sections: 42
  ✓ Time: ~2 seconds
```

### Previous Batch Test (8 Files ✅)

```bash
Directory: hekat-dsl/research
Files: 8 markdown documents
Workers: 4 (parallel)
Result: SUCCESS ✅

Generated:
  ✓ 16 PDFs (8 light + 8 dark)
  ✓ Total: 47,383 words
  ✓ Success rate: 100% (8/8)
  ✓ Index: Generated automatically
  ✓ Time: ~8 seconds
```

---

## 🔍 Troubleshooting

### Issue: "command not found: barque"

**Solution:**
```bash
source ~/.zshrc
```

### Issue: Need to use without alias

**Solution:**
```bash
/Users/manu/Documents/LUXOR/PROJECTS/BARQUE/venv/bin/barque --help
```

### Issue: PDF generation fails

**Check dependencies:**
```bash
which pandoc    # Should show path
python -c "import weasyprint"  # Should not error
```

---

## 📁 Output Locations

### Default Output Structure

```
output/
├── light/              # Light theme PDFs
│   ├── file1-light.pdf
│   └── file2-light.pdf
├── dark/               # Dark theme PDFs
│   ├── file1-dark.pdf
│   └── file2-dark.pdf
├── metadata/           # Document metadata (JSON)
│   ├── file1.json
│   └── file2.json
└── INDEX.md            # Comprehensive index
```

### Current Test Outputs

```
/Users/manu/Documents/LUXOR/PROJECTS/BARQUE/
├── sample-output/      # Single file test (HEKAT integration)
├── batch-output/       # Batch test (8 files from hekat-dsl/research)
├── demo-output/        # Demo test (MARS analysis)
├── quick-test-output/  # Quick test script output
└── test-outputs/       # Comprehensive test script output
```

---

## ✅ Checklist for New Users

- [ ] Alias activated: `source ~/.zshrc`
- [ ] Version check: `barque --version` shows 2.0.0
- [ ] Help works: `barque --help` shows commands
- [ ] Demo test passed: Single file generated successfully
- [ ] PDFs viewable: Can open light and dark PDFs
- [ ] Batch test passed: Multiple files processed
- [ ] Configuration works: `barque config --show` displays settings

---

## 🎯 Recommended First Tests

### Test 1: Verify Installation (10 seconds)

```bash
source ~/.zshrc
barque --version
barque --help
```

### Test 2: Single Small File (30 seconds)

```bash
barque generate /Users/manu/Documents/LUXOR/docs/organization/research/MARS-MERCURIO-ANALYSIS-SUMMARY.md
open output/light/*.pdf
```

### Test 3: Automated Quick Test (1 minute)

```bash
cd /Users/manu/Documents/LUXOR/PROJECTS/BARQUE
./quick-test.sh
```

---

## 📖 Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Complete package documentation (400+ lines) |
| **QUICK-START.md** | Quick reference guide |
| **TEST-EXAMPLES.md** | Comprehensive test examples (THIS FILE) |
| **IMPLEMENTATION-COMPLETE.md** | Full implementation summary |
| **BARQUE-PROJECT-STATUS.md** | Project status and metrics |
| **test-barque.sh** | Comprehensive test script (7 tests) |
| **quick-test.sh** | Quick test script (3 tests) |

---

## 🎉 Summary

**BARQUE is production-ready and tested!**

- ✅ Alias configured in ~/.zshrc
- ✅ `--help` works for all commands
- ✅ Tested on real LUXOR documents
- ✅ 100% success rate on batch processing
- ✅ Mathematical formulas render correctly
- ✅ Both light and dark themes working
- ✅ Automated test scripts available

**Quick start:**
```bash
source ~/.zshrc
barque --help
./quick-test.sh
```

**For more details, see TEST-EXAMPLES.md** 📚
