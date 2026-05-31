#!/usr/bin/env python3
"""Compare two URL CSV snapshots and write added/removed/unchanged CSVs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_urls(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = csv.DictReader(f)
        return {
            (row.get("url") or "").strip()
            for row in rows
            if (row.get("url") or "").strip()
        }


def write_urls(path: Path, urls: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url"])
        for url in urls:
            writer.writerow([url])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, help="Previous URL CSV with a url column")
    parser.add_argument("--new", required=True, help="Current URL CSV with a url column")
    parser.add_argument("--outdir", required=True, help="Directory for diff CSVs")
    parser.add_argument("--prefix", default="url_diff", help="Output file prefix")
    args = parser.parse_args()

    old_path = Path(args.old).resolve()
    new_path = Path(args.new).resolve()
    outdir = Path(args.outdir).resolve()

    old_urls = read_urls(old_path)
    new_urls = read_urls(new_path)

    added = sorted(new_urls - old_urls)
    removed = sorted(old_urls - new_urls)
    unchanged = sorted(old_urls & new_urls)

    write_urls(outdir / f"{args.prefix}_added.csv", added)
    write_urls(outdir / f"{args.prefix}_removed.csv", removed)
    write_urls(outdir / f"{args.prefix}_unchanged.csv", unchanged)

    summary_path = outdir / f"{args.prefix}_summary.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "count"])
        writer.writerow(["old", len(old_urls)])
        writer.writerow(["new", len(new_urls)])
        writer.writerow(["added", len(added)])
        writer.writerow(["removed", len(removed)])
        writer.writerow(["unchanged", len(unchanged)])

    print(f"Old URLs: {len(old_urls)}")
    print(f"New URLs: {len(new_urls)}")
    print(f"Added: {len(added)}")
    print(f"Removed: {len(removed)}")
    print(f"Unchanged: {len(unchanged)}")
    print(f"Wrote: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
