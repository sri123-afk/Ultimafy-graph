# Ultima-Graph

**Cost-Optimised, Evidence-First Codebase and Knowledge-Graph Intelligence**

Ultima-Graph is an agent skill that fuses deterministic AST code indexing with multimodal topological network analysis and an executive business translation layer. It equips AI coding agents (Claude Code, Google Antigravity, Cursor, Codex, OpenCode) with the ability to explore, navigate, refactor, audit, and estimate complex codebases with minimal token consumption and grounded evidence.

---

## Key Capabilities

* **Token Thrift (Cost Governor):** Replaces repetitive file crawling (`grep`/`glob`/`read` loops) with indexed retrieval, targeted line-range reads, and an append-only token ledger (`.ultima/ledger.jsonl`).
* **Evidence-First Logic Protocol:** Every statement cites an exact AST symbol identifier or file coordinates (`file:line`). All findings are tagged by confidence tier (`EXTRACTED`, `INFERRED`, `AMBIGUOUS`) with falsification checks.
* **Blast Radius and Impact Trees:** Traces upstream callers, downstream sinks, and maps git diffs directly to affected test suites.
* **Macro-Architecture Topology:** Identifies god nodes, community clusters, cohesion scores, and unexpected cross-boundary couplings.
* **Executive Translation Layer:** Converts technical debt, coupling, and architectural risks into business outcomes: release risk, downtime exposure, QA overhead, cost of delay, and implementation estimates.

---

## Installation

### Method 1: Install via Skill Directory (Recommended)

Clone or copy the `ultima-graph` folder into your agent's skill directory:

#### For Claude Code:
```bash
# User-global installation
mkdir -p ~/.claude/skills
cp -r ultima-graph ~/.claude/skills/

# Or per-project installation
mkdir -p .claude/skills
cp -r ultima-graph .claude/skills/
```

#### For Google Antigravity / Agents:
```bash
# User-global installation
mkdir -p ~/.gemini/antigravity/skills
cp -r ultima-graph ~/.gemini/antigravity/skills/

# Or per-project installation
mkdir -p .agents/skills
cp -r ultima-graph .agents/skills/
```

### Method 2: Single-Command Quick Install

Run this command inside your project directory to download and unpack the latest release:

```bash
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/latest/download/ultima-graph.tar.gz | tar -xz -C .agents/skills/
```

### Method 3: Packaged Skill Bundle

If your environment supports packaged `.skill` bundles, download `ultima-graph.skill` directly from the release assets and place it in your skill library.

---

## Directory Structure

```
ultima-graph/
├── SKILL.md                               # Master protocol and progressive disclosure router (<500 lines)
├── README.md                              # Public documentation and setup guide
├── LICENSE                                # MIT License
├── ATTRIBUTION.md                         # Upstream references and credits
├── references/
│   ├── mode-router.md                     # Intent routing matrix and 12 worked scenarios
│   ├── tactical-playbook.md               # AST indexing, symbol lookup, and impact analysis
│   ├── strategic-playbook.md              # Multimodal GraphRAG, clustering, and exports
│   ├── cost-governor.md                   # 7-rung cost ladder, budgets, stop rules, and ledger
│   ├── logic-protocol.md                  # Evidence chains, confidence tags, and falsification
│   ├── business-lens.md                   # Technical-to-business metric translation
│   ├── workflows.md                       # 12 step-by-step standard operating procedures
│   ├── output-templates.md                # Standardized response schemas with fill-in fields
│   ├── tool-detection-and-fallbacks.md    # Engine setup, MCP configs, and graceful degradation
│   └── evals.md                           # Verification prompts, pass criteria, and test runs
├── scripts/
│   ├── detect_tools.sh                    # Deterministic engine and index detector (bash)
│   ├── cost_ledger.py                     # Session cost, token, and avoidance tracker (Python stdlib)
│   └── preflight_estimate.py              # Ingestion volume and safety threshold checker (Python stdlib)
└── assets/
    ├── exec-brief.template.md             # One-page executive summary template
    ├── risk-register.template.md          # Architectural risk register template
    └── pr-triage.template.md              # Pull request triage report template
```

---

## Quick Start & Tool Detection

Run the included deterministic detection script to check your local environment:

```bash
bash scripts/detect_tools.sh .
```

The script reports whether:
1. **Tactical Engine (AST indexing):** Available and indexed.
2. **Strategic Engine (Topology & GraphRAG):** Available and clustered.
3. **Graceful Degradation:** When neither tool is installed, the skill automatically applies manual discipline (`rg -w`, line-range reads, token accounting).

---

## Token and Cost Governor

Ultima-Graph enforces a strict 7-rung Cost Ladder:

| Rung | Operation | Cost Profile |
|---|---|---|
| **L0** | In-Context Memory / Cached Report | Zero cost |
| **L1** | Deterministic Index Retrieval | Near-zero cost |
| **L2** | Cached Topology Analytics | Minimal cost |
| **L3** | Targeted Range Read (Bounded lines) | Low cost |
| **L4** | Incremental AST Synchronization | Compute only |
| **L5** | Multimodal LLM Extraction | Gated cost (Preflight approval required >500 files) |
| **L6** | Full Corpus Rebuild | Last resort |

To view accumulated session metrics and token avoidance:
```bash
python3 scripts/cost_ledger.py report
```

---

## Attribution and Upstream References

Ultima-Graph is inspired by and references foundational architectures from:

* **CodeGraph** by Colby McHenry ([github.com/colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)): Deterministic AST code intelligence, Tree-sitter kernel, SQLite WAL/FTS5 indexing, identifier sub-tokenization, and transitive test mapping.
* **Graphify** by Safi Shamsi / Graphify Labs ([github.com/Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)): Multimodal knowledge graph construction, Leiden community clustering, god-node centrality detection, cohesion scoring, and GraphRAG topological queries.

See [ATTRIBUTION.md](ATTRIBUTION.md) for full citations and architectural details.

---

## License

This project is licensed under the [MIT License](LICENSE).
