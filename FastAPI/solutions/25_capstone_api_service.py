"""Capstone B — worked solution (service.py).

DESIGN DECISIONS
----------------
1. cache TTL: 60s. Unauthenticated GitHub allows 60 requests/hour, so a short
   TTL still collapses a burst of identical requests into one upstream call.
   Longer would risk stale star counts for no real gain at this traffic level.
2. status mapping: an upstream 404 is a genuine "does not exist" and stays a
   404. An upstream 5xx is not OUR failure, so it becomes 502, and a timeout
   becomes 504. Returning 500 would tell callers to page us for someone
   else's outage.
3. partial failure: /compare returns the users it got plus an explicit
   `failed` list. Failing the whole request because one name was a typo
   throws away work the caller asked for and can use.
4. concurrency cap: a Semaphore of 5. Unbounded fan-out over ten names would
   burn a sixth of the hourly quota in one request and looks like abuse.
5. response filtering: every endpoint declares a response_model, so upstream
   fields we never asked for (email, urls, internal ids) cannot leak just
   because GitHub added them.
"""

import asyncio
import os
import time

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

GITHUB = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10.0
CACHE_TTL_SECONDS = 60
MAX_CONCURRENCY = 5

app = FastAPI(
    title="GitHub Insights",
    description="A slimmed, cached, analysed view of the GitHub API.",
    version="1.0.0",
)

_CACHE: dict[str, tuple[float, object]] = {}

ERROR_MAP = {
    "not_found": (404, "not found: {context}"),
    "rate_limited": (429, "upstream rate limited"),
    "timeout": (504, "upstream timeout"),
    "unavailable": (503, "upstream unavailable"),
    "bad_response": (502, "upstream error"),
}


def reset_cache():
    _CACHE.clear()


class UpstreamError(Exception):
    def __init__(self, kind, context=""):
        super().__init__(f"{kind}: {context}")
        self.kind = kind
        self.context = context


@app.exception_handler(UpstreamError)
async def handle_upstream_error(request: Request, exc: UpstreamError):
    status, template = ERROR_MAP.get(exc.kind, (502, "upstream error"))
    return JSONResponse(
        status_code=status,
        content={"detail": template.format(context=exc.context), "kind": exc.kind},
    )


# ==========================================================================
# Models
# ==========================================================================


class UserOut(BaseModel):
    login: str
    name: str | None = None
    followers: int = 0
    public_repos: int = 0
    created_year: int | None = None
    profile_url: str | None = None


class RepoOut(BaseModel):
    name: str
    stars: int = 0
    forks: int = 0
    language: str | None = None
    archived: bool = False
    license: str | None = None
    pushed: str | None = None


class RepoPage(BaseModel):
    username: str
    total: int
    count: int
    limit: int
    offset: int
    items: list[RepoOut] = Field(default_factory=list)


class LanguageStat(BaseModel):
    language: str
    repos: int
    stars: int
    share: float


class UserReport(BaseModel):
    user: UserOut
    repo_count: int
    total_stars: int
    total_forks: int
    mean_stars: float | None = None
    median_stars: float | None = None
    skewed: bool = False
    archived: int = 0
    licensed: int = 0
    languages: list[LanguageStat] = Field(default_factory=list)
    top_repos: list[RepoOut] = Field(default_factory=list)


class ComparedUser(BaseModel):
    login: str
    followers: int = 0
    public_repos: int = 0
    rank: int


class CompareOut(BaseModel):
    requested: int
    found: int
    failed: list[dict] = Field(default_factory=list)
    users: list[ComparedUser] = Field(default_factory=list)
    total_followers: int = 0


# ==========================================================================
# Dependencies
# ==========================================================================


async def get_client():
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        yield client


def pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return {"limit": limit, "offset": offset}


# ==========================================================================
# Service layer
# ==========================================================================


async def fetch(client, path, params=None, context=""):
    try:
        response = await client.get(f"{GITHUB}{path}", params=params)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        if status == 404:
            raise UpstreamError("not_found", context) from exc
        if status == 429:
            raise UpstreamError("rate_limited", context) from exc
        raise UpstreamError("bad_response", context) from exc
    except httpx.TimeoutException as exc:
        raise UpstreamError("timeout", context) from exc
    except httpx.RequestError as exc:
        raise UpstreamError("unavailable", context) from exc


async def cached_fetch(client, key, path, params=None, context=""):
    cached = _CACHE.get(key)
    if cached is not None:
        fetched_at, payload = cached
        if time.time() - fetched_at < CACHE_TTL_SECONDS:
            return payload

    payload = await fetch(client, path, params=params, context=context)
    _CACHE[key] = (time.time(), payload)
    return payload


async def get_user(client, username):
    return await cached_fetch(
        client, f"user:{username}", f"/users/{username}", context=username
    )


async def get_repos(client, username):
    return await cached_fetch(
        client,
        f"repos:{username}",
        f"/users/{username}/repos",
        params={"per_page": 100},
        context=username,
    )


async def get_many_users(client, usernames, concurrency=MAX_CONCURRENCY):
    semaphore = asyncio.Semaphore(concurrency)

    async def one(name):
        async with semaphore:
            return await get_user(client, name)

    outcomes = await asyncio.gather(
        *(one(name) for name in usernames), return_exceptions=True
    )

    payloads = []
    errors = []
    for name, outcome in zip(usernames, outcomes):
        if isinstance(outcome, Exception):
            errors.append({"username": name, "error": type(outcome).__name__})
        else:
            payloads.append(outcome)
    return payloads, errors


