#!/usr/bin/env python3

from __future__ import annotations

import csv
import re
from pathlib import Path


BASE = Path(r"C:\Users\sayuka\github\collabit\archive\2604_面接課題\frog_data")
SRC = BASE / "howma_mag_article_like.csv"
CLEAN = BASE / "howma_mag_article_like_clean.csv"
REVIEW = BASE / "howma_mag_article_like_review_needed.csv"


def classify_review_reason(url: str) -> str:
    reasons: list[str] = []
    if re.search(r"/p\d+/?$", url):
        reasons.append("p_number_slug")
    if "ccompletion-" in url:
        reasons.append("possible_typo_slug")
    if re.search(r"%[0-9a-fA-F]{2}", url):
        reasons.append("url_encoded_slug")
    return "|".join(reasons)


def main() -> int:
    with SRC.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    clean_rows: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []

    for row in rows:
        url = row["url"]
        reason = classify_review_reason(url)
        if reason:
            review_rows.append({"url": url, "review_reason": reason})
        else:
            clean_rows.append({"url": url})

    with CLEAN.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url"])
        writer.writeheader()
        writer.writerows(clean_rows)

    with REVIEW.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "review_reason"])
        writer.writeheader()
        writer.writerows(review_rows)

    print(f"clean={len(clean_rows)}")
    print(f"review_needed={len(review_rows)}")
    print(f"wrote={CLEAN}")
    print(f"wrote={REVIEW}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
