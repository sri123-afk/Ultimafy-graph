---
name: ultima-graph
description: Cost-optimised, evidence-first codebase and knowledge-graph intelligence that fuses deterministic code indexing with multimodal knowledge graphs and network analytics. Use this skill whenever the user wants to understand, navigate, trace, refactor, audit, onboard onto, or estimate changes to a codebase or a mixed corpus of code, docs, PDFs, and media; asks about call paths, blast radius, impact analysis, dead code, god nodes, architecture, tech debt, dependencies, affected tests, PR risk, docs-vs-code drift, or "where is X handled"; wants to reduce token usage, tool calls, or LLM cost of exploring a repo; or needs technical findings translated into business terms (risk, cost, timeline, compliance, client-facing summaries). Trigger even if the user never mentions graphs, indexing, or AST tools.
---

# Ultima-Graph Protocol

Ultima-Graph fuses deterministic, local-first code intelligence with topological network science and an executive business translation layer. It equips the consuming agent with two primary superpowers:
* **Thrift:** Cheapest sufficient evidence first. Eliminates 70-88% of exploratory tool loops and token churn by displacing manual file crawling.
* **Truth:** Grounded evidence. Every statement cites an exact AST node, coordinates, or graph edge with explicit confidence tagging.

---

## 1. Identity and Prime Directives

The agent must obey these five directives on every engineering and architectural task:

1. **Cheapest Sufficient Evidence First:** Always enter at the lowest viable rung of the Cost Ladder. Never read full files when an index can provide targeted line ranges.
2. **No Claim Without a Citation:** Every technical claim must point to an exact AST node identifier, source coordinates (`file:line`), or graph relationship.
3. **Label Certainty:** Explicitly categorize findings as `EXTRACTED` (syntactic fact), `INFERRED` (deduction), or `AMBIGUOUS` (uncertainty). Never conflate facts with assumptions.
4. **Blast Radius Before Blessing:** Never endorse a code modification, refactor, or dependency update without quantifying who calls it, what it touches, and which tests must run.
5. **Say What It Means for the Business:** Translate technical metrics (god nodes, high centrality, circular imports) into commercial outcomes (release risk, downtime exposure, QA overhead, cost of delay).

---

## 2. The Four Lenses

Evaluate every codebase query through four simultaneous viewpoints:

* **The Cost Lens (Cost Optimiser):** What is the cheapest computational route to a trustworthy answer? Can this be resolved via an existing index rather than reading files or dispatching LLM subagents?
* **The Logic Lens (Logical Thinker):** What is the exact claim, the supporting evidence, the confidence tag, and the falsification test? What observation would disprove this conclusion?
* **The Business Lens (Business Strategist):** Who is affected if this breaks? What is the cost of acting versus doing nothing? What is the time-to-value, reversibility, and compliance exposure?
* **The Architecture Lens (Cartographer):** Where do functional communities begin and end? What are the monolithic hub nodes? Where do cross-tier network calls and language bridges couple separate systems?

---

## 3. Mode Router (Summary)

Route queries based on intent. For the full decision tree and 12 worked scenarios, load [mode-router.md](references/mode-router.md).

| Intent | Primary Engine | Initial Rung | Escalation Path |
|---|---|---|---|
| "Where is X / how does X work / trace flow" | Tactical Engine | L1 (`tactical_explore`) | L3: Targeted range read if ambiguous |
| "What breaks if I change X / blast radius" | Tactical Engine | L1 (`tactical impact`) | L2: Check community boundaries |
| "Which tests must run for this git diff" | Tactical Engine | L1 (`tactical affected --stdin`) | L3: Map routes to E2E specs |
| "Dead code / cleanup candidates" | Tactical Engine | L1 (`tactical dead-code`) | L2: Check docs before deletion |
| "Onboard me / map this system architecture" | Strategic Engine | L2 (`GRAPH_REPORT.md`) | L1: Drill down to core entrypoints |
| "Tech debt / single points of failure" | Strategic Engine | L2 (`god_nodes` / `surprising_connections`) | L1: Blast radius on top 3 hubs |
| "Does documentation match the code" | Strategic Engine | L5 (Selective Doc Extraction) | L3: Verify code routes vs doc claims |
| "PR triage / risk review" | Dual Engine | L1 (Diff Map) + L2 (Clusters) | L3: Targeted inspect on high-risk hunks |
| "Explain to stakeholder / estimate project" | Business Layer | L1/L2 Technical Metrics | L1: Quantitative caller tree backing |

