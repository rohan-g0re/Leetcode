"""Unit 12 — worked solution."""

import json
import sys

import requests

BASE = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10


def fetch_json(url, params=None, timeout=TIMEOUT):
    response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.json()


def safe_fetch(url, params=None):
    try:
        return fetch_json(url, params=params), None
    except requests.RequestException as exc:
        return None, f"{type(exc).__name__}: {exc}"


def describe_response(response):
    content_type = response.headers.get("Content-Type", "") or ""

    try:
        data = response.json()
        is_json = True
    except ValueError:
        data = None
        is_json = False

    shape = "invalid"
    size = 0
    keys = []

    if is_json:
        if isinstance(data, list):
            shape = "list"
            size = len(data)
            if data and isinstance(data[0], dict):
                keys = sorted(data[0])
        elif isinstance(data, dict):
            shape = "dict"
            size = len(data)
            keys = sorted(data)
        else:
            shape = "other"

    return {
        "status": response.status_code,
        "ok": response.status_code < 400,
        "content_type": content_type,
        "is_json": is_json,
        "shape": shape,
        "size": size,
        "keys": keys,
    }


def get_user(username):
    response = requests.get(
        f"{BASE}/users/{username}", headers=HEADERS, timeout=TIMEOUT
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def get_repos(username, per_page=100, sort="updated"):
    return fetch_json(
        f"{BASE}/users/{username}/repos",
        params={"per_page": per_page, "sort": sort},
    )


def summarize_user(user):
    created = user.get("created_at")
    return {
        "login": user.get("login"),
        "name": user.get("name") or "unknown",
        "public_repos": user.get("public_repos") or 0,
        "followers": user.get("followers") or 0,
        "created_year": int(created[:4]) if created else None,
        "has_blog": bool(user.get("blog")),
    }


def top_repos(repos, n=5):
    ranked = sorted(
        repos,
        key=lambda r: (-(r.get("stargazers_count") or 0), r.get("name") or ""),
    )
    return [(r.get("name"), r.get("stargazers_count") or 0) for r in ranked[:n]]


def user_report(username):
    user = get_user(username)
    if user is None:
        return {"user": None, "repos": [], "error": "user not found"}

    repos, error = safe_fetch(
        f"{BASE}/users/{username}/repos",
        params={"per_page": 100, "sort": "updated"},
    )
    return {
        "user": summarize_user(user),
        "repos": top_repos(repos or [], 5),
        "error": error,
    }


if __name__ == "__main__":
    who = sys.argv[1] if len(sys.argv) > 1 else "pallets"
    print(json.dumps(user_report(who), indent=2))
