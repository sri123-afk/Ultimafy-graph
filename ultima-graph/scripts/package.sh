#!/usr/bin/env bash
# package.sh - Build distribution packages for ultima-graph
set -euo pipefail

SKILL_DIR="ultima-graph"
OUTPUT_DIR="dist"

echo "Building distribution packages for Ultima-Graph..."

# Clean temporary files
find "${SKILL_DIR}" -name ".DS_Store" -delete 2>/dev/null || true
find "${SKILL_DIR}" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

mkdir -p "${OUTPUT_DIR}"

# Build tarball
tar -czf "${OUTPUT_DIR}/ultima-graph.tar.gz" "${SKILL_DIR}"

# Build zip archive
(cd "${SKILL_DIR}" && zip -r -q "../${OUTPUT_DIR}/ultima-graph.zip" .)

# Build .skill bundle (zip copy)
cp "${OUTPUT_DIR}/ultima-graph.zip" "${OUTPUT_DIR}/ultima-graph.skill"

# Calculate SHA-256 checksums
(cd "${OUTPUT_DIR}" && shasum -a 256 ultima-graph.* > checksums.sha256)

echo "Packages generated in ${OUTPUT_DIR}/:"
ls -lh "${OUTPUT_DIR}"
cat "${OUTPUT_DIR}/checksums.sha256"
