# BARQUE: Master Roadmap 2025

**Vision**: Transform BARQUE from working prototype (3.5/10 maturity) to flexible, production-grade document orchestration platform (7/10+)

**Timeline**: 8 weeks focused development
**Status**: Ready to execute (specifications complete, architecture planned)

---

## Executive Overview

### The Situation
- ✅ **Working MVP**: 90% keystroke reduction achieved, real users validating core value
- 🔴 **Critical Gaps**: Zero tests, no observability, security vulnerabilities
- 📈 **Next Level**: Context-aware orchestration enabling flexible content delivery

### The Vision
> Generate markdown once. Understand context automatically. Deliver optimized content to every channel: PDF, email, web, ebook, plain text, Slack — each perfectly formatted for its purpose.

### The Path

```
Week 1-4: PRODUCTION SAFETY
├─ Comprehensive testing
├─ Error handling & logging
├─ Security hardening
└─ Architectural foundation (abstract engines, async)
Result: 3.5/10 → 5/10 (Production-safe but basic)

Week 5-8: CONTEXT AWARENESS
├─ Auto-context detection
├─ Multi-format rendering
├─ Smart template system
└─ Team context templates
Result: 5/10 → 7/10 (Flexible, intelligent orchestration)

Week 9+: ECOSYSTEM (Optional)
├─ Web publishing integration
├─ RSS/Feed distribution
├─ Cloud storage
└─ Webhook triggers
Result: 7/10 → 8.5/10 (Platform-grade)
```

---

## Phase 1: Production Safety (Weeks 1-4)

**Goal**: Create solid foundation that passes production requirements

### Week 1: Testing Foundation

**Deliverables**:
- pytest infrastructure with fixtures
- 40+ unit tests (>80% coverage on core)
- Test helpers and mocks
- CI/CD integration ready

**Key Tests**:
```
- PDFGenerator.generate() → PDF bytes
- EmailSender.send() → delivery confirmation
- BarqueConfig loading → validation
- Theme processing → CSS application
- Metadata extraction → structured data
- Error paths → graceful degradation
```

**Success Criteria**:
- All tests pass
- Coverage >80% on core modules
- Test execution <30 seconds

---

### Week 2: Error Handling & Observability

**Deliverables**:
- Comprehensive error handling (95%+ of code paths)
- Structured logging (all key operations)
- Health check endpoint
- Metrics infrastructure

**Key Operations Logged**:
```
- barque.pdf.generation_started (input, theme)
- barque.pdf.generation_completed (duration, size)
- barque.pdf.generation_failed (error, context)
- barque.email.send_started (recipient, subject)
- barque.email.send_completed (provider, duration)
- barque.email.send_failed (error, retry_count)
```

**Success Criteria**:
- Zero silent failures
- 100% of errors logged
- Can answer "what happened?" via logs
- Health check working

---

### Week 3: Security Hardening

**Deliverables**:
- API key encryption
- Input validation for all files
- Subprocess security (timeouts, isolation)
- Security tests for vulnerability vectors

**Key Hardening**:
```
1. API Keys: Encrypt at rest, env var in transport
2. Filenames: Validate + sanitize (no command injection)
3. File Size: Enforce limits (prevent OOM)
4. Subprocess: Timeout + capture + check status
5. Markdown Content: Scan for dangerous patterns
```

**Success Criteria**:
- 0 critical security issues
- All validators working
- No hardcoded secrets
- Subprocess timeouts enforced

---

### Week 4: Architecture Foundation

**Deliverables**:
- PDFEngine abstraction (swap pandoc/weasyprint)
- EmailProvider abstraction (swap providers)
- Async/await core operations
- Concurrent request handling

**Key Abstractions**:
```python
# PDFEngine interface
class PDFEngine(ABC):
    async def render(html: str, theme: Theme) -> bytes

# EmailProvider interface
class EmailProvider(ABC):
    async def send(message: EmailMessage) -> bool

# Async operations
async def generate(file: Path) -> GenerationResult
async def send_email(message: EmailMessage) -> bool
```

**Success Criteria**:
- 10+ concurrent requests handled
- Can swap PDF engine in config
- Can add email provider without core changes
- No memory leaks under load

---

## Phase 2: Context Awareness (Weeks 5-8)

**Goal**: Enable flexible document orchestration for multiple use cases

### Week 5: Context Infrastructure

**Deliverables**:
- Context base class
- Context auto-detection
- Context configuration system
- 4 context implementations (academic, business, technical, memo)

