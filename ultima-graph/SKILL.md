---
name: ultima-graph
description: Cost-optimised, evidence-first codebase intelligence that orchestrates CodeGraph (deterministic AST index - symbols, callers, impact, affected tests) and Graphify (knowledge graph over code + docs/PDFs/media - communities, god nodes, cross-domain links), with a business translation layer. Use whenever the user wants to understand, navigate, trace, debug, refactor, audit, onboard onto, implement a feature in, or estimate changes to a codebase or mixed code+docs corpus; asks about call paths, blast radius, impact, dead code, god nodes, hotspots, architecture, tech debt, dependency upgrades, affected tests, PR risk, docs-vs-code drift, or "where is X handled"; wants fewer tokens/tool calls when exploring a repo; or needs technical findings turned into business terms (risk, effort ranges, timeline, client or exec summaries). Trigger even if the user never mentions graphs or indexing.
---

# Ultima-Graph Protocol

Ultima-Graph is a **protocol layer**, not an indexer. It routes each question to the cheapest trustworthy evidence source, keeps claims grounded in real `file:line` coordinates, and translates findings for non-engineers.

| Engine | Real tool | State on disk | Best at |
|---|---|---|---|
| **Tactical** | `codegraph` CLI / `codegraph_explore` MCP tool | `.codegraph/codegraph.db` | Exact source, callers/callees, impact, affected tests, cross-tier hops (routes, fetch→handler, IPC, native bridges) |
| **Strategic** | `graphify` CLI / `graphify-mcp` MCP server | `graphify-out/graph.json`, `GRAPH_REPORT.md` | Communities, god nodes, surprising connections, code↔docs/PDF/media links, shortest concept paths |

Both are optional. Without them the protocol still works (Degraded Mode, §8).

---

## 1. Prime Directives

1. **Cheapest sufficient evidence.** Start at the lowest rung that can answer (§4). Stop as soon as the answer is verified, with no "just to be sure" calls.
2. **No claim without a pointer.** Technical claims cite `path:Lstart-Lend`, a symbol, or a graph edge. Never invent coordinates, counts, or tool output.
3. **Label certainty.** `EXTRACTED` (syntactic fact), `INFERRED` (deduction: routes, receiver binding, conventions), `AMBIGUOUS` (dynamic dispatch, reflection, name collision).
4. **Absence needs two witnesses.** "X is unused / doesn't exist / nothing calls Y" requires the index result **and** a word-boundary lexical search (`rg -w`), including string literals, configs, and docs. Index alone is not enough for a negative claim.
5. **Blast radius before edits.** Before changing a symbol, state its callers, what it touches, and which tests to run.
6. **Business "so what", proportionately.** Translate when the audience or decision needs it (risk, effort, release, compliance). Skip it for plain lookups.
7. **Never fabricate numbers.** Token counts you cannot measure are labelled `~est`. Money figures (cost of delay, revenue at risk) come **only** from user-supplied inputs; otherwise express impact in engineering-days, affected journeys, and ranges.

---

## 2. Session Start (once, cheap)

1. **Check the tool list first.** If `codegraph_explore` or graphify MCP tools (`query_graph`, `god_nodes`…) are already exposed, use them. No detection script is needed.
2. Otherwise run `bash scripts/detect_tools.sh .` once and **reuse its JSON for the whole session**. It reports binaries, index presence, staleness (including uncommitted edits), and version-gated features.
3. **Tiny repo rule:** if `preflight_estimate.py` reports `compact` (or you can see that the repo has fewer than ~30 source files), skip indexing entirely. Direct `rg` + range reads are cheaper than building any graph.
4. **Don't index on spec.** Only build indexes when the task will issue several structural queries, or when the user asks: `bash scripts/update.sh --init` (CodeGraph init + Graphify code-only, both local and LLM-free). Mention it in one line.

---

## 3. Mode Router (summary)

Full matrix and worked examples: [mode-router.md](references/mode-router.md).

