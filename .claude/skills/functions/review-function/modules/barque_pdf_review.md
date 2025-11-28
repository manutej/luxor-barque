# BARQUE PDF Review Module

**Type**: Project-specific extension module
**Parent**: `~/.claude/skills/functions/review-function/`
**Purpose**: Review PDF generation queue and research document status

---

## Why Project-Specific?

BARQUE is a dual-theme PDF generation system for research documentation. This review logic is:
- Unique to BARQUE's PDF workflow
- Not applicable to other projects
- Tightly coupled to BARQUE's directory structure

**Decision**: Implement as project-level extension, not global skill.

---

## Module Specification

### Purpose

Assess the health and status of BARQUE's PDF generation system:
- PDFs pending generation
- Recent PDF outputs
- Research document readiness
- Theme generation status (light/dark)

### Required Tools

- File system access (Glob, Read)
- BARQUE directory structure knowledge
- PDF metadata extraction

### Queries

1. **Pending PDFs**: Count markdown files without corresponding PDFs
2. **Recent Outputs**: List PDFs generated in last 24h
3. **Document Health**: Check markdown files for completeness
4. **Theme Status**: Verify both light/dark themes generated

---

## Implementation

### Query 1: Pending PDF Generation

```javascript
async function reviewPendingPDFs() {
    const markdownFiles = await glob("PROJECTS/BARQUE/docs/**/*.md");
    const pdfFiles = await glob("PROJECTS/BARQUE/exports-pdf/**/*.pdf");

    const pending = markdownFiles.filter(md => {
        const baseName = path.basename(md, '.md');
        const pdfLight = pdfFiles.find(pdf => pdf.includes(`${baseName}-light.pdf`));
        const pdfDark = pdfFiles.find(pdf => pdf.includes(`${baseName}-dark.pdf`));
        return !pdfLight || !pdfDark;
    });

    return {
        total_markdown: markdownFiles.length,
        total_pdfs: pdfFiles.length / 2,  // Divided by 2 (light + dark)
        pending: pending.length,
        pending_files: pending.map(p => path.basename(p))
    };
}
```

### Query 2: Recent PDF Outputs

```javascript
async function reviewRecentPDFs() {
    const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
    const pdfFiles = await glob("PROJECTS/BARQUE/exports-pdf/**/*.pdf");

    const recentPDFs = await Promise.all(
        pdfFiles.map(async pdf => {
            const stats = await fs.stat(pdf);
            return {
                file: path.basename(pdf),
                created: stats.birthtime,
                size: stats.size
            };
        })
    );

    const todaysPDFs = recentPDFs.filter(pdf => pdf.created > oneDayAgo);

    return {
        generated_today: todaysPDFs.length / 2,  // light + dark
        total_size_mb: todaysPDFs.reduce((sum, pdf) => sum + pdf.size, 0) / 1024 / 1024,
        files: todaysPDFs.map(p => p.file)
    };
}
```

### Query 3: Document Health

```javascript
async function reviewDocumentHealth() {
    const markdownFiles = await glob("PROJECTS/BARQUE/docs/**/*.md");

    const health = await Promise.all(
        markdownFiles.map(async file => {
            const content = await fs.readFile(file, 'utf-8');
            const wordCount = content.split(/\s+/).length;
            const hasTitle = content.includes('# ');
            const hasSections = (content.match(/^## /gm) || []).length;

            return {
                file: path.basename(file),
                words: wordCount,
                complete: wordCount > 500 && hasTitle && hasSections > 2,
                warnings: [
                    wordCount < 500 ? "Low word count" : null,
                    !hasTitle ? "Missing title" : null,
                    hasSections < 2 ? "Few sections" : null
                ].filter(Boolean)
            };
        })
    );

    return {
        total_docs: health.length,
        complete: health.filter(h => h.complete).length,
        incomplete: health.filter(h => !h.complete).length,
        warnings: health.filter(h => h.warnings.length > 0)
    };
}
```

### Query 4: Theme Generation Status

```javascript
async function reviewThemeStatus() {
    const pdfFiles = await glob("PROJECTS/BARQUE/exports-pdf/**/*.pdf");

    const themes = {
        light: pdfFiles.filter(f => f.includes('-light.pdf')),
        dark: pdfFiles.filter(f => f.includes('-dark.pdf'))
    };

    const mismatches = [];
    themes.light.forEach(lightPDF => {
        const baseName = path.basename(lightPDF).replace('-light.pdf', '');
        const darkExists = themes.dark.some(d => d.includes(`${baseName}-dark.pdf`));
        if (!darkExists) {
            mismatches.push({ file: baseName, missing: 'dark' });
        }
    });

    themes.dark.forEach(darkPDF => {
        const baseName = path.basename(darkPDF).replace('-dark.pdf', '');
        const lightExists = themes.light.some(l => l.includes(`${baseName}-light.pdf`));
        if (!lightExists) {
            mismatches.push({ file: baseName, missing: 'light' });
        }
    });

    return {
        light_count: themes.light.length,
        dark_count: themes.dark.length,
        balanced: mismatches.length === 0,
        mismatches: mismatches
    };
}
```