**Context Types**:
```
Academic: Research papers, theses, articles
├─ Optimizes: Citations, formulas, TOC
├─ Default formats: PDF, HTML, EPUB
└─ Email-friendly: No

Business: Reports, executive summaries, memos
├─ Optimizes: Tables, metrics, branding
├─ Default formats: PDF, HTML, Email
└─ Email-friendly: Yes

Technical: API docs, guides, tutorials
├─ Optimizes: Code, diagrams, cross-refs
├─ Default formats: PDF, HTML
└─ Email-friendly: No

Memo: Announcements, status updates
├─ Optimizes: Scannable, action items
├─ Default formats: Email, Text, PDF
└─ Email-friendly: Yes (optimized)
```

**Success Criteria**:
- Auto-detection >90% accuracy
- Context config in frontmatter + barque.yaml
- Easy to add new contexts
- Fallback to "default" works

---

### Week 6: Template System

**Deliverables**:
- Jinja2 templates for all contexts
- Context-specific CSS
- Email template library
- Template validation

**Template Structure**:
```
barque/templates/
├── academic/
│   ├── pdf.html.j2
│   ├── web.html.j2
│   ├── epub.html.j2
│   └── academic.css
├── business/
│   ├── pdf.html.j2
│   ├── email.html.j2
│   ├── web.html.j2
│   └── business.css
├── technical/
│   ├── pdf.html.j2
│   ├── web.html.j2
│   └── technical.css
└── memo/
    ├── email.html.j2
    ├── text.j2
    └── memo.css
```

**Success Criteria**:
- All templates render correctly
- CSS applies per context
- Email templates pass validation
- ~95% code reuse via shared partials

---

### Week 7: Multi-Format Output

**Deliverables**:
- OutputFormat abstraction
- 5+ format implementations (PDF, HTML, EPUB, PlainText, Slack)
- Format selection based on context
- Format validation

**Output Formats**:
```
PDFOutput (PDF files, light + dark)
HTMLOutput (Static HTML with TOC)
EPUBOutput (E-reader format)
PlainTextOutput (Accessible, universal)
EmailHTMLOutput (Email-optimized)
SlackOutput (Slack message format)
```

**Success Criteria**:
- All formats working
- Can request specific formats
- Format selection per context
- Quality consistent across formats

---

### Week 8: Context-Aware Features

**Deliverables**:
- Smart email delivery (context determines format)
- Batch processing with context awareness
- Team context templates
- Context metadata system

**Features**:
```bash
# Auto-generate appropriate formats
barque generate research.md
# → research-light.pdf, research-dark.pdf, research.html, research.epub

# Context-aware email
barque send announcement.md --to team@company.com
# Detects memo context → sends email-optimized HTML

# Batch with context awareness
barque batch research/ --auto-context
# Processes each file with detected context

# Team templates
barque new paper --template academic-research
# Creates structured markdown with academic frontmatter
```

**Success Criteria**:
- Email delivery optimized per context
- Batch processing efficient
- Templates save setup time
- User experience seamless

---

## Phase 3: Ecosystem (Optional, Weeks 9-12)

**Goal**: Enable BARQUE in larger systems (web publishing, feeds, automation)

### Week 9-10: Web Publishing Integration

**Features**:
- Hugo/Jekyll format generation
- Static site generator support
- Automatic TOC and navigation
- Sitemap generation

---

### Week 11: Feed & Distribution

**Features**:
- RSS feed generation
- Email newsletter publishing
- Scheduled distribution
- Archive building

---

### Week 12: Cloud & Automation

**Features**:
- S3/Cloud storage integration
- Webhook triggers
- CI/CD integration
- GitHub Actions support

---

## Development Roadmap: Detailed Timeline

### Week 1: Testing
```
Mon-Tue: pytest setup + fixtures
         - Conftest.py configuration
         - Fixtures for common operations
         - Mocks for external dependencies

Wed:     Write core tests (20+ tests)
         - PDFGenerator tests
         - Config loading tests
         - Metadata extraction tests

Thu:     Write integration tests
         - End-to-end workflow
         - CLI command testing

Fri:     Coverage check + cleanup
         - Target: >80%
         - Document test patterns
```

### Week 2: Error Handling & Logging
```
Mon:     Add logging everywhere
         - Structured logging format
         - Log levels (DEBUG, INFO, WARNING, ERROR)

Tue-Wed: Error handling
         - try/except blocks
         - Graceful degradation
         - User-friendly messages

Thu-Fri: Observability
         - Health check endpoint
         - Metrics infrastructure
         - Log parsing examples
```

### Week 3: Security
```
Mon:     Key encryption
         - Cryptography integration
         - Env var fallback

Tue:     Input validation
         - File type validation
         - Size limits
         - Content scanning

Wed-Fri: Subprocess security
         - Timeout enforcement
         - Output capture
         - Status checking
         - Security tests
```

### Week 4: Architecture
```
Mon:     PDFEngine abstraction
         - Interface definition
         - PandocEngine refactor

Tue:     EmailProvider abstraction
         - Interface definition
         - Existing providers refactor

Wed-Fri: Async foundation
         - Async file operations
         - Async rendering
         - Concurrent handling
         - Integration tests
```

