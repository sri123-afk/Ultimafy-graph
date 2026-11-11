# Logic Protocol: Evidence, Verification, Falsification

Load when forming architectural conclusions, resolving ambiguous edges, root-causing, or making negative ("unused", "never called") claims.

---

## 1. Evidence chain

For any non-trivial claim:
```
Claim → Evidence (file:L / node / edge) → Tag → Falsifier (checked? y/n) → Decision
```
For simple lookups, the citation alone is the chain. Don't spell out all five stages.

---

## 2. Confidence tags

| Tag | Meaning | Example |
|---|---|---|
| `EXTRACTED` | Declared in source: direct call, import, inheritance, signature | `BillingService.charge` calls `StripeClient.create` at `src/billing/service.ts:L45` |
| `INFERRED` | Second-pass deduction: route/fetch matching, receiver binding, DI convention, doc↔code link, lexical-only search | `fetch('/api/orders')` in `CheckoutView.tsx:L88` ↔ `@app.post('/api/orders')` in `order.py:L34`. Falsified if a proxy rewrites paths |
| `AMBIGUOUS` | Several candidates, reflection, string dispatch, env-conditional registration | `dispatcher.py:L22` calls `cb(*args)`. Subscribers are registered at runtime, maybe only when `AUDIT_ENABLED` |

Rules:
- A chain is only as strong as its weakest hop. A path with one `INFERRED` hop is `INFERRED`.
- `AMBIGUOUS` evidence can't be the sole basis for deleting or changing behavior. List it under **Needs human review**.
- Lexical (`rg`) evidence is at most `INFERRED`.

---

## 3. Facts / inferences / assumptions

In audits, briefs, and estimates, keep three buckets visible:
- **Facts** (cited, `EXTRACTED`)
- **Inferences** (cited, `INFERRED`, with falsifier)
- **Assumptions** (uncited: runtime config, prod traffic, team knowledge). Each is a risk to the conclusion.

---

## 4. Negative claims (absence of evidence)

"Unused", "dead", "nothing calls X", "feature doesn't exist" are the most common hallucination class. Require:
1. Index: `codegraph callers X` → 0 (or `graphify affected "X"` → none).
2. Lexical: `rg -n -w "X"` across the repo **including** configs (`*.yml`, `*.json`, `*.xml`), templates, SQL, docs, and string literals.
3. Dynamic-use scan: reflection/string dispatch near the name's tail (`getattr`, `send(:`, `[name]()`, `Class.forName`, DI registration, route tables, cron/job configs, public package exports).
4. Vocabulary expansion if the question used prose ("auth" → `login|session|token|guard|policy`).

All clean → `EXTRACTED (no references)`. Any dynamic hint → `AMBIGUOUS`. A public library export is never "dead" without checking downstream consumers.

---

## 5. Freshness gate

Before trusting line numbers on an actively edited project:
- detect `fresh:false`, the user mentions a pull/rebase/branch switch, or you edited files this session → `bash scripts/update.sh` once (or rely on the MCP watcher for CodeGraph).
- Can't sync → name the possibly-shifted files and read their ranges live.

---

## 6. Hub-hop guard

Hubs (`logger`, `utils`, `db.query`, DI container) connect everything and produce fake paths.
- Allow ≤ 1 unnamed hub hop when connecting the user's named symbols.
- Don't traverse through util/logging hubs unless the user named them.
- A path through any god node is `INFERRED (hub-bridged)` and needs a direct-edge confirmation.

---

## 7. Reasoning traps

| Trap | Countermeasure |
|---|---|
| Lexical coincidence (`UserService` vs `UserAccountService`) | Require an edge or import, not a name match |
| Zero-hit = doesn't exist | §4 negative-claim protocol |
| Generated code distortion | Exclude `DO NOT EDIT`, `*.pb.*`, `*.g.dart`, `*_generated.*`, `dist/`, `vendor/` |
| God-node blame (biggest class must be the bug) | Trace the failing path; centrality ≠ causation |
| Stale line numbers | §5 |
| Test-only callers inflate blast radius | Split prod vs test callers in every count |
| Correlation from git (co-change ≠ dependency) | Label co-change coupling `INFERRED (temporal)` |
| Confirmation bias on user's hypothesis | State one observation that would disprove it, then look for it |

---

## 8. Ground-truth verification (`scripts/verify_citations.py`)

Validation ends at disk, not at another LLM: does the file exist inside the repo, is the range in bounds, does the snippet/symbol appear there?

```bash
# Preferred: structured citations with snippet or symbol (meaningful check)
echo '[{"file":"src/auth.ts","lines":[12,18],"symbol":"verifyToken"}]' | python3 scripts/verify_citations.py
# From a markdown deliverable (checks every `path:Lx-Ly` in backticks, plus `Symbol` (`path:Lx`) pairs)
python3 scripts/verify_citations.py --input-file report.md
python3 scripts/verify_citations.py --canary   # self-test incl. path-escape and empty-input cases
```
Exit codes: `0` all verified · `1` at least one failure · `2` usage error · `3` no citations found (a deliverable with zero citations is not "verified").

**When to run** (proportionate; each run costs a round-trip):
- Written deliverables (audit, PR triage, brief, proposal, drift ledger).
- Citations recalled from earlier context or summaries rather than tool output in this turn.
- Before T1/T2 edits that rely on cited locations.

Skip it for answers quoting tool output you just received. That output is already ground truth.

A line-range-only citation proves only that the file has that many lines. Include `symbol` or `snippet` whenever possible.

---

## 9. Autonomy tiers & gates

| Tier | Scope | Gate |
|---|---|---|
| T0 | Read-only answers, audits, reports | Citations sound; verifier for deliverables |
| T1 | Reversible edits on a branch / working tree | Build + type-check + `affected` tests green, or state exactly what wasn't run |
| T2 | Merge, deploy, migration, deleting files, secrets, force-push | Explicit human approval every time |

**Ask before editing** (don't refuse to analyze) when SKILL.md §5's "Ask before editing" row triggers, or when two evidence sources disagree on callers. Report the disagreement with both results.

---

## 10. Decision record (for recommended structural changes)

```markdown
### Decision: [title]
- Context: [bottleneck, cited]
- Options: 1) … (cost/risk)  2) … (cost/risk)  3) do nothing (cost of delay)
- Choice + rationale: [caller counts, communities, test coverage]
- Reversibility: two-way / one-way door; undo cost
- Falsifier: [what result would make us revisit]
```
