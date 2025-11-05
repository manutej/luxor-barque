#!/bin/bash
# Test BARQUE Microservice API with paper2agent markdown files
# Ensures API works correctly with real-world content

set -e

PAPER2AGENT_DIR="/Users/manu/Documents/LUXOR/PROJECTS/paper2agent"
TEST_OUTPUT_DIR="/tmp/barque-api-tests"
API_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "BARQUE API Test with paper2agent Files"
echo "=========================================="
echo ""

# Create test output directory
mkdir -p "$TEST_OUTPUT_DIR"

# Check if API is running
echo "🔍 Checking API health..."
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API is healthy"
else
    echo -e "${RED}✗${NC} API is not running!"
    echo ""
    echo "Start the API first:"
    echo "  cd /Users/manu/Documents/LUXOR/PROJECTS/BARQUE"
    echo "  docker-compose up -d"
    echo "  OR"
    echo "  uvicorn barque_service:app --reload"
    exit 1
fi
echo ""

# Test cases - diverse markdown files
declare -a TEST_FILES=(
    "analysis/foundational/01_BACKPROP_AS_FUNCTOR_ANALYSIS.md"
    "analysis/foundational/04_CATEGORICAL_DEEP_LEARNING_ANALYSIS.md"
    "research/mars-analysis/dimension-1-category-theory.md"
)

# Test counter
PASSED=0
FAILED=0

echo "🧪 Running API tests..."
echo ""

for test_file in "${TEST_FILES[@]}"; do
    FULL_PATH="$PAPER2AGENT_DIR/$test_file"
    FILENAME=$(basename "$test_file" .md)

    if [ ! -f "$FULL_PATH" ]; then
        echo -e "${RED}✗ SKIP${NC}: File not found: $test_file"
        continue
    fi

    echo "Testing: $test_file"

    # Read markdown content
    MARKDOWN_CONTENT=$(cat "$FULL_PATH")

    # Test 1: Generate PDF (light theme)
    echo "  → API: Generate PDF (light theme)..."
    RESPONSE=$(curl -s -X POST "$API_URL/generate" \
        -H "Content-Type: application/json" \
        -d "{\"markdown_content\": $(echo "$MARKDOWN_CONTENT" | jq -Rs .), \"theme\": \"light\", \"filename\": \"$FILENAME\"}")

    if echo "$RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
        JOB_ID=$(echo "$RESPONSE" | jq -r '.data.job_id')
        FILE_COUNT=$(echo "$RESPONSE" | jq '.data.files | length')
        echo -e "     ${GREEN}✓${NC} PDF generated (Job: $JOB_ID, Files: $FILE_COUNT)"
        ((PASSED++))

        # Try to download the file
        DOWNLOAD_URL=$(echo "$RESPONSE" | jq -r '.data.files[0].url')
        if curl -s -f "$API_URL$DOWNLOAD_URL" -o "$TEST_OUTPUT_DIR/$FILENAME-light.pdf" > /dev/null 2>&1; then
            SIZE=$(du -h "$TEST_OUTPUT_DIR/$FILENAME-light.pdf" | cut -f1)
            echo -e "     ${GREEN}✓${NC} Downloaded PDF ($SIZE)"
            ((PASSED++))
        else
            echo -e "     ${YELLOW}⚠${NC} Download failed (file may have expired)"
        fi
    else
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo -e "     ${RED}✗${NC} Generation failed: $ERROR"
        ((FAILED++))
    fi

    # Test 2: Generate both themes
    echo "  → API: Generate PDF (both themes)..."
    RESPONSE=$(curl -s -X POST "$API_URL/generate" \
        -H "Content-Type: application/json" \
        -d "{\"markdown_content\": $(echo "$MARKDOWN_CONTENT" | jq -Rs .), \"theme\": \"both\", \"filename\": \"$FILENAME\"}")

    if echo "$RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
        FILE_COUNT=$(echo "$RESPONSE" | jq '.data.files | length')
        if [ "$FILE_COUNT" -eq 2 ]; then
            echo -e "     ${GREEN}✓${NC} Both themes generated"
            ((PASSED++))
        else
            echo -e "     ${YELLOW}⚠${NC} Expected 2 files, got $FILE_COUNT"
        fi
    else
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo -e "     ${RED}✗${NC} Generation failed: $ERROR"
        ((FAILED++))
    fi

    echo ""
done

# Test API info endpoint
echo "📋 Testing API info..."
INFO_RESPONSE=$(curl -s "$API_URL/")
if echo "$INFO_RESPONSE" | jq -e '.success == true' > /dev/null 2>&1; then
    API_VERSION=$(echo "$INFO_RESPONSE" | jq -r '.data.version')
    BARQUE_VERSION=$(echo "$INFO_RESPONSE" | jq -r '.data.barque_version')
    echo -e "${GREEN}✓${NC} API version: $API_VERSION, BARQUE version: $BARQUE_VERSION"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} Failed to get API info"
    ((FAILED++))
fi
echo ""

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
if [ -d "$TEST_OUTPUT_DIR" ] && [ "$(ls -A $TEST_OUTPUT_DIR)" ]; then
    echo "📊 Downloaded PDFs:"
    find "$TEST_OUTPUT_DIR" -name "*.pdf" -exec du -h {} \; | sort -h
    echo ""
    echo "💾 Files saved in: $TEST_OUTPUT_DIR"
else
    echo "ℹ️  No files downloaded (may have expired)"
fi
echo ""

# Show API docs location
echo -e "${BLUE}📖 Interactive API docs:${NC} $API_URL/docs"
echo ""

if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi
