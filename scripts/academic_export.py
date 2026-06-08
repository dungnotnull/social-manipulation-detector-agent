#!/usr/bin/env python
"""Export anonymized verdict data for academic contribution."""

from __future__ import annotations

import json
import sys
from datetime import date
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def export_dataset(output_dir: str, limit: int = 5000) -> Path:
    today = date.today().isoformat()
    output_path = Path(output_dir) / f"smda-academic-export-{today}.jsonl"

    sample_data = [
        {
            "text_hash": sha256(b"sample").hexdigest()[:16],
            "language": "en",
            "platform": "twitter",
            "manipulation_index": 0.04,
            "level": "CLEAN",
            "tactics_detected": [],
            "confidence": "HIGH",
        },
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        for record in sample_data:
            f.write(json.dumps(record) + "\n")

    print(f"Exported {len(sample_data)} records to {output_path}")
    print("Note: Replace with real DB queries for production export.")
    return output_path


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Export academic dataset (anonymized)")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--limit", type=int, default=5000, help="Max records")
    args = parser.parse_args()
    export_dataset(args.output_dir, args.limit)


if __name__ == "__main__":
    main()
