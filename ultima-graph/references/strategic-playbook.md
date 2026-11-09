# Strategic Engine Playbook: Topological Knowledge Intelligence

This playbook defines operational procedures for the multimodal knowledge-graph engine (CLI: `strategic`, MCP server: `strategic-mcp` / `strategic.serve`). Load this playbook whenever performing repository-wide architectural onboarding, identifying monolithic "god nodes", auditing technical debt, evaluating cross-community coupling, analyzing documentation drift, or triaging pull request risk.

---

## 1. Engine Core & Architectural Role

The strategic engine constructs a multimodal knowledge graph unifying structured source code with unstructured artifacts (Markdown documentation, PDF research papers/RFCs, architecture diagrams, and Whisper-transcribed audio/video). It applies network science algorithms—specifically Leiden and Louvain community detection via `graspologic-native` and NetworkX—to surface high-level architectural topology.

### Primary Objectives
1. **Bridge Code and Human Context:** Link source code functions to user stories, API documentation, design specifications, and pull requests.
2. **Surface Architectural Hotspots:** Quantify component centrality to identify single points of failure ("god nodes") and unexpected couplings ("surprising connections").
3. **GraphRAG Navigation:** Support intent-driven graph exploration with vocabulary-expansion matching, BFS/DFS traversal, and human-readable audit reports.

---

## 2. Real Tool Names, MCP Interface & Server Operation

### Starting the MCP Server
```bash
# Stdio transport (default for AI agent integration)
strategic-mcp
# or via module entrypoint
python3 -m strategic.serve

# HTTP transport for team dashboards
python3 -m strategic.serve --http --host 127.0.0.1 --port 8080
```

### Verified MCP Tools
* `query_graph`: Natural language GraphRAG traversal across nodes and edges (`query`, `mode: "bfs"|"dfs"`, `budget: int`).
* `get_node`: Inspect attributes, label, file location, and connections of a single node (`label` or `node_id`).
* `get_neighbors`: Fetch inbound and outbound edge connections for an entity (`node_id`).
* `get_community`: List all nodes belonging to a specific topological cluster (`community_id: int`).
* `god_nodes`: Retrieve top high-centrality hub nodes sorted by degree centrality (`top_n: int`).
* `graph_stats`: Return global metrics (node count, edge count, density, community count).
* `shortest_path`: Compute the shortest relationship chain between two concepts (`source`, `target`).
* `list_prs`: Enumerate tracked pull requests.
* `get_pr_impact`: Analyze graph components and communities affected by a pull request (`pr_number`).
* `triage_prs`: Prioritize open PRs by architectural risk score (`top_n`).

---

## 3. Real CLI Commands & Verified Flags

```bash
# 1. Full Pipeline Execution
strategic                                    # Full build on current directory (generates HTML + JSON + report)
strategic <path>                             # Run full pipeline on target directory
strategic <path> --mode deep                 # In-depth extraction with enriched INFERRED relationships
strategic <path> --update                    # Incremental update: extracts only modified or new files
strategic <path> --directed                  # Build DiGraph preserving edge direction (source -> target)
strategic <path> --cluster-only              # Re-run Leiden clustering on existing graph without re-extracting
strategic <path> --no-viz                    # Headless mode: emits JSON and GRAPH_REPORT.md only

# 2. Ecosystem Exports
strategic <path> --obsidian                  # Export graph as Obsidian vault (default: topology-out/obsidian)
strategic <path> --obsidian --obsidian-dir ~/vaults/project # Export to custom Obsidian path
strategic <path> --wiki                      # Generate crawlable Markdown wiki (index.md + community pages)
strategic <path> --neo4j                     # Generate Cypher statements (topology-out/cypher.txt)
strategic <path> --neo4j-push bolt://localhost:7687  # Directly ingest into Neo4j instance
strategic <path> --falkordb-push falkordb://localhost:6379 # Ingest into FalkorDB
strategic <path> --svg                       # Export high-resolution SVG diagram
strategic <path> --graphml                   # Export GraphML for Gephi or yEd

# 3. Targeted Query & Inspection
strategic query "<question>"                 # Breadth-First Search (BFS) for broad context
strategic query "<question>" --dfs           # Depth-First Search (DFS) to trace specific call paths
strategic query "<question>" --budget 2000   # Cap retrieval context at N tokens
strategic path "<SymbolA>" "<SymbolB>"       # Shortest path between two entities
strategic explain "<Symbol>"                 # Plain-language explanation of an entity and its cluster
strategic add <url> --author "Name"          # Ingest URL into corpus and incrementally re-index
```

---

## 4. Output Artifacts in `topology-out/`

All generated state lives under `topology-out/`:
* `graph.json`: The complete node-link JSON graph. Every link stores `source`, `target`, `relation`, and `confidence`.
* `GRAPH_REPORT.md`: Executive audit report containing God Nodes, Surprising Connections, Community Cohesion, and Suggested Questions.
* `.topology_analysis.json`: Serialized community memberships, cohesion scores, and hub rankings.
* `.topology_labels.json`: Curated human-readable community names (e.g., `0: "Payment Gateway", 1: "User Auth"`).
* `cost.json`: Cumulative token tracking across runs (`total_input_tokens`, `total_output_tokens`).
* `.vocab.txt`: Lexical vocabulary tokens extracted from node labels for IDF-safe query expansion.

---

## 5. Confidence Rubric on Relationships

Every edge emitted into the graph carries an explicit confidence level:
1. **`EXTRACTED`**: Direct syntactic statement in source code (e.g., explicit import, direct function call, class inheritance).
2. **`INFERRED`**: Deduced via second-pass resolution (e.g., Go receiver type binding, Ruby constant paths, co-occurrence in documentation, cross-tier HTTP paths).
3. **`AMBIGUOUS`**: Probabilistic or uncertain deduction (e.g., matching common method name across multiple unrelated interfaces). Flagged for human review.

---

## 6. Query Vocabulary Expansion Protocol

Before executing `strategic query` or querying the MCP server, apply the vocabulary expansion protocol to prevent zero-hit queries caused by lexical mismatch:
1. Extract vocabulary tokens from `topology-out/.vocab.txt`.
2. Map natural language query terms to exact graph vocabulary tokens (e.g., map "authentication" to `auth`, `login`, `token`).
3. Construct the expanded query string from verified tokens only. Do not invent tokens absent from the graph vocabulary.
4. Execute BFS traversal for structural overviews or DFS traversal for dependency chains.
