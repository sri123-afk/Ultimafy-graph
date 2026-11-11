# Output Templates

Load when producing a structured deliverable. Size the output to the question (SKILL §7): a lookup never needs a template. Drop any section with nothing real to put in it. Never pad with placeholders.

---

## T1 Lookup
```markdown
[1–3 sentence answer.] `[Symbol]` (`path:Lstart-Lend`)[, called from `path:L`].
```
Add a confidence note only if not `EXTRACTED`.

## T2 Call flow
```markdown
**[Source] → [Sink]: [N] hops**
1. `[Entry]` (`a.ts:L22`) → calls [EXTRACTED]
2. `[Middleware]` (`b.ts:L45`) → route [INFERRED: POST /api/orders]
3. `[Handler]` (`c.py:L110`) → calls [EXTRACTED]
4. `[Repo.save]` (`d.py:L78`)

Weakest hop: 2→3 (falsified if a proxy rewrites `/api/orders`).
[Business note only if relevant: critical path / sync DB call in request loop.]
```

## T3 Impact
```markdown
**Changing `[X]` (`path:L`): [LOW|MODERATE|HIGH|CRITICAL]** (basis: [N] prod callers, [K] packages, [hub? y/n])

| Depth | Prod callers | Test callers | Packages |
|---|---|---|---|
| 1 | n | n | … |
| 2 | n | n | … |

Notable callers: `[C1]` (`f:L`), `[C2]` (`f:L`)
Non-AST refs (rg): [strings/configs or "none"]
Tests: [affected list] · Full regression: [yes/no + rule]
Risk: [user journey affected] · Reversal: [two-way/one-way]
```

## T4 Selective tests
```markdown
Diff `[base]...[head]`: [N] files → [M] tests
| Test | Runner | Why |
|---|---|---|
Run: `[exact command]`
Full regression: [verdict + rule] · Coverage gaps: [changed files with 0 tests]
```

## T5 Architecture audit
```markdown
**Bottom line:** [1 sentence]
| # | Hotspot | Callers/degree | Churn 12m | Top-author % | Why it matters |
|---|---|---|---|---|---|
Surprising connections: `[A]` → `[B]` [tag] (why it's a smell)
Cycles: [N groups or "none" / "not checked: unsupported"]
Noise filtered: [what was excluded]
Backlog: P1 … (effort range) · P2 …
Needs human review: [AMBIGUOUS items]
```

## T6 Onboarding map
```markdown
**What it is:** [1–2 sentences]
Entry points: `[cmd/route]` → `[symbol]` (`path:L`)
Core modules: [name: responsibility] ×3–6
Data & externals: [DBs, queues, third-party APIs]
How a request flows: [3–5 step trace]
Start here for a first change: [file + why]
Gotchas: [generated code, env flags, unusual build]
```

## T7 Refactor plan
```markdown
Goal · Boundary (inbound edges: N) · Seam: [adapter/facade]
| Step | Change | Builds green? | Tests | Rollback |
|---|---|---|---|---|
| 0 | Break cycle: extract types → leaf | | | |
Door type: two-way/one-way · Flag: [name/none] · Decision record: [link/inline]
```

## T8 Dead-code audit
```markdown
| Symbol | File:L | Index callers | rg hits (non-def) | Dynamic risk | Verdict |
|---|---|---|---|---|---|
| | | 0 | 0 | none | Delete (EXTRACTED) |
| | | 0 | 2 (config) | yes | Keep / deprecate (AMBIGUOUS) |
Public exports excluded unless consumers checked.
```

## T9 Docs drift ledger
```markdown
| Doc claim (doc:L) | Code reality (path:L) | Status | Tag | Fix |
|---|---|---|---|---|
| `--verbose` flag | not in CLI parser | missing in code | EXTRACTED | remove from docs |
Summary: [X match / Y drift / Z missing / W undocumented]
```

## T10 Cost report
```markdown
Tasks [N] · Rungs: L0 a, L1 b, L2 c, L3 d, L4 e, L5 f · Range reads [n] · Files avoided [n] · LLM calls [n]
Tokens: [in/out] ([measured|~est]) · Escalations: [rung: reason]
```

## T11 Client proposal / estimate
```markdown
**Request:** [plain language]
**Estimate:** [low–high] eng-days · Confidence: [H/M/L]
Basis: [files N, prod callers N, packages N, tests to update N, unknown systems N]
Assumptions (each widens the range if false): 1. … 2. …
Narrowing spikes: [spike → new range]
Risks to users during delivery: [journeys, mitigation]
Out of scope: […]
```

---

## Cost footer (optional, one line)
Use on multi-step investigations or when asked:
`Rungs L1→L3 · 1 range read · ~9 files avoided · 0 LLM calls · tokens ~est`
