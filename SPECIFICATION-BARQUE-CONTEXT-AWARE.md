# BARQUE: Context-Aware Document Orchestration Specification

**Status**: Feasible Architecture for Production Implementation
**Version**: 3.0 Vision (Build Path from 2.1.0)
**Timeline**: Phase 1 (Weeks 1-4 per productivity plan) + Phase 2 (Weeks 5-8, context-aware features)

---

## Vision Alignment

**BARQUE's Core Purpose**:
> "Generate once, consume everywhere — in the theme that suits your context"

**Current Limitation**: Assumes all documents are the same type (generic markdown → generic PDF)

**Vision Extension**:
> "Understand context. Transform once. Deliver everywhere — optimized for each consumption pattern"

### What This Means
- **Single source** (markdown file)
- **Multiple contexts** (research, report, presentation, email, web, print)
- **Smart defaults** (automatically optimize for context)
- **User control** (override defaults when needed)
- **Extensible** (add new contexts without core changes)

---

## The Problem BARQUE Solves (Today)

✅ Markdown → PDF (light/dark themes) → Email delivery
✅ One command, beautiful output
✅ Dual themes by default

❌ But:
- Treats all documents the same
- No awareness of use context
- Can't optimize for different audiences
- Can't reuse content across channels
- Limited to PDF output

---

## The Problem Context-Aware BARQUE Would Solve (Vision)

**Use Case 1: Research Paper**
```
Input: research.md (academic content, citations, formulas)
Context: "academic"
Output:
  - PDF (light + dark) for reading/printing
  - HTML with syntax highlighting for web
  - Plain text for RSS/feeds
  - EPUB for e-readers
  - Markdown + citations for other tools
```

**Use Case 2: Company Report**
```
Input: quarterly-report.md (business metrics, narrative, recommendations)
Context: "business-report"
Output:
  - PDF (branded light theme) for distribution
  - Web-optimized HTML for intranet
  - Email-friendly HTML (constrained width)
  - Slide deck outline for presentations
  - Plain text for accessibility
```

**Use Case 3: Technical Documentation**
```
Input: api-guide.md (endpoints, code examples, diagrams)
Context: "technical-docs"
Output:
  - PDF (dark theme default) for developers
  - HTML with TOC for web
  - Static site generator format
  - Markdown with metadata for Jekyll/Hugo
  - Interactive HTML for API explorer
```

**Use Case 4: Internal Communication**
```
Input: announcement.md (team update, decisions, next steps)
Context: "internal-memo"
Output:
  - Email-optimized HTML (short, scannable)
  - Slack-formatted summary
  - PDF for archiving
  - Plain text for terminals
  - Markdown for wikis
```

---

## Architecture: Context-Aware Pipeline

### Level 1: Input Analysis
```
barque generate research.md
  ↓
1. Detect context from:
   - File metadata (frontmatter: context: "academic")
   - Content patterns (citations, formulas, citations)
   - User explicit flag (--context academic)
   - Configuration defaults (barque.yaml)
```

### Level 2: Template Selection
```
context: "academic"
  ↓
Select templates:
  - PDF template (academic.html.j2)
  - Web template (academic-web.html.j2)
  - EPUB template (academic-epub.html.j2)
  - Metadata (academic.yaml)
```

### Level 3: Transformation
```
markdown
  ↓
Parse metadata + context
  ↓
Select renderer(s) based on context
  ↓
Apply context-specific CSS
  ↓
Generate output(s)
  ↓
[PDF(light), PDF(dark), HTML(web), EPUB, TXT]
```

### Level 4: Distribution
```
Outputs available for:
  - Email delivery (EmailSender)
  - File storage (S3, local)
  - Web publishing (Hugo, static site)
  - Feed distribution (RSS, feeds)
  - Archive (Markdown + metadata)
```

---

## Implementation: 4 Context Types (MVP)

### Context Type 1: "academic"
**For**: Research papers, theses, technical articles
**Optimizations**:
- Citation handling (bibtex, footnotes)
- Math formula prominence
- Code block syntax highlighting
- Bibliography formatting
- Academic metadata (author, institution, date)
- PDF: A4 paper size, formal margins

**Outputs**: PDF (light + dark), HTML, EPUB, Markdown
**Email**: Not optimized for email
**Time to build**: 2-3 days

---

### Context Type 2: "business-report"
**For**: Quarterly reports, executive summaries, business memos
**Optimizations**:
- Table emphasis (financial data)
- Executive summary extraction
- Branded header/footer
- Metrics highlighting
- Recommendations callouts
- PDF: Letter size, corporate branding

