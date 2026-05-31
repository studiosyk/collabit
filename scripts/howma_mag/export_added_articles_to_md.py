#!/usr/bin/env python3
"""Export only newly added HowMa /mag/ articles to Markdown."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROUTINE_BASE = "core/_routine_定常作業/howma_mag_sources"
WRITING_ASSETS_BASE = "core/writing/_assets"
SNAPSHOT_FOLDER_PREFIX = "抽出作業_"
URL_RE = re.compile(r"^https://www\.how-ma\.com/mag/([^/]+)/([^/]+)/?$")


def read_urls(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [
            (row.get("url") or "").strip()
            for row in csv.DictReader(f)
            if (row.get("url") or "").strip()
        ]


def read_metadata(path: Path) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {
            (row.get("url") or "").strip(): row
            for row in csv.DictReader(f)
            if (row.get("url") or "").strip()
        }


def category_slug(url: str) -> tuple[str, str]:
    match = URL_RE.match(url)
    if not match:
        return "", ""
    return match.group(1), match.group(2)


def write_added_metadata(path: Path, added_urls: list[str], metadata: dict[str, dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["url", "category", "slug", "title", "h1", "meta_description", "fetch_error"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for url in added_urls:
            source = metadata.get(url, {})
            category, slug = category_slug(url)
            writer.writerow(
                {
                    "url": url,
                    "category": category,
                    "slug": slug,
                    "title": source.get("title", ""),
                    "h1": source.get("h1", ""),
                    "meta_description": source.get("meta_description", ""),
                    "fetch_error": source.get("fetch_error", ""),
                }
            )


def copy_markdown_to_writing_assets(repo: Path, date: str, source_dir: Path, count: int) -> Path:
    asset_dir = repo / WRITING_ASSETS_BASE / f"記事ソース_{date}"
    target_dir = asset_dir / "md_added"
    target_dir.mkdir(parents=True, exist_ok=True)

    for md_path in source_dir.glob("*.md"):
        shutil.copy2(md_path, target_dir / md_path.name)

    readme = asset_dir / "README.md"
    readme.write_text(
        "\n".join(
            [
                f"# 記事ソース_{date}",
                "",
                "HowMaマガジン `/mag/` の週次チェックで追加検出された記事本文Markdownの執筆用コピー。",
                "",
                "## Source",
                "",
                f"- スナップショット日: {date}",
                f"- 種別: 前回差分で追加されたURLのみ",
                f"- 件数: {count}件",
                f"- 定常作業の原本: `core/_routine_定常作業/howma_mag_sources/{SNAPSHOT_FOLDER_PREFIX}{date}/`",
                "",
                "## Files",
                "",
                "- `md_added/`: 追加URLの記事本文Markdown",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return target_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Snapshot date as yymmdd")
    parser.add_argument("--sleep-sec", type=float, default=0.2, help="Pause between article requests")
    parser.add_argument("--added-csv", default="", help="Override added URL CSV")
    parser.add_argument("--metadata-csv", default="", help="Override current metadata CSV")
    parser.add_argument("--outdir", default="", help="Override Markdown output directory")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    script_dir = Path(__file__).resolve().parent
    snapshot_dir = repo / ROUTINE_BASE / f"{SNAPSHOT_FOLDER_PREFIX}{args.date}" / "python_outputs"
    prefix = f"howma_mag_{args.date}"

    added_csv = Path(args.added_csv).resolve() if args.added_csv else snapshot_dir / "diff" / f"{prefix}_added.csv"
    metadata_csv = Path(args.metadata_csv).resolve() if args.metadata_csv else snapshot_dir / f"{prefix}_article_metadata.csv"
    outdir = Path(args.outdir).resolve() if args.outdir else snapshot_dir / f"md_added_{args.date}"
    added_metadata_csv = snapshot_dir / f"{prefix}_added_article_metadata.csv"

    added_urls = read_urls(added_csv)
    metadata = read_metadata(metadata_csv)
    write_added_metadata(added_metadata_csv, added_urls, metadata)

    print(f"Added URLs: {len(added_urls)}")
    print(f"Added metadata CSV: {added_metadata_csv}")
    print(f"Markdown output directory: {outdir}")

    subprocess.run(
        [
            sys.executable,
            str(script_dir / "export_postcontents_to_md.py"),
            "--input",
            str(added_metadata_csv),
            "--outdir",
            str(outdir),
            "--sleep-sec",
            str(args.sleep_sec),
            "--log-file",
            str(outdir / "_export_added_postcontents.log"),
        ],
        cwd=str(repo),
        check=True,
    )
    copied_dir = copy_markdown_to_writing_assets(repo, args.date, outdir, len(added_urls))
    print(f"Copied markdown files to writing assets: {copied_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
