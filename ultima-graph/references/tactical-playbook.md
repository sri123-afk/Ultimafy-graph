# Tactical Engine Playbook: Deterministic Code Intelligence

This playbook defines operational procedures for the local deterministic code intelligence engine (CLI: `tactical`, MCP tool: `tactical_explore`). Load this playbook whenever performing single-retrieval code lookups, call flow extraction, blast-radius analysis, circular import detection, or selective test impact mapping.

---

## 1. Engine Core & Architectural Role

The tactical engine is a 100% deterministic, local-first code indexer. It parses source code using compiled Tree-sitter grammars (Rust kernel for 20 core languages, portable TypeScript engine for 14+ others) into an embedded SQLite database (`.ultima/tactical.db`).

### Primary Objectives
1. **Displace Read and Grep loops:** Replace dozens of exploratory file reading round-trips with a single structured retrieval call.
2. **Surface Verbatim Line-Numbered Source:** Return code formatted as `<line_number>\t<source_line>`, identical to the native Read tool, safe for direct editing.
3. **Trace Dynamic Dispatch:** Traverse call chains across framework routes, client-server network tiers, mobile bridges, and parameter flows that lexical grep cannot follow.

---

## 2. Real Tool Names, MCP Interface & Environment Controls

### Primary MCP Tool
* **`tactical_explore`**: The primary Read-equivalent tool.
  * **Input:** Natural-language question or a bag of symbol and file names (e.g., `PaymentService processOrder checkout.ts`).
  * **Output:** Verbatim line-numbered source of matching symbols grouped by file, plus call paths connecting them, and blast-radius summaries of inbound/outbound callers.
  * **Session Deduplication:** If `TACTICAL_EXPLORE_DEDUP=1` is set, symbols previously sent in the conversation context are referenced back rather than re-emitted, saving context window space.

### Optional Secondary MCP Tools (Unlisted by Default)
To expose secondary tools, set environment variable:
```bash
export TACTICAL_MCP_TOOLS=explore,node,search,callers,callees,impact,files,status
```
* `tactical_node`: Detailed source and caller trail for a specific symbol or whole file.
* `tactical_search`: FTS5 full-text symbol search across the codebase.
* `tactical_callers`: Inbound caller tree for a given symbol.
* `tactical_callees`: Outbound callee tree for a given symbol.
* `tactical_impact`: Recursive dependency blast-radius evaluation.
* `tactical_files`: Structural file tree inspection.
* `tactical_status`: Index health, node/edge counts, and pending sync status.

---

## 3. Real CLI Commands & Verified Flags

Execute these commands when operating in terminal environments:

```bash
# 1. Project Initialization & Indexing
tactical init [path]             # Initialize index and build complete index in one pass
tactical index [path]            # Force full re-index (--force, --quiet)
tactical sync [path]             # Incremental synchronization of modified files
tactical status [path]           # Show index statistics and pending sync files (--json, --strict)
tactical unlock [path]           # Clear stale lockfile blocking index writes

# 2. Querying & Symbol Navigation
tactical explore "<query>"       # Verbatim source + call paths + blast radius (CLI equivalent of MCP tool)
tactical node <symbol|file>      # Symbol body + callers or line-numbered file contents
tactical query <search>          # Search symbol names via FTS5 (--kind <k>, --limit <n>, --json)
tactical callers <symbol>        # Inbound callers (--limit <n>, --json)
tactical callees <symbol>        # Outbound callees (--limit <n>, --json)
tactical impact <symbol>         # Recursive impact analysis (--depth <n>, --json)
tactical implementations <type>  # Types extending or implementing a class/interface (--depth <n>, --json)

# 3. Quality & Impact Analysis
tactical affected [files...]     # Transitively maps changed files to affected test files
git diff --name-only | tactical affected --stdin --quiet   # Pipe git diff directly to affected tests
tactical cycles [path]           # Detect circular import dependencies between files (exits 1 on cycles)
```

---

## 4. SQLite Storage Schema & Under-the-Hood Mechanisms

The database is stored at `.ultima/tactical.db` with SQLite WAL mode. Core tables include:

1. **`nodes`**: Stores code symbols.
   * Attributes: `id`, `kind`, `name`, `qualified_name`, `file_path`, `language`, `start_line`, `end_line`, `start_column`, `end_column`, `docstring`, `signature`, `visibility`, `is_exported`, `is_async`, `is_static`, `is_abstract`, `return_type`.
2. **`edges`**: Stores symbol relationships.
   * Attributes: `source`, `target`, `kind`, `metadata`, `line`, `col`, `provenance`.
   * Uniqueness constraint: Composite index on `(source, target, kind, IFNULL(line, -1), IFNULL(col, -1))`.
3. **`nodes_fts`**: Virtual table powered by SQLite FTS5 for sub-millisecond lexical queries.
4. **`name_segment_vocab`**: Materialized word-segment index splitting identifiers (e.g., `OrderStateMachine` -> `order`, `state`, `machine`). Enables exact matching of conversational terms to code symbols without vector hallucinations.
5. **`unresolved_refs`**: Tracks dangling calls during indexing, resolved in post-processing passes.

---

## 5. Dynamic Dispatch & Synthesized Hops

Static AST parsing stops at file and language boundaries. The tactical engine resolves these boundaries through synthesis passes:

| Boundary Type | Synthesized Edge | Mechanism |
|---|---|---|
| **Web Framework Routes** | `references` | Maps route declarations (`@app.get('/users')`, `Route::get()`) to handler methods across 17+ frameworks. |
| **Client-Side Routers** | `navigates` | Follows `router.push()`, `<Link href="...">`, `redirect()` in Next.js, React Router, SvelteKit, Expo Router. |
| **Cross-Tier Network** | `calls` (tier) | Connects frontend `fetch('/api/v1/orders')` or `axios` calls directly to backend route handlers. |
| **Mobile Native Bridges** | `calls` (bridge) | Swift `@objc` selector auto-bridging; React Native `NativeModules` and TurboModules to native ObjC/Kotlin. |
| **Desktop Native IPC** | `calls` (ipc) | Tauri `invoke('save_config')` mapped directly to Rust `#[tauri::command]`. |
| **Parameter Flow** | `calls` (flow) | Resolves method calls on abstract parameters to the concrete class instantiated at call sites. |

---

## 6. Freshness, Watcher & Staleness Handling

1. **Auto-Sync:** A native OS file watcher (FSEvents/inotify/ReadDirectoryChangesW) tracks source edits and syncs incrementally after a 2-second debounce window.
2. **Staleness Warning:** When a query references a file modified inside the debounce window, the response carries a warning banner:
   ```
   [STALENESS WARNING] Some files referenced below were edited since the last index sync:
   - src/services/OrderService.ts (modified 400ms ago)
   Read these specific files directly for live unsynced changes.
   ```
3. **Connect-Time Catch-up:** On agent startup or MCP reconnect, the server verifies `(size, mtime)` hashes across the working tree to absorb changes made while offline.
