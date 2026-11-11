#!/usr/bin/env bash
# package.sh - Build distribution bundles for ultima-graph. Works from any cwd.
# Output: <repo>/dist/ultima-graph.{tar.gz,zip,skill} + checksums.sha256
set -euo pipefail

SKILL_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_NAME="$(basename "$SKILL_PATH")"
REPO_ROOT="$(dirname "$SKILL_PATH")"
OUTPUT_DIR="$REPO_ROOT/dist"
EXCLUDES=(--exclude='.DS_Store' --exclude='__pycache__' --exclude='*.pyc' \
          --exclude='.ultima' --exclude='.codegraph' --exclude='graphify-out')

echo "Building ${SKILL_NAME} bundles from ${SKILL_PATH}..."
mkdir -p "$OUTPUT_DIR"
rm -f "$OUTPUT_DIR/${SKILL_NAME}".{tar.gz,zip,skill} "$OUTPUT_DIR/checksums.sha256"

# Quick self-test before shipping
python3 "$SKILL_PATH/scripts/verify_citations.py" --canary >/dev/null
bash -n "$SKILL_PATH/scripts/detect_tools.sh" "$SKILL_PATH/scripts/update.sh"

# tarball contains the top-level <skill>/ folder (extract into a skills dir)
tar -czf "$OUTPUT_DIR/${SKILL_NAME}.tar.gz" "${EXCLUDES[@]}" -C "$REPO_ROOT" "$SKILL_NAME"

# zip / .skill also contain the top-level folder, matching the tarball layout
(cd "$REPO_ROOT" && zip -r -q "$OUTPUT_DIR/${SKILL_NAME}.zip" "$SKILL_NAME" \
    -x '*.DS_Store' '*__pycache__*' '*.pyc' '*/.ultima/*' '*/.codegraph/*' '*/graphify-out/*')
cp "$OUTPUT_DIR/${SKILL_NAME}.zip" "$OUTPUT_DIR/${SKILL_NAME}.skill"

(cd "$OUTPUT_DIR" && shasum -a 256 "${SKILL_NAME}".tar.gz "${SKILL_NAME}".zip "${SKILL_NAME}".skill > checksums.sha256)
ls -lh "$OUTPUT_DIR"
cat "$OUTPUT_DIR/checksums.sha256"