| Intent | First move | Escalate to |
|---|---|---|
| Update / refresh the graph, "I just pulled" | `bash scripts/update.sh --check` → `bash scripts/update.sh` | Ask before L5 if `graphify_semantic: pending` |
| Where is X / how does X work / trace A→B | `codegraph_explore "<symbols or question>"` | L3 range read only if a branch is unclear |
| Implement / edit feature in area X | `codegraph_explore` on the area → edit from returned source | `codegraph affected` on changed files |
| What breaks if I change X | `codegraph impact X --depth 2` (+ `callers`) | graphify `affected "X"` for doc/config dependents |
| Which tests for this diff | `git diff --name-only <base>...HEAD \| codegraph affected --stdin -q` | Map routes → E2E specs (L3) |
| Bug / stack trace / error string | `rg -n "<error text>"` → `codegraph_explore` on the throwing symbol | `codegraph callers` up the stack |
| Dead code / safe to delete? | `codegraph callers X` = 0 **plus** `rg -w X` (Directive 4) | Docs/config check |
| Circular imports | `codegraph cycles` (if supported, see detect JSON) | Manual import scan |
| Onboard / map architecture | Read `graphify-out/GRAPH_REPORT.md` if present | `codegraph_explore` on each core entrypoint |
| Tech debt / hotspots / SPOFs | `graphify god-nodes --top 10` + git churn (WF 15) | `codegraph impact` on top 3 |
| Docs vs code drift | Extract claims from the named docs → verify each via codegraph | Gated L5 only for PDFs/media |
| PR triage | Diff → symbols → impact + communities crossed | L3 on high-risk hunks |
| Dependency upgrade impact | `rg -l "from '<pkg>'\|require\('<pkg>'\|import <pkg>"` → `codegraph callers` on wrapped APIs | Changelog breaking-change list |
| Estimate / exec brief / client proposal | Gather metrics above → [business-lens.md](references/business-lens.md) | Spike to narrow ranges |

Engine playbooks: [tactical-playbook.md](references/tactical-playbook.md) (CodeGraph) · [strategic-playbook.md](references/strategic-playbook.md) (Graphify).

---

## 4. Cost Ladder

State the rung only when you **escalate** (one short clause, e.g. "L3: need the retry branch"). Details and budgets: [cost-governor.md](references/cost-governor.md).

| Rung | What | Cost |
|---|---|---|
| **L0** | Already in context (earlier tool output, `GRAPH_REPORT.md` you read) | 0 |
| **L1** | CodeGraph query (`explore`, `node`, `callers`, `impact`, `affected`) | Low, local, no LLM |
| **L2** | Graphify cached graph (`query`, `god-nodes`, `path`, `explain`, `affected`) | Low, local, no LLM |
| **L3** | Targeted read: `rg -n` hit → read ±20 lines; whole file if it is < ~150 lines or you are about to edit most of it | Low |
| **L4** | Incremental refresh: `bash scripts/update.sh` (refreshes only stale engines: `codegraph sync` + `graphify update .`, AST only, no LLM) | Compute only |
| **L5** | LLM semantic extraction of docs/PDFs/images/media (graphify full build, `label`) | **Tokens, needs consent** above thresholds (§5) |
| **L6** | Full rebuild (`codegraph index`, `graphify extract --force`) | Only when L4 fails or the index is corrupt |

**Token discipline (always):**
- Never re-read a range or re-query a symbol already in context. Reuse it.
- One `codegraph_explore` with several symbols beats several single-symbol calls.
- Use `--json`/`-q` and `--limit` flags. Cap graphify with `--budget`.
- Subagents don't inherit MCP guidance: tell them to use the `codegraph explore` CLI and give them the symbols you already found.
- Don't run helper scripts (ledger, verifier) on trivial answers. See §6 for when they pay for themselves.

---

## 5. Thresholds (single source of truth)

All other files defer to this table. Absolute numbers scale badly, so the relative rule wins on large repos.

| Signal | Threshold |
|---|---|
| God node | In top 1% by degree **or** degree ≥ 25, excluding stdlib/vendored/generated nodes |
| High blast radius | ≥ 15 transitive callers **or** callers in ≥ 3 communities/packages |
| Full-regression trigger | High blast radius, god node touched, public API/schema/auth/payment path changed, or `affected` returns 0 tests for non-test source changes |
| Ask before editing (T1→T2) | God node, high blast radius, cross-tier/language boundary, 0 covering tests, or `AMBIGUOUS` primary evidence |
| L5 consent gate | > 50 LLM-bound files (docs+papers+images) **or** > 200k LLM-bound words, or any audio/video. Code files are AST-only and **do not** count |
| Hub-hop guard | ≤ 1 unnamed intermediate hop through a hub when connecting named symbols; label hub-bridged paths `INFERRED (hub-bridged)` |

---

## 6. Evidence & Verification

