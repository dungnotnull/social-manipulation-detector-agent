#!/usr/bin/env python
"""Build and package the browser extension for Chrome and Firefox."""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path


def build_chrome(source_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "smda-chrome.zip"

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in source_dir.rglob("*"):
            if file_path.is_dir():
                continue
            if "__pycache__" in str(file_path):
                continue
            arcname = str(file_path.relative_to(source_dir))
            zf.write(file_path, arcname)

    return output_path


def build_firefox(source_dir: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = source_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    bg = manifest.get("background", {})
    if "scripts" not in bg and "service_worker" in bg:
        bg["scripts"] = [bg.pop("service_worker")]
        manifest["background"] = bg
    manifest["manifest_version"] = 2

    browsers = manifest.pop("browser_specific_settings", None)

    firefox_manifest = {
        **manifest,
        "browser_specific_settings": browsers or {
            "gecko": {
                "id": "social-manipulation-detector@smda.dev",
                "strict_min_version": "115.0",
            }
        },
    }

    output_path = output_dir / "smda-firefox.zip"
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(firefox_manifest, indent=2))
        for file_path in source_dir.rglob("*"):
            if file_path.is_dir():
                continue
            if file_path.name == "manifest.json":
                continue
            if "__pycache__" in str(file_path):
                continue
            arcname = str(file_path.relative_to(source_dir))
            zf.write(file_path, arcname)

    return output_path


def main() -> None:
    source_dir = Path(__file__).parent.parent / "src" / "extension"
    output_dir = Path(__file__).parent.parent / "dist" / "extension"

    chrome_zip = build_chrome(source_dir, output_dir / "chrome")
    print(f"Chrome extension: {chrome_zip} ({chrome_zip.stat().st_size} bytes)")

    firefox_zip = build_firefox(source_dir, output_dir / "firefox")
    print(f"Firefox extension: {firefox_zip} ({firefox_zip.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
