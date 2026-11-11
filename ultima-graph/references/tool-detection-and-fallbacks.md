# Tool Detection, Setup, and Degraded Mode

Load when initializing in a fresh environment, configuring MCP, or working without either engine.

---

## 1. Detection

**Cheapest first:** if the session's tool list already contains `codegraph_explore` or graphify MCP tools, you're done.

Otherwise run once per session and reuse the output:
```bash
bash scripts/detect_tools.sh .
```
Output fields:
- `tool_state`: `both_available` | `tactical_only` | `strategic_only` | `none_available`
- `tactical_engine`: `binary`, `version`, `indexed` (`.codegraph/codegraph.db`), `fresh` (`true` | `false` | `unknown`), `features` (`cycles`, `implementations`)
- `strategic_engine`: `binary`, `mcp_binary`, `indexed` (`graphify-out/graph.json`), `fresh`, `report` (path to `GRAPH_REPORT.md` if present)
- `stale_files`: up to 10 tracked files changed after the index was written

`fresh: false` → run `bash scripts/update.sh` once (refreshes only stale engines, no LLM), or warn that line numbers in `stale_files` may have shifted. Missing index → `bash scripts/update.sh --init`.

---

## 2. Install (verified commands)

| Engine | Install | First index |
|---|---|---|
| CodeGraph | `npm i -g @colbymchenry/codegraph` (or `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh \| sh`) | `codegraph init` |
| Graphify | `uv tool install graphifyy` (or `pipx install graphifyy`) | `graphify extract . --code-only` (no LLM) or `/graphify .` in Claude Code |

`codegraph install -y -t auto` wires the MCP server into detected agents (Claude Code, Cursor, Codex, opencode, Gemini CLI, Antigravity, Copilot…). `--print-config <agent>` prints the snippet without writing anything. `graphify install --platform <p>` / `graphify claude install` set up graphify's skill/hook.

---

## 3. Manual MCP config

Claude Code (`.mcp.json` or `~/.claude.json`):
```json
{
  "mcpServers": {
    "codegraph": { "type": "stdio", "command": "codegraph", "args": ["serve", "--mcp"] },
    "graphify":  { "type": "stdio", "command": "graphify-mcp", "args": [] }
  }
}
```
Cursor (`.cursor/mcp.json`): same entries. Add `"--path", "${workspaceFolder}"` to codegraph args if the client doesn't send a root.

Codex (`~/.codex/config.toml`):
```toml
[mcp_servers.codegraph]
command = "codegraph"
args = ["serve", "--mcp"]

[mcp_servers.graphify]
command = "graphify-mcp"
args = []
```
Only one live codegraph writer per project. Extra clients proxy to the shared daemon automatically. Use `--no-watch` on slow filesystems (WSL `/mnt`).

---

## 4. Degraded Mode (no engines)

State it once, offer the install line, then work. Don't keep apologizing.

| Instead of | Do |
|---|---|
| `codegraph_explore` | `rg -n -w "Symbol"` → read the definition's range (±20 lines, or whole file if < ~150 lines) |
| `callers X` | `rg -n -w "X\s*\(" --glob '!**/*test*'` + `rg -n "\.X\b"` for method calls. Tag results `INFERRED` (lexical) |
| `impact X` | Repeat callers on each caller to depth 2, and stop at 20 hits/level |
| `affected` | `rg -l -w "<module or symbol>" <test dirs>` |
| `cycles` | Python: `madge --circular` if installed. JS/TS: `npx madge --circular src` (ask first: network) |
| `god-nodes` | Most-imported modules: `rg -o --no-filename "from ['\"]([^'\"]+)['\"]" -r '$1' \| sort \| uniq -c \| sort -nr \| head` (adapt per language) |
| Hotspots | `git log --since=6.months --name-only --format= \| sort \| uniq -c \| sort -nr \| head -20` |

Lexical results are always ≤ `INFERRED`. Say that coverage is weaker for dynamic dispatch and cross-tier calls.
