# Ultima-Graph Workflows: Step-by-Step Operating Procedures

This reference contains 12 end-to-end recipes. Load this file when executing a multi-step engineering, architecture, testing, or business evaluation workflow.

---

## Workflow 1: System Onboarding (Unfamiliar Codebase)

* **Trigger Phrases:** "Onboard me", "Map this repository", "Explain how this system is structured", "Give me a tour of the code".
* **Preconditions:** Repository cloned locally; `scripts/detect_tools.sh` executed.
* **Step-by-Step Procedure:**
  1. **Run Preflight Sizing [Rung L0]:** Execute `python3 scripts/preflight_estimate.py .` to determine corpus size and file breakdown.
  2. **Inspect Cached Architecture Report [Rung L2]:** Check for existing `topology-out/GRAPH_REPORT.md`. If present, read the Executive Summary, God Nodes, and Community Breakdown.
  3. **Build Strategic Graph (if missing) [Rung L2 / L4]:** If `topology-out/graph.json` is missing, execute `strategic . --no-viz` (or `strategic` with visualization if requested).
  4. **Examine Top Communities [Rung L2]:** Identify the top 3-5 functional clusters and their domain roles.
  5. **Drill Down to Core Entrypoints [Rung L1]:** For each core community, use the tactical engine (`tactical explore "<CommunityName> entrypoint"`) to inspect primary controllers and interfaces.
* **Output Reference:** Template 6 (`Onboarding Map & Architectural Tour`).
* **Stop Condition:** Primary entrypoints, core data models, and main external dependencies are mapped.
* **Common Failure & Fix:**
  * *Failure:* Strategic engine build times out on a massive repository (>2,000 files).
  * *Fix:* Execute `tactical files` and `tactical query` on the top-level directories to build an incremental map without whole-corpus clustering.

---

## Workflow 2: Call Flow Tracing (End-to-End)

* **Trigger Phrases:** "Trace how X reaches Y", "How does a request get processed", "Follow this event to the database".
* **Preconditions:** Tactical engine index (`.ultima/tactical.db`) exists and is fresh.
* **Step-by-Step Procedure:**
  1. **Extract Endpoint Symbols [Rung L0]:** Identify the source symbol (e.g., API route or UI event) and the sink symbol (e.g., database mutation or third-party call).
  2. **Query Named Symbol Flow [Rung L1]:** Execute `tactical_explore "<SourceSymbol> <SinkSymbol>"` (or CLI `tactical explore`).
  3. **Traverse Synthesized Hops [Rung L1]:** Verify if the flow crosses dynamic-dispatch boundaries (framework routes, client fetch literals, mobile bridges).
  4. **Targeted Verification (if needed) [Rung L3]:** If intermediate logic contains conditional branching or filters, read the exact line range (`L<start>-L<end>`) using `Read`.
* **Output Reference:** Template 2 (`End-to-End Call Flow Report`).
* **Stop Condition:** Unbroken call path established from source to sink with cited line coordinates.
* **Common Failure & Fix:**
  * *Failure:* Tactical engine returns disconnected symbols without a call path.
  * *Fix:* Check if an intermediate event bus or queue decouples the call. Supply the intermediate queue topic name into `tactical_explore`.

---

## Workflow 3: Impact Analysis & Blast Radius Evaluation

* **Trigger Phrases:** "What breaks if I change X", "Blast radius of modifying Y", "Who calls this function".
* **Preconditions:** Tactical engine index is active.
* **Step-by-Step Procedure:**
  1. **Locate Target Symbol [Rung L1]:** Query `tactical node <SymbolName>` to confirm exact signature and coordinate location.
  2. **Compute Caller Hierarchy [Rung L1]:** Execute `tactical callers <SymbolName>` to list immediate callers.
  3. **Calculate Recursive Blast Radius [Rung L1]:** Execute `tactical impact <SymbolName> --depth 3 --json` to generate the complete transitive dependency tree.
  4. **Cross-Community Risk Check [Rung L2]:** Check whether impacted callers reside within the same module or span foreign communities in `topology-out/graph.json`.
  5. **Map Business Impact [Business Lens]:** Translate caller count and impacted domains into a risk exposure rating.
