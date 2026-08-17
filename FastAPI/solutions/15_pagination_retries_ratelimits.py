"""Unit 15 — worked solution."""

import hashlib
import json
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
CACHE_DIR = HERE / ".cache"
TIMEOUT = 15
USER_AGENT = "python-api-course/1.0"

HN_SEARCH = "https://hn.algolia.com/api/v1/search"
GITHUB = "https://api.github.com"


def make_session(token=None):
    session = requests.Session()
    session.headers.update({"Accept": "application/json", "User-Agent": USER_AGENT})
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    return session


def retry_delay(response, attempt, base=2):
    if response is not None:
        raw = response.headers.get("Retry-After")
        if raw is not None:
            try:
                return int(raw)
            except (TypeError, ValueError):
                pass
    return base**attempt


def fetch_with_retry(session, url, params=None, attempts=3, sleeper=time.sleep):
    for attempt in range(attempts):
        is_last = attempt == attempts - 1

        try:
            response = session.get(url, params=params, timeout=TIMEOUT)
        except (requests.Timeout, requests.ConnectionError):
            if is_last:
                raise
            sleeper(retry_delay(None, attempt))
            continue

        if response.status_code == 429 or response.status_code >= 500:
            if is_last:
                response.raise_for_status()
            sleeper(retry_delay(response, attempt))
            continue

        response.raise_for_status()
        return response.json()

    return None  # unreachable: the loop either returns or raises


def _as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def rate_limit_status(response):
    lower = {key.lower(): value for key, value in response.headers.items()}
    return {
        "limit": _as_int(lower.get("x-ratelimit-limit")),
        "remaining": _as_int(lower.get("x-ratelimit-remaining")),
        "reset": _as_int(lower.get("x-ratelimit-reset")),
    }


def should_stop_for_rate_limit(response, floor=5):
    remaining = rate_limit_status(response)["remaining"]
    return remaining is not None and remaining <= floor


def paginate_offset(
    session,
    url,
    params=None,
    per_page=100,
    max_pages=5,
    page_param="page",
    sleeper=time.sleep,
):
    records = []
    for page in range(1, max_pages + 1):
        merged = dict(params or {})
        merged.update({page_param: page, "per_page": per_page})

        response = session.get(url, params=merged, timeout=TIMEOUT)
        response.raise_for_status()
        batch = response.json() or []
        records.extend(batch)

        if len(batch) < per_page:
            break
        if should_stop_for_rate_limit(response):
            break
    return records


def paginate_hn(session, query, tags="story", hits_per_page=50, max_pages=3):
    hits = []
    for page in range(max_pages):
        data = fetch_with_retry(
            session,
            HN_SEARCH,
            params={
                "query": query,
                "tags": tags,
                "hitsPerPage": hits_per_page,
                "page": page,
            },
        )
        batch = (data or {}).get("hits") or []
        if not batch:
            break
        hits.extend(batch)
        if page >= (data.get("nbPages") or 0) - 1:
            break
    return hits


def paginate_link_header(session, url, params=None, max_pages=5):
    records = []
    next_url = url
    next_params = params

    for _ in range(max_pages):
        response = session.get(next_url, params=next_params, timeout=TIMEOUT)
        response.raise_for_status()
        records.extend(response.json() or [])

        link = response.links.get("next")
        if not link:
            break
        next_url = link["url"]
        next_params = None

    return records


def cache_key(url, params=None):
    raw = url + json.dumps(params or {}, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def cached_fetch(session, url, params=None, cache_dir=CACHE_DIR, **kwargs):
    path = Path(cache_dir) / f"{cache_key(url, params)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    data = fetch_with_retry(session, url, params=params, **kwargs)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


if __name__ == "__main__":
    session = make_session()

    hits = paginate_hn(session, "fastapi", max_pages=2)
    print(f"hacker news: {len(hits)} hits")
    for hit in hits[:5]:
        print(f"  {hit.get('points'):>5}  {hit.get('title')}")

    repos = paginate_link_header(
        session, f"{GITHUB}/users/pallets/repos", params={"per_page": 5}, max_pages=2
    )
    print(f"\ngithub: {len(repos)} repos over 2 pages")

    response = session.get(f"{GITHUB}/rate_limit", timeout=TIMEOUT)
    print("\nrate limit:", rate_limit_status(response))
