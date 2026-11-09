# Ultima-Graph Output Templates & Formats

This reference defines the required output templates for all responses generated under the ultima-graph protocol. Every substantive response must strictly adhere to these structured markdown schemas.

---

## Universal Response Structure

Every technical response must follow this 5-part order:
1. **Direct Answer:** Immediate, concise technical response.
2. **Cited Evidence:** Exact pointers to node IDs, files, line numbers, and relationships.
3. **Confidence & Gaps:** Confidence tags (`EXTRACTED`, `INFERRED`, `AMBIGUOUS`), assumptions, and unverified areas.
4. **Business Impact:** Commercial, operational, or release risk consequences (omitted only for trivial single-line lookups).
5. **Cost Footer:** Ladder rung(s) used, files read vs. avoided, LLM calls, and token metrics.

---

## Template 1: Direct Code Lookup Answer

```markdown
### Answer
[Concise 1-3 sentence direct answer to the query.]

### Implementation Evidence
* **Component:** `[SymbolName]` ([Kind: Function/Class/Interface])
* **Source Location:** `[path/to/file.ext:Lstart-Lend]`
* **Exported / Visibility:** `[Yes/No]` | `[Public/Private]`
* **Signature:**
```[language]
[verbatim code snippet]
```

### Confidence & Verification
* **Confidence Rating:** `EXTRACTED`
* **Evidence Source:** Deterministic AST Index (Node ID: `[node_id]`)
* **Unverified Scope:** [e.g., Runtime environment variables or database schema migrations]

### Business Impact
* **Functional Role:** [e.g., Core customer payment authentication entrypoint]
* **Failure Exposure:** Failure in this method breaks the customer checkout flow.

---
**Cost & Efficiency Footer:** Rung: L1 | Files Read: 0 | Files Avoided: 4 | LLM Calls: 0 | Tokens: ~450 (measured)
```

---

## Template 2: End-to-End Call Flow Report

```markdown
### Call Flow Overview
Traced execution flow from `[Source]` to `[Terminal Sink]`: [N] hops identified.

### Flow Path Trace
1. **`[Entrypoint]`** (`[file1.ts:L22]`)
   └── `calls` [EXTRACTED] ──>
2. **`[Middleware / Validator]`** (`[file2.ts:L45]`)
   └── `navigates / references` [INFERRED] ──>
3. **`[Controller Action]`** (`[file3.py:L110]`)
   └── `calls (tier)` [INFERRED: Cross-Tier HTTP Route] ──>
4. **`[Database Repository]`** (`[file4.py:L78]`)

### Confidence & Edge Evidence
* Hop 1 -> 2: `EXTRACTED` via direct AST function invocation.
* Hop 2 -> 3: `INFERRED` via framework route mapping (`POST /api/v1/orders`).
* Hop 3 -> 4: `EXTRACTED` via repository method call.

### Falsification Condition
Flow would be severed if an intermediate API gateway rewrites the `/api/v1/orders` URL path before reaching the backend controller.

### Business Consequence
* **Critical Path:** Yes (Directly touches transaction processing).
* **Latency Exposure:** Database query at Hop 4 runs synchronously inside request loop.

---
**Cost & Efficiency Footer:** Rung: L1 | Files Read: 0 | Files Avoided: 11 | LLM Calls: 0 | Tokens: ~680 (measured)
```

---

## Template 3: Impact & Blast Radius Report

