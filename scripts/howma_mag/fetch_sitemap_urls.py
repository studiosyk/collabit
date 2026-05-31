#!/usr/bin/env python3
"""
Fetch and flatten sitemap URLs, then export filtered URLs to CSV.

Examples:
    python fetch_sitemap_urls.py ^
      --root https://www.how-ma.com/sitemap.xml.gz ^
      --include-prefix https://www.how-ma.com/mag/ ^
      --article-like-regex "^https://www\\.how-ma\\.com/mag/[^/]+/[^/]+/?$" ^
      --exclude-regex "/wp-|/category/|/page/\\d+/|/authors?/|/tag/|/feed/|/content_policy/?$" ^
      --output-prefix howma_mag

    python fetch_sitemap_urls.py ^
      --skip-sitemap ^
      --include-prefix https://www.how-ma.com/mag/ ^
      --article-like-regex "^https://www\\.how-ma\\.com/mag/[^/]+/[^/]+/?$" ^
      --exclude-regex "/wp-|/category/|/page/\\d+/|/authors?/|/tag/|/feed/|/content_policy/?$" ^
      --seed-url https://www.how-ma.com/mag/ ^
      --max-pages 2000 ^
      --output-prefix howma_mag_current
"""

from __future__ import annotations

import argparse
import csv
import gzip
import html
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
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
        return response.read()


def parse_xml_bytes(url: str, raw: bytes) -> ET.Element:
    if url.endswith(".gz"):
        raw = gzip.decompress(raw)
    return ET.fromstring(raw)


def child_texts(root: ET.Element, path: str) -> list[str]:
    values: list[str] = []
    for node in root.findall(path, NS):
        if node.text:
            values.append(node.text.strip())
    return values


def crawl_sitemaps(root_url: str, pause_sec: float = 0.2) -> list[str]:
    seen_sitemaps: set[str] = set()
    queue: deque[str] = deque([root_url])
    all_urls: set[str] = set()

    while queue:
        sitemap_url = queue.popleft()
        if sitemap_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sitemap_url)
        print(f"Fetching sitemap: {sitemap_url}")

        try:
            raw = fetch_bytes(sitemap_url)
            root = parse_xml_bytes(sitemap_url, raw)
        except (urllib.error.URLError, gzip.BadGzipFile, ET.ParseError, OSError) as exc:
            print(f"  ! Failed: {exc}", file=sys.stderr)
            continue

        nested = child_texts(root, ".//sm:sitemap/sm:loc")
        urls = child_texts(root, ".//sm:url/sm:loc")

        for child in nested:
            if child not in seen_sitemaps:
                queue.append(child)

        for url in urls:
            all_urls.add(url)

        time.sleep(pause_sec)

    return sorted(all_urls)


def write_csv(path: Path, urls: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["url"])
        for url in urls:
            writer.writerow([url])


def classify_review_reason(url: str) -> str:
    reasons: list[str] = []
    if re.search(r"/p\d+/?$", url):
        reasons.append("p_number_slug")
    if "ccompletion-" in url:
        reasons.append("possible_typo_slug")
    if re.search(r"%[0-9a-fA-F]{2}", url):
        reasons.append("url_encoded_slug")
    return "|".join(reasons)