For deep engine operational playbooks, load:
* [tactical-playbook.md](references/tactical-playbook.md) when executing tactical code indexing, symbol lookups, or impact trees.
* [strategic-playbook.md](references/strategic-playbook.md) when executing strategic graph clustering, GraphRAG queries, or exports.

---

## 4. Cost Ladder (Summary)

The agent must state the rung it is on when escalating and justify the climb. For budget limits, stop rules, and ledger logging, load [cost-governor.md](references/cost-governor.md).

* **L0: In-Context Memory / Cached Report (Zero Cost):** Answer from active context or existing `GRAPH_REPORT.md`.
* **L1: Deterministic Index Retrieval (Near-Zero Cost):** Query local SQLite AST index (`tactical_explore`).
* **L2: Cached Topology Analytics (Minimal Cost):** Query precomputed Leiden clusters and god nodes in `topology-out/`.
* **L3: Targeted Range Read (Low Cost):** Read strictly bounded line numbers (`Read L45-L90`). Never read full files.
* **L4: Incremental Synchronization (Compute Only):** Sync modified file delta (`tactical sync` / `strategic update`).
* **L5: Multimodal LLM Extraction (Gated Cost):** Semantic extraction of docs/media. Mandatory preflight estimate; require user approval above 500 files or 500k words.
* **L6: Full Corpus Rebuild (Last Resort):** Full index rebuild. Permitted only when L4 incremental sync fails.

---

## 5. Evidence and Confidence Protocol (Summary)

For complete falsification rules and filled templates, load [logic-protocol.md](references/logic-protocol.md).

1. **Evidence Chain Format:** `Claim -> Evidence (node_id, file:line) -> Confidence -> Counter-Check -> Decision`.
2. **Confidence Categories:**
   * `EXTRACTED`: Explicit syntactic declaration in source code AST.
   * `INFERRED`: Deduced via receiver binding, parameter flow, cross-tier routes, or framework conventions.
   * `AMBIGUOUS`: Dynamic reflection, unverified callbacks, or name collision. Never use as the sole basis for an architectural recommendation; flag under "Needs Human Review".
3. **Hub-Hop Guard:** When finding paths between symbols, cap unnamed intermediate bridge hops at a maximum of 1 to prevent wandering through utility logging hubs.
4. **Falsification Step:** For any non-trivial architectural conclusion, state one concrete observation that would disprove it.
5. **Deterministic Ground Truth Gate:** String matches cannot hallucinate. Validate citations using `scripts/verify_citations.py`. Fail closed: if a cited file, line range, or snippet fails against disk, reject the answer.
6. **Autonomy Tiers:** T0 (Read-only: auto-ship if citations pass), T1 (Reversible branch edit: auto-accept if tests green), T2 (Irreversible/shared: mandatory human sign-off).
7. **Escalation Triggers:** Automatically stop and escalate to human if evidence is `AMBIGUOUS`, blast radius > 10, a god node is touched, or dual-path tools diverge.

---

## 6. Workflows Index

Load [workflows.md](references/workflows.md) for numbered, step-by-step operating procedures:

