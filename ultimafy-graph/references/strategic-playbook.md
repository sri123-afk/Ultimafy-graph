# Strategic Engine Playbook: Graphify

Load for architecture onboarding, god nodes, communities, surprising connections, code↔docs links, PR graph risk, or exports.

Upstream: [github.com/Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) · PyPI `graphifyy` (note the double "y") · CLI `graphify`, MCP `graphify-mcp`. Verified against 0.8–0.9; run `graphify --help` if a flag errors.

---

## 1. What it is

Builds `graphify-out/graph.json` from code (local AST, no LLM) and optionally from docs/PDFs/images/transcribed media (LLM semantic extraction). It clusters the graph with Leiden, ranks hubs ("god nodes"), flags cross-community "surprising connections", and writes `GRAPH_REPORT.md`. Every edge carries `relation` and `confidence` (`EXTRACTED` / `INFERRED` / `AMBIGUOUS`).

### Cost split (critical)

| Operation | LLM tokens? | Rung |
|---|---|---|
| `graphify update .` (re-extract code, re-cluster) | **No** | L4 |
| `graphify extract . --code-only` | **No** | L4/L6 |
| `graphify cluster-only . --no-label` | No | L4 |
| `graphify query/path/explain/affected/god-nodes` | No | L2 |
| `graphify extract .` with docs/PDFs/images, `--mode deep` | **Yes**, scales with LLM-bound corpus | L5 |
| `graphify label .`, `cluster-only` with labeling | **Yes** (small) | L5 |
| Audio/video transcription | Local Whisper compute + then L5 | L5 |

Default to the code-only path unless the user's question needs docs/media.

---

## 2. CLI reference (verified)

```bash
# Build / refresh
graphify update .                         # code-only re-extract + recluster (no LLM). --force if nodes shrank after a refactor
graphify extract . --code-only            # headless build, code only, no API key
graphify extract . [--backend claude|gemini|openai|ollama|...] [--mode deep] [--token-budget N]
graphify cluster-only . [--no-viz] [--no-label]
graphify label . [--missing-only]         # (re)name communities via LLM
graphify check-update .                   # is semantic re-extraction pending?
graphify watch .                          # rebuild on code changes
graphify hook install                     # post-commit/checkout auto-update

# Query (L2) - all default to graphify-out/graph.json, override with --graph
graphify query "<question>" [--dfs] [--budget 2000] [--context C]
graphify path "A" "B"                     # shortest path between concepts
graphify explain "X"                      # node + neighbors in plain language
graphify affected "X" [--depth 2] [--relation R]   # reverse traversal: what depends on X (incl. docs)
graphify god-nodes [--top 10] [--json]

# Feedback loop (improves later queries)
graphify save-result --question Q --answer A --nodes N1 N2 --outcome useful|dead_end|corrected
graphify reflect                          # aggregate memory → graphify-out/reflections/LESSONS.md

# Multi-repo / exports
graphify merge-graphs g1.json g2.json --out merged.json
graphify global add graphify-out/graph.json --as <tag>
graphify export html|wiki|obsidian|svg|graphml|callflow-html
graphify export neo4j [--push bolt://...]   # set NEO4J_PASSWORD env, not --password
graphify extract . --postgres "<DSN>"       # add live DB schema (tables, FKs) to the graph
graphify prs                                # PR dashboard
graphify benchmark                          # token reduction vs naive full-corpus read
```

In Claude Code the `/graphify` skill drives full multimodal builds with subagents. Prefer it for L5 builds there.

---

## 3. MCP tools (`graphify-mcp`, stdio)

`query_graph` · `get_node` · `get_neighbors` · `get_community` · `god_nodes` · `graph_stats` · `shortest_path` · `list_prs` · `get_pr_impact` · `triage_prs`

---

## 4. Artifacts in `graphify-out/`

| File | Use |
|---|---|
| `GRAPH_REPORT.md` | **Read first (L0/L2).** God nodes, surprising connections, communities, suggested questions |
| `graph.json` | Node-link graph. Don't load it whole into context; query via the CLI |
| `.graphify_analysis.json` | Community membership, cohesion, hub ranks |
| `.graphify_labels.json` | Community id → human name |
| `.vocab.txt` | Label vocabulary for query expansion |
| `memory/`, `reflections/LESSONS.md` | Saved Q&A outcomes |

---

## 5. Query discipline

1. **Report before query.** If `GRAPH_REPORT.md` answers it, stop there.
2. **Vocabulary expansion before concluding "not found".** `rg -i -w "<term>" graphify-out/.vocab.txt` (or grep the stem) → rerun with terms that actually exist (e.g. "authorization" → `guard`, `policy`, `permission`).
3. **BFS for "what's around X", DFS (`--dfs`) for "how does A reach B".** Always set `--budget` (start 1500).
4. **Graphify finds; CodeGraph proves.** Treat graphify code edges as navigation. For exact call sites and line numbers, confirm with `codegraph_explore`/`callers` when available.
5. Doc→code edges from semantic extraction are usually `INFERRED`. Cite the doc path and the code symbol, and keep the tag.

---

## 6. Noise filters for rankings

Exclude from god-node / hotspot claims: stdlib and framework types (`object`, `dict`, `String`, `React`), logging/util hubs (`logger`, `utils`), generated files, vendored dirs, and test fixtures. State what you filtered.
