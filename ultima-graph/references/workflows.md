# Workflows

Load when executing a multi-step task. `T#` = template in [output-templates.md](output-templates.md). Commands assume CodeGraph/Graphify; in Degraded Mode use the equivalents in [tool-detection-and-fallbacks.md](tool-detection-and-fallbacks.md) §4.

---

## WF0 Update indexes ("ultima-graph update")
**Cues:** "update the graph", "refresh index", "I pulled", "switched branch", detect `fresh:false`.
1. `bash scripts/update.sh --check` (dry run). Exit 0 → nothing to do; stop.
2. `bash scripts/update.sh` → refreshes only stale engines. Report the one-line JSON result.
3. `graphify_semantic: "pending"` → tell the user the docs changed and that re-extraction costs LLM tokens. Run `/graphify --update` only on consent.
4. Failure → read the last ~20 lines of `.ultima/update.log`; common fixes: `codegraph unlock`, `--force` after large deletions.

## WF1 Onboarding
**Cues:** "onboard me", "map this repo", "tour".
1. If `graphify-out/GRAPH_REPORT.md` exists, read its summary, god nodes, and communities (L2). Otherwise, skip building unless the repo is large and the user wants a lasting map.
2. Find entry points: `codegraph files` + manifests (`package.json` scripts/bin, `main.go`, `manage.py`, `Dockerfile` CMD, route registries).
3. `codegraph_explore` on the 3–5 entry points/core models in **one** call.
4. List external dependencies (DBs, queues, third-party APIs) from config/env-example files.
**Output:** T6. **Stop:** entry points, core models, data stores, externals, and "where to start" for a first change.
**Failure:** huge monorepo → scope to the package the user works in (`-p`).

## WF2 Call-flow trace
1. Name the source (route/UI event/CLI) and sink (DB write/external call).
2. `codegraph_explore "<source> <sink> <suspected middle>"`.
3. Missing hop → likely a queue/event bus/DI. Search the topic/event name with `rg` and explore the consumer.
4. L3 only for conditional branches not shown.
**Output:** T2. **Stop:** unbroken cited path, or the exact gap named.

## WF3 Impact analysis
1. `codegraph node X` (confirm the definition; `-f` if overloaded).
2. `codegraph impact X -d 2 --json` → split **prod vs test** callers; count packages/communities.
3. `rg -n -w X` for string/config/serializer references the AST misses.
4. `codegraph affected <file of X> -q` → tests.
5. Apply SKILL §5 thresholds → rating + full-regression verdict.
**Output:** T3.

## WF4 Refactor plan
1. WF3 on the zone's public surface. Collect all inbound edges crossing the boundary.
2. Cycles: `codegraph cycles` (if available). A cycle becomes Step 0: extract shared types to a leaf.
3. Design the seam (adapter/facade/interface) so external callers change once.
4. Sequence leaf-first, each step building green and independently revertible. Name the tests per step.
5. Rollback per step; feature-flag anything user-visible.
**Output:** T7 + decision record (logic-protocol §10).

## WF5 Dead-code sweep
1. Candidate list: `codegraph node -f <file> --symbols-only` for target files, then `codegraph callers <sym> -l 1 --json` per exported symbol (batch in one shell loop).
2. For each 0-caller symbol, run the negative-claim protocol (logic-protocol §4): `rg -w`, configs, dynamic-use, public exports.
3. Tag: `EXTRACTED (no refs)` = safe, `AMBIGUOUS` = keep or deprecate first.
4. Deletion is T2 if the symbol is a public API. Otherwise propose one PR per module.
**Output:** T8.

## WF6 Selective tests
1. `{ git diff --name-only origin/main...HEAD; git ls-files -o --exclude-standard; } | codegraph affected --stdin -q`
2. Group by runner (Vitest/Jest/Pytest/Go test).
3. Changed routes/pages/components → map URL paths to E2E specs (`rg -l "<path>" e2e/ tests/`).
4. Full-regression verdict per SKILL §5. Note 0-test changes as a coverage gap.
**Output:** T4 + a ready-to-run command (`npx vitest run <files>`, `pytest <files>`).

## WF7 PR triage
1. Files: `git diff --name-only <base>...<head> -- . ':!*.lock' ':!package-lock.json' ':!*.pb.*' ':!dist/**'`.
2. Changed symbols: for each file, `git diff -U0` hunks ↔ `codegraph node -f <file> --symbols-only` line ranges.
3. Per symbol: callers count (prod/test), god-node match (`graphify god-nodes --json` if a graph exists), communities crossed.
4. Signals: public signature changed, schema/migration, auth/payment/PII path, new cross-package import, deleted tests.
5. Tests: WF6.
**Output:** `assets/pr-triage.template.md`. Reviewer focus = ≤ 5 hunks with reasons.

