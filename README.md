# Ultima-Graph

**Cost-Optimised, Evidence-First Codebase and Knowledge-Graph Intelligence Protocol**

Ultima-Graph is an open-source agent skill and operational protocol for AI coding agents (Claude Code, Google Antigravity, Cursor, OpenCode, Codex). It fuses deterministic AST code indexing with multimodal topological network analysis and an executive business translation layer.

> **Architecture Note:** Ultima-Graph is an **instruction and governance protocol layer**. The indexing engines, [CodeGraph](https://github.com/colbymchenry/codegraph) (tactical: symbols, callers, impact, affected tests) and [Graphify](https://github.com/Graphify-Labs/graphify) (strategic: communities, god nodes, code↔docs graph), are optional external tools. When installed, Ultima-Graph routes questions to them. When absent, it runs in **Degraded Mode** with targeted search discipline.

---

## Why Ultima-Graph?

Unguided coding agents spend much of their token budget and latency on iterative `grep`/`glob`/`read` loops, sometimes cite line numbers that don't exist, and describe structural debt in jargon that stakeholders can't evaluate.

Ultima-Graph solves this with four core pillars:

1. **Token Thrift (The Cost Ladder):** Cheapest sufficient evidence first: context → CodeGraph → Graphify → targeted reads → incremental refresh → (gated) LLM extraction. Optional hash-chained cost ledger for benchmarking.
2. **Deterministic Ground Truth:** Validation ends at disk, not at another LLM. `scripts/verify_citations.py` checks that cited files exist inside the repo, ranges are in bounds, and symbols/snippets appear there. Negative claims ("unused") need two independent witnesses.
3. **Autonomy Tiers:** T0 (read-only), T1 (reversible edits), T2 (shared/irreversible, needs human approval). Risky edits are confirmed first; analysis is never blocked.
4. **Executive Translation Layer:** Turns god nodes, churn × centrality hotspots, blast radius, and cycles into release risk, QA scope, key-person risk, and ranged estimates. Dollar figures only come from inputs you provide.

---

## What to expect (and how to measure it)

Ultima-Graph is a protocol, so its savings come from the engines it routes to and from the discipline it enforces (no re-reads, range reads, batched queries, no indexing tiny repos).

| Lever | Effect |
|---|---|
| `codegraph_explore` instead of grep→read loops | One call returns verbatim source plus callers. CodeGraph publishes its own with/without-MCP benchmarks in its README |
| `GRAPH_REPORT.md` / `graphify query --budget` | Architecture answers from a cached graph instead of reading dozens of files |
| Proportionate output and gates | No mandatory footers, ledger calls, or verifier runs on trivial answers |
| Code-only graph refresh (`scripts/update.sh`) | Keeps indexes fresh with zero LLM tokens |

**Measure it on your own repo:** run the same questions with and without the skill, and compare tool calls and tokens (`graphify benchmark`, or `scripts/cost_ledger.py` for per-task logs). Don't trust any number you haven't reproduced, including ours.

---

## Autonomy Tiers & Gates

| Tier | Scope | Gate |
|---|---|---|
| **T0** | Read-only answers, navigation, audits | Citations sound; `verify_citations.py` for written deliverables |
| **T1** | Reversible edits on a branch | Build + type-check + affected tests green |
| **T2** | Merge, deploy, migration, deletions, secrets | **Explicit human approval** |

The agent **asks before editing** (it never refuses to analyze) when a change touches a god node, has a high blast radius, crosses a tier/language boundary, has no covering tests, or rests on `AMBIGUOUS` evidence. Thresholds live in one table in `SKILL.md` §5.

---

## Installation

### For Claude Code
```bash
# Global installation (recommended)
mkdir -p ~/.claude/skills
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/ultima-graph.tar.gz | tar -xz -C ~/.claude/skills/

# Or per-project installation
mkdir -p .claude/skills
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/ultima-graph.tar.gz | tar -xz -C .claude/skills/
```

### For Google Antigravity
```bash
# Global installation
mkdir -p ~/.gemini/antigravity/skills
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/ultima-graph.tar.gz | tar -xz -C ~/.gemini/antigravity/skills/

# Or per-project installation
mkdir -p .agents/skills
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/ultima-graph.tar.gz | tar -xz -C .agents/skills/
```

### For OpenCode
```bash
mkdir -p ~/.opencode/skills
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/ultima-graph.tar.gz | tar -xz -C ~/.opencode/skills/
```

### For Cursor
Add a reference to the skill in your project's `.cursor/rules/ultima-graph.mdc` or `.cursorrules`:
```markdown
Always follow the Ultima-Graph protocol located at .agents/skills/ultima-graph/SKILL.md
for code exploration, blast radius analysis, and citation verification.
```

### For Codex & Universal Agent CLIs
Include the skill directory under `.agents/skills/ultima-graph` and reference `ultima-graph/SKILL.md` in your repository's root `AGENTS.md`.

---

## Single-Command Install with Checksum Verification

To download and verify the release archive before extracting:

```bash
mkdir -p .agents/skills
curl -fsSL -o /tmp/ultima-graph.tar.gz https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/ultima-graph.tar.gz

# Optional: verify SHA-256 checksum
curl -fsSL https://github.com/sri123-afk/Ultimafy-graph/releases/download/v1.0/checksums.sha256 | shasum -a 256 --check --ignore-missing

tar -xzf /tmp/ultima-graph.tar.gz -C .agents/skills/
rm /tmp/ultima-graph.tar.gz
```

---

## Degraded Mode (Standalone / Zero-Dependency Mode)

When neither engine is installed, Ultima-Graph runs in **Degraded Mode**: precise `rg -w` searches, range reads around hits (whole files only when small), lexical evidence tagged `INFERRED`, and one-line install guidance:

```bash
npm i -g @colbymchenry/codegraph && codegraph install -y -t auto   # CodeGraph + MCP wiring
uv tool install graphifyy                                          # Graphify (PyPI name has two y's)
bash scripts/update.sh --init                                      # build both indexes locally, no LLM
```

---

## Directory Structure

```
ultima-graph/
├── SKILL.md                               # Master protocol and progressive disclosure router (<500 lines)
├── README.md                              # Public documentation and setup guide
├── LICENSE                                # MIT License
├── NOTICE                                 # Upstream notices
├── ATTRIBUTION.md                         # Detailed upstream references and credits
├── references/
│   ├── mode-router.md                     # Intent routing matrix and 14 worked scenarios
│   ├── tactical-playbook.md               # CodeGraph: verified CLI/MCP, impact, affected tests
│   ├── strategic-playbook.md              # Graphify: verified CLI/MCP, cost split, clustering, exports
│   ├── cost-governor.md                   # 7-rung cost ladder, budgets, stop rules, and ledger
│   ├── logic-protocol.md                  # Evidence chains, confidence tags, and falsification
│   ├── business-lens.md                   # Technical-to-business metric translation
│   ├── workflows.md                       # 18 procedures (update, onboarding … bug root-cause, hotspots, upgrades, security flow)
│   ├── output-templates.md                # Standardized response schemas with fill-in fields
│   ├── tool-detection-and-fallbacks.md    # Engine setup, MCP configs, and graceful degradation
│   └── evals.md                           # Verification prompts, pass criteria, and test runs
├── scripts/
│   ├── update.sh                          # "ultima-graph update": refresh stale indexes, no LLM tokens
│   ├── detect_tools.sh                    # Engine, version, freshness & feature detector (JSON)
│   ├── cost_ledger.py                     # Session cost, token, and hash-chained ledger (Python stdlib)
│   ├── verify_citations.py                # Deterministic ground-truth citation verifier (Python stdlib)
│   ├── preflight_estimate.py              # Ingestion volume and safety threshold checker (Python stdlib)
│   └── package.sh                         # Package distribution bundles and generate checksums
└── assets/
    ├── exec-brief.template.md             # One-page executive summary template
    ├── risk-register.template.md          # Architectural risk register template
    └── pr-triage.template.md              # Pull request triage report template
```

---

## Tooling & Verification Commands

### 1. Detect Engines & Update Indexes
```bash
bash scripts/detect_tools.sh .        # JSON: binaries, versions, freshness, stale files
bash scripts/update.sh --check        # dry run (exit 10 = stale)
bash scripts/update.sh                # refresh only stale engines (codegraph sync + graphify update)
bash scripts/update.sh --init         # first-time local index build
python3 scripts/preflight_estimate.py .   # code vs LLM-bound cost split, sensitive files
```

### 2. Verify Citations (Ground Truth Gate)
```bash
# Validate citations from markdown response
python3 scripts/verify_citations.py --input-file response.md

# Run canary integrity checks
python3 scripts/verify_citations.py --canary
```

### 3. Track Session Tokens and Audit Ledger
```bash
# View session token savings report
python3 scripts/cost_ledger.py report

# Verify cryptographic hash-chain integrity
python3 scripts/cost_ledger.py verify
```

### 4. Build Release Packages
```bash
bash scripts/package.sh
```

---

## Attribution and Upstream References

Ultima-Graph is inspired by and references foundational architectures from:

* **CodeGraph** by Colby McHenry ([github.com/colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)): Deterministic AST code intelligence, Tree-sitter kernel, SQLite WAL/FTS5 indexing, identifier sub-tokenization, and transitive test mapping.
* **Graphify** by Safi Shamsi / Graphify Labs ([github.com/Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)): Multimodal knowledge graph construction, Leiden community clustering, god-node centrality detection, cohesion scoring, and GraphRAG topological queries.

See [ATTRIBUTION.md](ATTRIBUTION.md) and [NOTICE](NOTICE) for full citations and architectural details.

---

## License

This project is licensed under the [MIT License](LICENSE).
