#!/bin/bash
# Test BARQUE CLI with paper2agent markdown files
# This ensures the CLI works correctly before and after microservice addition

set -e

PAPER2AGENT_DIR="/Users/manu/Documents/LUXOR/PROJECTS/paper2agent"
TEST_OUTPUT_DIR="/tmp/barque-cli-tests"
BARQUE_BIN="/Users/manu/Documents/LUXOR/PROJECTS/BARQUE/venv/bin/barque"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "BARQUE CLI Test with paper2agent Files"
echo "=========================================="
echo ""

# Create test output directory
mkdir -p "$TEST_OUTPUT_DIR"
echo "📁 Test output directory: $TEST_OUTPUT_DIR"
echo ""

# Test cases - diverse markdown files from paper2agent
declare -a TEST_FILES=(
    "analysis/foundational/01_BACKPROP_AS_FUNCTOR_ANALYSIS.md"
    "analysis/foundational/04_CATEGORICAL_DEEP_LEARNING_ANALYSIS.md"
    "research/mars-analysis/dimension-1-category-theory.md"
    "CATEGORY_A_COMPLETE_GUIDE.md"
    "META_PROMPT_FOR_AGENT_GENERATION.md"
)

# Test counter
PASSED=0
FAILED=0

echo "🧪 Running CLI tests..."
echo ""

for test_file in "${TEST_FILES[@]}"; do
    FULL_PATH="$PAPER2AGENT_DIR/$test_file"
    FILENAME=$(basename "$test_file" .md)

    if [ ! -f "$FULL_PATH" ]; then
        echo -e "${RED}✗ SKIP${NC}: File not found: $test_file"
        continue
    fi

    echo "Testing: $test_file"

    # Test 1: Generate light theme only
    echo "  → Light theme..."
    if $BARQUE_BIN generate "$FULL_PATH" \
        --theme light \
        --output "$TEST_OUTPUT_DIR/test-$FILENAME" > /dev/null 2>&1; then

        # Check if PDF was created
        if [ -f "$TEST_OUTPUT_DIR/test-$FILENAME/light/$FILENAME-light.pdf" ]; then
            SIZE=$(du -h "$TEST_OUTPUT_DIR/test-$FILENAME/light/$FILENAME-light.pdf" | cut -f1)
            echo -e "     ${GREEN}✓${NC} Light PDF generated ($SIZE)"
            ((PASSED++))
        else
            echo -e "     ${RED}✗${NC} Light PDF not found"
            ((FAILED++))
        fi
    else
        echo -e "     ${RED}✗${NC} Generation failed"
        ((FAILED++))
    fi

    # Test 2: Generate both themes
    echo "  → Both themes..."
    if $BARQUE_BIN generate "$FULL_PATH" \
        --theme both \
        --output "$TEST_OUTPUT_DIR/test-$FILENAME-both" > /dev/null 2>&1; then

        LIGHT_EXISTS=false
        DARK_EXISTS=false

        if [ -f "$TEST_OUTPUT_DIR/test-$FILENAME-both/light/$FILENAME-light.pdf" ]; then
            LIGHT_EXISTS=true
        fi

        if [ -f "$TEST_OUTPUT_DIR/test-$FILENAME-both/dark/$FILENAME-dark.pdf" ]; then
            DARK_EXISTS=true
        fi

        if [ "$LIGHT_EXISTS" = true ] && [ "$DARK_EXISTS" = true ]; then
            LIGHT_SIZE=$(du -h "$TEST_OUTPUT_DIR/test-$FILENAME-both/light/$FILENAME-light.pdf" | cut -f1)
            DARK_SIZE=$(du -h "$TEST_OUTPUT_DIR/test-$FILENAME-both/dark/$FILENAME-dark.pdf" | cut -f1)
            echo -e "     ${GREEN}✓${NC} Both PDFs generated (Light: $LIGHT_SIZE, Dark: $DARK_SIZE)"
            ((PASSED++))
        else
            echo -e "     ${RED}✗${NC} Missing PDFs (Light: $LIGHT_EXISTS, Dark: $DARK_EXISTS)"
            ((FAILED++))
        fi
    else
        echo -e "     ${RED}✗${NC} Generation failed"
        ((FAILED++))
    fi

    echo ""
done

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "  Passed: $PASSED"
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    echo "  Passed: $PASSED"
    echo "  Failed: $FAILED"
fi
echo ""

# Show generated files
echo "📊 Generated PDFs:"
find "$TEST_OUTPUT_DIR" -name "*.pdf" -exec du -h {} \; | sort -h
echo ""

# Optional: Keep files for inspection
echo "💾 Test files saved in: $TEST_OUTPUT_DIR"
echo "   To clean up: rm -rf $TEST_OUTPUT_DIR"
echo ""

if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
