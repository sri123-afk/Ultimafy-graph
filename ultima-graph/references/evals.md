# Ultima-Graph Evaluation Suite: Benchmarks and Pass Criteria

This reference defines the evaluation benchmark suite for validating ultima-graph behavior. Load this file when running dry-run evaluations or auditing agent compliance against protocol standards.

---

## Benchmark Scenarios (10 Core Scenarios)

### Scenario 1: Precision Code Lookup
* **Prompt:** "Where do we handle failed payment retries?"
* **Target Engine & Rung:** Tactical Engine | Rung L1.
* **Pass Criteria:**
  - [ ] Invokes single retrieval tool (`tactical_explore` / `tactical explore`).
  - [ ] Returns verbatim line-numbered source snippet with exact file:line citation.
  - [ ] Zero whole-file reads performed.
  - [ ] Standard Cost Footer appended with measured/estimated tokens.

### Scenario 2: Blast Radius & Test Impact
* **Prompt:** "I'm changing `OrderService.cancel`. What can break and what should I test?"
* **Target Engine & Rung:** Tactical Engine | Rung L1.
* **Pass Criteria:**
  - [ ] Computes direct and transitive caller tree to depth >= 2.
  - [ ] Lists specific test spec files affected by the change.
  - [ ] Explicitly tags business failure consequence (e.g., impact on order fulfillment or refund flow).
  - [ ] States whether full regression suite is mandated.

### Scenario 3: System Onboarding with Mixed Corpus
* **Prompt:** "I just joined. Give me a map of this repo and the docs."
* **Target Engine & Rung:** Strategic Engine | Rung L2.
* **Pass Criteria:**
  - [ ] Runs `preflight_estimate.py` before attempting any extraction.
  - [ ] Checks for existing `GRAPH_REPORT.md` before initiating builds.
  - [ ] Summarizes core Leiden community clusters and their domain responsibilities.
  - [ ] Does NOT trigger L5 multimodal extraction across whole corpus without explicit consent.

### Scenario 4: Architectural Risk & Hotspot Audit
* **Prompt:** "What are the scariest parts of this codebase?"
* **Target Engine & Rung:** Strategic Engine | Rung L2.
* **Pass Criteria:**
  - [ ] Identifies top 3-5 high-centrality God Nodes (excluding stdlib noise).
  - [ ] Identifies cross-community or cross-language surprising connections.
  - [ ] Translates technical hubs into business single-points-of-failure and key-person risks.
  - [ ] Includes explicit list of `AMBIGUOUS` relationships requiring human review.

### Scenario 5: Documentation-vs-Code Drift Audit
* **Prompt:** "Does our README match what the code actually does?"
* **Target Engine & Rung:** Strategic Engine | Rung L5 (Selective).
* **Pass Criteria:**
  - [ ] Extracts documented endpoints and CLI flags from README.
  - [ ] Compares documented declarations against live AST routes.
  - [ ] Formulates a drift ledger with confidence ratings (`EXTRACTED` missing symbols vs `INFERRED` signature drift).
  - [ ] Does not re-extract non-documentation files.

### Scenario 6: Selective Test Impact Gating
* **Prompt:** "Here's a git diff. Which E2E suites must run?"
* **Target Engine & Rung:** Tactical Engine | Rung L1.
* **Pass Criteria:**
  - [ ] Runs `tactical affected` on the diff file list.
  - [ ] Maps modified web routes or UI components to corresponding Playwright/Cypress E2E specs.
  - [ ] Recommends a minimal CI gate test list.
  - [ ] Evaluates full-regression trigger rule (>15 callers or core hub touched).

### Scenario 7: Executive Client Proposal
* **Prompt:** "Write a one-pager for the client explaining the risk of touching the auth module."
* **Target Engine & Rung:** Business Translation Layer.
* **Pass Criteria:**
  - [ ] Output strictly adheres to `exec-brief.template.md`.
  - [ ] Provides low-to-high effort ranges based on quantitative caller counts.
  - [ ] States explicit assumptions and narrowing conditions.
  - [ ] Uses zero technical jargon without plain-English definitions; emphasizes data privacy.

### Scenario 8: Graceful Degradation (Zero Tools Installed)
* **Prompt:** "Neither tool is installed. Help me trace the checkout flow anyway."
* **Target Engine & Rung:** Graceful Degradation Protocol.
* **Pass Criteria:**
  - [ ] Openly acknowledges absence of indexing engines without fabricating results.
  - [ ] Provides verified one-line installation commands for both engines.
  - [ ] Employs manual discipline: uses `grep -n` / `rg -w` and strict line-range reads (`Read` lines N-M).
  - [ ] Logs task execution in `.ultima/ledger.jsonl` noting fallback status.

### Scenario 9: Sizing Threshold Enforcement
* **Prompt:** "Index everything including all our PDFs and videos."
* **Target Engine & Rung:** Preflight Gate & Cost Governor.
* **Pass Criteria:**
  - [ ] Executes `preflight_estimate.py` and inspects file counts and word mass.
  - [ ] Triggers warning if corpus exceeds 500,000 words or 500 files.
  - [ ] Refuses to trigger L5 semantic extraction without explicit user approval.
  - [ ] Excludes `.env`, credential, and customer data files by default.

### Scenario 10: Falsification of Ambiguous Relationship
* **Prompt:** "The graph says A calls B but I don't think it does."
* **Target Engine & Rung:** Logic Protocol & Falsification.
* **Pass Criteria:**
  - [ ] Inspects edge metadata and confidence tag (`EXTRACTED` vs `INFERRED` vs `AMBIGUOUS`).
  - [ ] Checks whether the edge was formed via parameter flow, framework routing, or name coincidence.
  - [ ] Proposes a concrete falsification check (e.g., checking if the call is wrapped in an inactive conditional).
  - [ ] Updates decision based on verified line coordinates.

---

## Adversarial & Edge Cases (4 Scenarios)

### Scenario 11: Stale Index Drift
* **Condition:** A file was modified on disk 500ms prior to the query.
* **Pass Criteria:**
  - [ ] Detects watcher staleness banner (`[STALENESS WARNING]`).
  - [ ] Flags that line numbers in the modified file may have shifted.
  - [ ] Executes Rung L4 sync (`tactical sync`) or performs a targeted live read on the modified file.

### Scenario 12: Zero-Hit Query via Vocabulary Mismatch
* **Condition:** User queries "Where is authorization logic?" on a codebase that names its module `GuardianSecurity`.
* **Pass Criteria:**
  - [ ] Does NOT conclude that authorization does not exist.
  - [ ] Reads `topology-out/.vocab.txt` to expand query terms to `guardian`, `security`, `credential`.
  - [ ] Re-runs traversal using verified vocabulary tokens.

### Scenario 13: High-Scale Monorepo Flood
* **Condition:** Monorepo with 5,000+ files and 20+ packages.
* **Pass Criteria:**
  - [ ] Caps explore bridge hops to avoid wandering through utility hubs.
  - [ ] Scopes tactical indexing to the active package directory (`--path`).
  - [ ] Warns before global clustering.

### Scenario 14: Generated Code Pollution
* **Condition:** Repository contains 100,000 lines of generated protobuf code (`*.pb.go`).
* **Pass Criteria:**
  - [ ] Generated code detection identifies `DO NOT EDIT` banners.
  - [ ] Generated symbols are deprioritized in search results and excluded from god-node rankings.
  - [ ] Analysis focuses strictly on hand-written business services.
