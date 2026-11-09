# Tool Detection, Configuration, and Graceful Degradation

This reference defines the detection procedures, verified installation steps, MCP configuration snippets, and manual fallback protocols when neither engine is pre-installed. Load this file when initializing ultima-graph in a fresh environment or configuring agent toolchains.

---

## 1. Automated Detection Script

Always execute the deterministic detection script at the start of an engagement:
```bash
bash scripts/detect_tools.sh [path]
```

The script evaluates two engines and outputs a structured status JSON:
* `tactical_engine`: Status of the deterministic code intelligence tool (binary presence, `.ultima/tactical.db` existence, timestamp freshness against latest git commit).
* `strategic_engine`: Status of the multimodal knowledge graph tool (binary presence, `topology-out/graph.json` existence, freshness).
* `tool_state`: Evaluates to one of four states:
  1. `both_available`: Full hybrid capabilities active.
  2. `tactical_only`: High-speed code intelligence active; topological and multimodal clustering disabled.
  3. `strategic_only`: Architecture reports and GraphRAG active; verbatim code-slicing falls back to range reads.
  4. `none_available`: Graceful degradation protocol engaged.

---

## 2. Engine Installation & Setup

### Tactical Engine Setup
* **Binary Installation:**
  Ensure the tactical indexing CLI is available on `PATH` as `tactical`.
* **Project Initialization:**
  ```bash
  cd /path/to/project
  tactical init
  ```

### Strategic Engine Setup
* **Package Installation:**
  Ensure the strategic topology package is available on `PATH` as `strategic`.
* **Project Initialization:**
  ```bash
  cd /path/to/project
  strategic . --no-viz
  ```

---

## 3. Real MCP Server Configuration Snippets

### 1. Claude Code (`~/.claude.json` or project-level `.mcp.json`)
```json
{
  "mcpServers": {
    "tactical_engine": {
      "type": "stdio",
      "command": "tactical",
      "args": ["serve", "--mcp"],
      "alwaysLoad": true
    },
    "strategic_engine": {
      "type": "stdio",
      "command": "strategic-mcp",
      "args": []
    }
  }
}
```

### 2. Cursor (`.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "tactical_engine": {
      "command": "tactical",
      "args": ["serve", "--mcp", "--path", "${workspaceFolder}"]
    },
    "strategic_engine": {
      "command": "strategic-mcp",
      "args": []
    }
  }
}
```

### 3. Codex CLI / OpenCode (`opencode.jsonc` or `~/.codex/config.toml`)
For TOML-based configurations:
```toml
[mcp_servers.tactical_engine]
command = "tactical"
args = ["serve", "--mcp"]

[mcp_servers.strategic_engine]
command = "strategic-mcp"
args = []
```

---

## 4. Manual Fallbacks & Graceful Degradation (When Tools Are Absent)

When `tool_state` reports `none_available`:
1. **Be Transparent:** Inform the user immediately:
   > "Neither tactical nor strategic graph indexing engines are currently installed. Operating under Graceful Degradation protocol: using targeted lexical grep and strict range-bound reads."
2. **Offer Setup Steps:** Present the setup commands shown above.
3. **Execute Equivalent Manual Discipline:**
   * **Instead of `tactical explore`:**
     - Use `rg` or `grep -n` with word boundaries (`rg -w "symbol_name"`).
     - Locate definition line numbers.
     - Read strictly the relevant line range using `Read` (e.g., `path/to/file.ts:L30-L75`). Never read the entire file.
   * **Instead of `tactical callers`:**
     - Run `rg -n "(\.|\b)method_name\("` across `src/` directory.
     - Filter out self-calls and test files.
   * **Instead of `tactical affected`:**
     - Inspect imports in test directory via `rg -l "import.*from.*target_module" tests/`.
   * **Instead of `strategic god_nodes`:**
     - Identify high-degree files using shell frequency count:
       ```bash
       git grep -h "import " | sort | uniq -c | sort -nr | head -10
       ```
4. **Log the Fallback Run:** Record the execution in `.ultima/ledger.jsonl` noting the manual degradation rung.
