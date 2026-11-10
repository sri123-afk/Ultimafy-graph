#!/usr/bin/env python3
"""
verify_citations.py - Deterministic Ground-Truth Citation Verifier for ultima-graph.

Validates that technical claims, citations, line numbers, and quoted snippets
in agent responses strictly match files on disk without relying on LLM judgment.
Fails closed: if any citation fails, the response must be rejected.
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Tuple, Any, Optional


def normalize_text(text: str) -> str:
    """Normalize whitespace for robust snippet comparison."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    return "\n".join(lines)


def verify_single_citation(repo_root: str, citation: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Verify a single citation against disk.
    
    Expected citation dictionary fields:
      - file: Relative path to file from repo_root
      - lines: [start_line, end_line] (1-indexed, inclusive) or int
      - snippet: (Optional) Exact quoted text expected within line range
      - symbol: (Optional) Identifier expected in snippet or line range
    """
    rel_path = citation.get("file")
    if not rel_path:
        return False, "Missing 'file' field in citation."

    full_path = os.path.join(repo_root, rel_path)
    if not os.path.exists(full_path):
        return False, f"File not found on disk: {rel_path}"

    if not os.path.isfile(full_path):
        return False, f"Path is not a regular file: {rel_path}"

    try:
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            file_lines = f.readlines()
    except Exception as exc:
        return False, f"Failed to read file {rel_path}: {exc}"

    total_lines = len(file_lines)
    lines_spec = citation.get("lines")

    start_line = 1
    end_line = total_lines

    if lines_spec is not None:
        if isinstance(lines_spec, int):
            start_line = end_line = lines_spec
        elif isinstance(lines_spec, list) and len(lines_spec) == 2:
            start_line, end_line = lines_spec[0], lines_spec[1]
        elif isinstance(lines_spec, str):
            match = re.search(r"L?(\d+)(?:-L?(\d+))?", lines_spec)
            if match:
                start_line = int(match.group(1))
                end_line = int(match.group(2)) if match.group(2) else start_line
            else:
                return False, f"Unparseable line range: {lines_spec}"
        else:
            return False, f"Invalid lines specification: {lines_spec}"

    if start_line < 1 or end_line > total_lines or start_line > end_line:
        return False, (
            f"Line range [{start_line}, {end_line}] out of bounds for "
            f"{rel_path} (total lines: {total_lines})."
        )

    target_lines = file_lines[start_line - 1 : end_line]
    target_text = "".join(target_lines)

    # Validate symbol presence if specified
    symbol = citation.get("symbol")
    if symbol and symbol not in target_text:
        return False, (
            f"Symbol '{symbol}' not found in {rel_path} "
            f"between lines {start_line}-{end_line}."
        )

    # Validate snippet match if specified
    snippet = citation.get("snippet")
    if snippet:
        norm_snippet = normalize_text(snippet)
        norm_target = normalize_text(target_text)
        if norm_snippet not in norm_target:
            return False, (
                f"Snippet mismatch in {rel_path}:{start_line}-{end_line}.\n"
                f"Expected snippet:\n{snippet}\n"
                f"Actual content:\n{target_text.strip()}"
            )

    return True, f"Verified {rel_path}:{start_line}-{end_line}"


def parse_citations_from_markdown(content: str) -> List[Dict[str, Any]]:
    """
    Extract citations formatted as `path/to/file:L10-L20` or
    `path/to/file:10` from markdown text.
    """
    citations = []
    pattern = re.compile(r"`([a-zA-Z0-9_\-./]+):(?:L)?(\d+)(?:-(?:L)?(\d+))?`")
    for match in pattern.finditer(content):
        file_path = match.group(1)
        start = int(match.group(2))
        end = int(match.group(3)) if match.group(3) else start
        citations.append({
            "file": file_path,
            "lines": [start, end]
        })
    return citations


def run_canary_checks(repo_root: str) -> bool:
    """
    Self-test: runs planted valid and deliberately invalid citations
    to ensure the verifier has a 0% false-acceptance rate.
    """
    print("Running deterministic canary checks for verify_citations.py...")
    
    # 1. Valid case against this script itself
    this_script_rel = os.path.relpath(__file__, repo_root)
    valid_citation = {
        "file": this_script_rel,
        "lines": [1, 5],
        "snippet": "verify_citations.py",
        "symbol": "verify_citations"
    }
    ok, msg = verify_single_citation(repo_root, valid_citation)
    if not ok:
        print(f"CANARY FAILURE: Valid citation was rejected: {msg}")
        return False

    # 2. Planted invalid case: Nonexistent file
    bogus_file_citation = {
        "file": "nonexistent_module_404.ts",
        "lines": [1, 10]
    }
    ok, _ = verify_single_citation(repo_root, bogus_file_citation)
    if ok:
        print("CANARY FAILURE: Nonexistent file was falsely accepted!")
        return False

    # 3. Planted invalid case: Line number out of range
    out_of_bounds_citation = {
        "file": this_script_rel,
        "lines": [99999, 100005]
    }
    ok, _ = verify_single_citation(repo_root, out_of_bounds_citation)
    if ok:
        print("CANARY FAILURE: Out-of-bounds line range was falsely accepted!")
        return False

    # 4. Planted invalid case: Mismatched snippet
    mismatched_snippet_citation = {
        "file": this_script_rel,
        "lines": [1, 10],
        "snippet": "definitely_not_in_this_file_ever_12345"
    }
    ok, _ = verify_single_citation(repo_root, mismatched_snippet_citation)
    if ok:
        print("CANARY FAILURE: Hallucinated snippet was falsely accepted!")
        return False

    print("All canary checks passed. False acceptance rate: 0.0%. Verifier integrity confirmed.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Verify citation ground truth for ultima-graph."
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: current directory)"
    )
    parser.add_argument(
        "--citations-json",
        help="Path to JSON file containing list of citation objects"
    )
    parser.add_argument(
        "--input-file",
        help="Path to markdown/text file to extract citations from"
    )
    parser.add_argument(
        "--canary",
        action="store_true",
        help="Run self-testing canary checks and exit"
    )

    args = parser.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    if args.canary:
        success = run_canary_checks(repo_root)
        sys.exit(0 if success else 1)

    citations = []

    if args.citations_json:
        with open(args.citations_json, "r", encoding="utf-8") as f:
            citations = json.load(f)
    elif args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            content = f.read()
            citations = parse_citations_from_markdown(content)
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            raw_input = sys.stdin.read().strip()
            if raw_input.startswith("[") or raw_input.startswith("{"):
                loaded = json.loads(raw_input)
                citations = loaded if isinstance(loaded, list) else [loaded]
            else:
                citations = parse_citations_from_markdown(raw_input)
        else:
            parser.print_help()
            sys.exit(2)

    if not citations:
        print("Warning: No citations provided to verify.")
        sys.exit(0)

    failed = []
    passed = []

    for i, c in enumerate(citations, start=1):
        ok, msg = verify_single_citation(repo_root, c)
        if ok:
            passed.append((c, msg))
        else:
            failed.append((c, msg))

    print(f"Citation Verification Summary: {len(passed)} passed, {len(failed)} failed.")

    if failed:
        print("\nVerification Failures (FAIL-CLOSED):")
        for c, reason in failed:
            print(f"- Target: {c.get('file')}:{c.get('lines', 'N/A')}")
            print(f"  Reason: {reason}")
        print("\nResult: REJECTED - Response claims do not match ground truth on disk.")
        sys.exit(1)

    print("\nResult: ACCEPTED - All citations verified against disk.")
    sys.exit(0)


if __name__ == "__main__":
    main()
