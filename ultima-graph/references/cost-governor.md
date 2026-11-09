# Cost Governor: The Ultima-Graph Economic Protocol

This reference defines the economic discipline, cost ladder, budgeting rules, and ledger tracking for ultima-graph. Load this file whenever escalating between execution rungs, evaluating token or compute budgets, or compiling session cost reports.

---

## 1. The Cost Ladder (Rungs L0 through L6)

The agent must climb the cost ladder only when a lower rung lacks the necessary information to provide a verified answer. The agent must state the rung it is on and justify why it escalated.

| Rung | Tier Name | Entry Condition | Typical Artifacts & Methods | Cost Class | Exit Criteria |
|---|---|---|---|---|---|
| **L0** | In-Context / Cached | Query can be answered by active conversation memory or existing report files. | `GRAPH_REPORT.md`, conversation history, prior tool outputs. | Zero | Evidence already exists in context; no tool calls required. |
| **L1** | Deterministic Index | Query targets source code symbols, call flows, or blast radius; index exists. | `tactical_explore`, `tactical impact`, `tactical affected`. | Near-Zero (<0.01 USD / ~500 tokens) | Complete source snippet, call path, and blast radius retrieved in 1-2 calls. |
| **L2** | Cached Topology | Query asks about architecture, communities, god nodes, or global cohesion. | `topology-out/graph.json`, `.topology_analysis.json`, `query_graph`. | Minimal (~1k-2k tokens) | Cluster membership, hub centrality rankings, or shortest path identified. |
| **L3** | Targeted Range Read | L1/L2 provided exact file and line coordinates, but surrounding implementation logic is required. | `Read` tool constrained strictly to line numbers (e.g., `L45-L90`). Never read full files. | Low (<1k tokens) | Implementation details or comments confirmed without reading extraneous file content. |
| **L4** | Incremental Sync | Index is flagged stale (modified files detected by watcher or git commit mismatch). | `tactical sync`, `strategic update`. | Moderate (compute only) | SQLite index or JSON graph updated with only the modified file subset. |
| **L5** | Multimodal LLM Extraction | User requests semantic analysis of unstructured media (Markdown docs, PDFs, images). | Parallel subagents or Gemini API over doc chunks. Preflight check mandatory. | Medium-High (token cost tracks corpus size) | Extracted semantic nodes and hyperedges persisted to disk cache. |
| **L6** | Full Corpus Rebuild | Corrupted index, major schema migration, or explicit user `--force` command. | `tactical index --force`, `strategic rebuild`. | High (maximum compute / tokens) | Complete rebuild verified; justified only when L4 incremental sync fails. |

---

## 2. Default Soft Budgets per Task Type

The agent must not exceed these soft limits without explicit operational justification:

| Task Type | Maximum Allowed Rung | Max Direct File Reads | Max LLM Extraction Calls | Hard Stop Condition |
|---|---|---|---|---|
| **Symbol / Code Lookup** | L1 (Escalate to L3 only if ambiguous) | 2 files (range-bound) | 0 | Symbol found and cited. |
| **Call Flow Tracing** | L1 | 1 file (range-bound) | 0 | Call chain reaches terminal sink or database boundary. |
| **Blast Radius / Impact** | L1 | 0 files | 0 | Caller tree compiled to specified depth (default 2-3). |
| **Affected Test Selection** | L1 | 0 files | 0 | Test files mapped from git diff. |
| **Dead Code Detection** | L1 (Escalate to L2 for doc check) | 0 files | 0 | Unreferenced symbol list compiled. |
| **Architecture Audit** | L2 | 3 files (range-bound hotspots) | 0 | Top 5 god nodes and surprising connections ranked. |
| **System Onboarding** | L2 (Escalate to L1 for drill-down) | 3 files | 0 | Module summaries and cluster map compiled. |
| **Docs vs Code Drift** | L5 (Selective changed docs only) | 5 files | Bounded by preflight check | All documented endpoints cross-checked against code. |

---

## 3. The Cost Ledger Protocol (`scripts/cost_ledger.py`)

Every substantive query must be logged to `.ultima/ledger.jsonl` using the deterministic ledger CLI.

### Logging a Task Run
```bash
python3 scripts/cost_ledger.py record \
  --task "trace_checkout_flow" \
  --rung "L1" \
  --files-read 0 \
  --files-avoided 14 \
  --llm-calls 0 \
  --input-tokens 480 \
  --output-tokens 150 \
  --notes "Retrieved via tactical explore in 1 round-trip"
```

### Compiling Session Cost Audit
To display cumulative token usage, avoidance rates, and rung distribution:
```bash
python3 scripts/cost_ledger.py report
```

### Ledger Logging Rules
1. **Never fabricate tokens:** If exact token counts from the MCP tool response are unavailable, calculate standard heuristic estimates (~4 characters per token) and pass `--estimate`.
2. **Files Avoided Metric:** Calculate files avoided as the count of files referenced in the graph retrieval result that the agent would have had to open and read manually.
3. **Session Reset:** Reset the ledger before starting a distinct, benchmarked evaluation (`python3 scripts/cost_ledger.py reset`).

---

## 4. Preflight Sizing & Threshold Enforcement

Before initiating any L5 multimodal extraction or L6 full rebuild, the agent must run:
```bash
python3 scripts/preflight_estimate.py [path]
```

### Threshold Action Rules
* **Floor Check (< 50,000 estimated words):** Inform the user that the corpus is compact and can be navigated via in-context L0 reads or lightweight L1 queries without expensive graph generation.
* **Ceiling Check (> 500,000 words OR > 500 files):**
  * **Mandatory Warning:** Alert the user to projected token consumption and execution time.
  * **Explicit Consent Gate:** The agent is forbidden from running L5 semantic extraction across the full corpus without explicit user approval.
  * **Subdirectory Narrowing:** Offer to run extraction only on the top 3-5 subdirectories ranked by file volume.
* **Safety Ceilings:** Automatically skip any file exceeding 50 MB raw on-disk size to protect against out-of-memory crashes.

---

## 5. Stop Rules and Caching Discipline

### Stop Rules (When to Terminate Exploration)
1. **Sufficiency Rule:** Stop immediately once a direct, verified citation answering the user's question has been obtained. Do not make supplemental calls to verify facts already proven by AST.
2. **Marginal Value Rule:** If escalating from L1 to L3 or L2 to L5 is projected to double session token consumption while improving answer confidence by less than 10%, terminate and present the current finding with an `INFERRED` tag.
3. **Re-Read Ban:** Never read a file range or request a symbol that was already returned earlier in the same conversation. Re-use the existing in-context snippet.

### Caching Discipline
1. Prefer incremental updates (`tactical sync` or `strategic update`) over full rebuilds.
2. Never re-extract unchanged source files verified by `(size, mtime)` content hashes.
3. Preserve all `.ultima/` and `topology-out/` cache artifacts across session turns.