**Outputs**: PDF (branded), HTML (intranet), Email HTML, Markdown
**Email**: Optimized for email delivery (scannable, short sections)
**Time to build**: 2-3 days

---

### Context Type 3: "technical-docs"
**For**: API documentation, guides, tutorials, architecture
**Optimizations**:
- Code block prominence (larger, darker)
- Table of contents generation
- Diagram support (mermaid, plantuml)
- API endpoint highlighting
- Cross-reference linking
- Dark theme default (developers prefer)

**Outputs**: PDF (dark default), HTML (TOC), Markdown, Static site format
**Email**: Not optimized for email
**Time to build**: 3-4 days

---

### Context Type 4: "internal-memo"
**For**: Team announcements, memos, status updates
**Optimizations**:
- Short, scannable format
- Action items highlighting
- Decision callouts
- Email-friendly (constrained width, short paragraphs)
- Slack-formatted summary
- Plain text for accessibility

**Outputs**: Email HTML, Plain text, PDF, Markdown
**Email**: Fully optimized for email
**Time to build**: 2-3 days

---

### Context Type 5: "default" (Fallback)
**For**: Generic content, unknown context
**Optimizations**: Current BARQUE behavior
**Outputs**: PDF (light + dark only)
**Time to build**: 0 (already exists)

---

## The Spec: Implementation Path

### Phase 1: Foundation (Weeks 1-4) ✅
Per NEXT-LEVEL-PRODUCTIVITY-PLAN.md
- Testing framework
- Error handling
- Logging
- Security hardening
- Abstract PDF engine
- Abstract email providers

### Phase 2: Context Awareness (Weeks 5-8)

#### Week 5: Context Infrastructure
```bash
barque/
└── core/
    ├── contexts/
    │   ├── __init__.py
    │   ├── base.py          # Context base class
    │   ├── academic.py      # Academic context
    │   ├── business.py      # Business report context
    │   ├── technical.py     # Technical docs context
    │   └── memo.py          # Internal memo context
    ├── context_detector.py  # Auto-detect context
    └── config.py            # Updated for contexts
```

**Deliverable**: Context infrastructure + base class

---

#### Week 6: Template System
```bash
barque/
├── templates/
│   ├── academic/
│   │   ├── pdf.html.j2
│   │   ├── web.html.j2
│   │   ├── epub.html.j2
│   │   └── metadata.yaml
│   ├── business/
│   │   ├── pdf.html.j2
│   │   ├── email.html.j2
│   │   ├── web.html.j2
│   │   └── metadata.yaml
│   ├── technical/
│   │   ├── pdf.html.j2
│   │   ├── web.html.j2
│   │   └── metadata.yaml
│   ├── memo/
│   │   ├── email.html.j2
│   │   ├── text.j2
│   │   └── metadata.yaml
│   └── styles/
│       ├── academic.css
│       ├── business.css
│       ├── technical.css
│       └── memo.css
```

**Deliverable**: Templates for all 4 contexts

---

#### Week 7: Multi-Format Output
```python
# Current: PDFGenerator only
# New: MultiFormatGenerator

class OutputFormat(ABC):
    @abstractmethod
    async def render(self, html: str, context: Context) -> bytes:
        pass

class PDFOutput(OutputFormat):
    async def render(self, html: str, context: Context) -> bytes:
        # Existing PDF rendering
        pass

class HTMLOutput(OutputFormat):
    async def render(self, html: str, context: Context) -> bytes:
        # Return as-is, with context CSS
        pass

class EPUBOutput(OutputFormat):
    async def render(self, html: str, context: Context) -> bytes:
        # Convert HTML to EPUB format
        pass

class PlainTextOutput(OutputFormat):
    async def render(self, html: str, context: Context) -> str:
        # Convert HTML to readable plain text
        pass

class SlackOutput(OutputFormat):
    async def render(self, html: str, context: Context) -> str:
        # Format for Slack message
        pass

# Usage
generator = MultiFormatGenerator(config)
result = await generator.generate(
    input_file="research.md",
    context="academic",
    formats=["pdf", "html", "epub"]  # Requested outputs
)
# Returns: {"pdf": bytes, "html": bytes, "epub": bytes}
```

**Deliverable**: Multi-format output system

---

#### Week 8: Context-Aware Features
```python
# Context auto-detection
detector = ContextDetector()
context = await detector.detect("research.md")
# Returns: Context(type="academic", confidence=0.92)

# Context-aware generation
result = await generator.generate(
    input_file="research.md",
    # auto-detect if not specified
    formats=context.default_formats,  # ["pdf", "html", "epub"]
)

# Context metadata
context_metadata = {
    "academic": {
        "default_formats": ["pdf", "html", "epub"],
        "email_safe": False,
        "theme_default": "light",
        "optimize_for": ["reading", "archiving", "sharing"],
    },
    "memo": {
        "default_formats": ["email_html", "text", "pdf"],
        "email_safe": True,
        "theme_default": "light",
        "optimize_for": ["scanning", "email", "communication"],
    },
}
```