### Week 5: Context Infrastructure
```
Mon-Tue: Context base class
         - Abstract definition
         - Metadata structure
         - Validation

Wed-Thu: Context implementations
         - Academic context
         - Business context
         - Technical context
         - Memo context

Fri:     Auto-detection
         - Detection algorithms
         - Fallback logic
         - Configuration loading
```

### Week 6: Template System
```
Mon-Tue: Template structure
         - Academic templates
         - Business templates

Wed-Thu: CSS and styling
         - Context-specific CSS
         - Dark theme support
         - Email styling

Fri:     Testing + validation
         - Template rendering tests
         - CSS application tests
         - Email validation
```

### Week 7: Multi-Format Output
```
Mon:     OutputFormat abstraction
         - Interface definition
         - Format registry

Tue-Wed: Format implementations
         - HTML output
         - EPUB output
         - PlainText output
         - Slack output

Thu-Fri: Integration + testing
         - Format selection
         - Quality validation
         - Performance testing
```

### Week 8: Context Features
```
Mon-Tue: Smart email delivery
         - Context → format mapping
         - Email optimization

Wed:     Batch processing
         - Auto-context detection
         - Efficient processing

Thu:     Team templates
         - Template creation
         - Frontmatter generation

Fri:     Documentation + release
         - Feature documentation
         - v3.0.0-rc1 release
         - Migration guide
```

---

## Success Metrics by Phase

### Phase 1: Production Safety ✅

**Code Quality**:
- ✅ Test coverage: 0% → 80%+
- ✅ Error handling: 0.5% → 95%
- ✅ Logging coverage: 0% → 100%
- ✅ Security issues: 4 critical → 0 critical

**Operational**:
- ✅ Debugging capability: Impossible → Full visibility
- ✅ Error recovery: None → Graceful
- ✅ Production safety: Risky → Controlled

**Measurable**:
- ✅ All tests pass
- ✅ Coverage >80%
- ✅ 0 high-severity security issues
- ✅ All operations logged

---

### Phase 2: Context Awareness ✅

**Features**:
- ✅ Context detection: Manual only → Auto-detect + fallback
- ✅ Output formats: PDF only → 6+ formats
- ✅ Use cases: Generic → 4 specialized contexts
- ✅ Content optimization: None → Context-specific

**User Experience**:
- ✅ Commands: 3+ steps → Single command
- ✅ Setup time: 15+ minutes → <2 minutes
- ✅ Format selection: Manual → Automatic
- ✅ Team efficiency: Per-user → Standardized templates

**Extensibility**:
- ✅ New contexts: Code change → Config + templates
- ✅ New formats: Core modification → Plugin
- ✅ Custom CSS: Monolithic → Per-context

**Measurable**:
- ✅ Context detection >90% accurate
- ✅ 4 contexts fully implemented
- ✅ 6+ output formats working
- ✅ Team templates ready

---

## Success Criteria: Definition of Done

### Phase 1 Complete When:
- [ ] All unit tests written and passing (40+ tests)
- [ ] Coverage report shows >80% on core modules
- [ ] 0 high-severity security issues identified
- [ ] All error paths handled and logged
- [ ] Health check endpoint responding correctly
- [ ] PDFEngine abstraction working (can swap engines)
- [ ] Async core operations completed
- [ ] 10+ concurrent requests handled

### Phase 2 Complete When:
- [ ] 4 context types implemented and tested
- [ ] Context auto-detection >90% accurate
- [ ] 6 output formats implemented
- [ ] All templates rendering correctly
- [ ] Email delivery context-optimized
- [ ] Batch processing efficient
- [ ] Team templates working
- [ ] Documentation complete with real examples

---

## Risk Mitigation

### Phase 1 Risks

**Risk: Testing is slow/boring**
- Mitigation: Write 10 tests first, see coverage grow, momentum builds
- Alternative: Pair testing with error handling (both needed anyway)

**Risk: Phase 1 feels like moving backward**
- Mitigation: Remember: you're trading development speed for production safety
- Reality: Will refactor faster after tests exist

**Risk: Discovery of major architectural issues**
- Mitigation: Phase 1 is designed to find and fix them early
- Safety: Abstract engines/providers give flexibility for changes

### Phase 2 Risks

**Risk: Context detection too complex**
- Mitigation: Start simple (keywords + patterns), improve over time
- Fallback: Always default to "generic" context

**Risk: Too many templates to maintain**
- Mitigation: Maximum 4 contexts in MVP, use shared partials
- Scaling: Plugin architecture for community contexts later

**Risk: Multi-format output breaks something**
- Mitigation: Formats are isolated (PDFOutput, HTMLOutput, etc.)
- Safety: PDF always works (backward compatible)

---