```markdown
### Impact Assessment: `[TargetSymbol]`
Modifying `[TargetSymbol]` (`[file:line]`) carries an overall impact rating of `[LOW / MODERATE / HIGH / CRITICAL]`.

### Blast Radius Hierarchy
* **Direct Callers (Depth 1):** [N] components
  * `[CallerSymbol1]` (`[file1.ts:L34]`)
  * `[CallerSymbol2]` (`[file2.ts:L89]`)
* **Transitive Downstream Callers (Depth 2-3):** [M] components across [K] distinct files
* **Functional Communities Impacted:** `[Community A (Billing)]`, `[Community B (Notifications)]`

### Regression Risk & Test Scope
* **Direct Unit Test Specs:** [N] test files cover this symbol directly.
* **Transitive Test Impact:** Run `tactical affected` on modified files.
* **Full Regression Trigger:** `[YES / NO]` (Triggered because inbound caller count exceeds 15).

### Business Risk & Rollback
* **Downside of Regression:** Outage in billing notifications; customer support escalation.
* **Reversal Cost:** Moderate (requires deploying patch to 2 dependent microservices).

---
**Cost & Efficiency Footer:** Rung: L1 | Files Read: 0 | Files Avoided: 16 | LLM Calls: 0 | Tokens: ~820 (measured)
```

---

## Template 4: Selective Test Execution Report

```markdown
### Selective Test Execution Plan
Git Diff: `[base]...[head]` ([N] files modified)

### Required Test Suite (Minimal CI Gate)
| Test Spec Path | Runner | Dependency Type | Rationale |
|---|---|---|---|
| `tests/unit/payment.test.ts` | Vitest | Direct | Covers modified `PaymentService.charge` |
| `tests/integration/order.test.ts` | Vitest | Transitive | Inbound caller of `PaymentService` |
| `e2e/checkout.spec.ts` | Playwright | Route Boundary | Exercises modified `/api/checkout` endpoint |

### Test Reduction Metrics
* **Total Repository Test Specs:** 48 specs
* **Targeted Minimal Gate:** 3 specs
* **Test Avoidance Ratio:** 93.8% of test suite safely bypassed for this commit.

### Full Regression Mandate
* **Verdict:** NOT MANDATED (Modified symbols exhibit localized blast radius < 5 callers).

---
**Cost & Efficiency Footer:** Rung: L1 | Files Read: 0 | Files Avoided: 45 | LLM Calls: 0 | Tokens: ~410 (measured)
```

---

## Template 5: Architecture Audit & Technical Debt Report

```markdown
### Architecture Audit Summary
**Target Codebase:** `[Repository Name]` | **Topology Model:** Leiden Community Clustering

### High-Centrality Architectural Hubs ("God Nodes")
| Rank | Component Identifier | Degree Centrality | Subsystem Role | Systemic Risk |
|---|---|---|---|---|
| 1 | `AppContainer` (`src/core/container.ts`) | 48 edges | Dependency Injection | Single point of failure for all services |
| 2 | `DatabaseClient` (`src/db/client.py`) | 39 edges | Data Persistence | Unmitigated connection leak exposure |

### Cross-Community Couplings ("Surprising Connections")
* `PaymentGateway` (`src/payment.ts`) directly imports `AdminDashboardView` (`src/admin/view.tsx`) [Confidence: `EXTRACTED`].
  * *Architectural Smell:* Core financial engine coupled directly to internal UI layer.

### Modularity & Cohesion Metrics
* **Average Cluster Cohesion:** `0.58` (Moderate; target > 0.70).
* **Circular Dependencies:** [N] cycles detected via `tactical cycles`.

### Prioritized Remediation Roadmap
1. **P1 (Immediate):** Decouple `PaymentGateway` from `AdminDashboardView` via shared event bus.
2. **P2 (Near-Term):** Split `AppContainer` into modular per-domain service providers.

---
**Cost & Efficiency Footer:** Rung: L2 | Files Read: 2 (range-bound) | Files Avoided: 60+ | LLM Calls: 0 | Tokens: ~1,450 (measured)
```

---

## Template 6: Standard Cost Footer

```markdown
---
**Cost & Efficiency Footer:**
* **Execution Rungs:** L1 (Tactical Explore) -> L3 (Targeted Range Read: lines 45-80)
* **Files Directly Opened:** 1 (Targeted Range)
* **Files Avoided via Index:** 18
* **LLM Calls:** 0
* **Tokens In/Out:** ~740 / ~210 (measured)
* **Escalation Rationale:** L3 accessed to verify conditional database rollback guard on line 65.
```