**Deliverable**: Context detection + auto-configuration

---

## Command Evolution

### Today (v2.1)
```bash
barque generate document.md --theme both
barque send document.md --to user@example.com
```

### Tomorrow (v3.0)
```bash
# Auto-detect context and generate appropriate formats
barque generate research.md
# Output: research-light.pdf, research-dark.pdf, research.html, research.epub

# Explicitly specify context
barque generate report.md --context business-report
# Output: report-branded.pdf, report-web.html, report-email.html

# Smart email based on context
barque send announcement.md --to team@company.com
# Auto-detects memo context → sends email-optimized HTML

# Batch with context awareness
barque batch research/ --context academic
# All .md files treated as academic papers → generates appropriate formats

# Context templates (for team standardization)
barque new paper --template academic-research
# Creates paper.md with academic frontmatter + structure
```

---

## Data Structures: Context Configuration

### Frontmatter (in markdown files)
```markdown
---
title: "Quantum Computing Overview"
author: "Dr. Smith"
date: 2025-01-15
context: "academic"
context_options:
  include_bibliography: true
  citation_style: "harvard"
  preferred_formats: ["pdf", "html", "epub"]
  email_safe: false
---

# Introduction
...
```

### Project Configuration (barque.yaml)
```yaml
# Default context for all documents
default_context: "academic"

# Context-specific settings
contexts:
  academic:
    formats: ["pdf", "html", "epub"]
    pdf_size: "a4"
    theme_default: "light"
    include_toc: true
    bibliography_style: "harvard"

  business-report:
    formats: ["pdf", "html", "email_html"]
    pdf_branding: "corporate"
    email_width: "600px"
    theme_default: "light"

  technical-docs:
    formats: ["pdf", "html"]
    theme_default: "dark"
    code_theme: "github-dark"
    include_toc: true

  internal-memo:
    formats: ["email_html", "text", "pdf"]
    email_friendly: true
    max_width: "600px"
    summary_length: "50-100 words"

# Global settings
output:
  organize_by_context: true  # output/academic/, output/business/, etc.
  preserve_source: true      # Keep original markdown
```

---

## Feature Matrix: What Context-Aware BARQUE Can Do

| Feature | Academic | Business | Technical | Memo | Generic |
|---------|----------|----------|-----------|------|---------|
| PDF generation | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dark theme | ✅ | ⚠️ | ✅ (default) | ✅ | ✅ |
| Email friendly | ❌ | ✅ | ❌ | ✅ (optimized) | ⚠️ |
| HTML output | ✅ | ✅ | ✅ | ✅ | ⚠️ |
| EPUB output | ✅ | ❌ | ❌ | ❌ | ❌ |
| Bibliography | ✅ | ❌ | ❌ | ❌ | ❌ |
| Branding support | ❌ | ✅ | ❌ | ❌ | ❌ |
| Code highlighting | ✅ | ⚠️ | ✅ | ❌ | ✅ |
| TOC generation | ✅ | ✅ | ✅ | ❌ | ⚠️ |
| Slack formatting | ❌ | ❌ | ❌ | ✅ | ❌ |

---

## Integration Points: Where Context Awareness Helps

### 1. Email Delivery
```python
# Current: Always send both PDFs
barque send document.md --to user@example.com

# Future: Smart delivery based on context
memo = ContextDetector().detect("announcement.md")
if memo.context_type == "memo":
    # Send email-optimized HTML directly
    send_email(
        to="team@company.com",
        html=render_output("email_html"),
        attachments=None  # No PDFs for memo
    )
elif memo.context_type == "academic":
    # Send PDFs (PDF is best format for academic)
    send_email(
        to="researcher@university.edu",
        html=render_output("email_intro"),
        attachments=["document-light.pdf", "document-dark.pdf"]
    )
```

### 2. Web Publishing
```python
# Publish to static site based on context
if context.type == "technical-docs":
    # Generate Hugo/Jekyll format
    generate_static_site_format(document)
    deploy_to_docs_site()

if context.type == "academic":
    # Generate EPUB + archive
    generate_ebook(document)
    archive_to_repository()
```

### 3. Batch Processing
```bash
# Process research papers differently from reports
barque batch papers/ --context academic
barque batch reports/ --context business-report

# Or auto-detect per file
barque batch mixed-docs/ --auto-context
# Detects each file's context independently
```

