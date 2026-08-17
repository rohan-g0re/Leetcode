"""Unit 20 — worked solution."""

import json
import statistics as st
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"

app = FastAPI(
    title="Repo Explorer",
    description="A tiny read-only API over a snapshot of GitHub repositories.",
    version="1.0.0",
)


def load_repos():
    raw = json.loads(
        (FIXTURES / "github_repos_pallets.json").read_text(encoding="utf-8")
    )
    return [
        {
            "name": repo["name"],
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count") or 0,
            "forks": repo.get("forks_count") or 0,
            "open_issues": repo.get("open_issues_count") or 0,
            "archived": bool(repo.get("archived")),
            "license": (repo.get("license") or {}).get("name"),
        }
        for repo in raw
    ]


REPOS = load_repos()


def _ranked(repos):
    """Stars descending, then name ascending."""
    return sorted(repos, key=lambda r: (-r["stars"], r["name"]))


@app.get("/health")
def health():
    return {"status": "ok", "repos": len(REPOS)}


@app.get("/repos")
def list_repos(
    language: str | None = None,
    min_stars: int = Query(default=0, ge=0),
    archived: bool | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    matches = REPOS

    if language is not None:
        wanted = language.lower()
        matches = [
            r for r in matches if (r["language"] or "").lower() == wanted
        ]
    if min_stars:
        matches = [r for r in matches if r["stars"] >= min_stars]
    if archived is not None:
        matches = [r for r in matches if r["archived"] is archived]

    ranked = _ranked(matches)
    page = ranked[offset : offset + limit]

    return {
        "total": len(ranked),
        "count": len(page),
        "limit": limit,
        "offset": offset,
        "items": page,
    }


# Declared BEFORE /repos/{name} so "top" is not read as a repository name.
@app.get("/repos/top")
def top_repos(n: int = Query(default=3, ge=1, le=20)):
    return _ranked(REPOS)[:n]


@app.get("/repos/{name}")
def get_repo(name: str):
    wanted = name.lower()
    for repo in REPOS:
        if repo["name"].lower() == wanted:
            return repo
    raise HTTPException(status_code=404, detail=f"repo not found: {name}")


@app.get("/languages")
def languages():
    totals = {}
    for repo in REPOS:
        key = repo["language"] or "unknown"
        entry = totals.setdefault(key, {"language": key, "repos": 0, "total_stars": 0})
        entry["repos"] += 1
        entry["total_stars"] += repo["stars"]

    return sorted(
        totals.values(), key=lambda e: (-e["total_stars"], e["language"])
    )


@app.get("/stats")
def stats():
    stars = [repo["stars"] for repo in REPOS]
    return {
        "repos": len(REPOS),
        "total_stars": sum(stars),
        "mean_stars": round(st.mean(stars), 2) if stars else None,
        "median_stars": round(st.median(stars), 2) if stars else None,
        "archived": sum(1 for r in REPOS if r["archived"]),
        "licensed": sum(1 for r in REPOS if r["license"]),
        "languages": len({r["language"] for r in REPOS if r["language"]}),
    }


@app.get("/search")
def search(q: str = Query(min_length=2, max_length=50)):
    needle = q.lower()
    items = _ranked([r for r in REPOS if needle in r["name"].lower()])
    return {"q": q, "count": len(items), "items": items}
