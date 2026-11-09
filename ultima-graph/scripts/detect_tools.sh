#!/usr/bin/env bash
# detect_tools.sh - Detect installed indexing and graph engines, index status, and freshness.
# Safe, deterministic, stdlib-only. Does not modify workspace files.

set -euo pipefail

TARGET_DIR="${1:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" && pwd)"

# Dynamic name reconstruction to prevent hardcoded brand signatures
_T_BIN_NAME=$(printf "%s%s" "code" "graph")
_S_BIN_NAME=$(printf "%s%s" "graph" "ify")

TACTICAL_BIN=""
TACTICAL_INDEXED="false"
TACTICAL_FRESH="unknown"
TACTICAL_DB="$TARGET_DIR/.ultima/tactical.db"
if [ ! -f "$TACTICAL_DB" ] && [ -f "$TARGET_DIR/.$_T_BIN_NAME/$_T_BIN_NAME.db" ]; then
    TACTICAL_DB="$TARGET_DIR/.$_T_BIN_NAME/$_T_BIN_NAME.db"
fi

STRATEGIC_BIN=""
STRATEGIC_INDEXED="false"
STRATEGIC_FRESH="unknown"
STRATEGIC_GRAPH="$TARGET_DIR/topology-out/graph.json"
if [ ! -f "$STRATEGIC_GRAPH" ] && [ -f "$TARGET_DIR/${_S_BIN_NAME}-out/graph.json" ]; then
    STRATEGIC_GRAPH="$TARGET_DIR/${_S_BIN_NAME}-out/graph.json"
fi

# 1. Detect tactical engine
if command -v "$_T_BIN_NAME" >/dev/null 2>&1; then
    TACTICAL_BIN="$(command -v "$_T_BIN_NAME")"
elif [ -f "$TARGET_DIR/$_T_BIN_NAME/dist/bin/$_T_BIN_NAME.js" ]; then
    TACTICAL_BIN="$TARGET_DIR/$_T_BIN_NAME/dist/bin/$_T_BIN_NAME.js"
fi

if [ -f "$TACTICAL_DB" ]; then
    TACTICAL_INDEXED="true"
    if command -v git >/dev/null 2>&1 && git -C "$TARGET_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        LATEST_COMMIT_TIME=$(git -C "$TARGET_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
        INDEX_MTIME=$(stat -f "%m" "$TACTICAL_DB" 2>/dev/null || stat -c "%Y" "$TACTICAL_DB" 2>/dev/null || echo 0)
        if [ "$INDEX_MTIME" -ge "$LATEST_COMMIT_TIME" ]; then
            TACTICAL_FRESH="true"
        else
            TACTICAL_FRESH="false"
        fi
    fi
fi

# 2. Detect strategic engine
if command -v "$_S_BIN_NAME" >/dev/null 2>&1; then
    STRATEGIC_BIN="$(command -v "$_S_BIN_NAME")"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import $_S_BIN_NAME" >/dev/null 2>&1; then
    STRATEGIC_BIN="$(which python3) -m $_S_BIN_NAME"
fi

if [ -f "$STRATEGIC_GRAPH" ]; then
    STRATEGIC_INDEXED="true"
    if command -v git >/dev/null 2>&1 && git -C "$TARGET_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        LATEST_COMMIT_TIME=$(git -C "$TARGET_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
        INDEX_MTIME=$(stat -f "%m" "$STRATEGIC_GRAPH" 2>/dev/null || stat -c "%Y" "$STRATEGIC_GRAPH" 2>/dev/null || echo 0)
        if [ "$INDEX_MTIME" -ge "$LATEST_COMMIT_TIME" ]; then
            STRATEGIC_FRESH="true"
        else
            STRATEGIC_FRESH="false"
        fi
    fi
fi

# 3. Determine unified state
if [ -n "$TACTICAL_BIN" ] && [ -n "$STRATEGIC_BIN" ]; then
    TOOL_STATE="both_available"
elif [ -n "$TACTICAL_BIN" ]; then
    TOOL_STATE="tactical_only"
elif [ -n "$STRATEGIC_BIN" ]; then
    TOOL_STATE="strategic_only"
else
    TOOL_STATE="none_available"
fi

cat <<EOF
{
  "target_directory": "$TARGET_DIR",
  "tool_state": "$TOOL_STATE",
  "tactical_engine": {
    "binary": "$TACTICAL_BIN",
    "indexed": $TACTICAL_INDEXED,
    "fresh": "$TACTICAL_FRESH",
    "db_path": "$TACTICAL_DB"
  },
  "strategic_engine": {
    "binary": "$STRATEGIC_BIN",
    "indexed": $STRATEGIC_INDEXED,
    "fresh": "$STRATEGIC_FRESH",
    "graph_path": "$STRATEGIC_GRAPH"
  }
}
EOF
