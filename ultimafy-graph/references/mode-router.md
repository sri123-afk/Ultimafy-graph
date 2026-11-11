# Mode Router

Load when a query's intent or engine choice is unclear. SKILL.md §3 has the summary table.

---

## 1. Routing order

1. **Answerable from context?** → L0, answer now.
2. **Tiny repo (`compact`)?** → `rg` + range reads. Skip engines.
3. **Code-structural** (where/how/callers/impact/tests/edit) → CodeGraph.
4. **System-level or non-code** (architecture, clusters, hubs, docs/PDF links) → Graphify (report first).
5. **Change risk** (PR, diff, upgrade) → both: CodeGraph for symbols and tests, Graphify for communities crossed.
6. **Audience is non-technical or a decision-maker** → add the business lens to whatever 3–5 produced.

If the preferred engine is missing: CodeGraph tasks fall back to `rg` + reads. Graphify tasks fall back to CodeGraph (`files`, `impact` on entrypoints) plus git churn.

---

## 2. Intent matrix

| Category | Phrasing cues | First call | Escalate when |
|---|---|---|---|
| Update indexes | "update graph", "refresh", "pulled", "switched branch" | `bash scripts/update.sh --check` | Stale → `update.sh`; semantic pending → ask (L5) |
| Lookup & flow | "where is", "how does", "trace", "what calls" | `codegraph_explore "<names>"` | A branch/config isn't in the returned source → L3 |
| Implement / modify | "add", "change", "implement", "fix in X" | `codegraph_explore` on area → edit | Ask-before-edit row (SKILL §5) → confirm first |
| Impact | "what breaks", "who uses", "safe to change" | `codegraph impact X -d 2 --json` | Callers span ≥ 3 packages → Graphify communities |
| Tests | "which tests", "minimal CI", "affected" | `codegraph affected --stdin -q` | Routes/UI changed → map to E2E specs |
| Debug | stack trace, error text, "why does X fail" | `rg -n "<message>"` → explore the thrower | Cause is upstream → `callers` up the stack |
| Dead code / cycles | "unused", "delete", "circular" | `callers` = 0 + `rg -w`; `codegraph cycles` | Dynamic-use hints → `AMBIGUOUS` |
| Onboarding | "onboard", "map", "tour" | `GRAPH_REPORT.md` → else `codegraph files` + entrypoints | User wants docs included → L5 gate |
| Debt / hotspots | "scariest", "god", "fragile", "debt" | `graphify god-nodes` + git churn | Top 3 → `codegraph impact` |
| Docs drift | "README lies", "docs vs code" | Read the named docs → verify claims via codegraph | PDFs/media → L5 gate |
| PR triage | "review PR", "risk of diff" | Diff → symbols → `impact` + `affected` | Hub touched → L3 on hunks |
| Upgrade impact | "bump", "upgrade", "migrate lib" | `rg -l` imports of the pkg → callers of wrappers | Breaking changes need changelog |
| Security flow | "where does PII go", "is X authz-checked" | `codegraph_explore` source→sink | Unchecked path → flag, don't assume |
| Business | "estimate", "brief", "client", "risk register" | Gather metrics above → business-lens | Unverified scope → spike |

---

## 3. Worked examples (compact)

| # | User says | Route | Notes |
|---|---|---|---|
| 1 | "How does an HTTP request reach the DB in billing?" | `codegraph_explore "BillingController charge Repository save"` | One call. Cite each hop |
| 2 | "I'm renaming `UserProfile.updateEmail`. What breaks?" | `codegraph impact UserProfile.updateEmail -d 2 --json` + `rg -w updateEmail` (strings, serializers) | Renames break string refs that the index misses |
| 3 | "Orders module feels fragile." | `graphify god-nodes` + `explain "OrderService"` + churn | Translate to change-failure risk |
| 4 | "What are we most afraid to touch?" | God nodes × churn × ownership (WF15) | Key-person claims need `git shortlog` evidence |
| 5 | "Just cloned, give me a tour." | Report if present; else `codegraph files` + explore entrypoints | No L5 unless asked |
| 6 | "Changed `auth_middleware.py`, what do I run?" | `codegraph affected src/auth_middleware.py -q` | Auth path → full-regression trigger |
| 7 | "Are our `/docs` lying?" | Read docs (L3) → verify each claim | Markdown needs no L5 |
| 8 | "Does web call inventory directly or via gateway?" | `codegraph_explore "inventoryClient fetchInventory gateway"` | Cross-tier edges are `INFERRED` |
| 9 | "Assess risk of `origin/main...feature-x`." | WF7 | Filter lockfiles/generated |
| 10 | "Client wants Auth0 instead of our auth. Estimate." | WF12 on auth symbols | Ranges + assumptions; no invented $ |
| 11 | "Is half of `legacy_reports.ts` unused?" | `node -f legacy_reports.ts --symbols-only` → callers per export + `rg -w` | Two witnesses per symbol |
| 12 | "Find Stripe webhook handling; I just pulled." | `bash scripts/update.sh` → explore `"stripe webhook"` | Freshness first |
| 13 | "TypeError at `cart.ts:88` in prod." | Read `cart.ts:L70-L100` → explore the null source | WF14 |
| 14 | "Upgrade axios 0.x → 1.x, how bad?" | WF16 | Count call sites per breaking API |
