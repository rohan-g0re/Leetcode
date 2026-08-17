"""Capstone A — worked solution (etl.py)."""

import argparse
import csv
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

HERE = Path(__file__).parent
CACHE_DIR = HERE / ".cache"

HN_SEARCH = "https://hn.algolia.com/api/v1/search"
HEADERS = {"Accept": "application/json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 15

CSV_COLUMNS = [
    "id",
    "title",
    "author",
    "points",
    "comments",
    "domain",
    "url",
    "created",
    "month",
]


# ==========================================================================
# EXTRACT
# ==========================================================================


def make_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def cache_path(params, cache_dir=CACHE_DIR):
    raw = json.dumps(params or {}, sort_keys=True)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return Path(cache_dir) / f"hn_{digest}.json"


def fetch_page(session, params, cache_dir=CACHE_DIR, sleeper=time.sleep, attempts=3):
    path = cache_path(params, cache_dir)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    for attempt in range(attempts):
        is_last = attempt == attempts - 1

        try:
            response = session.get(HN_SEARCH, params=params, timeout=TIMEOUT)
        except (requests.Timeout, requests.ConnectionError):
            if is_last:
                raise
            sleeper(2**attempt)
            continue

        if response.status_code == 429 or response.status_code >= 500:
            if is_last:
                response.raise_for_status()
            sleeper(2**attempt)
            continue

        response.raise_for_status()
        data = response.json()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data), encoding="utf-8")
        return data

    return None  # unreachable


def extract(
    session,
    query,
    pages=3,
    hits_per_page=100,
    tags="story",
    cache_dir=CACHE_DIR,
    sleeper=time.sleep,
):
    hits = []
    total_available = 0
    fetched = 0

    for page in range(pages):
        params = {
            "query": query,
            "tags": tags,
            "hitsPerPage": hits_per_page,
            "page": page,
        }
        data = fetch_page(session, params, cache_dir=cache_dir, sleeper=sleeper) or {}
        fetched += 1

        if page == 0:
            total_available = data.get("nbHits") or 0

        batch = data.get("hits") or []
        if not batch:
            break
        hits.extend(batch)

        if page >= (data.get("nbPages") or 0) - 1:
            break

    return hits, {
        "pages_fetched": fetched,
        "total_available": total_available,
        "query": query,
    }


# ==========================================================================
# TRANSFORM
# ==========================================================================


def parse_timestamp(text):
    if not isinstance(text, str) or not text.strip():
        return None
    try:
        parsed = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def domain_of(url):
    if not url or "://" not in str(url):
        return None
    host = urlparse(str(url)).netloc.lower()
    return host or None


def transform(hits):
    records = []
    dropped = 0

    for raw in hits:
        object_id = raw.get("objectID")
        created = parse_timestamp(raw.get("created_at"))
        if object_id is None or created is None:
            dropped += 1
            continue

        url = raw.get("url")
        records.append(
            {
                "id": str(object_id),
                "title": raw.get("title") or "",
                "author": raw.get("author"),
                "points": raw.get("points") or 0,
                "comments": raw.get("num_comments") or 0,
                "url": url,
                "domain": domain_of(url),
                "created": created.isoformat(),
                "month": created.strftime("%Y-%m"),
            }
        )

    return records, dropped


def filter_records(records, min_points=0, domain=None, since=None):
    out = records

    if min_points:
        out = [r for r in out if r["points"] >= min_points]
    if domain:
        wanted = domain.lower()
        out = [r for r in out if (r["domain"] or "").lower() == wanted]
    if since:
        out = [r for r in out if r["created"][:10] >= since]

    return out


# ==========================================================================
# ANALYZE
# ==========================================================================


def numeric_summary(values):
    usable = [v for v in values if v is not None]
    if not usable:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "p90": None,
            "skewed": False,
        }

    ordered = sorted(usable)
    count = len(ordered)
    mean = round(sum(ordered) / count, 2)
    middle = count // 2
    median = (
        ordered[middle]
        if count % 2
        else round((ordered[middle - 1] + ordered[middle]) / 2, 2)
    )
    p90 = ordered[min(int(0.9 * count), count - 1)]

    return {
        "count": count,
        "min": ordered[0],
        "max": ordered[-1],
        "mean": mean,
        "median": round(median, 2),
        "p90": round(p90, 2),
        "skewed": bool(mean > median * 1.2),
    }


