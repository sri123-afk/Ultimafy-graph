# Cost Governor

Load when deciding whether to escalate, budgeting a large task, running preflight before L5/L6, or reporting session efficiency. Thresholds live in SKILL.md §5.

---

## 1. Ladder rules

| Rung | Enter when | Exit when |
|---|---|---|
| L0 Context | The answer is already in this conversation or a report you read | Always check first |
| L1 CodeGraph | Code symbols, flows, callers, impact, tests | Verbatim source/caller list in hand |
| L2 Graphify | Architecture, communities, hubs, code↔docs links | Report section / query result in hand |
| L3 Targeted read | You need logic the index didn't return (a branch, config value, comment) | The specific lines are seen |
| L4 Incremental | Index stale (detect `fresh:false`, pull, branch switch) | `bash scripts/update.sh` done, then retry the lower rung |
| L5 LLM extraction | The question needs docs/PDFs/images/media semantics | Consent obtained if over the gate |
| L6 Full rebuild | L4 failed or index corrupt | Never as a default |

**Escalation is justified only by a specific missing fact.** "To be thorough" is not a reason.

---

## 2. Soft budgets per task

| Task | Typical rungs | Max range reads | LLM calls | Stop when |
|---|---|---|---|---|
| Symbol lookup | L1 | 1 | 0 | Symbol found and cited |
| Call-flow trace | L1 (+L3) | 2 | 0 | Path reaches sink or an external boundary |
| Impact | L1 (+L2) | 0 | 0 | Callers to depth 2, communities counted |
| Affected tests | L1 | 0–1 | 0 | Test list plus full-regression verdict |
| Feature implementation | L1 → edit | 3 | 0 | Edit made, affected tests listed or run |
| Bug root-cause | L3 → L1 | 4 | 0 | Faulty line identified and fix proposed |
| Dead code | L1 + `rg` | 0 | 0 | Each candidate has two-witness evidence |
| Architecture audit | L2 → L1 | 3 | 0 | Top 5 hotspots ranked with evidence |
| Onboarding | L2 → L1 | 3 | 0 | Entry points, core models, externals mapped |
| Docs drift | L3 on docs → L1 | 5 docs | 0 (L5 only for PDFs/media) | Each doc claim verified or flagged |

Over budget? Present what you have with its gaps. Don't silently keep spending.

---

## 3. Preflight (before L5/L6 only)

```bash
python3 scripts/preflight_estimate.py . [--json]
```
It reports `llm_bound` (docs/papers/images/media, which cost tokens) separately from `code` (AST, free), plus `sensitive_files` and `skipped_large_files`. It uses `git ls-files` when available, so `.gitignore` is respected.

| Result | Action |
|---|---|
| `compact` | Skip indexing; direct `rg` + reads |
| `normal` | Proceed with L1/L2. L5 is fine for named docs |
| `large` (over the L5 gate) | State file/word counts and that tokens scale with them. Get explicit consent. Offer narrowing (top dirs, `--code-only`, local `--backend ollama`) |
| `sensitive_files` non-empty | Add them to `.graphifyignore` before any L5 run |

Files > 50 MB are skipped and listed; never silently included.

---

## 4. Stop rules

1. **Sufficiency:** stop once the answer is verified. AST-returned source doesn't need re-verifying with grep (negative claims excepted, Directive 4).
2. **Marginal value:** if the next rung would roughly double cost for a minor confidence gain, stop and present the answer with its tag and gap.
3. **No re-reads:** reuse ranges and symbols already in context.
4. **Batch:** combine symbols into one `explore`, and combine independent shell checks into one command.

---

## 5. `update.sh`: one-command refresh (L4)

```bash
bash scripts/update.sh --check     # free dry run: exit 0 fresh, 10 stale
bash scripts/update.sh             # refresh ONLY stale engines (codegraph sync, graphify update .)
bash scripts/update.sh --init      # build missing indexes (local, no LLM)
bash scripts/update.sh --force     # full codegraph index + graphify update --force (after big refactors)
bash scripts/update.sh --only codegraph
```
- Never spends LLM tokens. If Graphify reports pending **semantic** re-extraction (docs/PDFs changed), the JSON `hint` says so. That is L5: ask before running `/graphify --update`.
- Tool output goes to `.ultima/update.log`. Stdout is one JSON line, so it barely costs context.
- In MCP/daemon mode CodeGraph's watcher already syncs, so you rarely need it for CodeGraph. It matters for CLI-only use and for Graphify.
- Automate: `graphify hook install` (post-commit) or a git `post-merge`/`post-checkout` hook calling `bash <skill>/scripts/update.sh -q` (add `>/dev/null`).

## 6. Ledger (opt-in)

The ledger is for **benchmarking or when the user asks for cost tracking**. It is not a per-answer ritual: every call is itself a tool round-trip.

```bash
python3 scripts/cost_ledger.py record --task "trace_checkout" --rung L1 \
  --files-read 1 --files-avoided 9 --llm-calls 0 --estimate --notes "1 explore + 1 range read"
python3 scripts/cost_ledger.py report     # summary + rung distribution
python3 scripts/cost_ledger.py verify     # hash-chain integrity
python3 scripts/cost_ledger.py reset      # archives to ledger.<timestamp>.jsonl, never deletes
```

Rules:
- Agents rarely see real token counts. Use `--estimate` (≈ chars/4) unless a tool returned exact numbers.
- `files_avoided` = files the index result spanned that you didn't open. Count them, don't guess.
- The hash chain detects accidental edits and casual tampering. It is **not** proof against someone who can rewrite the whole file. Don't oversell it.
