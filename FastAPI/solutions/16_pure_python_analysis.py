"""Unit 16 — worked solution."""

import json
import statistics as st
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def parse_timestamp(text):
    if isinstance(text, bool):
        return None
    if isinstance(text, (int, float)):
        try:
            return datetime.fromtimestamp(text, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None

    try:
        cleaned = text.strip().replace("Z", "+00:00")
        parsed = datetime.fromisoformat(cleaned)
    except (AttributeError, TypeError, ValueError):
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def count_by(records, field, missing="unknown"):
    counts = Counter()
    for record in records:
        value = record.get(field)
        counts[missing if value is None else value] += 1
    return counts


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
    mean = round(st.mean(ordered), 2)
    median = round(st.median(ordered), 2)
    index = min(int(0.9 * len(ordered)), len(ordered) - 1)

    return {
        "count": len(ordered),
        "min": ordered[0],
        "max": ordered[-1],
        "mean": mean,
        "median": median,
        "p90": round(ordered[index], 2),
        "skewed": bool(mean > median * 1.2),
    }


def group_stats(records, group_field, value_field, missing="unknown"):
    groups = defaultdict(list)
    for record in records:
        key = record.get(group_field)
        key = missing if key is None else key
        groups[key]  # touch, so empty groups still exist
        value = record.get(value_field)
        if value is not None:
            groups[key].append(value)
    return {key: numeric_summary(values) for key, values in groups.items()}


def top_n_by(records, field, n=5, label_field=None):
    def value_of(record):
        return record.get(field) or 0

    if label_field is None:
        ranked = sorted(records, key=lambda r: -value_of(r))
        return ranked[:n]

    ranked = sorted(records, key=lambda r: (-value_of(r), r.get(label_field) or ""))
    return [(r.get(label_field), value_of(r)) for r in ranked[:n]]


def bucket_by_month(records, date_field):
    counts = Counter()
    for record in records:
        parsed = parse_timestamp(record.get(date_field))
        if parsed is not None:
            counts[parsed.strftime("%Y-%m")] += 1
    return dict(sorted(counts.items()))


def join_records(left, right, left_key, right_key, fields, prefix=""):
    lookup = {record[right_key]: record for record in right if right_key in record}

    joined = []
    for record in left:
        merged = dict(record)
        match = lookup.get(record.get(left_key))
        if match:
            for name in fields:
                if name in match:
                    merged[f"{prefix}{name}"] = match[name]
        joined.append(merged)
    return joined


def analyze_hn(hits):
    authors = count_by(hits, "author")
    return {
        "count": len(hits),
        "points": numeric_summary([h.get("points") for h in hits]),
        "comments": numeric_summary([h.get("num_comments") for h in hits]),
        "top_stories": top_n_by(hits, "points", 5, label_field="title"),
        "by_author": authors.most_common(5),
        "by_month": bucket_by_month(hits, "created_at"),
        "distinct_authors": len({h.get("author") for h in hits if h.get("author")}),
    }


def format_table(rows, headers):
    text_rows = [[str(cell) for cell in headers]]
    text_rows.extend([str(cell) for cell in row] for row in rows)

    widths = [max(len(row[i]) for row in text_rows) for i in range(len(headers))]

    lines = []
    for row in text_rows:
        cells = []
        for index, cell in enumerate(row):
            width = widths[index]
            cells.append(f"{cell:<{width}}" if index == 0 else f"{cell:>{width}}")
        lines.append("  ".join(cells).rstrip())
    return "\n".join(lines)


if __name__ == "__main__":
    hits = load("hn_search_python")["hits"]
    report = analyze_hn(hits)

    print(f"{report['count']} stories, {report['distinct_authors']} distinct authors\n")

    print("points:", report["points"])
    print("skewed:", report["points"]["skewed"], "\n")

    print(format_table(report["top_stories"], ["title", "points"]))
    print()
    print(format_table(report["by_author"], ["author", "stories"]))