def analyze(records, meta=None, top_n=10):
    meta = meta or {}

    domain_stories = Counter(r["domain"] for r in records if r["domain"])
    domain_points = {}
    for record in records:
        if record["domain"]:
            domain_points[record["domain"]] = (
                domain_points.get(record["domain"], 0) + record["points"]
            )

    authors = Counter(r["author"] for r in records if r["author"])
    months = Counter(r["month"] for r in records)
    dates = sorted(r["created"] for r in records)

    top_stories = sorted(records, key=lambda r: (-r["points"], r["title"]))[:top_n]

    return {
        "query": meta.get("query"),
        "pages_fetched": meta.get("pages_fetched", 0),
        "total_available": meta.get("total_available", 0),
        "records": len(records),
        "points": numeric_summary([r["points"] for r in records]),
        "comments": numeric_summary([r["comments"] for r in records]),
        "date_range": {
            "first": dates[0] if dates else None,
            "last": dates[-1] if dates else None,
        },
        "top_stories": [
            {"title": r["title"], "points": r["points"], "domain": r["domain"]}
            for r in top_stories
        ],
        "top_domains": [
            {
                "domain": domain,
                "stories": stories,
                "total_points": domain_points.get(domain, 0),
            }
            for domain, stories in sorted(
                domain_stories.items(), key=lambda kv: (-kv[1], kv[0])
            )[:top_n]
        ],
        "top_authors": [
            {"author": author, "stories": stories}
            for author, stories in sorted(
                authors.items(), key=lambda kv: (-kv[1], kv[0])
            )[:top_n]
        ],
        "by_month": dict(sorted(months.items())),
        "self_posts": sum(1 for r in records if not r["domain"]),
    }


# ==========================================================================
# LOAD
# ==========================================================================


def save_csv(records, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    return len(records)


def save_json(report, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def format_report(report):
    points = report["points"]
    lines = [
        f"query: {report['query']}",
        f"pages fetched: {report['pages_fetched']}   "
        f"matching upstream: {report['total_available']:,}",
        f"stories: {report['records']}",
        "",
        f"points   min {points['min']}   median {points['median']}   "
        f"mean {points['mean']}   p90 {points['p90']}   max {points['max']}",
    ]

    if points["skewed"]:
        lines.append("  (mean well above median: a few big stories dominate)")

    first = report["date_range"]["first"]
    last = report["date_range"]["last"]
    if first:
        lines.append(f"range: {first[:10]} .. {last[:10]}")

    lines.append("")
    lines.append("top domains")
    for entry in report["top_domains"][:10]:
        lines.append(
            f"  {entry['stories']:>4}  {entry['total_points']:>7,}  {entry['domain']}"
        )
    lines.append(f"  {report['self_posts']:>4}  {'':>7}  (self posts, no url)")

    lines.append("")
    lines.append("top stories")
    for entry in report["top_stories"][:10]:
        title = entry["title"]
        if len(title) > 70:
            title = title[:67] + "..."
        lines.append(f"  {entry['points']:>6,}  {title}")

    return "\n".join(lines)


# ==========================================================================
# CLI
# ==========================================================================


def build_parser():
    parser = argparse.ArgumentParser(description="Hacker News search ETL")
    parser.add_argument("query", help="search term")
    parser.add_argument("--pages", type=int, default=3, help="max pages to fetch")
    parser.add_argument("--min-points", type=int, default=0, dest="min_points")
    parser.add_argument("--domain", default=None, help="keep only this domain")
    parser.add_argument("--since", default=None, help="YYYY-MM-DD")
    parser.add_argument("--out", default="reports", help="output directory")
    parser.add_argument("--no-cache", action="store_true", dest="no_cache")
    return parser


def run(argv=None):
    args = build_parser().parse_args(argv)
    session = make_session()

    cache_dir = CACHE_DIR
    if args.no_cache:
        import tempfile

        cache_dir = Path(tempfile.mkdtemp())

    hits, meta = extract(session, args.query, pages=args.pages, cache_dir=cache_dir)
    records, dropped = transform(hits)
    kept = filter_records(
        records, min_points=args.min_points, domain=args.domain, since=args.since
    )

    report = analyze(kept, meta=meta)
    report["dropped_in_transform"] = dropped
    report["filtered_out"] = len(records) - len(kept)

    out_dir = Path(args.out)
    save_csv(kept, out_dir / "stories.csv")
    save_json(report, out_dir / "summary.json")

    print(format_report(report))
    print(
        f"\nfetched {len(hits)}, dropped {dropped}, "
        f"filtered out {report['filtered_out']}, kept {len(kept)}"
    )
    print(f"wrote {out_dir / 'stories.csv'} and {out_dir / 'summary.json'}")

    return report


if __name__ == "__main__":
    run()