# ==========================================================================
# Pure analysis
# ==========================================================================


def slim_user(payload):
    created = payload.get("created_at")
    return {
        "login": payload.get("login"),
        "name": payload.get("name"),
        "followers": payload.get("followers") or 0,
        "public_repos": payload.get("public_repos") or 0,
        "created_year": int(created[:4]) if created else None,
        "profile_url": payload.get("html_url"),
    }


def slim_repo(payload):
    return {
        "name": payload.get("name"),
        "stars": payload.get("stargazers_count") or 0,
        "forks": payload.get("forks_count") or 0,
        "language": payload.get("language"),
        "archived": bool(payload.get("archived")),
        "license": (payload.get("license") or {}).get("name"),
        "pushed": payload.get("pushed_at"),
    }


def language_breakdown(repos):
    totals: dict[str, dict] = {}
    for repo in repos:
        key = repo.get("language") or "unknown"
        entry = totals.setdefault(key, {"language": key, "repos": 0, "stars": 0})
        entry["repos"] += 1
        entry["stars"] += repo.get("stars") or 0

    all_stars = sum(entry["stars"] for entry in totals.values())
    for entry in totals.values():
        entry["share"] = round(entry["stars"] / all_stars * 100, 1) if all_stars else 0.0

    return sorted(totals.values(), key=lambda e: (-e["stars"], e["language"]))


def build_report(user_payload, repo_payloads, top_n=5):
    repos = [slim_repo(repo) for repo in repo_payloads]
    stars = sorted(repo["stars"] for repo in repos)

    mean = round(sum(stars) / len(stars), 2) if stars else None
    if stars:
        middle = len(stars) // 2
        median = (
            stars[middle]
            if len(stars) % 2
            else round((stars[middle - 1] + stars[middle]) / 2, 2)
        )
    else:
        median = None

    ranked = sorted(repos, key=lambda r: (-r["stars"], r["name"] or ""))

    return {
        "user": slim_user(user_payload),
        "repo_count": len(repos),
        "total_stars": sum(stars),
        "total_forks": sum(repo["forks"] for repo in repos),
        "mean_stars": mean,
        "median_stars": median,
        "skewed": bool(mean is not None and median and mean > median * 1.2),
        "archived": sum(1 for repo in repos if repo["archived"]),
        "licensed": sum(1 for repo in repos if repo["license"]),
        "languages": language_breakdown(repos),
        "top_repos": ranked[:top_n],
    }


# ==========================================================================
# Endpoints
# ==========================================================================


@app.get("/health")
def health():
    return {"status": "ok", "cached_keys": len(_CACHE)}


@app.get("/users/{username}", response_model=UserOut)
async def user_endpoint(
    username: str, client: httpx.AsyncClient = Depends(get_client)
):
    return slim_user(await get_user(client, username))


@app.get("/users/{username}/repos", response_model=RepoPage)
async def repos_endpoint(
    username: str,
    client: httpx.AsyncClient = Depends(get_client),
    page: dict = Depends(pagination),
    language: str | None = None,
    min_stars: int = Query(default=0, ge=0),
):
    repos = [slim_repo(repo) for repo in await get_repos(client, username)]

    if language is not None:
        wanted = language.lower()
        repos = [r for r in repos if (r["language"] or "").lower() == wanted]
    if min_stars:
        repos = [r for r in repos if r["stars"] >= min_stars]

    ranked = sorted(repos, key=lambda r: (-r["stars"], r["name"] or ""))
    window = ranked[page["offset"] : page["offset"] + page["limit"]]

    return {
        "username": username,
        "total": len(ranked),
        "count": len(window),
        "limit": page["limit"],
        "offset": page["offset"],
        "items": window,
    }


@app.get("/users/{username}/report", response_model=UserReport)
async def report_endpoint(
    username: str,
    client: httpx.AsyncClient = Depends(get_client),
    top: int = Query(default=5, ge=1, le=20),
):
    user_payload, repo_payloads = await asyncio.gather(
        get_user(client, username), get_repos(client, username)
    )
    return build_report(user_payload, repo_payloads, top_n=top)


@app.get("/compare", response_model=CompareOut)
async def compare_endpoint(
    users: str = Query(min_length=1),
    client: httpx.AsyncClient = Depends(get_client),
):
    names = [name.strip() for name in users.split(",") if name.strip()]
    if not 1 <= len(names) <= 10:
        raise HTTPException(
            status_code=400, detail="give between 1 and 10 comma-separated usernames"
        )

    payloads, errors = await get_many_users(client, names)
    slimmed = sorted(
        (slim_user(payload) for payload in payloads),
        key=lambda u: -u["followers"],
    )

    ranked = [
        {
            "login": user["login"],
            "followers": user["followers"],
            "public_repos": user["public_repos"],
            "rank": index,
        }
        for index, user in enumerate(slimmed, start=1)
    ]

    return {
        "requested": len(names),
        "found": len(ranked),
        "failed": errors,
        "users": ranked,
        "total_followers": sum(user["followers"] for user in ranked),
    }


@app.delete("/cache")
def clear_cache():
    cleared = len(_CACHE)
    _CACHE.clear()
    return {"cleared": cleared}
