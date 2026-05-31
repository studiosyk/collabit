#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


URL_RE = re.compile(r"^https://www\.how-ma\.com/mag/([^/]+)/([^/]+)/?$")


def extract_category_slug(url: str) -> tuple[str, str]:
    match = URL_RE.match(url.strip())
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input metadata CSV")
    parser.add_argument("--output", required=True, help="Output enriched CSV")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    out_rows: list[dict[str, str]] = []
    for row in rows:
        url = row.get("url", "")
        category, slug = extract_category_slug(url)
        out_rows.append(
            {
                "url": url,
                "category": category,
                "slug": slug,
                "title": row.get("title", ""),
                "h1": row.get("h1", ""),
                "meta_description": row.get("meta_description", ""),
                "fetch_error": row.get("fetch_error", ""),
            }
        )

    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "category",
                "slug",
                "title",
                "h1",
                "meta_description",
                "fetch_error",
            ],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote: {output_path}")
    print(f"Rows: {len(out_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
