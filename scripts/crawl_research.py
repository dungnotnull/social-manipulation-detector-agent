#!/usr/bin/env python
"""Weekly research paper crawler for SMDA pattern library updates."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.crawler.research_crawler import ResearchCrawler


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl research papers for manipulation detection insights")
    parser.add_argument(
        "--topics",
        nargs="+",
        default=[
            "disinformation detection",
            "bot detection NLP",
            "LLM text detection",
            "coordinated inauthentic behavior",
            "FOMO manipulation crypto",
        ],
        help="Research topics to search",
    )
    parser.add_argument("--max-papers", type=int, default=30, help="Max papers per source")
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to save paper summaries",
    )
    args = parser.parse_args()

    crawler = ResearchCrawler()
    count = crawler.run_weekly_crawl(
        topics=args.topics,
        output_dir=Path(args.output_dir),
    )

    print(f"Crawled and saved {count} papers to {args.output_dir}")


if __name__ == "__main__":
    main()
