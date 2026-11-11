#!/usr/bin/env bash
# detect_tools.sh - Detect CodeGraph (tactical) and Graphify (strategic): binaries,
# versions, index presence, freshness (incl. uncommitted edits), version-gated features.
# Read-only: never modifies the workspace. Emits one JSON object on stdout.
# Run once per session and reuse the result.

set -uo pipefail

TARGET_DIR="${1:-.}"
if ! TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)"; then
    printf '{"error": "target directory not found"}\n'
    exit 2
fi

json_str() {  # JSON-escape a string (backslash, quote, control chars)
    local s=${1//\\/\\\\}
    s=${s//\"/\\\"}
    s=${s//$'\n'/\\n}
    s=${s//$'\t'/\\t}
    s=${s//$'\r'/}
    printf '"%s"' "$s"
}

mtime() { stat -f "%m" "$1" 2>/dev/null || stat -c "%Y" "$1" 2>/dev/null || echo 0; }

IN_GIT=false
if command -v git >/dev/null 2>&1 && git -C "$TARGET_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    IN_GIT=true
fi

# Freshness: index is stale if any tracked-modified or untracked source file
# (or the last commit) is newer than the index file.
STALE_FILES=()
freshness() {
    local index="$1"
    [ -f "$index" ] || { echo "unknown"; return; }
    $IN_GIT || { echo "unknown"; return; }
    local imt; imt=$(mtime "$index")
    local commit_t; commit_t=$(git -C "$TARGET_DIR" log -1 --format=%ct 2>/dev/null || echo 0)
    local stale=false f
    while IFS= read -r f; do
        [ -n "$f" ] || continue
        [ -f "$TARGET_DIR/$f" ] || continue
        if [ "$(mtime "$TARGET_DIR/$f")" -gt "$imt" ]; then
            stale=true
            [ "${#STALE_FILES[@]}" -lt 10 ] && STALE_FILES+=("$f")
        fi
    done < <( { git -C "$TARGET_DIR" diff --name-only HEAD 2>/dev/null
                git -C "$TARGET_DIR" ls-files -o --exclude-standard 2>/dev/null; } \
              | grep -vE '^(\.codegraph|graphify-out|\.ultima)/' | sort -u | head -2000)
    [ "${commit_t:-0}" -gt "$imt" ] && stale=true
    $stale && echo "false" || echo "true"
}

# --- Tactical: CodeGraph ---------------------------------------------------
CG_BIN=""; CG_VER=""; CG_INDEXED=false; CG_FRESH="unknown"
CG_DB="$TARGET_DIR/.codegraph/codegraph.db"
CG_CYCLES=false; CG_IMPL=false
if command -v codegraph >/dev/null 2>&1; then
    CG_BIN="$(command -v codegraph)"
    CG_VER="$(codegraph --version 2>/dev/null | head -1 | tr -d '[:space:]')"
    CG_HELP="$(codegraph --help 2>/dev/null)"
    grep -qE '^[[:space:]]+cycles' <<<"$CG_HELP" && CG_CYCLES=true
    grep -qE '^[[:space:]]+implementations' <<<"$CG_HELP" && CG_IMPL=true
fi
if [ -f "$CG_DB" ]; then
    CG_INDEXED=true
    CG_FRESH="$(freshness "$CG_DB")"
fi

# --- Strategic: Graphify ---------------------------------------------------
GF_BIN=""; GF_MCP=""; GF_INDEXED=false; GF_FRESH="unknown"; GF_REPORT=""
GF_GRAPH="$TARGET_DIR/graphify-out/graph.json"
if command -v graphify >/dev/null 2>&1; then
    GF_BIN="$(command -v graphify)"
elif command -v python3 >/dev/null 2>&1 && python3 -c "import graphify" >/dev/null 2>&1; then
    GF_BIN="python3 -m graphify"
fi
command -v graphify-mcp >/dev/null 2>&1 && GF_MCP="$(command -v graphify-mcp)"
if [ -f "$GF_GRAPH" ]; then
    GF_INDEXED=true
    GF_FRESH="$(freshness "$GF_GRAPH")"
fi
[ -f "$TARGET_DIR/graphify-out/GRAPH_REPORT.md" ] && GF_REPORT="graphify-out/GRAPH_REPORT.md"

# --- State -----------------------------------------------------------------
if [ -n "$CG_BIN" ] && [ -n "$GF_BIN" ]; then TOOL_STATE="both_available"
elif [ -n "$CG_BIN" ]; then TOOL_STATE="tactical_only"
elif [ -n "$GF_BIN" ]; then TOOL_STATE="strategic_only"
else TOOL_STATE="none_available"; fi

STALE_JSON=""
for f in "${STALE_FILES[@]+"${STALE_FILES[@]}"}"; do
    STALE_JSON+="${STALE_JSON:+, }$(json_str "$f")"
done

cat <<EOF
{
  "target_directory": $(json_str "$TARGET_DIR"),
  "tool_state": "$TOOL_STATE",
  "in_git": $IN_GIT,
  "tactical_engine": {
    "name": "codegraph",
    "binary": $(json_str "$CG_BIN"),
    "version": $(json_str "$CG_VER"),
    "indexed": $CG_INDEXED,
    "fresh": "$CG_FRESH",
    "db_path": ".codegraph/codegraph.db",
    "features": { "cycles": $CG_CYCLES, "implementations": $CG_IMPL }
  },
  "strategic_engine": {
    "name": "graphify",
    "binary": $(json_str "$GF_BIN"),
    "mcp_binary": $(json_str "$GF_MCP"),
    "indexed": $GF_INDEXED,
    "fresh": "$GF_FRESH",
    "graph_path": "graphify-out/graph.json",
    "report": $(json_str "$GF_REPORT")
  },
  "stale_files": [${STALE_JSON}]
}
EOF