---

## Output Structure

```json
{
  "pdf_queue": {
    "total_markdown": 15,
    "total_pdfs": 12,
    "pending": 3,
    "pending_files": ["research-notes.md", "new-paper.md", "draft.md"]
  },
  "recent_activity": {
    "generated_today": 2,
    "total_size_mb": 8.4,
    "files": ["consciousness-light.pdf", "consciousness-dark.pdf"]
  },
  "document_health": {
    "total_docs": 15,
    "complete": 12,
    "incomplete": 3,
    "warnings": [
      {"file": "draft.md", "warnings": ["Low word count", "Few sections"]}
    ]
  },
  "theme_status": {
    "light_count": 12,
    "dark_count": 12,
    "balanced": true,
    "mismatches": []
  },
  "insights": [
    "2 PDFs generated today (8.4 MB)",
    "3 documents pending PDF generation",
    "Theme balance: ✓ All PDFs have both light/dark versions"
  ]
}
```

---

## Integration with Global review-function

This module is **automatically discovered** when /daily runs from BARQUE project:

```
User in BARQUE: /daily

1. Load global review-function
2. Discover global modules:
   - linear_review.md
   - git_review.md
   - project_review.md
3. Discover BARQUE modules:
   - barque_pdf_review.md  ← THIS MODULE
4. Execute all modules in parallel
5. Compose results
```

**Result**: BARQUE /daily includes PDF status!

---

## Output in /daily

```markdown
🌅 Daily Review - November 5, 2025

📊 Quick Stats
├─ 3 active projects
├─ 5 Linear issues (2 in progress)
├─ 7 commits today
├─ 2 PRs awaiting review
└─ 12 PDFs (2 generated today, 3 pending)  ← BARQUE-specific!

📋 Active Work

[... standard sections ...]

📚 BARQUE PDF Status                        ← BARQUE-specific section!
├─ Generated today: 2 PDFs (8.4 MB)
├─ Pending generation: 3 documents
│   ├─ research-notes.md
│   ├─ new-paper.md
│   └─ draft.md
└─ Theme balance: ✓ All PDFs dual-themed

💡 Insights
- High PDF velocity: 2 generated today vs 1.2 avg
- draft.md needs attention: low word count
- Theme system healthy: all PDFs have light+dark
```

---

## Configuration

BARQUE can configure this module via `.claude/settings.json`:

```json
{
  "review-function": {
    "barque_pdf_review": {
      "pending_threshold": 5,
      "recent_hours": 24,
      "health_min_words": 500,
      "warn_if_pending": true
    }
  }
}
```

---

## Testing

### Test 1: Module Discovery

```bash
cd LUXOR/PROJECTS/BARQUE
claude-code "/daily --debug"

Expected:
  Loaded modules:
    - linear_review.md (global)
    - git_review.md (global)
    - project_review.md (global)
    - barque_pdf_review.md (project)  ✓
```

### Test 2: PDF Detection

```bash
# Create test scenario
touch PROJECTS/BARQUE/docs/test.md
# Don't create PDF

claude-code "/daily"

Expected output includes:
  "Pending generation: test.md"
```

### Test 3: Theme Mismatch

```bash
# Create only light PDF
touch PROJECTS/BARQUE/exports-pdf/test-light.pdf

claude-code "/daily"

Expected warning:
  "Theme mismatch: test.md missing dark version"
```

---

## Maintenance

### When to Update

- BARQUE changes PDF directory structure
- New PDF metadata fields added
- Theme system expanded (e.g., high-contrast theme)

### What NOT to Change

- Don't make this global (other projects don't use BARQUE PDFs)
- Don't couple to specific PDF content (keep generic to structure)

---

## Future Enhancements

### Short Term

- PDF quality metrics (file size anomalies)
- Generation time tracking (slow PDFs)
- Error log integration (failed generations)

### Medium Term

- AI-powered PDF content analysis
- Automatic regeneration suggestions
- Cross-document consistency checks

### Long Term

- Integration with BARQUE workflow automation
- Predictive generation (suggest docs needing updates)
- Team collaboration metrics (who's generating PDFs)

---

## Conclusion

This module demonstrates **project-level skill extension**:
- ✅ Extends global review-function
- ✅ BARQUE-specific logic
- ✅ Auto-discovered and integrated
- ✅ Doesn't pollute global skills

**Proof**: Function-first architecture enables clean project customization while maintaining core function stability.

---

## References

- Global review-function: `~/.claude/skills/functions/review-function/`
- BARQUE project: `LUXOR/PROJECTS/BARQUE/`
- Skill Inheritance Model: `LUXOR/docs/SKILL-INHERITANCE-MODEL.md`

---

**Status**: Specification complete
**Next**: Implement actual PDF scanning logic
**Integration**: Auto-loads when /daily runs from BARQUE
