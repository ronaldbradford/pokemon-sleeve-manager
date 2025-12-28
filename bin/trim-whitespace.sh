#!/bin/bash

# Trim trailing whitespace from source files
# Usage: ./bin/trim-whitespace.sh [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "🔍 Dry run mode - showing files with trailing whitespace"
    echo ""
fi

# File patterns to process
PATTERNS=(
    "*.py"
    "*.html"
    "*.css"
    "*.js"
    "*.json"
    "*.md"
    "*.sh"
    "*.yml"
    "*.yaml"
    "*.txt"
)

# Directories to exclude
EXCLUDES=(
    ".git"
    "venv"
    "__pycache__"
    "node_modules"
    ".pytest_cache"
    "*.pyc"
)

# Build find exclude arguments
EXCLUDE_ARGS=""
for exc in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS -path '*/$exc' -prune -o -path '*/$exc/*' -prune -o"
done

# Build find include arguments for file patterns
INCLUDE_ARGS=""
for i in "${!PATTERNS[@]}"; do
    if [[ $i -eq 0 ]]; then
        INCLUDE_ARGS="-name '${PATTERNS[$i]}'"
    else
        INCLUDE_ARGS="$INCLUDE_ARGS -o -name '${PATTERNS[$i]}'"
    fi
done

FILES_FOUND=0
FILES_MODIFIED=0

# Find and process files
while IFS= read -r file; do
    if [[ -f "$file" ]]; then
        # Check if file has trailing whitespace
        if grep -q '[[:space:]]$' "$file" 2>/dev/null; then
            FILES_FOUND=$((FILES_FOUND + 1))
            if [[ "$DRY_RUN" == true ]]; then
                echo "  📄 $file"
                # Show lines with trailing whitespace (first 5)
                grep -n '[[:space:]]$' "$file" | head -5 | while read -r line; do
                    echo "      Line $line"
                done
                COUNT=$(grep -c '[[:space:]]$' "$file")
                if [[ $COUNT -gt 5 ]]; then
                    echo "      ... and $((COUNT - 5)) more lines"
                fi
            else
                # Remove trailing whitespace (works on both macOS and Linux)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' 's/[[:space:]]*$//' "$file"
                else
                    sed -i 's/[[:space:]]*$//' "$file"
                fi
                FILES_MODIFIED=$((FILES_MODIFIED + 1))
                echo "  ✅ $file"
            fi
        fi
    fi
done < <(eval "find . $EXCLUDE_ARGS \( $INCLUDE_ARGS \) -type f -print 2>/dev/null")

echo ""
if [[ "$DRY_RUN" == true ]]; then
    echo "📊 Found $FILES_FOUND files with trailing whitespace"
    echo "   Run without --dry-run to fix them"
else
    if [[ $FILES_MODIFIED -gt 0 ]]; then
        echo "✨ Trimmed trailing whitespace from $FILES_MODIFIED files"
    else
        echo "✨ No files needed trimming"
    fi
fi

