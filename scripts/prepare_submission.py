#!/usr/bin/env python
"""Prepare extension package for Chrome Web Store and Firefox Add-ons submission."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def prepare_submission(output_dir: str | None = None) -> Path:
    if output_dir is None:
        output_dir = "dist/store-submission"

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    package = {
        "name": "Social Manipulation Detector Agent",
        "version": "0.1.0",
        "description": "AI-powered psychological manipulation & fake news shield for social platforms. "
                       "Detects coordinated bot networks, FOMO/FUD campaigns, and AI-generated disinformation "
                       "across Twitter/X, Reddit, YouTube, Facebook, Telegram, and Discord.",
        "category": "social_network_tools",
        "homepage_url": "https://github.com/social-manipulation-detector-agent",
        "support_url": "https://github.com/social-manipulation-detector-agent/issues",
        "privacy_policy_url": "https://github.com/social-manipulation-detector-agent/PRIVACY.md",
        "screenshots": [],
        "languages": ["en"],
        "permissions_justification": {
            "storage": "Store user preferences and verdict cache locally",
            "activeTab": "Detect manipulation in comments on the current tab only",
            "scripting": "Inject manipulation warning badges into comment sections",
            "alarms": "Periodically refresh campaign statistics",
        },
    }

    manifest_path = out / "store-package.json"
    manifest_path.write_text(json.dumps(package, indent=2), encoding="utf-8")

    readme_content = """# Social Manipulation Detector Agent

## Description
AI-powered browser extension that identifies psychological manipulation tactics,
coordinated bot behavior, and AI-generated synthetic content in social media comments.

## Supported Platforms
- Twitter/X
- Reddit
- YouTube
- Facebook
- Telegram Web
- Discord Web

## How It Works
1. Scans comments in real-time as you browse
2. Detects manipulation tactics (social proof, urgency, FOMO/FUD, AI-generated text)
3. Shows color-coded warning badges (🔴 HIGH, 🟠 ELEVATED, 🟡 MODERATE)
4. Click badges to see detailed evidence with exact text spans

## Privacy
- All analysis happens locally or on your own SMDA API server
- No data sent to third parties
- Comment text processed ephemerally — only verdict scores stored
"""
    (out / "README.md").write_text(readme_content, encoding="utf-8")

    print(f"Store submission package prepared at {out}")
    print("Files:")
    for f in out.iterdir():
        print(f"  {f.name}")

    return out


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Prepare extension for store submission")
    parser.add_argument("--output-dir", help="Output directory")
    args = parser.parse_args()
    prepare_submission(args.output_dir)


if __name__ == "__main__":
    main()
