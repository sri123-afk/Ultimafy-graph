# Tactical Engine Playbook: CodeGraph

Load when doing symbol lookups, call-flow tracing, impact/blast radius, affected tests, or editing code with structure in view.

Upstream: [github.com/colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) · npm `@colbymchenry/codegraph` · verified against v1.6.x. Run `codegraph <cmd> --help` if a flag errors; the CLI evolves.

---

## 1. What it is

A local, deterministic Tree-sitter indexer (30+ languages) writing a SQLite graph to `.codegraph/codegraph.db`. No LLM, no network. A file watcher keeps the index ~1s behind writes while the MCP server/daemon runs.

It resolves edges that grep cannot follow: framework routes → handlers, client `fetch`/`axios` → backend routes, client routers (`router.push`, `<Link>`), Tauri `invoke` → `#[tauri::command]`, React Native/Swift native bridges, and parameter-flow dispatch to concrete classes.

---

## 2. MCP surface

- **Default exposed tool: `codegraph_explore` only.** It takes a natural-language question **or** a bag of symbol/file names (`"PaymentService processOrder checkout.ts"`). It returns verbatim `<n>\t<line>` source grouped by file (safe to `Edit` from), plus call paths and caller/callee summaries.
- More tools (`codegraph_node`, `_search`, `_callers`, `_callees`, `_impact`, `_files`, `_status`, `_context`) exist but are hidden unless `CODEGRAPH_MCP_TOOLS=explore,node,callers,...` is set. Don't assume they're present: check the tool list. The CLI equivalents always work.
- `CODEGRAPH_EXPLORE_DEDUP=1` lets the server reference source it already sent instead of re-sending it. Enable it only on hosts with one durable context per connection, because it is unsafe after compaction or in subagents.
- **Subagents don't get the MCP instructions.** Tell them: "use `codegraph explore '<symbols>'` via Bash instead of Read/Grep".

### Using `codegraph_explore` well (token rules)
1. Pass **all** relevant names in one call (source + sink + suspected middle). One call beats N.
2. Prefer exact identifiers from the user/error message over prose. Prose works but returns broader context.
3. Don't follow up with `Read`/`rg` to "double-check" what explore returned verbatim. It *is* the file content.
4. Use `--max-files N` (CLI) to cap output on broad questions.

---

## 3. CLI reference (verified)

```bash
# Setup / health
codegraph init [path]                  # create .codegraph/ and build index (one-time)
codegraph sync [path]                  # incremental update (L4)
codegraph index [path]                 # full rebuild (L6)
codegraph status [path] [--json]       # node/edge counts, pending changes
codegraph unlock [path]                # clear stale lock
codegraph install -y -t auto           # wire MCP into detected agents (global)

# Retrieval (L1)
codegraph explore "<query...>" [--max-files N]   # = codegraph_explore
codegraph node <symbol> [-f file]                # one symbol: source + caller/callee trail
codegraph node -f <file> --offset N --limit M    # line-numbered file slice (+dependents)
codegraph node -f <file> --symbols-only          # just the symbol map of a file (cheap outline)
codegraph query <search> [-k function|class|...] [-l N] [--json]   # FTS symbol search
codegraph context "<task>" [-n N] [--no-code]    # task-oriented bundle; --no-code = structure only
codegraph files                                  # indexed file tree

# Graph analysis (L1)
codegraph callers <symbol> [-f file] [-l N] [--json]
codegraph callees <symbol> [-f file] [-l N] [--json]
codegraph impact  <symbol> [-f file] [-d DEPTH=2] [--json]
codegraph affected [files...] [--stdin] [-d DEPTH=5] [-f "<test glob>"] [--json] [-q]

# Version-gated (present in newer builds; check detect_tools.sh "features")
codegraph implementations <type> [--json]        # implementors/subclasses
codegraph cycles [path] [--json]                 # circular file imports; exit 1 if any
```

**Not a CLI command:** there is no `codegraph dead-code`. Dead-code candidates come from `callers X` → 0 results, verified by `rg -w` (see workflows.md WF5).

**Disambiguation:** if a name is overloaded, pass `-f <file-suffix>` to `callers`/`callees`/`impact`/`node`. Results that merge multiple same-named definitions are `AMBIGUOUS` until narrowed.

**Monorepos:** run commands with `-p packages/<svc>` or index per package to keep results focused.

---

## 4. Patterns

| Need | Cheapest call |
|---|---|
| Outline a big file before reading | `codegraph node -f path --symbols-only` |
| Read only one function | `codegraph node <Symbol> -f path` |
| Find a symbol by fuzzy name | `codegraph query <term> -l 5` |
| Who calls it (direct) | `codegraph callers <Symbol> -l 50 --json` |
| Transitive blast radius | `codegraph impact <Symbol> -d 2 --json` (raise to 3 only if depth-2 is small) |
| Tests for a diff | `git diff --name-only origin/main...HEAD \| codegraph affected --stdin -q` |
| Tests incl. untracked/staged | `{ git diff --name-only HEAD; git ls-files -o --exclude-standard; } \| codegraph affected --stdin -q` |

---

## 5. Freshness

- MCP/daemon mode: the watcher syncs automatically. If a response carries a staleness warning for a file, read that file's range directly. Don't trust the line numbers for it.
- CLI-only usage (no daemon running): run `codegraph sync` after pulls, branch switches, or bulk edits before querying.
- `detect_tools.sh` reports `fresh: false` when tracked files changed after the DB was written, including uncommitted edits.

---

## 6. Known limits (say these when relevant)

- Reflection, string-built dispatch, DI containers configured in YAML/XML, and event buses with string topics may produce **missing** edges. Treat "0 callers" as a hypothesis until `rg -w` agrees.
- Generated code (`*.pb.go`, `*.g.dart`, `*_generated.*`, `DO NOT EDIT` banners) inflates counts. Exclude it from god-node and blast-radius rankings.
- `affected` finds tests by import graph. Tests that hit code only over HTTP (E2E) need the route → spec mapping step.
