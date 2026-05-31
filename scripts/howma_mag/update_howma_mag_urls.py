#!/usr/bin/env python3
"""Weekly HowMa /mag/ URL snapshot updater.

Creates a current URL snapshot by crawling public /mag/ listing pages, then
compares it with a previous snapshot CSV.
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


ROUTINE_BASE = "core/_routine_定常作業/howma_mag_sources"
SNAPSHOT_FOLDER_PREFIX = "抽出作業_"
LEGACY_FOLDER_PREFIX = "記事ソース_"
FALLBACK_PREVIOUS = (
    f"{ROUTINE_BASE}/{SNAPSHOT_FOLDER_PREFIX}250501/python_outputs/"
    "howma_mag_article_like_clean.csv"
)
FALLBACK_PREVIOUS_METADATA = (
    f"{ROUTINE_BASE}/{SNAPSHOT_FOLDER_PREFIX}250501/python_outputs/"
    "howma_mag_article_metadata.csv"
)
DEFAULT_SEEDS = [
    "https://www.how-ma.com/mag/",
    "https://www.how-ma.com/mag/category/sell/",
    "https://www.how-ma.com/mag/category/buy/",
    "https://www.how-ma.com/mag/category/interview/",
    "https://www.how-ma.com/mag/category/market/",
    "https://www.how-ma.com/mag/category/special/",
]


def yymmdd_today() -> str:
    return dt.datetime.now().strftime("%y%m%d")


def log_line(log_path: Path, message: str = "") -> None:
    encoding = sys.stdout.encoding or "utf-8"
    print(message.encode(encoding, errors="replace").decode(encoding, errors="replace"))
    with log_path.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def run(cmd: list[str], cwd: Path, log_path: Path) -> None:
    log_line(log_path, "Running: " + " ".join(cmd))
    process = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert process.stdout is not None
    for line in process.stdout:
        log_line(log_path, line.rstrip())
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def snapshot_csv_candidates(base: Path, suffix: str) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = []
    for prefix in (SNAPSHOT_FOLDER_PREFIX, LEGACY_FOLDER_PREFIX):
        for path in base.glob(f"{prefix}*/python_outputs/*{suffix}"):
            date = path.parent.parent.name.replace(prefix, "", 1)
            candidates.append((date, path))
    return candidates


def find_previous_snapshot(repo: Path, current_date: str) -> Path:
    bases = [
        repo / ROUTINE_BASE,
        repo / "core" / "writing" / "_assets",
    ]
    candidates: list[tuple[str, Path]] = []
    for base in bases:
        for date, path in snapshot_csv_candidates(base, "_article_like_clean.csv"):
            if date < current_date:
                candidates.append((date, path))
    if candidates:
        return sorted(candidates, key=lambda item: item[0])[-1][1]
    return repo / FALLBACK_PREVIOUS


def find_previous_metadata(repo: Path, current_date: str) -> Path:
    bases = [
        repo / ROUTINE_BASE,
        repo / "core" / "writing" / "_assets",
    ]
    candidates: list[tuple[str, Path]] = []
    for base in bases:
        for date, path in snapshot_csv_candidates(base, "_article_metadata.csv"):
            if date < current_date:
                candidates.append((date, path))
    if candidates:
        return sorted(candidates, key=lambda item: item[0])[-1][1]
    return repo / FALLBACK_PREVIOUS_METADATA


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=yymmdd_today(), help="Snapshot date as yymmdd")
    parser.add_argument(
        "--previous",
        default="",
        help="Previous URL CSV. Defaults to the latest older snapshot under core/writing/_assets",
    )
    parser.add_argument(
        "--previous-metadata",
        default="",
        help="Previous metadata CSV. Defaults to the latest older metadata snapshot",
    )
    parser.add_argument("--max-pages", type=int, default=2000, help="Max listing pages to crawl")
    parser.add_argument("--sleep-sec", type=float, default=0.2, help="Pause between page requests")
    parser.add_argument("--seed-url", action="append", default=[], help="Seed URL. Repeatable")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    script_dir = Path(__file__).resolve().parent
    outdir = repo / ROUTINE_BASE / f"{SNAPSHOT_FOLDER_PREFIX}{args.date}" / "python_outputs"
    outdir.mkdir(parents=True, exist_ok=True)
    output_prefix = f"howma_mag_{args.date}"
    log_path = outdir / f"{output_prefix}_run.log"
    log_path.write_text("", encoding="utf-8")
    previous_csv = Path(args.previous).resolve() if args.previous else find_previous_snapshot(repo, args.date)
    previous_metadata_csv = (
        Path(args.previous_metadata).resolve()
        if args.previous_metadata
        else find_previous_metadata(repo, args.date)
    )

    seeds = args.seed_url or DEFAULT_SEEDS
    log_line(log_path, f"Started: {dt.datetime.now().isoformat(timespec='seconds')}")
    log_line(log_path, f"Snapshot date: {args.date}")
    log_line(log_path, f"Previous URL CSV: {previous_csv}")
    log_line(log_path, f"Previous metadata CSV: {previous_metadata_csv}")
    log_line(log_path, f"Output directory: {outdir}")

    fetch_cmd = [
        sys.executable,
        str(script_dir / "fetch_sitemap_urls.py"),
        "--skip-sitemap",
        "--include-prefix",
        "https://www.how-ma.com/mag/",
        "--article-like-regex",
        r"^https://www\.how-ma\.com/mag/[^/]+/[^/]+/?$",
        "--exclude-regex",
        r"/wp-|/category/|/page/\d+/|/authors?/|/tag/|/feed/|/content_policy/?$",
        "--max-pages",
        str(args.max_pages),
        "--pause-sec",
        str(args.sleep_sec),
        "--output-prefix",
        output_prefix,
        "--outdir",
        str(outdir),
    ]
    for seed in seeds:
        fetch_cmd.extend(["--seed-url", seed])

    run(fetch_cmd, repo, log_path)

    current_csv = outdir / f"{output_prefix}_article_like_clean.csv"
    metadata_csv = outdir / f"{output_prefix}_article_metadata.csv"
    metadata_cmd = [
        sys.executable,
        str(script_dir / "fetch_page_metadata.py"),
        "--input",
        str(current_csv),
        "--output",
        str(metadata_csv),
        "--sleep-sec",
        str(args.sleep_sec),
    ]
    run(metadata_cmd, repo, log_path)

    diff_dir = outdir / "diff"
    run(
        [
            sys.executable,
            str(script_dir / "compare_url_csvs.py"),
            "--old",
            str(previous_csv),
            "--new",
            str(current_csv),
            "--outdir",
            str(diff_dir),
            "--prefix",
            f"howma_mag_{args.date}",
        ],
        repo,
        log_path,
    )
    run(
        [
            sys.executable,
            str(script_dir / "compare_article_metadata_csvs.py"),
            "--old",
            str(previous_metadata_csv),
            "--new",
            str(metadata_csv),
            "--outdir",
            str(diff_dir),
            "--prefix",
            f"howma_mag_{args.date}",
        ],
        repo,
        log_path,
    )
    report_path = outdir.parent / f"review_report_{args.date}.md"
    run(
        [
            sys.executable,
            str(script_dir / "generate_howma_review_report.py"),
            "--date",
            args.date,
            "--out",
            str(report_path),
        ],
        repo,
        log_path,
    )

    log_line(log_path)
    log_line(log_path, f"Previous URL CSV: {previous_csv}")
    log_line(log_path, f"Previous metadata CSV: {previous_metadata_csv}")
    log_line(log_path, f"Current URL CSV: {current_csv}")
    log_line(log_path, f"Current metadata CSV: {metadata_csv}")
    log_line(log_path, f"Diff directory: {diff_dir}")
    log_line(log_path, f"Review report: {report_path}")
    log_line(log_path, f"Run log: {log_path}")
    log_line(log_path, f"Finished: {dt.datetime.now().isoformat(timespec='seconds')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
