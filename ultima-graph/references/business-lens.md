# Business Lens: Translating Technical Graphs into Enterprise Value

This reference defines the business translation framework for ultima-graph. Load this file whenever communicating architectural findings to non-technical stakeholders, compiling executive summaries, estimating refactoring timelines, or evaluating commercial risk.

---

## 1. Technical-to-Business Translation Matrix

Every technical graph metric corresponds directly to a commercial, financial, or operational outcome:

| Technical Finding | Graph Manifestation | Direct Business Consequence | Commercial Downside / Exposure | Recommended Executive Action |
|---|---|---|---|---|
| **God Node** | Class or function with in-degree > 25 across multiple modules | **Single Point of Failure & Key-Person Risk** | Any defect halts multiple revenue flows; only 1-2 veteran engineers dare touch it | Fund decoupling sprint; establish strict contract tests |
| **Surprising Connection** | Edge bridging distant Leiden communities or language families | **Hidden Coupling & Release Fragility** | Unintended side effects break production during unrelated feature deployments | Introduce explicit API boundary or message queue |
| **High Blast Radius** | Symbol with > 15 transitive callers across client tiers | **Elevated QA Cost & Regression Risk** | Extended manual QA cycles; slowed feature delivery; high defect escape rate | Enforce automated regression suite; gate behind feature flag |
| **Dead Code** | Unreferenced exported symbols (0 callers, 0 imports) | **Maintenance Drag & Attack Surface** | Engineers waste time reading dead logic; security vulnerabilities remain unpatched | Schedule phased deprecation and removal in upcoming sprint |
| **Documentation Drift** | Doc claims conflict with extracted code AST and routes | **Onboarding Drag & Customer Support Load** | Slower time-to-productivity for new hires; customer frustration over broken API docs | Automate doc generation from live AST route nodes |
| **Circular Dependencies** | File import cycles detected via `tactical cycles` | **Monolithic Lock-in & Build Inefficiency** | Cannot extract services into microservices or libraries; slowed CI builds | Refactor shared abstractions into a common leaf module |
| **Cross-Tier Boundary Gaps** | Client `fetch` literal missing corresponding backend route | **Integration Defect & Broken User Journey** | Silent client-side runtime errors; abandoned checkout or signup conversions | Reconcile API endpoint routes before releasing frontend |

---

## 2. Business Metrics Vocabulary

When communicating with executive leadership, express technical findings through these six business lenses:

1. **Cost of Delay:** The financial cost of postponing a release or refactor (e.g., "$15,000/week in lost conversion due to unstable checkout service").
2. **Risk Exposure (Likelihood x Impact):** Quantify risk as a bounded range rather than a single number (e.g., "Probability: High (60-80%), Financial Impact: $50k-$120k in emergency outage remediation").
3. **Time-to-Value (TTV):** The duration required for an engineering investment to yield tangible operational benefits.
4. **Reversibility (Two-Way vs. One-Way Doors):** Can this architectural decision be undone cheaply?
   * *Two-Way Door:* Adding an adapter facade (reversal cost: 1 developer day).
   * *One-Way Door:* Migrating primary database schema without backwards compatibility (reversal cost: weeks of downtime).
5. **Regulatory & IP Compliance Exposure:** The legal and compliance risks of code exposure. Highlight that local-first AST indexing keeps 100% of proprietary source code on premises, complying with SOC2, ISO 27001, HIPAA, and GDPR data residency standards.
6. **Opportunity Cost:** What revenue-generating features are delayed because engineering is bogged down maintaining brittle architecture?

---

## 3. Stakeholder Communication Modes

Tailor language and emphasis depending on the designated audience:

### Mode A: CTO & Engineering Leadership
* **Focus:** System resilience, maintainability index, technical debt remediation, team velocity, architecture governance.
* **Tone:** Technical, precise, metric-backed.
* **Example:** "Refactoring `PaymentRouter` decouples 3 core communities, reducing our regression surface from 42 files to 6 files."

### Mode B: Product Manager (PM)
* **Focus:** Feature delivery speed, release reliability, user journey protection, scope trade-offs.
* **Tone:** Outcome-oriented, timeline-focused.
* **Example:** "Modifying this checkout flow touches 18 dependent components. We need 3 additional QA days to verify no regression in subscription renewals."

### Mode C: QA & Test Engineering Lead
* **Focus:** Selective test automation, regression test scoping, flaky test containment, test-impact mapping.
* **Tone:** Procedural, verification-focused.
* **Example:** "The PR affects 4 source files. Running `tactical affected` isolates the necessary test gate to exactly 5 unit specs and 1 Playwright E2E spec."

### Mode D: Finance & Procurement
* **Focus:** Infrastructure compute costs, LLM token efficiency, licensing compliance, ROI.
* **Tone:** Cost-efficiency, dollar-and-cents ROI.
* **Example:** "Switching to deterministic local indexing reduces exploratory LLM API token spend by an estimated 40-60% per engineering seat."

### Mode E: External Client & Non-Technical Executive
* **Focus:** Project scope certainty, milestone delivery, risk containment, transparency.
* **Tone:** Plain English, jargon-free, objective.
* **Example:** "We mapped the system's internal connections. The requested feature intersects with the core billing engine, which requires rigorous verification before go-live."

---

## 4. Estimation Rules: The Range and Basis Protocol

When asked for effort or timeline estimates, the agent must adhere to four strict rules:

1. **Always Provide Ranges:** Never provide a single-point estimate (e.g., say "3 to 5 developer days", never "4 days").
2. **State the Quantitative Basis:** Base the range on graph facts:
   * Number of directly modified files.
   * Number of inbound callers in the blast radius.
   * Number of existing automated test suites that cover the affected paths.
3. **Mark Unverified Assumptions:** Clearly state assumptions that, if false, would expand the estimate (e.g., "Assumes third-party payment gateway sandbox behaves identically to production").
4. **Define Narrowing Conditions:** State exactly what investigation or spike would collapse the estimation range (e.g., "A 4-hour spike to verify the Stripe webhook signature will narrow this estimate to +/- 0.5 days").

---

## 5. Build vs. Adopt vs. Integrate Framework

Use this evaluation framework when advising whether a team should deploy tactical code indexing, strategic knowledge graphs, or both:

| Input Variable | Lean / Tactical Path | Hybrid / Full Ultima-Graph Path |
|---|---|---|
| **Repository Size** | < 200 files, single language | > 500 files, polyglot monorepo |
| **Team Size** | 1-5 developers | > 10 developers across multiple squads |
| **Regulatory Posture** | Standard commercial | Strict compliance (air-gapped, zero external LLM API usage permitted) |
| **Documentation Mass** | Code is self-documenting, minimal docs | Heavy documentation (RFCs, PRDs, API schemas, PDF compliance specs) |
| **Primary Pain Point** | Slow agent code exploration, high token bills | Architecture spaghetti, difficult onboarding, cross-service regression outages |
