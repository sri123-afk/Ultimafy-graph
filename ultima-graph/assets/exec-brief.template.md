# Executive Architectural Brief: [System / Initiative Name]

**Date:** [YYYY-MM-DD]  
**Audience:** Executive Leadership / VP of Engineering / CTO  
**Prepared by:** [Name / team] (with ultima-graph analysis)  
**Scope:** [Target Repository / Microservice / Module]  

---

## 1. Executive Summary & Business Bottom Line
* **Current Architectural Posture:** [Stable / Modular / High Coupling / Monolithic Hotspots]
* **Key Finding:** [1-2 sentences summarizing the single highest-impact technical finding and why it matters to revenue, delivery speed, or stability.]
* **Direct Recommendation:** [Specific action required: e.g., Approve Refactoring Sprint / Decouple Service / Isolate Gateway]
* **Cost of Inaction:** [Eng-days of rework/sprint, delayed roadmap items, or exposure band. $ figures only if the reader supplied rates/revenue]

---

## 2. Quantitative Architecture Footprint
| Metric | Measured Value | Indicative Baseline* | Business Interpretation |
|---|---|---|---|
| Total Tracked Components | [N] | - | Scale of the indexed system |
| Identified High-Centrality Hubs | [N] | < 5 | Potential architectural single points of failure |
| Cross-Boundary Couplings | [N] | < 10 | Unplanned dependencies across domain modules |
| Average Cluster Cohesion Score | [0.00 - 1.00] | > 0.65 | Degree of domain encapsulation |
| Unreferenced / Stale Symbols | [N] ([%]) | < 5% | Maintenance drag and dead code footprint |

---

*Baselines are rules of thumb, not industry standards; calibrate to this codebase over time.

## 3. Top Systemic Risks & Business Exposure
1. **[Risk Title - e.g., Core Payment Hub Dependency]**
   * **Technical Root:** Symbol `[Class.Method]` exhibits [N] inbound call edges across [M] separate feature domains.
   * **Business Downside:** Any modification or outage directly halts [Core User Journey - e.g., Checkout].
   * **Mitigation Plan:** [e.g., Introduce Interface Facade and Circuit Breaker].
   * **Investment Required:** [X–Y eng-days; basis: files, callers, tests]

2. **[Risk Title - e.g., Hidden Client-to-Database Coupling]**
   * **Technical Root:** [e.g. route `GET /admin/export` (`path:L`) reaches `UserRepo.dump` with no auth guard on the path, INFERRED]
   * **Business Downside:** [e.g. personal data exposure; likely audit finding and incident-response cost]
   * **Mitigation Plan:** [e.g., Re-route calls via validated API gateway layer].
   * **Investment Required:** [X–Y eng-days; basis: files, callers, tests]

---

## 4. Delivery Roadmap & Resource Allocation
```
Phase 1: Stabilization (Weeks 1-2) ──> Phase 2: Decoupling (Weeks 3-4) ──> Phase 3: Verification (Week 5)
```
* **Phase 1 Priority:** Isolate high-centrality hub nodes; implement regression test boundaries.
* **Phase 2 Priority:** Break cross-boundary circular imports; prune dead code paths.
* **Phase 3 Priority:** Enforce CI dependency linting and automated blast radius checks.

---

## 5. Audit & Compliance Sign-Off
* **Analysis Methodology:** Deterministic Static AST Indexing + Network Community Detection.
* **Data Handling (state facts only):** [e.g. "Code analysed locally (CodeGraph/Graphify AST); no source sent externally." OR "Docs X, Y were sent to <LLM backend> for extraction."] No compliance-certification claims.
* **Confidence Rating:** [HIGH / MEDIUM / LOW]: HIGH only if key findings are `EXTRACTED` and citations passed `verify_citations.py`.
* **Key Assumptions:** [unverified items that would change the recommendation]
