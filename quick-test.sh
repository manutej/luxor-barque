#!/bin/bash

##############################################################################
# BARQUE Quick Test - Fast Verification
# Tests BARQUE with 3 key examples
##############################################################################

set -e

# Setup
BARQUE_DIR="/Users/manu/Documents/LUXOR/PROJECTS/BARQUE"
LUXOR_DOCS="/Users/manu/Documents/LUXOR/docs"
OUTPUT="$BARQUE_DIR/quick-test-output"

cd "$BARQUE_DIR"
source venv/bin/activate

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              BARQUE Quick Test (3 Examples)                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

##############################################################################
# Example 1: Single File - Both Themes
##############################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Example 1: Single File (Both Themes)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

barque generate "$LUXOR_DOCS/CATEGORY_A_COMPLETE_GUIDE.md" \
    --output "$OUTPUT/example1"

echo ""

##############################################################################
# Example 2: Batch Processing - MARS docs
##############################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Example 2: Batch Processing (MARS Documentation)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

barque batch "$LUXOR_DOCS/mars" \
    --workers 2 \
    --output "$OUTPUT/example2"

echo ""

##############################################################################
# Example 3: Large File - HEKAT Synthesis
##############################################################################

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Example 3: Large File (44KB - Meta Prompting Synthesis)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

barque generate "$LUXOR_DOCS/hekat-dsl/CATEGORICAL_META_PROMPTING_SYNTHESIS.md" \
    --output "$OUTPUT/example3"

echo ""

##############################################################################
# Summary
##############################################################################

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    Quick Test Complete!                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Count PDFs
TOTAL=$(find "$OUTPUT" -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
SIZE=$(du -sh "$OUTPUT" 2>/dev/null | awk '{print $1}')

echo "Results:"
echo "  ✓ Generated: $TOTAL PDFs"
echo "  ✓ Total size: $SIZE"
echo "  ✓ Output: $OUTPUT/"
echo ""

echo "View PDFs:"
echo "  Example 1: open $OUTPUT/example1/light/*.pdf"
echo "  Example 2: open $OUTPUT/example2/INDEX.md"
echo "  Example 3: open $OUTPUT/example3/dark/*.pdf"
echo ""
