#!/usr/bin/env python3
"""
preflight_estimate.py - Sizing, cost and safety preflight for ultima-graph.

Separates CODE (AST-indexed locally, no LLM tokens) from LLM-BOUND files
(docs, papers, images, media - these cost tokens under L5 semantic extraction),
flags sensitive files to exclude, and applies the SKILL.md section 5 L5 gate.
Uses `git ls-files` when inside a repo so .gitignore is respected. Stdlib only.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
from pathlib import Path

CODE_EXTS = {
    ".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
    ".rb", ".swift", ".kt", ".kts", ".cs", ".scala", ".php", ".lua",
    ".zig", ".dart", ".vue", ".svelte", ".astro", ".sql", ".sh", ".bash",
    ".ex", ".exs", ".erl", ".hs", ".ml", ".clj", ".r", ".jl", ".m", ".mm",
}
CONFIG_EXTS = {".json", ".yaml", ".yml", ".toml", ".hcl", ".tf", ".ini", ".xml", ".gradle", ".properties"}
DOC_EXTS = {".md", ".mdx", ".txt", ".rst", ".adoc", ".html", ".htm"}
PAPER_EXTS = {".pdf", ".docx", ".pptx", ".xlsx"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MEDIA_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".mp3", ".wav", ".m4a"}

IGNORE_DIRS = {
    "node_modules", "vendor", "dist", "build", "target", ".git", ".next", ".nuxt",
    "Pods", ".venv", "venv", "__pycache__", ".codegraph", "graphify-out", ".ultima",
    "coverage", ".turbo", ".cache",
}
SENSITIVE_GLOBS = [
    ".env", ".env.*", "*.pem", "*.key", "*.p12", "*.pfx", "id_rsa*", "id_ed25519*",
    "*credentials*", "*secret*", "*.kdbx", "*.sqlite", "*.db", "*.dump", "*.bak",
]
SENSITIVE_DIRS = {"secrets", "customer-data", "customer_data", "pii", "exports", "backups"}
GENERATED_GLOBS = ["*.pb.go", "*_pb2.py", "*.g.dart", "*.generated.*", "*_generated.*", "*.min.js", "*.lock"]

COMPACT_MAX_SOURCE = 30
L5_MAX_FILES = 50
L5_MAX_WORDS = 200_000
MAX_RAW_FILE_BYTES = 50 * 1024 * 1024
WORD_SAMPLE_BYTES = 250_000


def list_files(root: Path) -> tuple[list[Path], str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
            capture_output=True, check=True, timeout=30,
        ).stdout
        files = [root / p for p in out.decode("utf-8", "replace").split("\0") if p]
        files = [f for f in files if not (set(f.relative_to(root).parts[:-1]) & IGNORE_DIRS)]
        return files, "git"
    except (OSError, subprocess.SubprocessError):
        pass
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        files.extend(Path(dirpath) / f for f in filenames)
    return files, "walk"


def is_sensitive(rel: Path) -> bool:
    name = rel.name.lower()
    if any(fnmatch.fnmatch(name, g) for g in SENSITIVE_GLOBS) and not name.endswith((".example", ".sample", ".template")):
        return True
    return bool({p.lower() for p in rel.parts[:-1]} & SENSITIVE_DIRS)


def analyze_corpus(root: Path) -> dict:
    files, source = list_files(root)
    counts = {k: 0 for k in ("code", "config", "document", "paper", "image", "media", "generated", "other")}
    words = 0
    sensitive, skipped_large = [], []

    for fpath in files:
        try:
            st = fpath.stat()
        except OSError:
            continue
        rel = fpath.relative_to(root)
        if is_sensitive(rel):
            sensitive.append(str(rel))
            continue
        if st.st_size > MAX_RAW_FILE_BYTES:
            skipped_large.append({"path": str(rel), "size_mb": round(st.st_size / 1048576, 2)})
            continue
        name, ext = fpath.name.lower(), fpath.suffix.lower()
        if any(fnmatch.fnmatch(name, g) for g in GENERATED_GLOBS):
            counts["generated"] += 1
        elif ext in CODE_EXTS:
            counts["code"] += 1
        elif ext in CONFIG_EXTS:
            counts["config"] += 1
        elif ext in DOC_EXTS:
            counts["document"] += 1
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    words += len(f.read(WORD_SAMPLE_BYTES).split())
            except OSError:
                pass
        elif ext in PAPER_EXTS:
            counts["paper"] += 1
            words += int(st.st_size / 20)  # rough: ~20 bytes/word in PDF/Office
        elif ext in IMAGE_EXTS:
            counts["image"] += 1
        elif ext in MEDIA_EXTS:
            counts["media"] += 1
        else:
            counts["other"] += 1

    llm_bound_files = counts["document"] + counts["paper"] + counts["image"] + counts["media"]
    source_files = counts["code"] + counts["config"]
    needs_consent = llm_bound_files > L5_MAX_FILES or words > L5_MAX_WORDS or counts["media"] > 0

    if source_files < COMPACT_MAX_SOURCE and llm_bound_files < COMPACT_MAX_SOURCE:
        status, rec = "compact", "Skip indexing; use rg + targeted reads."
    elif needs_consent:
        status, rec = "large", ("L5 would send ~{:,} words / {} files to an LLM backend. Get explicit consent; "
                                "offer --code-only, narrower dirs, or a local backend.").format(words, llm_bound_files)
    else:
        status, rec = "normal", "CodeGraph/Graphify code-only indexing is free (local AST). L5 on named docs is fine."
    if sensitive:
        rec += f" {len(sensitive)} sensitive file(s) found: add them to .graphifyignore before any L5 run."

    return {
        "root": str(root),
        "file_source": source,
        "status": status,
        "recommendation": rec,
        "code": {"files": counts["code"], "config_files": counts["config"], "generated_files": counts["generated"],
                 "llm_tokens": 0},
        "llm_bound": {"files": llm_bound_files, "estimated_words": words,
                      "estimated_tokens": int(words * 1.33),
                      "documents": counts["document"], "papers": counts["paper"],
                      "images": counts["image"], "media": counts["media"]},
        "l5_consent_required": needs_consent,
        "other_files": counts["other"],
        "sensitive_files": sensitive[:50],
        "sensitive_count": len(sensitive),
        "skipped_large_files": skipped_large,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Corpus preflight: cost split, L5 gate, sensitive files.")
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args()
    r = analyze_corpus(Path(args.path).resolve())
    if args.json:
        print(json.dumps(r, indent=2))
        return
    c, l = r["code"], r["llm_bound"]
    print(f"Preflight: {r['root']} [{r['status'].upper()}] (files via {r['file_source']})")
    print(f"  Code (local AST, 0 LLM tokens): {c['files']} source, {c['config_files']} config, {c['generated_files']} generated")
    print(f"  LLM-bound (L5 cost): {l['files']} files: {l['documents']} docs, {l['papers']} papers, "
          f"{l['images']} images, {l['media']} media, ~{l['estimated_words']:,} words (~{l['estimated_tokens']:,} tokens est)")
    print(f"  L5 consent required: {'YES' if r['l5_consent_required'] else 'no'}")
    if r["sensitive_count"]:
        print(f"  Sensitive (exclude): {r['sensitive_count']}: " + ", ".join(r["sensitive_files"][:10]))
    for s in r["skipped_large_files"]:
        print(f"  Skipped >50MB: {s['path']} ({s['size_mb']} MB)")
    print(f"  → {r['recommendation']}")


if __name__ == "__main__":
    main()
