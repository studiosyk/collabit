#!/usr/bin/env python3
"""
Read a CSV with a `url` column, fetch each page, and output metadata CSV.

Example:
    python fetch_page_metadata.py ^
      --input "C:\\path\\howma_mag_article_like_clean.csv" ^
      --output "C:\\path\\howma_mag_article_metadata.csv"
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def fetch_html(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="ignore")


def strip_tags(text: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_first(pattern: str, body: str, flags: int = re.I | re.S) -> str:
    match = re.search(pattern, body, flags)
    if not match:
        return ""
    return strip_tags(match.group(1))


def extract_meta_description(body: str) -> str:
    patterns = [
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        r'<meta\s+content=["\'](.*?)["\']\s+name=["\']description["\']',
        r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, body, re.I | re.S)
        if match:
            return html.unescape(match.group(1)).strip()
    return ""


def extract_title(body: str) -> str:
    return extract_first(r"<title[^>]*>(.*?)</title>", body)


def extract_h1(body: str) -> str:
    return extract_first(r"<h1[^>]*>(.*?)</h1>", body)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input CSV path with `url` column")
    parser.add_argument("--output", required=True, help="Output CSV path")
    parser.add_argument("--sleep-sec", type=float, default=0.2, help="Pause between requests")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    out_rows: list[dict[str, str]] = []

    for index, row in enumerate(rows, start=1):
        url = (row.get("url") or "").strip()
        if not url:
            continue

        print(f"[{index}/{len(rows)}] Fetching {url}")
        title = ""
        h1 = ""
        meta_description = ""
        fetch_error = ""

        try:
            body = fetch_html(url)
            title = extract_title(body)
            h1 = extract_h1(body)
            meta_description = extract_meta_description(body)
        except urllib.error.URLError as exc:
            fetch_error = str(exc)
            print(f"  ! Failed: {fetch_error}", file=sys.stderr)

        out_rows.append(
            {
                "url": url,
                "title": title,
                "h1": h1,
                "meta_description": meta_description,
                "fetch_error": fetch_error,
            }
        )
        time.sleep(args.sleep_sec)

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["url", "title", "h1", "meta_description", "fetch_error"],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote: {output_path}")
    print(f"Rows: {len(out_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
