"""Unit 22 — worked solution."""

import asyncio
import time

import httpx
from fastapi import FastAPI, HTTPException, Query

GITHUB = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10.0
CACHE_TTL_SECONDS = 60

app = FastAPI(title="GitHub Gateway", version="1.0.0")

_CACHE: dict[str, tuple[float, dict]] = {}


def reset_cache():
    _CACHE.clear()


def get_client():
    return httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS)


async def fetch_json(client, url, params=None):
    response = await client.get(url, params=params)
    response.raise_for_status()
    return response.json()


def upstream_error(exc, context=""):
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 404:
            return HTTPException(status_code=404, detail=f"not found: {context}")
        if status == 429:
            return HTTPException(status_code=429, detail="upstream rate limited")
        return HTTPException(status_code=502, detail=f"upstream error: {status}")

    if isinstance(exc, httpx.TimeoutException):
        return HTTPException(status_code=504, detail="upstream timeout")

    return HTTPException(status_code=502, detail="upstream unreachable")


async def get_user(client, username):
    cached = _CACHE.get(username)
    if cached is not None:
        fetched_at, payload = cached
        if time.time() - fetched_at < CACHE_TTL_SECONDS:
            return payload

    payload = await fetch_json(client, f"{GITHUB}/users/{username}")
    _CACHE[username] = (time.time(), payload)
    return payload


def summarize_user(user):
    created = user.get("created_at")
    return {
        "login": user.get("login"),
        "name": user.get("name"),
        "followers": user.get("followers") or 0,
        "public_repos": user.get("public_repos") or 0,
        "created_year": int(created[:4]) if created else None,
    }


async def get_many_users(client, usernames, concurrency=5):
    semaphore = asyncio.Semaphore(concurrency)

    async def one(name):
        async with semaphore:
            return await get_user(client, name)

    outcomes = await asyncio.gather(
        *(one(name) for name in usernames), return_exceptions=True
    )

    results = []
    errors = []
    for name, outcome in zip(usernames, outcomes):
        if isinstance(outcome, Exception):
            errors.append({"username": name, "error": type(outcome).__name__})
        else:
            results.append(summarize_user(outcome))
    return results, errors


@app.get("/health")
def health():
    return {"status": "ok", "cached_users": len(_CACHE)}


@app.get("/users/{username}")
async def user_endpoint(username: str):
    client = get_client()
    try:
        payload = await get_user(client, username)
    except httpx.HTTPError as exc:
        raise upstream_error(exc, context=username)
    finally:
        await client.aclose()
    return summarize_user(payload)


@app.get("/users/{username}/repos")
async def repos_endpoint(
    username: str,
    limit: int = Query(default=5, ge=1, le=100),
    sort: str = Query(default="stars", pattern="^(stars|name)$"),
):
    client = get_client()
    try:
        raw = await fetch_json(
            client, f"{GITHUB}/users/{username}/repos", params={"per_page": 100}
        )
    except httpx.HTTPError as exc:
        raise upstream_error(exc, context=username)
    finally:
        await client.aclose()

    items = [
        {
            "name": repo.get("name"),
            "stars": repo.get("stargazers_count") or 0,
            "language": repo.get("language"),
            "archived": bool(repo.get("archived")),
        }
        for repo in raw
    ]

    if sort == "name":
        items.sort(key=lambda r: r["name"] or "")
    else:
        items.sort(key=lambda r: (-r["stars"], r["name"] or ""))

    items = items[:limit]
    return {"username": username, "count": len(items), "items": items}


@app.get("/compare")
async def compare_endpoint(users: str = Query(min_length=1)):
    names = [name.strip() for name in users.split(",") if name.strip()]
    if not 1 <= len(names) <= 10:
        raise HTTPException(
            status_code=400, detail="give between 1 and 10 comma-separated usernames"
        )

    client = get_client()
    try:
        results, errors = await get_many_users(client, names)
    finally:
        await client.aclose()

    results.sort(key=lambda u: -u["followers"])
    return {
        "requested": len(names),
        "found": len(results),
        "failed": errors,
        "users": results,
        "total_followers": sum(u["followers"] for u in results),
    }


@app.delete("/cache")
def clear_cache():
    cleared = len(_CACHE)
    _CACHE.clear()
    return {"cleared": cleared}