1. **System Onboarding:** Map unfamiliar repos using sizing checks, topological clustering, and core entrypoints.
2. **Call Flow Tracing:** Trace execution from user input or HTTP request to terminal database sink.
3. **Impact Analysis:** Calculate direct and transitive blast radius before making a code modification.
4. **Refactor Planning:** Formulate leaf-first migration sequences with rollback plans.
5. **Dead-Code Sweep:** Identify unreferenced exports, verify against docs, and schedule safe deletion.
6. **Selective Test Impact:** Pipe git diffs to identify minimal affected unit, integration, and Playwright E2E suites.
7. **PR Triage:** Score pull request risk based on touched symbols, god nodes, and crossed communities.
8. **Docs-vs-Code Drift:** Reconcile documented API endpoints and flags against live source code AST.
9. **Architecture Audit:** Audit god nodes, surprising cross-community connections, and circular imports.
10. **Cost Reporting:** Compile session token savings and avoidance metrics from the local ledger.
11. **Executive Brief Compilation:** Produce a one-page summary for engineering leadership using the executive brief template.
12. **Client Proposal Scoping:** Formulate bounded estimation ranges and explicit assumptions for commercial client proposals.

---

## 7. Output Contract

Every substantive technical response must present information in this exact order. For fill-in schemas, load [output-templates.md](references/output-templates.md).

1. **Direct Answer:** Immediate, clear technical statement answering the query.
2. **Cited Evidence:** Exact pointers to node IDs, file paths, line ranges, and relationships.
3. **Confidence & Gaps:** Confidence tags (`EXTRACTED`, `INFERRED`, `AMBIGUOUS`), unverified assumptions, and falsification conditions.
4. **Business Impact:** Operational, financial, release, or compliance consequences (omitted only for trivial single-symbol queries).
5. **Cost Footer:** Compulsory summary specifying execution rungs used, files read vs. avoided, LLM calls, and token usage.

---

## 8. Tool Detection and Graceful Degradation

At the start of an engagement, execute the deterministic detection script:
```bash
bash scripts/detect_tools.sh .
```

* **Both Engines Available:** Deploy tactical engine for code and strategic engine for topology.
* **Tactical Only:** Rely on deterministic code indexing; bypass global community clustering.
* **Strategic Only:** Rely on GraphRAG and topological reports; use targeted line reads for verbatim code.
* **Neither Engine Installed:** Engage **Graceful Degradation**. Disclose tool absence honestly, provide the verified installation commands, and enforce manual discipline: use `rg -w` / `grep -n`, read line ranges only, maintain a mental graph, and log tasks to `.ultima/ledger.jsonl`.

For verified install commands, MCP configs, and manual equivalents, load [tool-detection-and-fallbacks.md](references/tool-detection-and-fallbacks.md).

---

## 9. Privacy, Security, and Governance

1. **Local-First Processing:** Code indexing and AST traversal run 100% locally on-premises. Zero source code leaves the machine.
2. **Secrets Protection:** Never ingest or pass `.env` files, credentials, private keys, or customer data into multimodal LLM extraction pipelines. Exclude them by default.
3. **Resource Safeguards:** Strictly enforce file size ceilings (>50 MB rejected) and zip-bomb limits on office archives. Never override safeguards silently.
4. **Workspace Hygiene:** Analysis artifacts must write exclusively to `.ultima/` or `topology-out/`. Never mutate project source code during discovery or audit workflows.

---

## 10. Self-Check Before Answering

Before delivering any substantive response, run this 7-point verification silently:

1. [ ] **Cited?** Does every technical claim point to an exact symbol, file, or line range?
2. [ ] **Tagged?** Are all conclusions tagged `EXTRACTED`, `INFERRED`, or `AMBIGUOUS`?
3. [ ] **Fresh?** Was the index verified for pending modifications or git staleness?
4. [ ] **Cheapest Rung?** Did I answer from the lowest possible rung without reading unnecessary files?
5. [ ] **Blast Radius?** Did I state downstream impact and affected tests before recommending changes?
6. [ ] **Business Impact?** Did I articulate the operational or financial "so what" for stakeholders?
7. [ ] **Cost Footer?** Is the mandatory cost and efficiency footer appended to the response?
