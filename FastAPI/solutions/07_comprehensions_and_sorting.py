"""Unit 07 — worked solution."""

REPOS = [
    {"name": "flask", "language": "Python", "stars": 66000, "forks": 16000, "archived": False},
    {"name": "jinja", "language": "Python", "stars": 10000, "forks": 1600, "archived": False},
    {"name": "click", "language": "Python", "stars": 15000, "forks": 1400, "archived": False},
    {"name": "meta", "language": None, "stars": 100, "forks": 30, "archived": False},
    {"name": "flask-website", "language": "HTML", "stars": 200, "archived": True},
    {"name": "werkzeug", "language": "Python", "stars": 6500, "forks": 1700, "archived": False},
    {"name": "itsdangerous", "language": "Python", "stars": 2800, "forks": 220, "archived": True},
]


def names_of(records):
    return [r["name"] for r in records]


def active_python_repos(records):
    return [
        r["name"]
        for r in records
        if r.get("language") == "Python" and not r.get("archived")
    ]


def stars_by_name(records):
    return {r["name"]: r["stars"] for r in records}


def distinct_languages(records):
    return sorted({r["language"] for r in records if r.get("language") is not None})


def total_forks(records):
    return sum(r.get("forks", 0) for r in records)


def rank_by_stars(records, limit=None):
    ranked = sorted(records, key=lambda r: (-r.get("stars", 0), r["name"]))
    names = [r["name"] for r in ranked]
    if limit is None:
        return names
    return names[:limit]


def sort_with_missing_last(records, field):
    def key(record):
        value = record.get(field)
        return (value is None, value if value is not None else 0)

    return sorted(records, key=key)


def group_names_by_language(records):
    grouped = {}
    for record in records:
        grouped.setdefault(record.get("language"), []).append(record["name"])
    return grouped


def stars_summary(records):
    if not records:
        return {"count": 0, "total": 0, "mean": None, "max_name": None}
    total = sum(r.get("stars", 0) for r in records)
    ranked = sorted(records, key=lambda r: (-r.get("stars", 0), r["name"]))
    return {
        "count": len(records),
        "total": total,
        "mean": round(total / len(records), 2),
        "max_name": ranked[0]["name"],
    }


def label_sizes(records, threshold=5000):
    return [
        (r["name"], "big" if r.get("stars", 0) >= threshold else "small")
        for r in records
    ]
