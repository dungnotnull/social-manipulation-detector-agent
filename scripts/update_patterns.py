#!/usr/bin/env python
"""Auto-update manipulation pattern YAML files from research findings."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))


PATTERN_CATEGORIES = {
    "A": "psychological_influence",
    "B": "coordinated_behavior",
    "C": "financial_manipulation",
    "D": "disinformation",
    "E": "llm_patterns",
}


def _load_existing_patterns(output_dir: Path) -> dict[str, dict]:
    existing: dict[str, dict] = {}
    for cat_letter, cat_name in PATTERN_CATEGORIES.items():
        path = output_dir / f"{cat_letter}_{cat_name}.yaml"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                existing[cat_letter] = yaml.safe_load(f) or {}
    return existing


def _bump_version(version_str: str) -> str:
    try:
        parts = version_str.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    except (ValueError, IndexError):
        return "1.0.0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Update manipulation pattern YAML files")
    parser.add_argument(
        "--source",
        required=True,
        help="Directory containing research paper summaries (papers.json)",
    )
    parser.add_argument(
        "--output",
        default="data/manipulation_patterns",
        help="Output directory for pattern YAML files",
    )
    args = parser.parse_args()

    source_dir = Path(args.source)
    papers_file = source_dir / "papers.json"
    if not papers_file.exists():
        print(f"No papers.json found in {args.source}")
        return

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(papers_file, encoding="utf-8") as f:
        papers = json.load(f)

    new_patterns_by_category: dict[str, list[dict]] = {}
    for paper in papers:
        for tactic in paper.get("extracted_tactics", []):
            cat = tactic.get("category", "A")
            new_patterns_by_category.setdefault(cat, []).append({
                "name": tactic.get("name", "UNKNOWN"),
                "description": tactic.get("description", ""),
                "source": paper.get("title", "Unknown paper"),
                "added_date": date.today().isoformat(),
            })

    if not new_patterns_by_category:
        print("No new patterns found. Nothing to update.")
        return

    total_new = 0
    for cat_letter, new_patterns in new_patterns_by_category.items():
        cat_name = PATTERN_CATEGORIES.get(cat_letter, "unknown")
        file_path = output_dir / f"{cat_letter}_{cat_name}.yaml"

        if file_path.exists():
            with open(file_path, encoding="utf-8") as f:
                existing = yaml.safe_load(f) or {}
            version = _bump_version(existing.get("version", "1.0.0"))
            existing_tactics = existing.get("tactics", [])
        else:
            version = "1.0.0"
            existing_tactics = []

        existing_names = {t["name"] for t in existing_tactics}
        for pattern in new_patterns:
            if pattern["name"] not in existing_names:
                existing_tactics.append(pattern)
                total_new += 1

        output = {
            "version": version,
            "category": cat_letter,
            "category_name": cat_name.replace("_", " ").title(),
            "last_updated": date.today().isoformat(),
            "tactics": existing_tactics,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(output, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"Added {total_new} new patterns across {len(new_patterns_by_category)} categories.")


if __name__ == "__main__":
    main()
