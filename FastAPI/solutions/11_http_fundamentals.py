"""Unit 11 — worked solution."""

import re
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

LINK_PATTERN = re.compile(r'<([^>]*)>\s*;\s*rel\s*=\s*"?([^",;\s]+)"?')


def split_url(url):
    parts = urlparse(url)
    return {
        "scheme": parts.scheme,
        "host": parts.netloc,
        "path": parts.path,
        "query": dict(parse_qsl(parts.query)),
        "fragment": parts.fragment,
    }


def add_params(url, **new_params):
    parts = urlparse(url)
    params = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in new_params.items():
        if value is None:
            params.pop(key, None)
        else:
            params[key] = value
    return urlunparse(parts._replace(query=urlencode(params)))


def join_path(base, *parts):
    parsed = urlparse(base)
    path = parsed.path
    for part in parts:
        if not part:
            continue
        path = f"{path.rstrip('/')}/{str(part).strip('/')}"
    return urlunparse(parsed._replace(path=path))


def classify(status):
    if 100 <= status < 200:
        category = "informational"
    elif 200 <= status < 300:
        category = "success"
    elif 300 <= status < 400:
        category = "redirect"
    elif 400 <= status < 500:
        category = "client_error"
    elif 500 <= status < 600:
        category = "server_error"
    else:
        category = "unknown"

    return {
        "code": status,
        "category": category,
        "retryable": status == 429 or 500 <= status < 600,
        "our_fault": 400 <= status < 500,
    }


def build_auth_headers(token=None, api_key=None, user_agent="python-course/1.0"):
    headers = {"Accept": "application/json", "User-Agent": user_agent}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def parse_link_header(value):
    return {rel: url for url, rel in LINK_PATTERN.findall(value or "")}


def next_page_url(link_header):
    return parse_link_header(link_header).get("next")


def seconds_until_reset(headers, now_epoch):
    lower = {key.lower(): value for key, value in headers.items()}

    retry_after = lower.get("retry-after")
    if retry_after is not None:
        try:
            return int(retry_after)
        except (TypeError, ValueError):
            pass

    if lower.get("x-ratelimit-remaining") == "0":
        try:
            reset = int(lower.get("x-ratelimit-reset"))
        except (TypeError, ValueError):
            return 0
        return max(0, reset - now_epoch)

    return 0