Full rules: [logic-protocol.md](references/logic-protocol.md).

- **Chain (non-trivial claims):** Claim → `file:L` / edge → tag → what would falsify it → decision.
- **Fresh?** If detect reports `fresh:false` or the user just pulled/switched branches, run `bash scripts/update.sh` once (it skips fresh engines; `--check` is a free dry run, exit 10 = stale). Can't refresh? Name the files whose lines may have shifted.
- **Verifier, proportionately:** run `scripts/verify_citations.py` (JSON via stdin with `snippet`/`symbol`) when citations come from memory/summary rather than tool output in this turn, for any written deliverable (audit, brief, PR triage, proposal), and before T1/T2 edits. A failed citation gets fixed or removed. Never ship it.
- **Autonomy tiers:** **T0** read-only answers, no gate. **T1** reversible edits on a branch: run build/type-check plus the `affected` tests. **T2** irreversible or shared (merge, deploy, migration, deleting files, secrets): explicit human approval. Analysis never halts because a number is big. Big numbers change *what you recommend*, and gate *edits*.

---

## 7. Output Contract (scaled to the question)

| Question type | Shape |
|---|---|
| Lookup / "where is" / quick how | 1–3 sentence answer + citations. No other sections. |
| Trace / impact / tests / debug | Answer → evidence (path or caller list) → confidence & gaps → tests to run |
| Audit / PR triage / refactor / drift | Template from [output-templates.md](references/output-templates.md) incl. business impact |
| Exec / client / estimate | [assets/](assets/) template; plain language; ranges with basis |

**Cost footer:** one line, only on multi-step investigations or when the user asks about efficiency. Example: `Rungs L1→L3 · 1 range read · ~3 files avoided · 0 LLM calls`. Never print token counts as "measured" unless a tool returned them.

---

## 8. Degraded Mode (no engines)

Say it once ("No code index available; using targeted search."), offer the one-line install (`npm i -g @colbymchenry/codegraph && codegraph init`; `uv tool install graphifyy`), then continue with: `rg -n -w` to locate → read only the hit's range → follow imports/callers with more `rg`. Fallback recipes: [tool-detection-and-fallbacks.md](references/tool-detection-and-fallbacks.md).

---

## 9. Commands & Workflows

**Helper commands:** `scripts/update.sh` (ultima-graph update: `--check`, `--init`, `--force`, `--only codegraph|graphify`) · `scripts/detect_tools.sh` · `scripts/preflight_estimate.py` · `scripts/verify_citations.py` · `scripts/cost_ledger.py`

Step-by-step procedures in [workflows.md](references/workflows.md):

**0 Update indexes** · 1 Onboarding · 2 Call-flow trace · 3 Impact analysis · 4 Refactor plan · 5 Dead-code sweep · 6 Selective tests · 7 PR triage · 8 Docs-vs-code drift · 9 Architecture audit · 10 Cost report · 11 Exec brief · 12 Client proposal · **13 Feature implementation context** · **14 Bug root-cause** · **15 Hotspots & ownership (churn × centrality)** · **16 Dependency upgrade impact** · **17 Security/data-flow trace**

---

## 10. Privacy & Safety

1. **CodeGraph and `graphify update` are local and AST-only.** Nothing leaves the machine.
2. **Graphify L5 (semantic extraction, community `label`) sends file contents to an LLM backend** (Claude/Gemini/OpenAI/… or local Ollama). Say so before running it, and offer `--code-only` or a local backend for sensitive repos. Never claim "zero data leaves" for L5.
3. Exclude secrets before L5: add `.env*`, `*.pem`, `*.key`, credentials, and customer-data dirs to `.graphifyignore`. `preflight_estimate.py` lists sensitive files it sees.
4. Don't claim compliance (SOC 2, HIPAA, GDPR). You can state *data-residency facts* ("source stayed local"), not certifications.
5. Discovery and audit workflows never modify source. Index artifacts live in `.codegraph/`, `graphify-out/`, `.ultima/`. Suggest gitignoring them.

---

## 11. Final Check (silent, 5 points)

1. Every technical claim has a pointer, and any negative claim had two witnesses?
2. Confidence tags on non-obvious claims?
3. Cheapest rung, no re-reads, no unnecessary script runs?
4. Edits: blast radius + tests stated, and tier gate respected?
5. No fabricated tokens, dollars, or coordinates; output length matches the question?
