#!/usr/bin/env python3
"""
Export article body content from HowMa-like pages to one Markdown file per URL.

Input CSV is expected to have at least:
  - url
  - category
  - slug
  - title
  - h1
  - meta_description

The script fetches each URL, extracts `.dividerBottom .postContents` content,
does a light HTML-to-Markdown conversion, and writes one file per article:

    {category}__{slug}.md
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


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_postcontents(body: str) -> str:
    # Prefer the article body block inside dividerBottom.
    match = re.search(
        r'<div class="dividerBottom">.*?<div class="postContents">(.*?)</div>\s*<!--/postContents-->',
        body,
        flags=re.I | re.S,
    )
    if match:
        return match.group(1)

    # Fallback when comments are absent or structure shifts slightly.
    match = re.search(
        r'<div class="postContents">(.*?)</div>\s*(?:<!--|<aside class="profile"|<aside class="related")',
        body,
        flags=re.I | re.S,
    )
    if match:
        return match.group(1)

    return ""


def html_fragment_to_markdown(fragment: str) -> str:
    text = fragment

    # Remove scripts/styles.
    text = re.sub(r"<script\b[^>]*>.*?</script>", "", text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", "", text, flags=re.I | re.S)

    # Images: keep alt/src as markdown image.
    def repl_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        alt_match = re.search(r'alt=["\'](.*?)["\']', tag, flags=re.I | re.S)
        src_match = re.search(r'src=["\'](.*?)["\']', tag, flags=re.I | re.S)
        alt = html.unescape(alt_match.group(1)).strip() if alt_match else ""
        src = src_match.group(1).strip() if src_match else ""
        if not src:
            return ""
        return f"\n\n![{alt}]({src})\n\n"

    text = re.sub(r"<img\b[^>]*>", repl_img, text, flags=re.I | re.S)

    # Links.
    text = re.sub(
        r'<a\b[^>]*href=["\'](.*?)["\'][^>]*>(.*?)</a>',
        lambda m: f"[{clean_inline_html(m.group(2))}]({m.group(1).strip()})",
        text,
        flags=re.I | re.S,
    )

    # Headings.
    for level in range(6, 0, -1):
        text = re.sub(
            rf"<h{level}\b[^>]*>(.*?)</h{level}>",
            lambda m, lvl=level: "\n\n" + ("#" * lvl) + " " + clean_inline_html(m.group(1)) + "\n\n",
            text,
            flags=re.I | re.S,
        )

    # List items.
    text = re.sub(
        r"<li\b[^>]*>(.*?)</li>",
        lambda m: "\n- " + clean_inline_html(m.group(1)),
        text,
        flags=re.I | re.S,
    )
    text = re.sub(r"</?(ul|ol)\b[^>]*>", "\n", text, flags=re.I)

    # Blockquotes.
    text = re.sub(
        r"<blockquote\b[^>]*>(.*?)</blockquote>",
        lambda m: "\n\n> " + clean_inline_html(m.group(1)).replace("\n", "\n> ") + "\n\n",
        text,
        flags=re.I | re.S,
    )

    # Paragraph-like blocks.
    text = re.sub(r"</?(p|div|section|article)\b[^>]*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)

    # Strong/em.
    text = re.sub(r"<(strong|b)\b[^>]*>(.*?)</\1>", lambda m: f"**{clean_inline_html(m.group(2))}**", text, flags=re.I | re.S)
    text = re.sub(r"<(em|i)\b[^>]*>(.*?)</\1>", lambda m: f"*{clean_inline_html(m.group(2))}*", text, flags=re.I | re.S)

    # Strip remaining tags.
    text = re.sub(r"<[^>]+>", "", text)
    return clean_text(text)


def clean_inline_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return clean_text(text)


def safe_name(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", value)
    value = re.sub(r"\s+", "_", value)
    return value[:180].strip("_")


def build_front_matter(row: dict[str, str]) -> str:
    fields = [
        ("url", row.get("url", "")),
        ("category", row.get("category", "")),
        ("slug", row.get("slug", "")),
        ("title", row.get("title", "")),
        ("h1", row.get("h1", "")),
        ("meta_description", row.get("meta_description", "")),
    ]
    lines = ["---"]
    for key, value in fields:
        value = value.replace("\r", " ").replace("\n", " ").strip()
        value = value.replace('"', '\\"')
        lines.append(f'{key}: "{value}"')
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input enriched metadata CSV")
    parser.add_argument("--outdir", required=True, help="Output directory for markdown files")
    parser.add_argument("--sleep-sec", type=float, default=0.2, help="Pause between requests")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    errors: list[tuple[str, str]] = []

    for index, row in enumerate(rows, start=1):
        url = (row.get("url") or "").strip()
        category = safe_name(row.get("category", "uncategorized") or "uncategorized")
        slug = safe_name(row.get("slug", f"item_{index}") or f"item_{index}")
        out_path = outdir / f"{category}__{slug}.md"

        print(f"[{index}/{len(rows)}] {out_path.name}")

        try:
            body = fetch_html(url)
            fragment = extract_postcontents(body)
            if not fragment:
                raise ValueError("postContents not found")
            markdown = html_fragment_to_markdown(fragment)
            content = build_front_matter(row) + "\n\n" + markdown + "\n"
            out_path.write_text(content, encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            errors.append((url, str(exc)))
            print(f"  ! Failed: {exc}", file=sys.stderr)

        time.sleep(args.sleep_sec)

    if errors:
        error_path = outdir / "_export_errors.csv"
        with error_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "error"])
            writer.writerows(errors)
        print(f"Wrote errors: {error_path}")

    print(f"Wrote markdown files to: {outdir}")
    print(f"Errors: {len(errors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
