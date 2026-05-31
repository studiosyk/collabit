#!/usr/bin/env python3
"""Generate a human review report for a HowMa /mag/ weekly snapshot."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROUTINE_BASE = "core/_routine_定常作業/howma_mag_sources"
SNAPSHOT_FOLDER_PREFIX = "抽出作業_"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def count_from_summary(path: Path) -> dict[str, int]:
    values: dict[str, int] = {}
    for row in read_csv(path):
        metric = row.get("metric", "")
        try:
            values[metric] = int(row.get("count", "0"))
        except ValueError:
            values[metric] = 0
    return values


def table(headers: list[str], rows: list[list[str]], max_rows: int = 30) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows[:max_rows]:
        escaped = [cell.replace("\n", " ").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(escaped) + " |")
    if len(rows) > max_rows:
        overflow = [f"... and {len(rows) - max_rows} more"] + ["" for _ in headers[1:]]
        lines.append("| " + " | ".join(overflow) + " |")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Snapshot date as yymmdd")
    parser.add_argument("--out", default="", help="Output markdown path")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    snapshot_dir = repo / ROUTINE_BASE / f"{SNAPSHOT_FOLDER_PREFIX}{args.date}"
    output_dir = snapshot_dir / "python_outputs"
    diff_dir = output_dir / "diff"
    prefix = f"howma_mag_{args.date}"
    out_path = Path(args.out).resolve() if args.out else snapshot_dir / f"review_report_{args.date}.md"

    url_summary = count_from_summary(diff_dir / f"{prefix}_summary.csv")
    metadata_summary = count_from_summary(diff_dir / f"{prefix}_metadata_summary.csv")
    added = read_csv(diff_dir / f"{prefix}_added.csv")
    removed = read_csv(diff_dir / f"{prefix}_removed.csv")
    changed = read_csv(diff_dir / f"{prefix}_changed.csv")
    metadata_rows = {row.get("url", ""): row for row in read_csv(output_dir / f"{prefix}_article_metadata.csv")}

    added_rows = [
        [row.get("url", ""), metadata_rows.get(row.get("url", ""), {}).get("h1", "")]
        for row in added
    ]
    removed_rows = [[row.get("url", "")] for row in removed]
    changed_rows = [
        [
            row.get("url", ""),
            row.get("old_h1", ""),
            row.get("new_h1", ""),
            row.get("old_title", ""),
            row.get("new_title", ""),
        ]
        for row in changed
    ]

    lines = [
        f"# HowMa /mag/ 定期チェック レポート {args.date}",
        "",
        "## Summary",
        "",
        f"- 前回URL数: {url_summary.get('old', 0)}",
        f"- 現在URL数: {url_summary.get('new', 0)}",
        f"- 追加URL: {url_summary.get('added', 0)}",
        f"- 削除URL: {url_summary.get('removed', 0)}",
        f"- 継続URL: {url_summary.get('unchanged', 0)}",
        f"- title/H1変更: {metadata_summary.get('changed', 0)}",
        "- 追加URL MD化: 要確認",
        "- 判定: 要確認",
        "",
        "## Human Check",
        "",
        "- [ ] `added` を確認した",
        "- [ ] `removed` を確認した",
        "- [ ] `changed` を確認した",
        "- [ ] 追加URLをMarkdown化してよい",
        "",
        "## Added URLs",
        "",
        table(["URL", "H1"], added_rows) if added_rows else "追加URLはありません。",
        "",
        "## Removed URLs",
        "",
        table(["URL"], removed_rows) if removed_rows else "削除URLはありません。",
        "",
        "## Changed Title/H1",
        "",
        table(["URL", "Old H1", "New H1", "Old Title", "New Title"], changed_rows)
        if changed_rows
        else "title/H1変更はありません。",
        "",
        "## Output Files",
        "",
        f"- `python_outputs/{prefix}_article_like_clean.csv`",
        f"- `python_outputs/{prefix}_article_metadata.csv`",
        f"- `python_outputs/diff/{prefix}_added.csv`",
        f"- `python_outputs/diff/{prefix}_removed.csv`",
        f"- `python_outputs/diff/{prefix}_changed.csv`",
        f"- `python_outputs/diff/{prefix}_summary.csv`",
        f"- `python_outputs/diff/{prefix}_metadata_summary.csv`",
        f"- `python_outputs/{prefix}_run.log`",
        "",
        "## Next Step",
        "",
        "人間確認後、問題なければ以下を実行する。",
        "",
        "```powershell",
        f"python .\\scripts\\howma_mag\\export_added_articles_to_md.py --date {args.date} --sleep-sec 0",
        "```",
        "",
    ]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
