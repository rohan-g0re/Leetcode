"""Unit 14 — worked solution."""

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

import requests

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"
TIMEOUT = 15
HEADERS = {"Accept": "application/json", "User-Agent": "python-api-course/1.0"}


def _is_record_list(value):
    return isinstance(value, list) and bool(value) and isinstance(value[0], dict)


def find_records(data):
    if isinstance(data, list):
        inner = [value for value in data if _is_record_list(value)]
        if inner:
            return max(inner, key=len)
        return data if _is_record_list(data) else []

    if isinstance(data, dict):
        candidates = [value for value in data.values() if _is_record_list(value)]
        if candidates:
            return max(candidates, key=len)

    return []


def profile_fields(records):
    profile = {}
    for record in records:
        for key, value in record.items():
            info = profile.setdefault(key, {"present": 0, "null": 0, "types": set()})
            info["present"] += 1
            if value is None:
                info["null"] += 1
            else:
                info["types"].add(type(value).__name__)
    return {
        key: {"present": info["present"], "null": info["null"], "types": sorted(info["types"])}
        for key, info in profile.items()
    }


def inconsistent_fields(records):
    total = len(records)
    profile = profile_fields(records)
    return sorted(key for key, info in profile.items() if info["present"] < total)


def walk_paths(data, prefix=""):
    if isinstance(data, dict) and data:
        out = []
        for key, value in data.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            out.extend(walk_paths(value, child))
        return out

    if isinstance(data, list) and data:
        out = []
        for index, value in enumerate(data):
            out.extend(walk_paths(value, f"{prefix}[{index}]"))
        return out

    return [(prefix, data)]


def search_paths(data, needle):
    lowered = needle.lower()
    return [(path, value) for path, value in walk_paths(data) if lowered in path.lower()]


def load_fixture_file(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def _clean(value):
    """Strip a string and turn "" into None. Non-strings pass through."""
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    return stripped or None


def _as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def flatten_worldbank_countries(payload):
    rows = []
    for record in find_records(payload):
        rows.append(
            {
                "code": _clean(record.get("id")),
                "name": _clean(record.get("name")),
                "region": _clean((record.get("region") or {}).get("value")),
                "income_level": _clean((record.get("incomeLevel") or {}).get("value")),
                "capital": _clean(record.get("capitalCity")),
                "latitude": _as_float(_clean(record.get("latitude"))),
                "longitude": _as_float(_clean(record.get("longitude"))),
            }
        )
    return rows


def summarize_by_region(countries):
    counts = Counter(c["region"] for c in countries if c.get("region"))
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def flatten_hn_hits(payload):
    rows = []
    for hit in find_records(payload):
        url = hit.get("url")
        created = hit.get("created_at")
        rows.append(
            {
                "id": str(hit.get("objectID")),
                "title": hit.get("title") or "",
                "author": hit.get("author"),
                "points": hit.get("points") or 0,
                "comments": hit.get("num_comments") or 0,
                "domain": urlparse(url).netloc.lower() or None if url else None,
                "date": created[:10] if created else None,
            }
        )
    return rows


def pokemon_profile(payload):
    types = sorted(payload.get("types") or [], key=lambda t: t.get("slot", 0))
    abilities = sorted(payload.get("abilities") or [], key=lambda a: a.get("slot", 0))

    stats = {}
    for entry in payload.get("stats") or []:
        name = (entry.get("stat") or {}).get("name")
        if name is not None:
            stats[name] = entry.get("base_stat") or 0

    return {
        "name": payload.get("name"),
        "id": payload.get("id"),
        "height": payload.get("height"),
        "weight": payload.get("weight"),
        "types": [(t.get("type") or {}).get("name") for t in types],
        "abilities": [(a.get("ability") or {}).get("name") for a in abilities],
        "stats": stats,
        "total_stats": sum(stats.values()),
    }


if __name__ == "__main__":
    payload = load_fixture_file("worldbank_countries")
    records = find_records(payload)
    print(f"{len(records)} records found\n")

    for field, info in profile_fields(records).items():
        print(f"{field:>14}  present={info['present']:>4}  types={info['types']}")

    print("\ninconsistent:", inconsistent_fields(records))

    countries = flatten_worldbank_countries(payload)
    print("\ntop regions:")
    for region, count in summarize_by_region(countries)[:5]:
        print(f"  {count:>4}  {region}")
