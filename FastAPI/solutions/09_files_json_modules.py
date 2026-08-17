"""Unit 09 — worked solution."""

import csv
import json
from pathlib import Path

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def read_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def append_jsonl(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(read_jsonl(path))


def write_csv(path, rows, fieldnames=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        if fieldnames:
            writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def load_repos():
    return read_json(FIXTURES / "github_repos_pallets.json")


def repo_field_names(repos):
    names = set()
    for repo in repos:
        names.update(repo.keys())
    return sorted(names)


def slim_repos(repos):
    slim = []
    for repo in repos:
        license_info = repo.get("license") or {}
        slim.append(
            {
                "name": repo.get("name"),
                "owner": (repo.get("owner") or {}).get("login"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "license": license_info.get("name"),
            }
        )
    return slim


def language_report(repos):
    slim = slim_repos(repos)
    languages = {}
    for repo in slim:
        key = repo["language"] or "unknown"
        languages[key] = languages.get(key, 0) + 1
    ranked = sorted(slim, key=lambda r: (-r["stars"], r["name"]))
    return {
        "total_repos": len(slim),
        "languages": languages,
        "total_stars": sum(r["stars"] for r in slim),
        "top_repo": ranked[0]["name"] if ranked else None,
    }
