# Logic Protocol: Evidence, Verification, and Falsification

This reference defines the epistemological rules, evidence chain formatting, confidence tagging, and reasoning safeguards for ultima-graph. Load this file whenever formulating architectural conclusions, evaluating ambiguous relationships, or performing root-cause analysis.

---

## 1. The Evidence Chain Protocol

Every technical statement made to the user must follow the five-stage evidence chain:
```
Claim ──> Evidence (Node ID, File:Line) ──> Confidence Tag ──> Counter-Check / Falsification ──> Decision
```

### Stage Definitions
1. **Claim:** The specific technical conclusion being asserted.
2. **Evidence:** Concrete pointer to an AST node, database row, line coordinates, or graph relationship.
3. **Confidence Tag:** `EXTRACTED`, `INFERRED`, or `AMBIGUOUS`.
4. **Counter-Check / Falsification:** A concrete test or condition that would invalidate the claim, and whether it was checked.
5. **Decision:** The actionable conclusion or recommendation derived from the evidence.

---

## 2. Confidence Tagging Rubric & Worked Examples

### Tag 1: `EXTRACTED` (Syntactic Ground Truth)
* **Definition:** Relationship or property is explicitly declared in source code AST (e.g., direct import, method signature, inheritance declaration).
* **Worked Example:**
  * **Claim:** `BillingService.processPayment` invokes `StripeClient.chargeCustomer`.
  * **Evidence:** Node `billing.BillingService.processPayment` in `src/billing/service.ts:L45` has an outbound `calls` edge to `src/gateways/stripe.ts:L112`.
  * **Confidence:** `EXTRACTED`.
  * **Counter-Check:** Verified line 112 is not inside an inactive dead branch or disabled mock block.
  * **Decision:** Safe to refactor `StripeClient.chargeCustomer` only after updating `BillingService`.

### Tag 2: `INFERRED` (High-Probability Deduction)
* **Definition:** Relationship deduced through secondary resolution passes, such as receiver type binding, cross-tier route mapping, parameter flow analysis, or framework conventions.
* **Worked Example:**
  * **Claim:** The frontend checkout button in `CheckoutView.tsx` routes to the backend endpoint `POST /api/v1/orders`.
  * **Evidence:** `fetch('/api/v1/orders', { method: 'POST' })` literal in `src/views/CheckoutView.tsx:L88` matches route decorator `@app.post('/api/v1/orders')` on `OrderController.createOrder` in `src/controllers/order.py:L34`.
  * **Confidence:** `INFERRED` (Cross-tier synthesis).
  * **Counter-Check:** Falsified if an intermediate reverse proxy (e.g., NGINX / Cloudflare Worker) rewrites URL paths before they hit the Python backend.
  * **Decision:** Treat as connected in blast-radius analysis; review proxy configuration if routing fails in production.

### Tag 3: `AMBIGUOUS` (Uncertain / Requires Human Review)
* **Definition:** Multiple conflicting candidates exist, symbol name is overloaded across disparate classes without clear receiver binding, or dynamic reflection prevents static resolution.
* **Worked Example:**
  * **Claim:** `EventDispatcher.notify` calls `AuditLogger.log`.
  * **Evidence:** Dynamic subscriber registry in `src/events/dispatcher.py:L22` receives generic callback handler `cb(*args)`. `AuditLogger.log` is registered dynamically in container setup.
  * **Confidence:** `AMBIGUOUS`.
  * **Counter-Check:** Cannot prove statically whether `AuditLogger` is subscribed in every environment or only when `AUDIT_ENABLED=true`.
  * **Decision:** Flag under "Needs Human Review". Do not delete `AuditLogger.log` assuming it is unused.

---

## 3. Facts, Inferences, and Assumptions Separation

Every substantive finding must explicitly partition technical statements into three distinct buckets:

```markdown
### Analysis Breakdown
* **Facts (Extracted):**
  - `OrderController` is defined in `src/api/orders.ts:L12-L140`.
  - It exposes three HTTP methods: GET, POST, DELETE.
* **Inferences (Deductions):**
  - Database mutations run inside a transaction because `withTransaction` wraps lines 45-80.
* **Assumptions (Unverified Context):**
  - We assume Redis caching is enabled in production based on config defaults in `.env.example`.
```

---

## 4. Freshness Gate

The agent must never trust an index blindly. Before providing answers on a project undergoing active modification:
1. Verify index status: Check if the file watcher reports pending files or if `git status` reveals modified source files since the last indexing run.
2. If the index is stale:
   * Execute an incremental sync (Rung L4: `tactical sync` or `strategic update`).
   * If sync cannot be run immediately, prepend a staleness notice and restrict conclusions to unflagged files.

---

## 5. Hub-Hop Guard (Preventing Graph Traversal Explosion)

When tracing dependency paths between symbols:
1. **The Problem:** High-centrality hub functions (e.g., `logger.info`, `utils.format`, `db.query`) connect to thousands of nodes. Traversal algorithms that wander through hubs produce false-positive connections and context bloat.
2. **The Guard:**
   * Cap unnamed intermediate bridge hops at a maximum of **1 hop** when finding paths among a query's named symbols.
   * Do not traverse through known utility or logging hubs unless the user explicitly names the hub in their query.
   * If a path traverses a node with in-degree > 25, label the connection as `INFERRED (Hub-Bridged)` and require secondary confirmation.

---

## 6. Common Reasoning Traps & Countermeasures

| Reasoning Trap | Vulnerability Description | Required Countermeasure |
|---|---|---|
| **Lexical Coincidence** | Assuming two symbols with similar names (e.g., `UserService` and `UserAccountService`) are related without an edge. | Require an explicit AST `calls`, `references`, or `imports` edge before declaring coupling. |
| **Zero-Hit Premature Conclusion** | Concluding a feature does not exist because a search returned 0 hits. | Check vocabulary expansion first against `topology-out/.vocab.txt`. Translate synonyms (e.g., "auth" vs "login" vs "credential"). |
| **Generated Code Distortion** | Treating generated protobufs or client stubs (`*.pb.go`, `*.g.dart`) as complex business logic. | Filter out generated files using header banner checks (`DO NOT EDIT`) and filename conventions. |
| **Monolithic Hub Fallacy** | Assuming a high-degree "god node" is the root cause of a defect simply because of its size. | Trace the exact call path of the failing flow rather than blaming the most connected class. |
| **Stale Index Drift** | Serving shifted line coordinates from files that were modified after the last indexing pass. | Check the staleness banner and fall back to targeted line-range reads on modified files. |

---

## 7. Architectural Decision Records (ADR Format)

When recommending an architectural change or refactor, document the decision using this structure:
```markdown
### Decision Record: [Title]
* **Context:** [Current structural bottleneck or defect]
* **Options Evaluated:**
  1. [Option 1: e.g., In-place refactor] - [Pros / Cons / Cost]
  2. [Option 2: e.g., Introduce Facade Interface] - [Pros / Cons / Cost]
* **Chosen Approach:** [Selected Option]
* **Rationale:** [Evidence from graph: caller count, blast radius, test coverage]
* **Reversal Cost:** [Low / Moderate / High - what is required to undo this if wrong?]
```
