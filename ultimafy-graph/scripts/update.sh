#!/usr/bin/env bash
# update.sh - "ultimafy-graph update": one command to bring BOTH engines up to date.
#
#   bash scripts/update.sh [path] [--check] [--init] [--force] [--only codegraph|graphify] [--verbose]
#
# Behaviour (cheapest-first, never spends LLM tokens):
#   * Runs detect_tools.sh, then refreshes ONLY engines that are installed, indexed and stale.
#       CodeGraph -> `codegraph sync`            (incremental, local AST)
#       Graphify  -> `graphify update <path>`    (code-only re-extract + recluster, no LLM)
#   * Fresh engines are skipped (zero cost). Missing indexes are skipped unless --init.
#   * Reports (but never runs) pending Graphify SEMANTIC re-extraction (docs/PDFs changed).
#     That is L5 and needs user consent: run `/graphify --update` or `graphify extract`.
#   * Tool output goes to .ultima/update.log; stdout is one compact JSON summary.
#
# Flags:
#   --check    dry run: report what would be refreshed. Exit 0 if all fresh, 10 if stale.
#   --init     build missing indexes (codegraph init -y; graphify extract --code-only).
#   --force    refresh even if fresh. CodeGraph does a full `index`; Graphify `update --force`
#              (accepts a smaller graph after refactors that delete code).
#   --only X   limit to one engine.
#   --verbose  stream tool output instead of logging it.
# Exit: 0 ok | 1 an engine refresh failed | 2 usage error | 10 stale (with --check)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="."; CHECK=false; INIT=false; FORCE=false; ONLY=""; VERBOSE=false
while [ $# -gt 0 ]; do
    case "$1" in
        --check) CHECK=true ;;
        --init) INIT=true ;;
        --force) FORCE=true ;;
        --only) shift; ONLY="${1:-}"; [[ "$ONLY" =~ ^(codegraph|graphify)$ ]] || { echo "--only expects codegraph|graphify" >&2; exit 2; } ;;
        --verbose|-v) VERBOSE=true ;;
        -h|--help) sed -n '2,24p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
        -*) echo "unknown flag: $1" >&2; exit 2 ;;
        *) TARGET="$1" ;;
    esac
    shift
done
TARGET="$(cd "$TARGET" 2>/dev/null && pwd)" || { echo '{"error":"target directory not found"}'; exit 2; }

DETECT="$(bash "$SCRIPT_DIR/detect_tools.sh" "$TARGET")" || { echo '{"error":"detect_tools.sh failed"}'; exit 1; }
field() {  # field <engine_key> <name>  -> raw JSON value (strings unquoted)
    DETECT_JSON="$DETECT" python3 -c '
import json, os, sys
v = json.loads(os.environ["DETECT_JSON"]).get(sys.argv[1], {}).get(sys.argv[2], "")
print(str(v).lower() if isinstance(v, bool) else v)' "$1" "$2" 2>/dev/null
}

LOG="$TARGET/.ultima/update.log"
mkdir -p "$TARGET/.ultima"
# Self-ignoring dir: keeps logs/ledger out of git AND out of graphify's corpus (it honours .gitignore).
[ -f "$TARGET/.ultima/.gitignore" ] || printf '*\n' >"$TARGET/.ultima/.gitignore"
run() {  # run <label> <cmd...>
    printf '\n[%s] %s: %s\n' "$(date -u +%FT%TZ)" "$1" "${*:2}" >>"$LOG"
    if $VERBOSE; then (cd "$TARGET" && "${@:2}") 2>&1 | tee -a "$LOG"; return "${PIPESTATUS[0]}"
    else (cd "$TARGET" && "${@:2}") >>"$LOG" 2>&1; fi
}

RESULTS=(); FAILED=false; STALE_ANY=false

