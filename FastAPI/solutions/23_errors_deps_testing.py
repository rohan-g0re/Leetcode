"""Unit 23 — worked solution."""

import os
import time

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

GITHUB = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10.0
API_KEY_ENV = "GATEWAY_API_KEY"

app = FastAPI(title="GitHub Gateway v2", version="2.0.0")

ERROR_MAP = {
    "not_found": (404, "not found: {context}"),
    "rate_limited": (429, "upstream rate limited"),
    "timeout": (504, "upstream timeout"),
    "unavailable": (503, "upstream unavailable"),
    "bad_response": (502, "upstream returned an unusable response"),
}


class UpstreamError(Exception):
    def __init__(self, kind, context=""):
        super().__init__(f"{kind}: {context}")
        self.kind = kind
        self.context = context


async def get_client():
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        yield client


def pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return {"limit": limit, "offset": offset}


def require_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.environ.get(API_KEY_ENV)
    if not expected:
        return None
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid or missing api key")
    return x_api_key


@app.exception_handler(UpstreamError)
async def handle_upstream_error(request: Request, exc: UpstreamError):
    status, template = ERROR_MAP.get(exc.kind, (502, "upstream error"))
    return JSONResponse(
        status_code=status,
        content={"detail": template.format(context=exc.context), "kind": exc.kind},
    )


@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started:.4f}"
    return response


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


def slim_repo(repo):
    return {
        "name": repo.get("name"),
        "stars": repo.get("stargazers_count") or 0,
        "language": repo.get("language"),
        "archived": bool(repo.get("archived")),
    }


def _ranked(repos):
    return sorted(repos, key=lambda r: (-r["stars"], r["name"] or ""))


@app.get("/health")
def health():
    return {"status": "ok", "auth_required": bool(os.environ.get(API_KEY_ENV))}


@app.get("/users/{username}")
async def user_endpoint(
    username: str,
    client: httpx.AsyncClient = Depends(get_client),
    _key: str | None = Depends(require_api_key),
):
    payload = await fetch(client, f"/users/{username}", context=username)
    return {
        "login": payload.get("login"),
        "name": payload.get("name"),
        "followers": payload.get("followers") or 0,
        "public_repos": payload.get("public_repos") or 0,
    }


@app.get("/users/{username}/repos")
async def repos_endpoint(
    username: str,
    client: httpx.AsyncClient = Depends(get_client),
    page: dict = Depends(pagination),
    _key: str | None = Depends(require_api_key),
):
    raw = await fetch(
        client, f"/users/{username}/repos", params={"per_page": 100}, context=username
    )
    items = _ranked([slim_repo(repo) for repo in raw])
    window = items[page["offset"] : page["offset"] + page["limit"]]

    return {
        "username": username,
        "total": len(items),
        "count": len(window),
        "limit": page["limit"],
        "offset": page["offset"],
        "items": window,
    }


@app.get("/search/repos")
async def search_endpoint(
    q: str = Query(min_length=2, max_length=100),
    client: httpx.AsyncClient = Depends(get_client),
    page: dict = Depends(pagination),
    _key: str | None = Depends(require_api_key),
):
    payload = await fetch(
        client, "/search/repositories", params={"q": q, "per_page": 100}, context=q
    )
    items = _ranked([slim_repo(repo) for repo in payload.get("items") or []])
    window = items[page["offset"] : page["offset"] + page["limit"]]

    return {
        "q": q,
        "total": payload.get("total_count") or 0,
        "count": len(window),
        "limit": page["limit"],
        "offset": page["offset"],
        "items": window,
    }
