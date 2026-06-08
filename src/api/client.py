#!/usr/bin/env python
"""CLI client for the Social Manipulation Detector Agent API."""

from __future__ import annotations

import argparse
import json
import sys

import httpx

BASE_URL = "http://localhost:8000"


def analyze_text(args: argparse.Namespace) -> None:
    payload = {
        "text": args.text,
        "platform": args.platform,
        "thread_id": args.thread_id or "",
        "author_id": args.author_id or "",
    }
    response = httpx.post(f"{BASE_URL}/analyze/text", json=payload)
    _print_response(response)


def analyze_thread(args: argparse.Namespace) -> None:
    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    payload = {
        "comments": data.get("comments", []),
        "platform": args.platform,
        "thread_id": data.get("thread_id", ""),
    }
    response = httpx.post(f"{BASE_URL}/analyze/thread", json=payload)
    _print_response(response)


def analyze_account(args: argparse.Namespace) -> None:
    payload = {
        "account_id": args.account_id,
        "platform": args.platform,
        "recent_comments": [],
    }
    response = httpx.post(f"{BASE_URL}/analyze/account", json=payload)
    _print_response(response)


def _print_response(response: httpx.Response) -> None:
    if response.status_code >= 400:
        print(f"Error {response.status_code}: {response.text}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(response.json(), indent=2, default=str))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="smda-client",
        description="Social Manipulation Detector Agent CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    text_parser = subparsers.add_parser("analyze-text", help="Analyze a single text")
    text_parser.add_argument("--text", required=True, help="Comment text to analyze")
    text_parser.add_argument("--platform", default="unknown", help="Platform name")
    text_parser.add_argument("--thread-id", default="", help="Thread ID for context")
    text_parser.add_argument("--author-id", default="", help="Author account ID")
    text_parser.set_defaults(func=analyze_text)

    thread_parser = subparsers.add_parser("analyze-thread", help="Analyze a thread from JSON file")
    thread_parser.add_argument("--input", required=True, help="JSON file with thread data")
    thread_parser.add_argument("--platform", default="unknown", help="Platform name")
    thread_parser.set_defaults(func=analyze_thread)

    account_parser = subparsers.add_parser("analyze-account", help="Analyze account behavior")
    account_parser.add_argument("--account-id", required=True, help="Account ID")
    account_parser.add_argument("--platform", required=True, help="Platform name")
    account_parser.set_defaults(func=analyze_account)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
