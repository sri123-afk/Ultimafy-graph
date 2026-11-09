# Pull Request Structural Risk Triage: [PR Number / Title]

**Author:** [PR Author]  
**Reviewer:** [Assigned Reviewer / Architecture Lead]  
**Timestamp:** [YYYY-MM-DD HH:MM UTC]  
**Git Diff Range:** `[base_commit]...[head_commit]`  

---

## 1. Automated Risk Classification
* **Overall PR Risk Category:** `[LOW / MODERATE / HIGH / CRITICAL]`
* **Core Risk Drivers:**
  * Modified Symbols Touching High-Centrality Hubs: `[YES (Count: N) / NO]`
  * Architectural Communities Crossed: `[N Communities]`
  * Cross-Tier Synthesized Boundaries Touched: `[YES / NO]`
  * Circular Imports Introduced: `[YES (Count: N) / NO]`

---

## 2. Blast Radius & Affected Graph Topology
| Changed File | Modified Symbol(s) | Direct Inbound Callers | Transitive Inbound Callers | Functional Communities Impacted |
|---|---|---|---|---|
| `[path/to/file1.ext]` | `[SymbolName1]` | [N] callers | [M] callers | `[Community A, Community B]` |
| `[path/to/file2.ext]` | `[SymbolName2]` | [N] callers | [M] callers | `[Community A]` |

---

## 3. Targeted Test Execution Plan (Affected Testing)
* **Required Unit & Integration Suites (Minimal CI Gate):**
  * `[path/to/test_spec_1.test.ts]` (Direct dependency)
  * `[path/to/test_spec_2.test.ts]` (Transitive dependency via `[SymbolName]`)
* **Required E2E & Browser Specs (Playwright / Cypress):**
  * `[e2e/flow_spec.spec.ts]` (Covers synthesized route: `[GET /api/v1/endpoint]`)
* **Full Regression Trigger Condition:** `[Met / Not Met]`
  *(Full regression mandated if any modified symbol exhibits >15 inbound callers or bridges multiple core business communities)*.

---

## 4. Reviewer High-Salience Focus List
Focus code review strictly on these high-risk hunks:
1. `[path/to/file:L45-L80]` - Dynamic dispatch parameter change affecting `[DependentClass]`.
2. `[path/to/file:L110-L135]` - Exported signature change with [N] external consumers.

---

## 5. Triage Recommendation & Business Clearance
* **Review Decision:** `[APPROVE / REQUEST CHANGES / ELEVATE TO ARCHITECTURAL REVIEW]`
* **Rollback Exposure:** `[LOW / MEDIUM / HIGH]` (Is the change backwards-compatible? Database migrations involved?)
* **Business Release Window:** `[Standard Release / Off-Peak Deployment / Feature-Flag Gated]`
