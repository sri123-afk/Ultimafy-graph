# Architectural Risk Register: [Project / Initiative Name]

**Last Updated:** [YYYY-MM-DD]  
**Evaluation Standard:** Likelihood (1-5) x Impact (1-5) = Risk Score (1-25)  
**Governance Scope:** Production Software Engineering & Architecture  

---

## Risk Scoring Matrix
* **1-6: Low** (Monitor during routine maintenance)
* **7-14: Medium** (Remediate within current quarter)
* **15-25: High / Critical** (Immediate sprint allocation required; blocks major releases)

---

## Active Risk Register

| Risk ID | Component / Seam | Technical Root Cause | Likelihood (1-5) | Impact (1-5) | Score (1-25) | Business Impact | Mitigation Strategy | Owner | Target Date |
|---|---|---|---|---|---|---|---|---|---|
| RSK-01 | `[Namespace.Class]` | High-centrality hub with [N] inbound cross-tier calls | [L] | [I] | [Score] | [e.g., Critical revenue outage if modified] | [e.g., Introduce adapter facade and contract tests] | [Lead] | [Date] |
| RSK-02 | `[Route / API Handler]` | Cross-tier unvalidated navigation link | [L] | [I] | [Score] | [e.g., Security vulnerability / API breach] | [e.g., Strict schema validation via middleware] | [Lead] | [Date] |
| RSK-03 | `[Module A <-> Module B]` | Circular dependency cycle across package boundary | [L] | [I] | [Score] | [e.g., Fragile builds, inability to isolate services] | [e.g., Extract shared domain models to leaf package] | [Lead] | [Date] |
| RSK-04 | `[Legacy Service]` | Dead code with ambiguous documentation references | [L] | [I] | [Score] | [e.g., Onboarding drag, false positive alerts] | [e.g., Staged deprecation and automated deletion] | [Lead] | [Date] |

---

## Detailed Risk Fact Sheets

### RSK-01: [Component Name]
* **Graph Evidence:** Node ID `[node_id]`, defined in `[file_path:line]`.
* **Inbound Callers (Blast Radius):** [N] direct callers, [M] transitive callers across [K] distinct feature modules.
* **Falsification Condition:** What observation would downgrade this risk? (e.g., "If inbound callers are non-production test harnesses only, risk score reduces from 20 to 6").
* **Verification Check:** Verified against live AST index; confirmed production callers:
  * `[caller_1_file:line]`
  * `[caller_2_file:line]`
* **Reversal Cost:** [Low / Moderate / High] (e.g., "Contract change requires updating 4 client consumers").
