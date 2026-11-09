#!/usr/bin/env python3
"""
preflight_estimate.py - Sizing and safety preflight check for ultima-graph.
Standard library only. Categorizes corpus files, estimates word count,
and flags token cost and safety thresholds prior to extraction.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

CODE_EXTS = {
    ".py", ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".cpp", ".cc", ".cxx", ".c", ".h", ".hpp",
    ".rb", ".swift", ".kt", ".kts", ".cs", ".scala", ".php", ".lua",
    ".zig", ".dart", ".vue", ".svelte", ".astro", ".sql", ".sh", ".bash",
    ".json", ".yaml", ".yml", ".toml", ".hcl", ".tf"
}
DOC_EXTS = {".md", ".mdx", ".txt", ".rst", ".html", ".skill"}
PAPER_EXTS = {".pdf"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".mp3", ".wav", ".m4a"}

IGNORE_DIRS = {
    "node_modules", "vendor", "dist", "build", "target", ".git",
    ".next", ".nuxt", "Pods", ".venv", "venv", "__pycache__",
    ".tactical", "topology-out", ".ultima"
}

WARN_FLOOR_WORDS = 50_000
WARN_CEILING_WORDS = 500_000
WARN_CEILING_FILES = 500
MAX_RAW_FILE_BYTES = 50 * 1024 * 1024  # 50 MB safety ceiling


def analyze_corpus(root: Path) -> dict:
    categories = {
        "code": [],
        "document": [],
        "paper": [],
        "image": [],
        "video": [],
        "unclassified": []
    }
    skipped_large = []
    total_words = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in place
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in filenames:
            if fname.startswith("."):
                continue
            fpath = Path(dirpath) / fname
            try:
                st = fpath.stat()
            except OSError:
                continue

            if st.st_size > MAX_RAW_FILE_BYTES:
                skipped_large.append({"path": str(fpath), "size_mb": round(st.st_size / (1024 * 1024), 2)})
                continue

            ext = fpath.suffix.lower()
            if ext in CODE_EXTS:
                categories["code"].append(str(fpath))
            elif ext in DOC_EXTS:
                categories["document"].append(str(fpath))
                # Word estimation for docs
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(250_000)  # sample up to 250KB for word count
                        total_words += len(content.split())
                except OSError:
                    pass
            elif ext in PAPER_EXTS:
                categories["paper"].append(str(fpath))
                total_words += int(st.st_size / 20)  # rough heuristic: ~20 bytes per word in PDF
            elif ext in IMAGE_EXTS:
                categories["image"].append(str(fpath))
            elif ext in VIDEO_EXTS:
                categories["video"].append(str(fpath))
            else:
                categories["unclassified"].append(str(fpath))

    total_files = sum(len(fl) for fl in categories.values())

    status = "normal"
    recommendation = "Proceed with standard L1 deterministic or L2 topological analysis."

    if total_words < WARN_FLOOR_WORDS and total_files < 30:
        status = "compact"
        recommendation = "Corpus is compact. In-context L0 reads or lightweight L1 lookups sufficient."
    elif total_words > WARN_CEILING_WORDS or total_files > WARN_CEILING_FILES:
        status = "large"
        recommendation = "Corpus exceeds standard thresholds. Rely strictly on L1 deterministic code index and obtain user consent before L5 multimodal extraction."

    return {
        "root": str(root),
        "total_files": total_files,
        "estimated_words": total_words,
        "status": status,
        "recommendation": recommendation,
        "breakdown": {
            "code_files": len(categories["code"]),
            "document_files": len(categories["document"]),
            "paper_files": len(categories["paper"]),
            "image_files": len(categories["image"]),
            "video_files": len(categories["video"]),
            "unclassified_files": len(categories["unclassified"]),
        },
        "skipped_large_files": skipped_large,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Corpus preflight sizing and threshold check.")
    parser.add_argument("path", nargs="?", default=".", help="Directory to inspect")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    target = Path(args.path).resolve()
    result = analyze_corpus(target)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("\n# Ultima-Graph Preflight Sizing & Threshold Assessment\n")
    print(f"- Target Path: {result['root']}")
    print(f"- Total Detected Files: {result['total_files']:,}")
    print(f"- Estimated Word Mass: ~{result['estimated_words']:,} words")
    print(f"- Sizing Assessment: {result['status'].upper()}")
    print(f"- Protocol Recommendation: {result['recommendation']}\n")

    print("## File Classification Breakdown\n")
    print("| Category | File Count | Handling Protocol |")
    print("|---|---|---|")
    bd = result["breakdown"]
    print(f"| Code Files | {bd['code_files']} | Deterministic AST indexing (L1) - No LLM Cost |")
    print(f"| Document Files | {bd['document_files']} | Markdown/Text extraction - Selective L5 |")
    print(f"| PDF / Papers | {bd['paper_files']} | Structural text conversion - Requires L5 gating |")
    print(f"| Images | {bd['image_files']} | Vision parsing - Requires explicit approval |")
    print(f"| Audio / Video | {bd['video_files']} | Whisper transcription - Offline only |")
    print(f"| Unclassified | {bd['unclassified_files']} | Bypassed by default |")

    if result["skipped_large_files"]:
        print("\n## Skipped Large Files (>50 MB safety ceiling)\n")
        for sk in result["skipped_large_files"]:
            print(f"- {sk['path']} ({sk['size_mb']} MB)")


if __name__ == "__main__":
    main()
