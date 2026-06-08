#!/usr/bin/env python
"""Auto-update SECOND-KNOWLEDGE-BRAIN.md from research findings."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SECTION_10_HEADER = "## 10. Research Findings Log (Auto-appended)"
AUTO_APPEND_MARKER = "[Auto-append zone"


def _generate_entry(papers: list[dict]) -> str:
    today = date.today().isoformat()
    entries: list[str] = [f"\n### [v0.1 — {today}] — Weekly Crawl [AUTO]\n"]

    for paper in papers:
        entries.append(f"**Paper:** \"{paper.get('title', 'Untitled')}\"")
        entries.append(f"**Source:** {paper.get('source', 'Unknown')}")
        findings = paper.get("key_findings", [])
        if findings:
            entries.append("**Key Findings:**")
            for finding in findings:
                entries.append(f"- {finding}")
        if paper.get("url"):
            entries.append(f"**URL:** {paper.get('url')}")
        entries.append("")  # blank line between papers

    return "\n".join(entries)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update SECOND-KNOWLEDGE-BRAIN.md with new research")
    parser.add_argument(
        "--input",
        required=True,
        help="Directory containing research paper summaries",
    )
    parser.add_argument(
        "--output",
        default="SECOND-KNOWLEDGE-BRAIN.md",
        help="Path to SECOND-KNOWLEDGE-BRAIN.md",
    )
    args = parser.parse_args()

    papers_file = Path(args.input) / "papers.json"
    if not papers_file.exists():
        print(f"No papers.json found in {args.input}")
        return

    with open(papers_file, encoding="utf-8") as f:
        papers = json.load(f)

    if not papers:
        print("No papers to add.")
        return

    output_path = Path(args.output)
    if not output_path.exists():
        print(f"SECOND-KNOWLEDGE-BRAIN.md not found at {output_path}")
        return

    content = output_path.read_text(encoding="utf-8")

    auto_append_idx = content.find(AUTO_APPEND_MARKER)
    if auto_append_idx == -1:
        content += f"\n\n{SECTION_10_HEADER}\n\n[AUTO-APPEND ZONE]\n"

    new_entry = _generate_entry(papers)

    marker_idx = content.find(AUTO_APPEND_MARKER)
    if marker_idx != -1:
        insert_idx = content.rfind("*[", marker_idx - 100, marker_idx)
        if insert_idx == -1:
            insert_idx = content.find("[AUTO-APPEND ZONE]")
            if insert_idx == -1:
                insert_idx = marker_idx

        content = content[:insert_idx] + new_entry + content[insert_idx:]
    else:
        content += new_entry

    output_path.write_text(content, encoding="utf-8")
    print(f"Updated {output_path} with {len(papers)} papers.")


if __name__ == "__main__":
    main()
