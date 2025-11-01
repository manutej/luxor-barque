#!/bin/bash

##############################################################################
# BARQUE Test Suite - Comprehensive Examples
# Tests BARQUE with recently created LUXOR documentation
##############################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BARQUE_DIR="/Users/manu/Documents/LUXOR/PROJECTS/BARQUE"
LUXOR_DOCS="/Users/manu/Documents/LUXOR/docs"
OUTPUT_DIR="$BARQUE_DIR/test-outputs"

# Test files (recently created, varying sizes)
TEST_FILES=(
    "$LUXOR_DOCS/CATEGORY_A_COMPLETE_GUIDE.md"                                    # 16KB - Category theory guide
    "$LUXOR_DOCS/MARS_MERCURIO_FRAMEWORK.md"                                      # 33KB - MARS framework
    "$LUXOR_DOCS/hekat-dsl/CATEGORICAL_META_PROMPTING_SYNTHESIS.md"              # 44KB - Meta prompting synthesis
    "$LUXOR_DOCS/organization/research/MARS-MERCURIO-ANALYSIS-SUMMARY.md"        # 13KB - Analysis summary
)

# Activate virtual environment
cd "$BARQUE_DIR"
source venv/bin/activate

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          BARQUE Test Suite - Comprehensive Examples          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

##############################################################################
# Test 1: Single File - Light Theme Only
##############################################################################

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 1: Single File Generation (Light Theme)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "File: CATEGORY_A_COMPLETE_GUIDE.md"
echo "Theme: Light only"
echo ""

barque generate "$LUXOR_DOCS/CATEGORY_A_COMPLETE_GUIDE.md" \
    --theme light \
    --output "$OUTPUT_DIR/test1-single-light"

echo ""
echo -e "${YELLOW}✓ Output: $OUTPUT_DIR/test1-single-light/light/${NC}"
echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test 2: Single File - Dark Theme Only
##############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 2: Single File Generation (Dark Theme)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "File: MARS_MERCURIO_FRAMEWORK.md"
echo "Theme: Dark only"
echo ""

barque generate "$LUXOR_DOCS/MARS_MERCURIO_FRAMEWORK.md" \
    --theme dark \
    --output "$OUTPUT_DIR/test2-single-dark"

echo ""
echo -e "${YELLOW}✓ Output: $OUTPUT_DIR/test2-single-dark/dark/${NC}"
echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test 3: Single File - Both Themes (Default)
##############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 3: Single File Generation (Both Themes)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "File: CATEGORICAL_META_PROMPTING_SYNTHESIS.md (44KB - Large file)"
echo "Theme: Both (default)"
echo ""

barque generate "$LUXOR_DOCS/hekat-dsl/CATEGORICAL_META_PROMPTING_SYNTHESIS.md" \
    --theme both \
    --output "$OUTPUT_DIR/test3-single-both"

echo ""
echo -e "${YELLOW}✓ Output: $OUTPUT_DIR/test3-single-both/light/ and dark/${NC}"
echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test 4: Batch Processing - Small Set
##############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 4: Batch Processing (Small Set - MARS docs)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Directory: docs/mars/"
echo "Workers: 2"
echo "Theme: Both"
echo ""

barque batch "$LUXOR_DOCS/mars" \
    --workers 2 \
    --theme both \
    --output "$OUTPUT_DIR/test4-batch-mars"

echo ""
echo -e "${YELLOW}✓ Output: $OUTPUT_DIR/test4-batch-mars/${NC}"
echo -e "${YELLOW}✓ Index: $OUTPUT_DIR/test4-batch-mars/INDEX.md${NC}"
echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test 5: Batch Processing - HEKAT DSL Research
##############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 5: Batch Processing (HEKAT DSL Research)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Directory: docs/hekat-dsl/research/"
echo "Workers: 4"
echo "Theme: Both"
echo ""

barque batch "$LUXOR_DOCS/hekat-dsl/research" \
    --workers 4 \
    --theme both \
    --output "$OUTPUT_DIR/test5-batch-hekat"

echo ""
echo -e "${YELLOW}✓ Output: $OUTPUT_DIR/test5-batch-hekat/${NC}"
echo -e "${YELLOW}✓ Index: $OUTPUT_DIR/test5-batch-hekat/INDEX.md${NC}"
echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test 6: Batch Processing - Organization Docs
##############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 6: Batch Processing (Organization Documentation)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Directory: docs/organization/"
echo "Workers: 4"
echo "Theme: Light only (for printing)"
echo ""

barque batch "$LUXOR_DOCS/organization" \
    --workers 4 \
    --theme light \
    --output "$OUTPUT_DIR/test6-batch-org"

echo ""
echo -e "${YELLOW}✓ Output: $OUTPUT_DIR/test6-batch-org/${NC}"
echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test 7: Configuration Management
##############################################################################

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Test 7: Configuration Management${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo "Current configuration:"
barque config --show

echo ""
echo "Validating configuration:"
barque config --validate

echo ""
read -p "Press Enter to continue..."

##############################################################################
# Test Summary
##############################################################################

echo ""
echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                       Test Summary                            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "All tests completed! Generated PDFs in:"
echo ""
echo "Test 1: $OUTPUT_DIR/test1-single-light/"
echo "Test 2: $OUTPUT_DIR/test2-single-dark/"
echo "Test 3: $OUTPUT_DIR/test3-single-both/"
echo "Test 4: $OUTPUT_DIR/test4-batch-mars/"
echo "Test 5: $OUTPUT_DIR/test5-batch-hekat/"
echo "Test 6: $OUTPUT_DIR/test6-batch-org/"
echo ""

# Count generated PDFs
LIGHT_COUNT=$(find "$OUTPUT_DIR" -name "*-light.pdf" 2>/dev/null | wc -l)
DARK_COUNT=$(find "$OUTPUT_DIR" -name "*-dark.pdf" 2>/dev/null | wc -l)
TOTAL_COUNT=$((LIGHT_COUNT + DARK_COUNT))

echo "Statistics:"
echo "  Light PDFs: $LIGHT_COUNT"
echo "  Dark PDFs:  $DARK_COUNT"
echo "  Total PDFs: $TOTAL_COUNT"
echo ""

# Show disk usage
DU_SIZE=$(du -sh "$OUTPUT_DIR" 2>/dev/null | awk '{print $1}')
echo "  Total Size: $DU_SIZE"
echo ""

echo -e "${GREEN}✅ All tests passed!${NC}"
echo ""
echo "To view the PDFs, run:"
echo "  open $OUTPUT_DIR/test3-single-both/light/*.pdf"
echo "  open $OUTPUT_DIR/test3-single-both/dark/*.pdf"
echo ""
