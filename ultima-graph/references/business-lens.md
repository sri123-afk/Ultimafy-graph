# Business Lens

Load when the audience is non-technical or a decision-maker, or for estimates, briefs, risk registers, and client proposals.

**Golden rule:** business claims inherit the confidence of their technical evidence. A god node is a *fact*. "Only one engineer dares touch it" is a *claim* that needs `git shortlog` evidence (WF15) or must be labeled an assumption.

---

## 1. Translation matrix

| Finding | Evidence required | Business meaning | Typical action |
|---|---|---|---|
| God node | Degree rank (SKILL §5), noise-filtered | Single point of failure; changes there carry outsized regression risk | Contract tests around it; split by domain over time |
| Hotspot (churn × centrality) | WF15 table | Where defects and delivery slowdowns concentrate | Prioritize refactor/test investment here first |
| Key-person risk | `git shortlog` > 70% one author | Delivery stalls if that person is unavailable | Pairing, docs, review rotation |
| Surprising connection | Cross-community edge, tagged | Hidden coupling: "unrelated" releases break things | Explicit interface or event boundary |
| High blast radius | Prod-caller count, communities | Larger QA scope, slower releases | Feature flag; targeted regression suite |
| Dead code | Two-witness evidence | Maintenance drag, unpatched attack surface | Staged removal |
| Docs drift | Drift ledger | Onboarding drag, support load, integration errors | Generate docs from code; drift check in CI |
| Cycles | `codegraph cycles` | Can't split or extract modules; slower builds | Extract shared leaf module |
| Test gap | `affected` = 0 for changed source | Defects reach users undetected | Add tests before changing |
| Unguarded route / PII flow | WF17 finding | Security / regulatory exposure | Fix before release; involve security |

---

## 2. Vocabulary (use with discipline)

1. **Cost of delay:** only in money if the user gave revenue/rate figures. Otherwise "N eng-days/sprint of rework" or "blocks feature X".
2. **Risk exposure:** likelihood band × impact band, each with a stated basis ("High likelihood: 14 fix-commits in 12 months").
3. **Time-to-value:** when the investment starts paying back (e.g. "after phase 1, checkout changes stop needing full regression").
4. **Reversibility:** two-way door (cheap undo) vs one-way door (schema/data/public API). Say which.
5. **Compliance:** state facts ("analysis ran locally; no source sent to third parties" or "docs were sent to <backend> for extraction"). **Never** claim certification or compliance with SOC 2/ISO/HIPAA/GDPR.
6. **Opportunity cost:** what roadmap items this work displaces. Ask the user if unknown.

**Hard rule:** never invent dollar figures, revenue, conversion rates, or probabilities as percentages without a basis. Use bands (Low/Med/High) with reasons, or ask for inputs.

---

## 3. Audience modes

| Audience | Lead with | Avoid |
|---|---|---|
| CTO / eng leadership | Hotspots, regression surface, velocity drag, sequencing | Unbacked $ |
| PM | Which user journeys are at risk, timeline ranges, scope trade-offs | Class names |
| QA lead | Test scope, full-regression verdict, coverage gaps | Architecture theory |
| Finance / procurement | Effort ranges × user-supplied rates; tool cost (local = no API spend; L5 = token spend) | Unsupported % savings |
| Client / non-technical exec | Plain-language risk, milestones, assumptions, what narrows uncertainty | Jargon without a one-line definition |

---

## 4. Estimation protocol

1. **Ranges only** ("3–6 eng-days"), never a single point.
2. **Basis:** files to modify, prod callers in the blast radius, tests to update/add, communities/packages crossed, unknown systems.
3. **Rule of thumb, to be calibrated with the team's history:**
   - Base: 0.5–1 day per directly modified module with tests.
   - +25–50% if blast radius is high, +50–100% if crossing a one-way door (schema/public API), +1 spike if any `AMBIGUOUS` or unindexed dependency.
   - State that this is a heuristic. Replace it with the team's actuals if they share them.
4. **Assumptions** that would widen the range, each with a **narrowing spike** ("4h spike on webhook signing collapses ±2 days to ±0.5").
5. **Confidence:** High (all `EXTRACTED`, tests exist) / Medium / Low (key assumptions unverified).

---

## 5. Lean vs full setup advice

| Situation | Recommend |
|---|---|
| < ~30 files | No index; direct search |
| Single service, pain = slow agent exploration | CodeGraph only |
| Polyglot monorepo, onboarding pain, heavy docs/RFCs | CodeGraph + Graphify |
| Air-gapped / no external LLM allowed | CodeGraph + `graphify --code-only` or local `--backend ollama` |