plan() {  # plan <engine> <installed> <indexed> <fresh>  -> action word
    local installed="$2" indexed="$3" fresh="$4"
    if [ -n "$ONLY" ] && [ "$ONLY" != "$1" ]; then echo "skipped"; return; fi
    [ -n "$installed" ] || { echo "not_installed"; return; }
    if [ "$indexed" != "true" ]; then $INIT && echo "init" || echo "no_index"; return; fi
    if $FORCE; then echo "force"; return; fi
    case "$fresh" in
        true) echo "fresh" ;;
        *) echo "refresh" ;;   # false or unknown (no git) -> incremental refresh is cheap
    esac
}

t0=$(date +%s)

# --- CodeGraph -------------------------------------------------------------
CG_ACTION="$(plan codegraph "$(field tactical_engine binary)" "$(field tactical_engine indexed)" "$(field tactical_engine fresh)")"
CG_STATUS="$CG_ACTION"
case "$CG_ACTION" in refresh|force|init) STALE_ANY=true ;; esac
if ! $CHECK; then
    case "$CG_ACTION" in
        refresh) run codegraph codegraph sync -q . && CG_STATUS="synced" || { CG_STATUS="sync_failed"; FAILED=true; } ;;
        force)   run codegraph codegraph index -q . && CG_STATUS="reindexed" || { CG_STATUS="index_failed"; FAILED=true; } ;;
        init)    run codegraph codegraph init -y . && CG_STATUS="initialized" || { CG_STATUS="init_failed"; FAILED=true; } ;;
    esac
fi

# --- Graphify --------------------------------------------------------------
GF_BIN="$(field strategic_engine binary)"
GF_ACTION="$(plan graphify "$GF_BIN" "$(field strategic_engine indexed)" "$(field strategic_engine fresh)")"
GF_STATUS="$GF_ACTION"; GF_SEMANTIC="unknown"
case "$GF_ACTION" in refresh|force|init) STALE_ANY=true ;; esac
read -r -a GF <<<"$GF_BIN"
if ! $CHECK; then
    case "$GF_ACTION" in
        refresh) run graphify "${GF[@]}" update . && GF_STATUS="updated" || { GF_STATUS="update_failed"; FAILED=true; } ;;
        force)   run graphify env GRAPHIFY_FORCE=1 "${GF[@]}" update . --force && GF_STATUS="updated_forced" || { GF_STATUS="update_failed"; FAILED=true; } ;;
        init)    run graphify "${GF[@]}" extract . --code-only && GF_STATUS="initialized_code_only" || { GF_STATUS="init_failed"; FAILED=true; } ;;
    esac
fi
# Pending semantic (L5) work? Report only; never run it here.
if [ -n "$GF_BIN" ] && [ -f "$TARGET/graphify-out/graph.json" ] && { [ -z "$ONLY" ] || [ "$ONLY" = graphify ]; }; then
    if out="$(cd "$TARGET" && "${GF[@]}" check-update . 2>/dev/null)"; then
        if grep -qiE 'pending|needs?[_ ]update|re-?extract' <<<"$out"; then GF_SEMANTIC="pending"; else GF_SEMANTIC="none"; fi
    fi
fi

# --- Summary ---------------------------------------------------------------
HINT=""
[ "$GF_SEMANTIC" = "pending" ] && HINT="Docs/papers changed: semantic re-extraction is L5 (LLM tokens). Ask the user before running '/graphify --update' or 'graphify extract .'."
[ "$CG_ACTION" = "no_index" ] && HINT="${HINT:+$HINT }CodeGraph not indexed: rerun with --init (local, no LLM)."
[ "$CG_ACTION" = "not_installed" ] && [ "$GF_ACTION" = "not_installed" ] && HINT="No engines installed: see references/tool-detection-and-fallbacks.md section 2."
$FAILED && HINT="${HINT:+$HINT }See .ultima/update.log for errors."

printf '{"mode":"%s","codegraph":"%s","graphify":"%s","graphify_semantic":"%s","seconds":%s,"log":".ultima/update.log","hint":"%s"}\n' \
    "$($CHECK && echo check || echo update)" "$CG_STATUS" "$GF_STATUS" "$GF_SEMANTIC" "$(( $(date +%s) - t0 ))" "${HINT//\"/\\\"}"

$FAILED && exit 1
$CHECK && $STALE_ANY && exit 10
exit 0
