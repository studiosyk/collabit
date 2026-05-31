#!/usr/bin/env python3
"""Compare article metadata snapshots by URL, title, and H1."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = csv.DictReader(f)
        return {
            (row.get("url") or "").strip(): row
            for row in rows
            if (row.get("url") or "").strip()
        }


def normalize(value: str) -> str:
    return " ".join(value.split())


def write_rows(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, help="Previous metadata CSV")
    parser.add_argument("--new", required=True, help="Current metadata CSV")
    parser.add_argument("--outdir", required=True, help="Directory for comparison CSVs")
    parser.add_argument("--prefix", default="metadata_diff", help="Output file prefix")
    args = parser.parse_args()

    old_rows = read_rows(Path(args.old).resolve())
    new_rows = read_rows(Path(args.new).resolve())
    outdir = Path(args.outdir).resolve()

    changed: list[dict[str, str]] = []
    unchanged: list[dict[str, str]] = []
    comparable_urls = sorted(set(old_rows) & set(new_rows))

    for url in comparable_urls:
        old = old_rows[url]
        new = new_rows[url]
        old_title = normalize(old.get("title", ""))
        new_title = normalize(new.get("title", ""))
        old_h1 = normalize(old.get("h1", ""))
        new_h1 = normalize(new.get("h1", ""))
        title_changed = old_title != new_title
        h1_changed = old_h1 != new_h1

        row = {
            "url": url,
            "title_changed": "yes" if title_changed else "no",
            "h1_changed": "yes" if h1_changed else "no",
            "old_title": old_title,
            "new_title": new_title,
            "old_h1": old_h1,
            "new_h1": new_h1,
        }
        if title_changed or h1_changed:
            changed.append(row)
        else:
            unchanged.append(row)

    fields = [
        "url",
        "title_changed",
        "h1_changed",
        "old_title",
        "new_title",
        "old_h1",
        "new_h1",
    ]
    write_rows(outdir / f"{args.prefix}_changed.csv", fields, changed)
    write_rows(outdir / f"{args.prefix}_metadata_unchanged.csv", fields, unchanged)

    summary_path = outdir / f"{args.prefix}_metadata_summary.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "count"])
        writer.writerow(["old_metadata", len(old_rows)])
        writer.writerow(["new_metadata", len(new_rows)])
        writer.writerow(["comparable", len(comparable_urls)])
        writer.writerow(["changed", len(changed)])
        writer.writerow(["metadata_unchanged", len(unchanged)])

    print(f"Old metadata rows: {len(old_rows)}")
    print(f"New metadata rows: {len(new_rows)}")
    print(f"Comparable URLs: {len(comparable_urls)}")
    print(f"Changed title/H1: {len(changed)}")
    print(f"Metadata unchanged: {len(unchanged)}")
    print(f"Wrote: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