## Resource Allocation

### Week 1-4: Safety (Full Attention Required)
- Testing: 50% of time
- Error handling: 25%
- Security: 15%
- Architecture: 10%

### Week 5-8: Context (Focus on Specification)
- Context infrastructure: 25%
- Templates: 25%
- Formats: 25%
- Features: 15%
- Testing: 10%

### Total Effort
- **Phase 1**: 144 hours (~4 weeks full-time)
- **Phase 2**: 120 hours (~4 weeks, slightly less intensive)
- **Total**: ~264 hours (~6.5 weeks full-time, or 8 weeks with buffers)

---

## Communication Plan

### During Development

**Weekly Updates** (Friday):
```
✅ What was completed
🚧 What's in progress
⚠️ What's blocked
📊 Metrics (coverage, test count, etc.)
```

**Monthly Milestones**:
```
End of Week 4: Production-safe system ready for testing
End of Week 8: Context-aware system ready for release
```

### Release Strategy

**Phase 1**: v2.2.0 (Production-safe)
- All tests passing
- Full logging/error handling
- Backward compatible
- No new features (internal improvements only)

**Phase 2**: v3.0.0 (Context-aware)
- New context system
- Multi-format support
- New commands/options
- Migration guide from 2.x

---

## What Stays the Same

### User-Facing (Zero Changes)
- ✅ CLI interface (still works)
- ✅ Dual-theme support (still default)
- ✅ Email delivery (still simple)
- ✅ Configuration (still pragmatic)

### User Sees (New Capabilities)
- ✨ Smart context detection
- ✨ Multiple output formats
- ✨ Context templates
- ✨ Better error messages

### Internal (Everything Changes)
- 🔧 Tests added (for safety)
- 🔧 Logging added (for visibility)
- 🔧 Error handling improved (for reliability)
- 🔧 Architecture refactored (for flexibility)

---

## The Vision Realized

### After Phase 1 Complete
> BARQUE is production-safe and maintainable. You can refactor without fear. You can debug in production. The foundation is solid.

### After Phase 2 Complete
> BARQUE understands context. Generate markdown once. It optimizes automatically for academic papers, business reports, technical documentation, internal memos. One markdown file → multiple perfect outputs. Beautiful always. Context-aware always.

---

## Starting Tomorrow

### Day 1: 2 Hours
```bash
# 1. Create test structure
mkdir -p tests/{unit,integration,fixtures}
touch tests/__init__.py tests/conftest.py

# 2. Write first test
# tests/unit/test_generator.py
def test_pdf_generation_basic(tmp_path):
    from barque.core.generator import PDFGenerator
    gen = PDFGenerator()
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test\nHello")
    result = gen.generate(md_file, theme="light")
    assert result.success
    assert result.files
    assert "light" in result.files[0]

# 3. Run it
pytest -v

# 4. Watch first test pass ✅
```

### Week 1: Priority
```
✓ Get test infrastructure working
✓ Write 10+ tests first (build momentum)
✓ See coverage grow
✓ Document test patterns
```

---

## Questions to Guide Decisions

### On Priorities
1. Which context matters most to you? (Focus there first)
2. Which output format would add most value?
3. Who is your first target user?

### On Scope
1. Do you want Phase 3 (ecosystem)? Or focus on Phase 1-2?
2. Should contexts be user-extensible in v3.0?
3. What's the minimum viable set of templates?

### On Success
1. How do you measure "successful"? (Coverage? User adoption? Flexibility?)
2. What would make BARQUE 10x more valuable to you?

---

## Next Steps

### This Week
- [ ] Review all three documents:
  - HONEST-GAP-ANALYSIS-2025.md (detailed gaps)
  - NEXT-LEVEL-PRODUCTIVITY-PLAN.md (4-week plan)
  - SPECIFICATION-BARQUE-CONTEXT-AWARE.md (context design)
- [ ] Provide feedback/questions
- [ ] Commit to Phase 1 timeline

### Next Week
- [ ] Start Phase 1 Week 1 (Testing)
- [ ] Create test structure
- [ ] Write first 10 tests
- [ ] Set up CI/CD for coverage

### Ongoing
- [ ] Weekly updates on progress
- [ ] Monthly roadmap refinement
- [ ] Community feedback integration

---

## Success Statement

**This is not just "refactoring for the sake of it."**

You're:
1. **Making BARQUE production-grade** (Phase 1)
2. **Making BARQUE flexible** (Phase 2)
3. **Making BARQUE extraordinary** (entire arc)

The work is real. The payoff is significant. The path is clear.

---

**Document Version**: 1.0 (Master Roadmap)
**Generated**: November 18, 2025
**Status**: Ready to execute
**Confidence**: High (based on real analysis + proven patterns)

**Next Step**: Start tomorrow with test structure setup. Everything else flows from there.