def write_review_csv(path: Path, rows: list[tuple[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "review_reason"])
        for url, reason in rows:
            writer.writerow([url, reason])


def fetch_text(url: str, timeout: int = 30) -> str:
    raw = fetch_bytes(url, timeout=timeout)
    return raw.decode("utf-8", errors="ignore")


def extract_links(page_url: str, body: str) -> list[str]:
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', body, flags=re.IGNORECASE)
    links: list[str] = []
    for href in hrefs:
        href = html.unescape(href.strip())
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            parts = urllib.parse.urlsplit(page_url)
            href = f"{parts.scheme}://{parts.netloc}{href}"
        elif not href.startswith("http://") and not href.startswith("https://"):
            continue
        href = urllib.parse.urldefrag(href)[0]
        links.append(href)
    return links


def scrape_from_seed_pages(
    seed_urls: list[str],
    include_prefix: str,
    article_like_pattern: re.Pattern[str] | None,
    exclude_pattern: re.Pattern[str] | None,
    pause_sec: float = 0.2,
    max_pages: int = 500,
) -> tuple[list[str], list[str]]:
    seen_pages: set[str] = set()
    queue: deque[str] = deque(seed_urls)
    filtered_urls: set[str] = set()
    article_like_urls: set[str] = set()

    while queue and len(seen_pages) < max_pages:
        page_url = queue.popleft()
        if page_url in seen_pages:
            continue
        seen_pages.add(page_url)
        print(f"Fetching page: {page_url}")

        try:
            body = fetch_text(page_url)
        except urllib.error.URLError as exc:
            print(f"  ! Failed: {exc}", file=sys.stderr)
            continue

        for link in extract_links(page_url, body):
            if include_prefix and not link.startswith(include_prefix):
                continue
            if exclude_pattern and exclude_pattern.search(link):
                continue
            filtered_urls.add(link)
            if article_like_pattern and article_like_pattern.match(link):
                article_like_urls.add(link)
            if link.startswith(include_prefix) and link not in seen_pages:
                is_listing_like = (
                    link.rstrip("/") == include_prefix.rstrip("/")
                    or "/category/" in link
                    or re.search(r"/page/\d+/?$", link)
                    or "/authors/" in link
                )
                if is_listing_like:
                    queue.append(link)

        # Also follow explicit pagination-style links even if they were excluded
        # from the final output set; this helps us traverse deeper archive pages.
        for link in extract_links(page_url, body):
            if not include_prefix or not link.startswith(include_prefix):
                continue
            if link in seen_pages:
                continue
            if (
                "/category/" in link
                or re.search(r"/page/\d+/?$", link)
                or link.rstrip("/") == include_prefix.rstrip("/")
            ):
                queue.append(link)

        time.sleep(pause_sec)

    return sorted(filtered_urls), sorted(article_like_urls)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="", help="Root sitemap URL")
    parser.add_argument(
        "--skip-sitemap",
        action="store_true",
        help="Skip sitemap crawling and use seed-page scraping only",
    )
    parser.add_argument("--include-prefix", default="", help="Keep only URLs starting with this prefix")
    parser.add_argument("--article-like-regex", default="", help="Regex for a narrower article-like subset")
    parser.add_argument("--exclude-regex", default="", help="Regex for URLs to exclude")
    parser.add_argument("--output-prefix", default="sitemap_urls", help="Prefix for output filenames")
    parser.add_argument("--outdir", default=".", help="Output directory")
    parser.add_argument("--pause-sec", type=float, default=0.2, help="Pause between requests")
    parser.add_argument(
        "--seed-url",
        action="append",
        default=[],
        help="Fallback listing page URL to scrape when sitemap is unavailable. Repeatable.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
        help="Max listing pages to scrape in fallback mode",
    )
    args = parser.parse_args()

    include_prefix = args.include_prefix.strip()
    article_like_pattern = re.compile(args.article_like_regex) if args.article_like_regex else None
    exclude_pattern = re.compile(args.exclude_regex) if args.exclude_regex else None
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    all_urls: list[str] = []
    if not args.skip_sitemap:
        if not args.root:
            parser.error("--root is required unless --skip-sitemap is set")
        all_urls = crawl_sitemaps(args.root, pause_sec=args.pause_sec)

    filtered_urls = all_urls
    if include_prefix:
        filtered_urls = [url for url in filtered_urls if url.startswith(include_prefix)]
    if exclude_pattern:
        filtered_urls = [url for url in filtered_urls if not exclude_pattern.search(url)]

    article_like_urls = filtered_urls
    if article_like_pattern:
        article_like_urls = [url for url in filtered_urls if article_like_pattern.match(url)]

    if (args.skip_sitemap or not filtered_urls) and args.seed_url:
        if args.skip_sitemap:
            print("Skipping sitemap. Scraping from seed pages...")
        else:
            print("No URLs from sitemap. Falling back to listing-page scraping...")
        filtered_urls, article_like_urls = scrape_from_seed_pages(
            seed_urls=args.seed_url,
            include_prefix=include_prefix,
            article_like_pattern=article_like_pattern,
            exclude_pattern=exclude_pattern,
            pause_sec=args.pause_sec,
            max_pages=args.max_pages,
        )

    clean_article_urls: list[str] = []
    review_rows: list[tuple[str, str]] = []
    for url in article_like_urls:
        reason = classify_review_reason(url)
        if reason:
            review_rows.append((url, reason))
        else:
            clean_article_urls.append(url)

    all_csv = outdir / f"{args.output_prefix}_all.csv"
    filtered_csv = outdir / f"{args.output_prefix}_filtered.csv"
    article_csv = outdir / f"{args.output_prefix}_article_like.csv"
    clean_article_csv = outdir / f"{args.output_prefix}_article_like_clean.csv"
    review_csv = outdir / f"{args.output_prefix}_article_like_review_needed.csv"
    write_csv(all_csv, all_urls)
    write_csv(filtered_csv, filtered_urls)
    write_csv(article_csv, article_like_urls)
    write_csv(clean_article_csv, clean_article_urls)
    write_review_csv(review_csv, review_rows)

    print()
    print(f"All sitemap URLs: {len(all_urls)}")
    print(f"Filtered URLs: {len(filtered_urls)}")
    print(f"Article-like URLs: {len(article_like_urls)}")
    print(f"Clean article-like URLs: {len(clean_article_urls)}")
    print(f"Review-needed article-like URLs: {len(review_rows)}")
    print(f"Wrote: {all_csv}")
    print(f"Wrote: {filtered_csv}")
    print(f"Wrote: {article_csv}")
    print(f"Wrote: {clean_article_csv}")
    print(f"Wrote: {review_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
