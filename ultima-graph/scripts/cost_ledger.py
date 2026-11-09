#!/usr/bin/env python3
"""
cost_ledger.py - Session Cost and Evidence Ledger for ultima-graph.
Standard library only. Tracks task costs, rung escalations, files read vs avoided,
and token metrics. Writes to .ultima/ledger.jsonl.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_LEDGER_DIR = Path(".ultima")
DEFAULT_LEDGER_FILE = DEFAULT_LEDGER_DIR / "ledger.jsonl"


def ensure_ledger_dir(ledger_path: Path) -> Path:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    return ledger_path


def cmd_record(args: argparse.Namespace) -> None:
    ledger_path = Path(args.ledger_path)
    ensure_ledger_dir(ledger_path)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_name": args.task,
        "rung": args.rung,
        "files_read": args.files_read,
        "files_avoided": args.files_avoided,
        "llm_calls": args.llm_calls,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "is_estimate": bool(args.estimate),
        "notes": args.notes or "",
    }

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Recorded task: {args.task} [Rung: {args.rung}] -> {ledger_path}")


def cmd_report(args: argparse.Namespace) -> None:
    ledger_path = Path(args.ledger_path)
    if not ledger_path.exists():
        print(f"Ledger file not found at {ledger_path}. No runs recorded yet.")
        return

    entries = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not entries:
        print("Ledger is empty.")
        return

    total_tasks = len(entries)
    total_files_read = sum(e.get("files_read", 0) for e in entries)
    total_files_avoided = sum(e.get("files_avoided", 0) for e in entries)
    total_llm_calls = sum(e.get("llm_calls", 0) for e in entries)
    total_input_tokens = sum(e.get("input_tokens", 0) for e in entries)
    total_output_tokens = sum(e.get("output_tokens", 0) for e in entries)
    has_estimates = any(e.get("is_estimate", False) for e in entries)

    rungs_count: dict[str, int] = {}
    for e in entries:
        rung = e.get("rung", "unknown")
        rungs_count[rung] = rungs_count.get(rung, 0) + 1

    # Output markdown report
    print("\n# Ultima-Graph Session Cost & Efficiency Ledger\n")
    print(f"- Total Tasks Executed: {total_tasks}")
    print(f"- Files Directly Read: {total_files_read}")
    print(f"- Files Avoided via Index: {total_files_avoided}")
    avoidance_rate = (
        (total_files_avoided / (total_files_read + total_files_avoided) * 100)
        if (total_files_read + total_files_avoided) > 0
        else 0.0
    )
    print(f"- File Avoidance Ratio: {avoidance_rate:.1f}%")
    print(f"- LLM Extraction Calls: {total_llm_calls}")
    token_label = " (contains estimates)" if has_estimates else " (measured)"
    print(f"- Total Ingested Tokens: {total_input_tokens:,}{token_label}")
    print(f"- Total Emitted Tokens: {total_output_tokens:,}{token_label}")

    print("\n## Execution Rung Distribution\n")
    print("| Rung | Level Description | Invocations |")
    print("|---|---|---|")
    rung_labels = {
        "L0": "In-context / Cached Artifact",
        "L1": "Deterministic Index Query",
        "L2": "Cached Topology Analytics",
        "L3": "Targeted Code Range Read",
        "L4": "Incremental Delta Re-index",
        "L5": "LLM Semantic Extraction",
        "L6": "Full Corpus Rebuild",
    }
    for rung_key in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        cnt = rungs_count.get(rung_key, 0)
        print(f"| {rung_key} | {rung_labels.get(rung_key, 'Custom')} | {cnt} |")

    print("\n## Recent Task Ledger\n")
    print("| Timestamp (UTC) | Task | Rung | Read | Avoided | Tokens (In/Out) | Notes |")
    print("|---|---|---|---|---|---|---|")
    for e in entries[-10:]:
        ts = e.get("timestamp", "").replace("T", " ")[:19]
        task = e.get("task_name", "")
        rg = e.get("rung", "")
        fr = e.get("files_read", 0)
        fa = e.get("files_avoided", 0)
        tin = e.get("input_tokens", 0)
        tout = e.get("output_tokens", 0)
        notes = e.get("notes", "")[:35]
        print(f"| {ts} | {task} | {rg} | {fr} | {fa} | {tin:,} / {tout:,} | {notes} |")


def cmd_reset(args: argparse.Namespace) -> None:
    ledger_path = Path(args.ledger_path)
    if ledger_path.exists():
        ledger_path.unlink()
        print(f"Reset ledger file: {ledger_path}")
    else:
        print("No active ledger file to reset.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ultima-Graph Cost and Efficiency Ledger")
    parser.add_argument(
        "--ledger-path",
        default=str(DEFAULT_LEDGER_FILE),
        help="Path to ledger.jsonl file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    rec_p = subparsers.add_parser("record", help="Record task metrics")
    rec_p.add_argument("--task", required=True, help="Task identifier or query summary")
    rec_p.add_argument(
        "--rung",
        required=True,
        choices=["L0", "L1", "L2", "L3", "L4", "L5", "L6"],
        help="Execution ladder rung",
    )
    rec_p.add_argument("--files-read", type=int, default=0, help="Count of files directly opened")
    rec_p.add_argument(
        "--files-avoided", type=int, default=0, help="Count of files answered via index"
    )
    rec_p.add_argument("--llm-calls", type=int, default=0, help="Count of LLM extraction calls")
    rec_p.add_argument("--input-tokens", type=int, default=0, help="Input tokens consumed")
    rec_p.add_argument("--output-tokens", type=int, default=0, help="Output tokens emitted")
    rec_p.add_argument(
        "--estimate", action="store_true", help="Mark token numbers as estimated rather than measured"
    )
    rec_p.add_argument("--notes", default="", help="Context or rationale notes")

    subparsers.add_parser("report", help="Display audit summary report")
    subparsers.add_parser("reset", help="Clear ledger")

    args = parser.parse_args()
    if args.command == "record":
        cmd_record(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "reset":
        cmd_reset(args)


if __name__ == "__main__":
    main()
