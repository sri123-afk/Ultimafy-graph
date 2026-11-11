#!/usr/bin/env python3
"""
verify_citations.py - Deterministic ground-truth citation verifier for ultimafy-graph.

Checks that cited files exist INSIDE the repo, line ranges are in bounds, and
quoted snippets / symbols actually appear in the cited range. No LLM involved.

Exit codes:
  0  all citations verified
  1  one or more citations failed (fail closed)
  2  usage / input error (bad JSON, unreadable input)
  3  no citations found (use --allow-empty to treat as success)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

EXIT_OK, EXIT_FAIL, EXIT_USAGE, EXIT_EMPTY = 0, 1, 2, 3
MAX_FILE_BYTES = 20 * 1024 * 1024

# `path/to/file.ext:L10-L20`, `path:10`, `path:L10-20`, optionally preceded by
# a backticked symbol:  `Symbol` (`path:L10-L20`)
_CITE = r"`([A-Za-z0-9_\-./@+]+\.[A-Za-z0-9_+\-]+|[A-Za-z0-9_\-./@+]+):L?(\d+)(?:-L?(\d+))?`"
CITE_RE = re.compile(_CITE)
SYMBOL_CITE_RE = re.compile(r"`([A-Za-z_$][\w$.:#]*)`\s*\(\s*" + _CITE + r"\s*\)")


def normalize_text(text: str) -> str:
    return "\n".join(line.strip() for line in text.strip().splitlines() if line.strip())


def _resolve_inside(repo_root: str, rel_path: str) -> Optional[str]:
    """Return the real path if it is inside repo_root, else None."""
    if os.path.isabs(rel_path):
        candidate = os.path.realpath(rel_path)
    else:
        candidate = os.path.realpath(os.path.join(repo_root, rel_path))
    root = os.path.realpath(repo_root)
    try:
        if os.path.commonpath([root, candidate]) != root:
            return None
    except ValueError:  # different drives on Windows
        return None
    return candidate


def _parse_lines(spec: Any, total: int) -> Tuple[Optional[Tuple[int, int]], str]:
    if spec is None:
        return (1, total), ""
    if isinstance(spec, bool):
        return None, f"Invalid lines specification: {spec!r}"
    if isinstance(spec, int):
        return (spec, spec), ""
    if isinstance(spec, list) and len(spec) == 2 and all(
        isinstance(x, int) and not isinstance(x, bool) for x in spec
    ):
        return (spec[0], spec[1]), ""
    if isinstance(spec, str):
        m = re.fullmatch(r"\s*L?(\d+)(?:\s*-\s*L?(\d+))?\s*", spec)
        if m:
            start = int(m.group(1))
            return (start, int(m.group(2)) if m.group(2) else start), ""
        return None, f"Unparseable line range: {spec!r}"
    return None, f"Invalid lines specification: {spec!r}"


def verify_single_citation(repo_root: str, citation: Dict[str, Any]) -> Tuple[bool, str]:
    """
    citation fields:
      file    (required) path relative to repo_root
      lines   [start, end] | int | "L10-L20"  (1-indexed, inclusive)
      snippet optional text that must appear (whitespace-normalised) in range
      symbol  optional identifier that must appear in range
    """
    if not isinstance(citation, dict):
        return False, f"Citation must be an object, got {type(citation).__name__}."
    rel_path = citation.get("file")
    if not rel_path or not isinstance(rel_path, str):
        return False, "Missing 'file' field in citation."

    full_path = _resolve_inside(repo_root, rel_path)
    if full_path is None:
        return False, f"Path escapes repository root: {rel_path}"
    if not os.path.exists(full_path):
        return False, f"File not found on disk: {rel_path}"
    if not os.path.isfile(full_path):
        return False, f"Path is not a regular file: {rel_path}"
    if os.path.getsize(full_path) > MAX_FILE_BYTES:
        return False, f"File exceeds {MAX_FILE_BYTES // (1024 * 1024)} MB verifier limit: {rel_path}"

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            file_lines = f.readlines()
    except OSError as exc:
        return False, f"Failed to read {rel_path}: {exc}"

    total = len(file_lines)
    rng, err = _parse_lines(citation.get("lines"), total)
    if rng is None:
        return False, err
    start, end = rng
    if start < 1 or end > total or start > end:
        return False, f"Line range [{start}, {end}] out of bounds for {rel_path} (total lines: {total})."

    target_text = "".join(file_lines[start - 1:end])

    symbol = citation.get("symbol")
    if symbol:
        # Accept qualified names: Class.method matches if the last segment is present.
        tail = re.split(r"[.:#]", str(symbol))[-1] or str(symbol)
        if str(symbol) not in target_text and not re.search(rf"\b{re.escape(tail)}\b", target_text):
            return False, f"Symbol '{symbol}' not found in {rel_path}:{start}-{end}."

    snippet = citation.get("snippet")
    if snippet:
        if normalize_text(str(snippet)) not in normalize_text(target_text):
            preview = target_text.strip()
            if len(preview) > 600:
                preview = preview[:600] + "\n[...truncated]"
            return False, (
                f"Snippet mismatch in {rel_path}:{start}-{end}.\n"
                f"Expected snippet:\n{snippet}\nActual content:\n{preview}"
            )

    strength = "symbol/snippet" if (symbol or snippet) else "range-only"
    return True, f"Verified {rel_path}:{start}-{end} ({strength})"


def parse_citations_from_markdown(content: str) -> List[Dict[str, Any]]:
    """Extract `path:Lx-Ly` citations; attach a symbol when written as `Sym` (`path:Lx`)."""
    citations: List[Dict[str, Any]] = []
    seen = set()
    for m in SYMBOL_CITE_RE.finditer(content):
        sym, path, s, e = m.group(1), m.group(2), int(m.group(3)), m.group(4)
        key = (path, s, int(e) if e else s)
        seen.add(key)
        citations.append({"file": path, "lines": [key[1], key[2]], "symbol": sym})
    for m in CITE_RE.finditer(content):
        path, s, e = m.group(1), int(m.group(2)), m.group(3)
        key = (path, s, int(e) if e else s)
        if key in seen:
            continue
        seen.add(key)
        citations.append({"file": path, "lines": [key[1], key[2]]})
    return citations


def run_canary_checks() -> bool:
    """Plant valid and invalid citations in a temp repo; any false accept or false reject fails."""
    print("Running canary checks for verify_citations.py...")
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "repo")
        os.makedirs(os.path.join(root, "src"))
        with open(os.path.join(root, "src", "auth.ts"), "w", encoding="utf-8") as f:
            f.write("import x from 'y';\n\nexport function verifyToken(t: string) {\n  return t.length > 0;\n}\n")
        with open(os.path.join(tmp, "outside.txt"), "w", encoding="utf-8") as f:
            f.write("secret\n")

        must_pass = [
            {"file": "src/auth.ts", "lines": [3, 5], "symbol": "verifyToken"},
            {"file": "src/auth.ts", "lines": "L3-L4", "snippet": "export function verifyToken(t: string) {\n return t.length > 0;"},
            {"file": "src/auth.ts", "lines": 3, "symbol": "AuthService.verifyToken"},
        ]
        must_fail = [
            {"file": "src/missing.ts", "lines": [1, 2]},
            {"file": "src/auth.ts", "lines": [99, 120]},
            {"file": "src/auth.ts", "lines": [5, 3]},
            {"file": "src/auth.ts", "lines": True},
            {"file": "src/auth.ts", "lines": [1, 2], "symbol": "verifyToken"},
            {"file": "src/auth.ts", "lines": [3, 5], "snippet": "hallucinated_call()"},
            {"file": "../outside.txt", "lines": 1},
            {"file": os.path.join(tmp, "outside.txt"), "lines": 1},
            {"file": "src", "lines": 1},
        ]
        ok = True
        for c in must_pass:
            passed, msg = verify_single_citation(root, c)
            if not passed:
                print(f"CANARY FAILURE (false reject): {c} -> {msg}")
                ok = False
        for c in must_fail:
            passed, _ = verify_single_citation(root, c)
            if passed:
                print(f"CANARY FAILURE (false accept): {c}")
                ok = False
        md = "See `verifyToken` (`src/auth.ts:L3-L5`) and `src/auth.ts:1`."
        parsed = parse_citations_from_markdown(md)
        if len(parsed) != 2 or parsed[0].get("symbol") != "verifyToken":
            print(f"CANARY FAILURE (markdown parse): {parsed}")
            ok = False
    if ok:
        print(f"All canary checks passed ({len(must_pass)} valid, {len(must_fail)} planted invalid, 1 parse).")
    return ok


def _load_citations(args: argparse.Namespace) -> List[Dict[str, Any]]:
    if args.citations_json:
        with open(args.citations_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else [data]
    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            return parse_citations_from_markdown(f.read())
    if sys.stdin.isatty():
        raise ValueError("no input: pass --citations-json, --input-file, or pipe JSON/markdown on stdin")
    raw = sys.stdin.read().strip()
    if raw.startswith("[") or raw.startswith("{"):
        data = json.loads(raw)
        return data if isinstance(data, list) else [data]
    return parse_citations_from_markdown(raw)


def main() -> None:
    p = argparse.ArgumentParser(description="Verify citations against files on disk (fail closed).")
    p.add_argument("--repo-root", default=".", help="Repository root (default: cwd)")
    p.add_argument("--citations-json", help="JSON file with a list of citation objects")
    p.add_argument("--input-file", help="Markdown/text file to extract `path:Lx-Ly` citations from")
    p.add_argument("--canary", action="store_true", help="Run self-test and exit")
    p.add_argument("--allow-empty", action="store_true", help="Exit 0 when no citations are found")
    p.add_argument("--quiet", "-q", action="store_true", help="Only print failures and the result line")
    args = p.parse_args()

    if args.canary:
        sys.exit(EXIT_OK if run_canary_checks() else EXIT_FAIL)

    repo_root = os.path.abspath(args.repo_root)
    try:
        citations = _load_citations(args)
    except (OSError, ValueError) as exc:  # JSONDecodeError is a ValueError
        print(f"Input error: {exc}", file=sys.stderr)
        sys.exit(EXIT_USAGE)

    if not citations:
        print("No citations found.")
        sys.exit(EXIT_OK if args.allow_empty else EXIT_EMPTY)

    failed, passed, weak = [], 0, 0
    for c in citations:
        ok, msg = verify_single_citation(repo_root, c)
        if ok:
            passed += 1
            weak += msg.endswith("(range-only)")
            if not args.quiet:
                print(f"  ok   {msg}")
        else:
            failed.append((c, msg))

    for c, reason in failed:
        target = f"{c.get('file')}:{c.get('lines', 'N/A')}" if isinstance(c, dict) else repr(c)
        print(f"  FAIL {target}\n       {reason}")
    note = f" ({weak} range-only: add symbol/snippet for a meaningful check)" if weak else ""
    print(f"Result: {'REJECTED' if failed else 'ACCEPTED'}: {passed} passed, {len(failed)} failed{note}.")
    sys.exit(EXIT_FAIL if failed else EXIT_OK)


if __name__ == "__main__":
    main()
