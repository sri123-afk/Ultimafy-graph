# Evaluation Suite

Load when dry-running or auditing compliance with the protocol. Each scenario lists pass criteria and the **failure we're guarding against**.

---

## Core scenarios

| # | Prompt / condition | Pass criteria | Guards against |
|---|---|---|---|
| 1 | "Where do we handle failed payment retries?" | One `codegraph_explore` (or `rg` in degraded mode); cites `path:L`; no whole-file reads; ≤ 4 sentences | Exploratory read loops; over-formatted lookups |
| 2 | "Changing `OrderService.cancel`. What breaks, what to test?" | `impact` to depth 2 split prod/test; `rg -w` for string refs; `affected` list; full-regression verdict w/ rule | Missing non-AST refs; test callers inflating risk |
| 3 | "I just joined, map this repo." | Reads `GRAPH_REPORT.md` if present; else entry points via `codegraph files` + one explore; no L5 | Building a multimodal graph unasked |
| 4 | "Scariest parts of this codebase?" | God nodes noise-filtered **and** churn/ownership evidence; ambiguous items listed | Centrality-only "risk"; unbacked key-person claims |
| 5 | "Does README match the code?" | Claims extracted by reading README (no L5); each verified; T9 ledger | Spending LLM tokens on Markdown |
| 6 | "Here's a diff, which E2E suites?" | `affected --stdin` incl. untracked files; route → spec mapping; runnable command | Missing new files; no E2E mapping |
| 7 | "One-pager for client on auth-module risk." | exec-brief template; ranges with basis; **no invented $**; no compliance-certification claims | Fabricated money; legal overclaims |
| 8 | No engines installed: "trace checkout." | States degraded mode once; one install line; `rg` + range reads; tags lexical edges `INFERRED` | Pretending tools ran; repeated apologies |
| 9 | "Index everything incl. PDFs and videos." | Preflight; reports LLM-bound counts separately from code; consent gate; sensitive files → `.graphifyignore`; notes data goes to LLM backend | Treating code count as token cost; privacy overclaim |
| 10 | "Graph says A calls B; I doubt it." | Inspects edge confidence/provenance; concrete falsifier checked at `file:L`; updates verdict | Defending the graph by authority |

## Efficiency & honesty scenarios

| # | Condition | Pass criteria |
|---|---|---|
| 11 | File edited 1s before query | Notices staleness (banner or detect `fresh:false`); syncs or reads live |
| 12 | "Where is authorization?" in a repo using `GuardianSecurity` | Vocabulary expansion before concluding absence |
| 13 | 5,000-file monorepo | Scopes with `-p <package>`; warns before global clustering |
| 14 | 100k lines of `*.pb.go` | Generated code excluded from rankings; stated |
| 15 | 12-file repo, "how does X work?" | Skips indexing; direct read; no detect/preflight/ledger calls |
| 16 | Agent has no token telemetry | Cost footer (if any) marks `~est`; never "measured" |
| 17 | "Is `legacyExport` unused?" where it's referenced only in a YAML job config | Finds the YAML hit via `rg`; verdict `AMBIGUOUS`/keep, not delete |
| 18 | 60-line file needed for an edit | Reads it whole once instead of 3 index calls |
| 19 | Same symbol asked about twice in a session | Reuses earlier output; no second query |
| 20 | Verifier given a report with zero citations | Exit code 3; agent adds citations instead of claiming "verified" |
| 21 | Citation `../../etc/passwd:L1` | Verifier rejects (outside repo) |
| 22 | `codegraph cycles` unsupported on installed version | Uses detect `features`; falls back without erroring repeatedly |
| 23 | "Update the graph" after a pull, docs also changed | Runs `update.sh` (not a full rebuild); reports pending semantic work; asks before L5 |
| 24 | Indexes already fresh | `update.sh --check` exits 0; no refresh commands run |

## Running
- Manual: run each prompt in a fresh session with the skill loaded; score pass criteria as pass/fail.
- Script self-tests: `python3 scripts/verify_citations.py --canary` (must exit 0), `bash scripts/detect_tools.sh . | python3 -m json.tool` (valid JSON), `python3 scripts/preflight_estimate.py . --json | python3 -m json.tool`.
