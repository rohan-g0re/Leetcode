import pytest

from task import (
    build_query_string,
    extract_domain,
    format_table_row,
    normalize_key,
    parse_iso_date,
    title_words,
    truncate,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  First Name ", "first_name"),
        ("User-ID", "user_id"),
        ("total   count", "total_count"),
        ("API_Key", "api_key"),
        ("already_ok", "already_ok"),
        ("", ""),
        ("   ", ""),
        ("A-B C", "a_b_c"),
    ],
)
def test_normalize_key(raw, expected):
    assert normalize_key(raw) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("2024-01-05", (2024, 1, 5)),
        ("2024-01-05T10:30:00Z", (2024, 1, 5)),
        ("1999-12-31", (1999, 12, 31)),
        ("not a date", None),
        ("2024-01", None),
        ("2024-01-05-06", None),
        ("abcd-01-05", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_iso_date(text, expected):
    assert parse_iso_date(text) == expected


@pytest.mark.parametrize(
    "text,limit,expected",
    [
        ("hello world", 8, "hello..."),
        ("hello", 8, "hello"),
        ("hello", 5, "hello"),
        ("hello", 4, "h..."),
        ("hello", 3, "..."),
        ("hello", 2, ".."),
        ("", 5, ""),
    ],
)
def test_truncate(text, limit, expected):
    assert truncate(text, limit) == expected
    assert len(truncate(text, limit)) <= limit


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://api.github.com/users/x", "api.github.com"),
        ("http://Example.COM/a/b?c=1", "example.com"),
        ("https://site.org", "site.org"),
        ("ftp://files.net/x", "files.net"),
        ("https://a.b.c.d/", "a.b.c.d"),
        ("not a url", None),
        ("", None),
    ],
)
def test_extract_domain(url, expected):
    assert extract_domain(url) == expected


def test_build_query_string():
    assert build_query_string({"q": "python", "page": 2}) == "q=python&page=2"
    assert build_query_string({}) == ""
    assert build_query_string({"a": None, "b": 1}) == "b=1"
    assert build_query_string({"a": None}) == ""
    assert build_query_string({"x": 0}) == "x=0"


def test_title_words():
    assert title_words("Show HN: A tool for parsing JSON, fast!") == [
        "fast",
        "json",
        "parsing",
        "show",
        "tool",
    ]
    assert title_words("a b c", min_length=1) == ["a", "b", "c"]
    assert title_words("Repeat repeat REPEAT", min_length=3) == ["repeat"]
    assert title_words("") == []


def test_format_table_row():
    assert format_table_row(["ab", "c"], [5, 3]) == "ab    | c"
    assert format_table_row(["abcdef"], [3]) == "abcdef"
    assert format_table_row(["a", "b", "c"], [2, 2, 2]) == "a  | b  | c"