## WF8 Docs-vs-code drift
1. Scope: the docs the user named, else `README*` + `docs/**/*.md` (preflight if > 50 files).
2. Extract checkable claims: CLI flags, env vars, endpoints, function signatures, config keys, version numbers, install commands. Read the docs at L3. No L5 is needed for Markdown.
3. Verify each claim: `codegraph query`/`explore` for symbols and routes; `rg` for flags/env vars; manifests for versions.
4. Classify: `match` / `drift (signature)` / `missing in code` / `undocumented in docs`.
**Output:** T9. PDFs/images/media need L5 consent.

## WF9 Architecture audit
1. `graphify god-nodes --top 15 --json` → drop noise (strategic-playbook §6) → top 5–10.
2. Surprising connections + low-cohesion communities from `GRAPH_REPORT.md`.
3. `codegraph cycles`.
4. Combine with churn (WF15). Risk = centrality × churn, not centrality alone.
5. `codegraph impact` on the top 3 to quantify.
6. Backlog ranked by risk × effort (business-lens §4 ranges).
**Output:** T5 (+ `assets/risk-register.template.md`).

## WF10 Cost report
`python3 scripts/cost_ledger.py verify && python3 scripts/cost_ledger.py report`. If there is no ledger, summarize this session's rungs and calls from context, marked `~est`. For an engine-level benchmark: `graphify benchmark`. **Output:** T10.

## WF11 Exec brief
Prereq: WF3 or WF9 done. Fill `assets/exec-brief.template.md`: one-line bottom line, ≤ 3 risks in user-journey terms, recommendation, cost of inaction (ranges in eng-days; $ only from user-provided rates/revenue). Replace class names with what they do for users. Run the verifier on the appendix citations.

## WF12 Client proposal / estimate
1. Map scope to symbols/files (WF13 step 1–2).
2. Impact + test counts (WF3/WF6).
3. Range per business-lens §4, with the basis stated.
4. Assumptions + the spike that would narrow each.
5. Third-party/unindexed systems → explicit assumption + paid spike.
**Output:** T11.

## WF13 Feature implementation context (most common coding task)
**Cues:** "add X", "implement Y", "change behavior of Z".
1. `codegraph_explore "<feature nouns> <nearest existing similar feature>"`. Find the pattern to copy, not just the place to edit.
2. Identify the conventions in returned code: error handling, validation, DI, logging, test style.
3. Check the blast radius of each symbol you'll modify (`callers`). New symbols have none.
4. Edit from the returned verbatim source (no extra Read needed).
5. `codegraph affected <changed files> -q` → run those tests (T1 gate).
**Stop:** change made + tests run (or listed with the reason they weren't run).

## WF14 Bug root-cause
**Cues:** stack trace, error message, "why does X return Y".
1. Exact error string → `rg -n -F "<message>"`. Top stack frame → read `file:L±15`.
2. `codegraph_explore "<throwing fn> <caller from trace> <data source>"`.
3. Walk upstream with `codegraph callers` until the bad value's origin. Form one hypothesis, state its falsifier, and check it.
4. Recent change? `git log -L <start>,<end>:<file> -n 3` or `git log -S "<symbol>" -n 5 --oneline`.
5. Fix + regression test. Run `affected`.
**Output:** cause (cited), fix, test, and related call sites with the same bug pattern (`rg` for the pattern).

## WF15 Hotspots & ownership (churn × centrality)
Evidence for "fragile" and key-person-risk claims.
1. Churn: `git log --since=12.months --name-only --format= | grep -v '^$' | sort | uniq -c | sort -nr | head -30`.
2. Centrality: `graphify god-nodes --json` or caller counts from `codegraph callers`.
3. Hotspot = high churn ∩ high centrality.
4. Ownership: `git shortlog -sn --since=12.months -- <file>`. If one author has > 70% of commits, that's key-person risk (`INFERRED`).
5. Bug density (optional): `git log --since=12.months --oneline -i --grep='fix\|bug' -- <file> | wc -l`.
**Output:** ranked table (file, churn, callers, top-author %, fixes) feeding T5 / the risk register.

## WF16 Dependency upgrade impact
1. Usage sites: `rg -l -w "<pkg>"` over source (imports/requires), excluding lockfiles.
2. List the breaking API changes (changelog/migration guide; ask the user or fetch with permission).
3. Per breaking API: `rg -n "<api>"` count + `codegraph callers` on local wrappers.
4. Effort = sites × change complexity. Note transitive peers (`npm ls <pkg>`, `pip show`).
**Output:** table (API, sites, wrapped?, effort range) + test plan via WF6.

## WF17 Security / data-flow trace
**Cues:** "where does PII go", "is every route authz-checked", "can user input reach SQL".
1. Sources (request handlers, form inputs, webhooks) and sinks (DB, logs, outbound HTTP, file writes) via `codegraph_explore`.
2. For authz: list routes (`codegraph query` for route handlers or framework route files), then check each for guard/middleware on its path.
3. Report unguarded or unsanitized paths as findings with `INFERRED`/`AMBIGUOUS` tags. Static analysis can't prove runtime middleware ordering, so say so.
4. Hand off deep audits to a dedicated security skill if one is available.
**Output:** finding list (path, source→sink, guard present?, tag).
