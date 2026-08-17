import pytest

from task import (
    add_params,
    build_auth_headers,
    classify,
    join_path,
    next_page_url,
    parse_link_header,
    seconds_until_reset,
    split_url,
)


def test_split_url_full():
    assert split_url("https://api.github.com/users/x?a=1&b=2#top") == {
        "scheme": "https",
        "host": "api.github.com",
        "path": "/users/x",
        "query": {"a": "1", "b": "2"},
        "fragment": "top",
    }


def test_split_url_minimal():
    assert split_url("https://api.github.com") == {
        "scheme": "https",
        "host": "api.github.com",
        "path": "",
        "query": {},
        "fragment": "",
    }


def test_split_url_repeated_param_keeps_last():
    assert split_url("https://x.com/?a=1&a=2")["query"] == {"a": "2"}


def test_split_url_decodes_values():
    assert split_url("https://x.com/?q=hello%20world")["query"] == {"q": "hello world"}


def test_add_params():
    assert add_params("https://x.com/a?p=1", q="hi") == "https://x.com/a?p=1&q=hi"
    assert add_params("https://x.com/a?p=1", p=2) == "https://x.com/a?p=2"
    assert add_params("https://x.com/a", q="a b") == "https://x.com/a?q=a+b"
    assert add_params("https://x.com/a", q=None) == "https://x.com/a"
    assert add_params("https://x.com/a?p=1", p=None) == "https://x.com/a"


def test_add_params_preserves_fragment():
    assert add_params("https://x.com/a#top", q=1) == "https://x.com/a?q=1#top"


def test_add_params_no_change():
    assert add_params("https://x.com/a?p=1") == "https://x.com/a?p=1"


def test_join_path():
    assert join_path("https://x.com", "users", "torvalds") == (
        "https://x.com/users/torvalds"
    )
    assert join_path("https://x.com/api/", "/users/", "/torvalds/") == (
        "https://x.com/api/users/torvalds"
    )
    assert join_path("https://x.com") == "https://x.com"
    assert join_path("https://x.com/", ) == "https://x.com/"


def test_join_path_preserves_query():
    assert join_path("https://x.com/api?k=1", "users") == "https://x.com/api/users?k=1"


def test_join_path_skips_empty_segments():
    assert join_path("https://x.com", "a", "", None, "b") == "https://x.com/a/b"


@pytest.mark.parametrize(
    "status,category,retryable,our_fault",
    [
        (200, "success", False, False),
        (204, "success", False, False),
        (301, "redirect", False, False),
        (400, "client_error", False, True),
        (404, "client_error", False, True),
        (429, "client_error", True, True),
        (500, "server_error", True, False),
        (503, "server_error", True, False),
        (100, "informational", False, False),
        (42, "unknown", False, False),
        (700, "unknown", False, False),
    ],
)
def test_classify(status, category, retryable, our_fault):
    assert classify(status) == {
        "code": status,
        "category": category,
        "retryable": retryable,
        "our_fault": our_fault,
    }


def test_build_auth_headers_default():
    assert build_auth_headers() == {
        "Accept": "application/json",
        "User-Agent": "python-course/1.0",
    }


def test_build_auth_headers_token():
    headers = build_auth_headers(token="abc", user_agent="mine/2")
    assert headers == {
        "Accept": "application/json",
        "User-Agent": "mine/2",
        "Authorization": "Bearer abc",
    }


def test_build_auth_headers_api_key():
    assert build_auth_headers(api_key="k")["X-API-Key"] == "k"


def test_build_auth_headers_empty_strings_ignored():
    assert build_auth_headers(token="", api_key="") == {
        "Accept": "application/json",
        "User-Agent": "python-course/1.0",
    }


GITHUB_LINK = (
    '<https://api.github.com/user/repos?page=2>; rel="next", '
    '<https://api.github.com/user/repos?page=50>; rel="last"'
)


def test_parse_link_header():
    assert parse_link_header(GITHUB_LINK) == {
        "next": "https://api.github.com/user/repos?page=2",
        "last": "https://api.github.com/user/repos?page=50",
    }


def test_parse_link_header_empty():
    assert parse_link_header("") == {}
    assert parse_link_header(None) == {}


def test_parse_link_header_tolerates_whitespace_and_extras():
    value = '  <https://x.com/a>;rel="next" ,  <https://x.com/b>; rel="prev"; title="x" '
    assert parse_link_header(value) == {
        "next": "https://x.com/a",
        "prev": "https://x.com/b",
    }


def test_parse_link_header_skips_malformed():
    assert parse_link_header('garbage, <https://x.com/a>; rel="next"') == {
        "next": "https://x.com/a"
    }


def test_next_page_url():
    assert next_page_url(GITHUB_LINK) == "https://api.github.com/user/repos?page=2"
    assert next_page_url('<https://x.com/a>; rel="last"') is None
    assert next_page_url("") is None


def test_seconds_until_reset_retry_after():
    assert seconds_until_reset({"Retry-After": "30"}, 1000) == 30
    assert seconds_until_reset({"retry-after": "5"}, 1000) == 5


def test_seconds_until_reset_ratelimit():
    headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1100"}
    assert seconds_until_reset(headers, 1000) == 100
    assert seconds_until_reset(headers, 1200) == 0


def test_seconds_until_reset_not_limited():
    assert seconds_until_reset({"x-ratelimit-remaining": "5"}, 1000) == 0
    assert seconds_until_reset({}, 1000) == 0


def test_seconds_until_reset_ignores_unparseable_retry_after():
    headers = {"Retry-After": "Wed, 21 Oct 2015 07:28:00 GMT"}
    assert seconds_until_reset(headers, 1000) == 0