* **Output Reference:** Template 3 (`Impact & Blast Radius Report`).
* **Stop Condition:** Transitive caller tree enumerated to depth 3; business downside identified.
* **Common Failure & Fix:**
  * *Failure:* High-degree utility function (e.g., `logger.error`) causes impact radius to encompass 1,000+ files.
  * *Fix:* Filter out utility hubs by scoping the impact query to non-utility calling packages.

---

## Workflow 4: Refactor Planning

* **Trigger Phrases:** "Plan refactoring of X", "How to decouple module Y", "Migration plan for service Z".
* **Preconditions:** Impact analysis (Workflow 3) completed.
* **Step-by-Step Procedure:**
  1. **Compile Dependency Boundary [Rung L1]:** Identify all inbound edges entering the target refactoring zone.
  2. **Design Intermediate Abstraction [Rung L0 / Architecture Lens]:** Formulate an adapter, facade, or interface to shield external callers.
  3. **Sequence Refactoring Steps [Rung L1]:** Order modifications leaf-first (callees first, callers last) to keep the build green at each commit.
  4. **Define Rollback & Safety Nets [Business Lens]:** Determine whether the refactor is a two-way or one-way door; specify feature-flag gating if appropriate.
* **Output Reference:** Template 7 (`Refactoring & Migration Plan`).
* **Stop Condition:** Numbered step-by-step refactor plan with verification gates and rollback procedure.
* **Common Failure & Fix:**
  * *Failure:* Circular dependencies make leaf-first refactoring impossible.
  * *Fix:* Run `tactical cycles` to locate the circular import, and add an initial Step 0 to extract the shared types to a neutral leaf module.

---

## Workflow 5: Dead-Code Sweep

* **Trigger Phrases:** "Find dead code", "Purge unused functions", "Cleanup unused exports".
* **Preconditions:** Tactical engine index is fresh.
* **Step-by-Step Procedure:**
  1. **Run Dead-Code Detection [Rung L1]:** Execute `tactical dead-code [path]` to identify unreferenced exports (0 inbound calls, 0 imports).
  2. **Filter Framework Entrypoints [Rung L1]:** Discard false positives (exported route handlers, CLI commands, test runners, public API library exports).
  3. **Check Documentation Mentions [Rung L2]:** Verify whether identified candidates are referenced in Markdown docs or schema files in `topology-out/graph.json`.
  4. **Tag Confidence & Human Review [Logic Protocol]:** Label candidates as `EXTRACTED (Verified Dead)` or `AMBIGUOUS (Dynamic Reflection Risk)`.
* **Output Reference:** Template 8 (`Dead Code Cleanup Audit`).
* **Stop Condition:** Prioritized list of deletion candidates with retained reasons.
* **Common Failure & Fix:**
  * *Failure:* Exported method is called via reflection or dynamic string lookup in configuration.
  * *Fix:* Perform a tight lexical check on the candidate's name tail before deleting.

---

## Workflow 6: Selective Test Impact (CI & Git Diff Gating)

* **Trigger Phrases:** "Which tests must run", "Affected test specs for this commit", "Minimal CI gate for diff".
* **Preconditions:** Git repository with unstaged changes or git diff against target branch.
* **Step-by-Step Procedure:**
  1. **Pipe Git Diff to Tactical Engine [Rung L1]:** Execute:
     ```bash
     git diff --name-only origin/main...HEAD | tactical affected --stdin --quiet
     ```
  2. **Partition Unit & Integration Tests [Rung L1]:** Group returned test files by test runner (e.g., Vitest, Jest, Pytest).
  3. **Map Route Changes to E2E Suites [Rung L1 / L3]:** If modified files define web routes or UI components, map their URL paths to corresponding Playwright or Cypress E2E specs.
  4. **Evaluate Full Regression Rule [Logic Protocol]:** If any changed symbol has > 15 inbound callers or touches a designated core hub, trigger the full test suite instead of the minimal gate.