### 4. Team Templates
```bash
# Create new document with context-appropriate structure
barque new "q4-report" --template business-report
# Creates Q4 report with:
# - Executive summary section
# - Business context frontmatter
# - Metrics tables
# - Recommendations format
```

---

## Extensibility: Adding New Contexts

**Easy Case**: Add new context without modifying core
```python
# In barque/core/contexts/custom.py
from .base import Context

class CustomContext(Context):
    name = "custom"
    description = "Custom document context"

    default_formats = ["pdf", "html"]
    email_friendly = True
    theme_default = "light"

    def optimize_template(self, html: str) -> str:
        # Custom HTML optimization
        return optimized_html

# Register in config
contexts:
  custom:
    formats: ["pdf", "html"]
    css_file: "custom.css"
```

**Complex Case**: Add new output format
```python
# In barque/core/outputs/custom_format.py
class CustomFormatOutput(OutputFormat):
    name = "custom_format"

    async def render(self, html: str, context: Context) -> bytes:
        # Transform HTML to custom format
        return custom_format_bytes
```

---

## Why This Works

### Feasible
- ✅ Builds on production foundation (Phase 1)
- ✅ Incremental (one context at a time)
- ✅ No breaking changes to current users
- ✅ Uses established patterns (Jinja2 templates, plugin architecture)
- ✅ Estimated 4 weeks for MVP (4 contexts)

### Flexible
- ✅ Easy to add new contexts
- ✅ Easy to add new output formats
- ✅ Configuration-driven (no code changes)
- ✅ Supports user customization
- ✅ Detects context automatically

### Vision-Aligned
- ✅ "Generate once" (single markdown)
- ✅ "Consume everywhere" (multiple formats/contexts)
- ✅ "Theme that suits your context" (context-aware defaults)
- ✅ Beautiful output (context-optimized rendering)
- ✅ Automated (smart detection + generation)

### Realistic
- ✅ Proven template pattern (Jinja2)
- ✅ Existing plugin architecture in Phase 1
- ✅ No new dependencies required
- ✅ Backward compatible with 2.1.0 documents
- ✅ Can be adopted incrementally

---

## Success Metrics for Context-Aware BARQUE

### Technical
- [ ] 4 context types implemented and tested
- [ ] Auto-detection >90% accuracy
- [ ] Multi-format output working (PDF, HTML, EPUB, TXT)
- [ ] Context configuration via frontmatter and barque.yaml
- [ ] Extensibility tested with custom context

### User-Facing
- [ ] Single command generates appropriate outputs
- [ ] Email delivery optimized per context
- [ ] Team templates reduce setup time
- [ ] Documentation shows 5+ real-world workflows
- [ ] Community contexts can be added

### Production
- [ ] Backward compatible with 2.1.0
- [ ] No performance regression
- [ ] Context detection errors handled gracefully
- [ ] Fallback to "default" context always available

---

## Development Path: From 2.1.0 to 3.0

### Phase 1: Production Ready (Weeks 1-4)
- Testing, error handling, logging, security
- Abstract PDF engine, email providers, async foundation
- Result: Solid technical foundation

### Phase 2: Context Aware (Weeks 5-8)
- Context infrastructure + detection
- Templates for 4 contexts
- Multi-format output system
- Result: Flexible, context-aware orchestration

### Phase 3: Ecosystem (Weeks 9-12, optional)
- Web publishing integration (Hugo, Jekyll)
- RSS/feed distribution
- Webhook triggers
- Cloud storage integration
- Result: Complete document orchestration platform

---

## Vision Statement (Complete)

### Current (2.1.0)
> "Beautiful Automated Report and Query Universal Engine - Multi-modal document orchestration with dual-theme PDF generation"

### Future (3.0)
> "Beautiful Automated Report and Query Universal Engine - Context-aware document orchestration that transforms markdown once and optimizes for every consumption context: academic papers, business reports, technical documentation, internal communications, and beyond. Generate once. Consume everywhere. Beautiful always."

---

## Open Questions for Your Feedback

1. **Context Priority**: Which of the 4 contexts matters most to you? (Focus there first)
2. **Output Formats**: Beyond PDF/HTML/EPUB, what formats would add value?
3. **Detection**: Should context detection be automatic or user-explicit?
4. **Teams**: Should BARQUE support team-level context templates?
5. **Integration**: Where do you see BARQUE fitting in your workflow?

---

**Document Version**: 1.0 Specification
**Status**: Ready for refinement and feedback
**Next Step**: Prioritize which context to implement first in Phase 2