* **Output Reference:** Template 4 (`Selective Test Execution Report`).
* **Stop Condition:** Minimal test spec list produced with explicit full-regression trigger verdict.
* **Common Failure & Fix:**
  * *Failure:* `tactical affected` returns 0 test files despite source changes.
  * *Fix:* Check test file glob configuration in `tactical.json` or pass explicit `--filter "**/*.spec.ts"`.

---

## Workflow 7: Pull Request Triage & Risk Review

* **Trigger Phrases:** "Triage this PR", "Review PR risk", "Risk evaluation on pull request".
* **Preconditions:** Git diff available; both tactical and strategic engines initialized.
* **Step-by-Step Procedure:**
  1. **Identify Modified Symbols [Rung L1]:** Extract symbols modified in the PR diff.
  2. **Calculate Inbound Blast Radius [Rung L1]:** Count direct and transitive inbound callers for modified symbols.
  3. **Detect Crossed Architectural Communities [Rung L2]:** Check if modified symbols reside in multiple functional clusters.
  4. **Identify Touched Hub Nodes [Rung L2]:** Cross-reference modified symbols against the top 10 God Nodes.
  5. **Compile PR Triage Form [Business Lens]:** Categorize PR risk as Low, Moderate, High, or Critical.
* **Output Reference:** `assets/pr-triage.template.md`.
* **Stop Condition:** PR Triage form completed with reviewer focus list.
* **Common Failure & Fix:**
  * *Failure:* PR contains 5,000+ line diff due to lockfiles or generated assets.
  * *Fix:* Filter out lockfiles and generated assets (`git diff -- . ':!package-lock.json' ':!*.pb.go'`).

---

## Workflow 8: Documentation-vs-Code Drift Audit

* **Trigger Phrases:** "Audit docs against code", "Does README match implementation", "Check API doc drift".
* **Preconditions:** Documentation files exist in repository.
* **Step-by-Step Procedure:**
  1. **Run Preflight Check [Rung L0]:** Check word count of documentation files via `scripts/preflight_estimate.py`.
  2. **Extract Declared Endpoints & Examples [Rung L5]:** Extract documented function signatures, CLI flags, and route endpoints from Markdown files.
  3. **Verify Against Code AST [Rung L1]:** Query the tactical index for each documented symbol or endpoint.
  4. **Compile Drift Ledger [Logic Protocol]:** Label mismatches with confidence ratings (`EXTRACTED (Missing Symbol)`, `INFERRED (Signature Drift)`).
* **Output Reference:** Template 9 (`Documentation Drift Ledger`).
* **Stop Condition:** All documented API claims verified or flagged as drifted.
* **Common Failure & Fix:**
  * *Failure:* L5 extraction exceeds token budget on massive doc folder.
  * *Fix:* Restrict audit to top-level `README.md` and primary `docs/` specifications.

---

## Workflow 9: Architecture Audit & Technical Debt Assessment

* **Trigger Phrases:** "Perform architecture audit", "Identify technical debt", "Assess code quality and coupling".
* **Preconditions:** Strategic engine graph (`topology-out/graph.json`) generated.
* **Step-by-Step Procedure:**
  1. **Analyze God Nodes [Rung L2]:** Retrieve top 5-10 highest-degree nodes using `strategic god_nodes` or inspecting `GRAPH_REPORT.md`.
  2. **Inspect Surprising Connections [Rung L2]:** Review cross-community edges bridging disparate subsystems or languages.
  3. **Evaluate Community Cohesion [Rung L2]:** Identify clusters with cohesion scores below 0.40 (indicating poorly encapsulated spaghetti code).
  4. **Check Circular Imports [Rung L1]:** Run `tactical cycles` to find architectural cycles.
  5. **Formulate Prioritized Remediation Backlog [Business Lens]:** Rank findings by business impact and estimate refactoring effort.
* **Output Reference:** Template 5 (`Architecture Audit & Debt Report`).
* **Stop Condition:** Top architectural hotspots identified with remediation recommendations.
* **Common Failure & Fix:**
  * *Failure:* Standard library utilities (e.g., `dict`, `object`, `String`) pollute god node rankings.
  * *Fix:* Ensure stdlib noise filters in `analyze.py` are respected; filter non-project nodes.

---

## Workflow 10: Session Cost & Efficiency Reporting

* **Trigger Phrases:** "Show cost report", "How many tokens did we save", "Session efficiency audit".
* **Preconditions:** At least one task recorded in `.ultima/ledger.jsonl`.
* **Step-by-Step Procedure:**
  1. **Execute Ledger Summary [Rung L0]:** Run `python3 scripts/cost_ledger.py report`.
  2. **Compare Against Baseline:** Compute estimated tokens saved versus a brute-force Grep-and-Read baseline.
  3. **Audit Escalation Justifications:** Review instances where execution escalated to Rung L5 or L6.
* **Output Reference:** Template 10 (`Session Cost & Efficiency Report`).
* **Stop Condition:** Formatted cost report presented to user.
* **Common Failure & Fix:**
  * *Failure:* Ledger file missing or corrupt.
  * *Fix:* Run `scripts/cost_ledger.py reset` and log current session retrospectively.

---

## Workflow 11: Executive Architectural Brief Compilation

* **Trigger Phrases:** "Prepare executive brief", "Write one-pager for VP of Engineering", "Summarize architecture for CTO".
* **Preconditions:** Architecture audit (Workflow 9) or Impact analysis (Workflow 3) completed.
* **Step-by-Step Procedure:**
  1. **Extract Core Metrics [Rung L0 / L2]:** Gather total component counts, hub centrality scores, and cohesion ratings.
  2. **Formulate Executive Narrative [Business Lens]:** Draft 1-2 sentence commercial bottom line.
  3. **Populate Brief Template [Business Lens]:** Complete `assets/exec-brief.template.md`.
  4. **Perform Self-Check:** Verify zero technical jargon without plain-language explanation; verify data privacy guarantees.
* **Output Reference:** `assets/exec-brief.template.md`.
* **Stop Condition:** Complete one-page brief ready for executive delivery.
* **Common Failure & Fix:**
  * *Failure:* Brief is too technical for C-level readers.
  * *Fix:* Replace class and method names in the executive summary with user journey and financial impact terms.

---

## Workflow 12: External Client Estimate & Proposal Scoping

* **Trigger Phrases:** "Estimate client request", "Quote this project", "Timeline and risk for client".
* **Preconditions:** Scope of requested modifications defined.
* **Step-by-Step Procedure:**
  1. **Map Scope to Existing Graph [Rung L1]:** Locate symbols and files directly touched by the client's feature request.
  2. **Calculate Downstream Impact [Rung L1]:** Compute blast radius and affected test suite count.
  3. **Establish Estimation Ranges [Business Lens]:** Formulate low/high developer-day ranges based on caller complexity.
  4. **Document Assumptions & Narrowing Spikes [Business Lens]:** State what unverified dependencies could expand the timeline.
* **Output Reference:** Template 11 (`Client Proposal & Scope Estimate`).
* **Stop Condition:** Scoped proposal with bounded ranges and explicit assumptions.
* **Common Failure & Fix:**
  * *Failure:* Scope encompasses unindexed third-party APIs.
  * *Fix:* Explicitly document third-party API integration as an assumption subject to a paid technical spike.
