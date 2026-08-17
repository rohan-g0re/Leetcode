from collections import Counter
from datetime import datetime, timezone

import pytest

import task

# --------------------------------------------------------------------------
# parse_timestamp
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw",
    [
        "2024-01-05T10:30:00Z",
        "2024-01-05T10:30:00.000Z",
        "2024-01-05T10:30:00+00:00",
    ],
)
def test_parse_timestamp_iso_variants(raw):
    parsed = task.parse_timestamp(raw)
    assert parsed is not None
    assert (parsed.year, parsed.month, parsed.day) == (2024, 1, 5)
    assert parsed.hour == 10
    assert parsed.tzinfo is not None, "result must be timezone-aware"


def test_parse_timestamp_date_only():
    parsed = task.parse_timestamp("2024-01-05")
    assert parsed == datetime(2024, 1, 5, tzinfo=timezone.utc)
    assert parsed.tzinfo is not None


def test_parse_timestamp_epoch():
    parsed = task.parse_timestamp(1700000000)
    assert parsed.year == 2023
    assert parsed.tzinfo is not None
    assert task.parse_timestamp(1700000000.5) is not None


@pytest.mark.parametrize("raw", ["not a date", "", None, [], "2024-13-45"])
def test_parse_timestamp_bad_input(raw):
    assert task.parse_timestamp(raw) is None


def test_parse_timestamp_on_real_data():
    hits = task.load("hn_search_python")["hits"]
    parsed = [task.parse_timestamp(h["created_at"]) for h in hits]
    assert all(p is not None for p in parsed)
    assert all(p.tzinfo is not None for p in parsed)


# --------------------------------------------------------------------------
# count_by
# --------------------------------------------------------------------------


def test_count_by():
    counts = task.count_by([{"a": "x"}, {"a": "x"}, {"b": 1}], "a")
    assert counts == Counter({"x": 2, "unknown": 1})
    assert isinstance(counts, Counter)


def test_count_by_null_value():
    assert task.count_by([{"a": None}], "a", missing="none") == Counter({"none": 1})


def test_count_by_empty():
    assert task.count_by([], "a") == Counter()


# --------------------------------------------------------------------------
# numeric_summary
# --------------------------------------------------------------------------


def test_numeric_summary_basic():
    summary = task.numeric_summary([1, 2, 3, 4])
    assert summary["count"] == 4
    assert summary["min"] == 1
    assert summary["max"] == 4
    assert summary["mean"] == 2.5
    assert summary["median"] == 2.5
    assert summary["skewed"] is False


def test_numeric_summary_ignores_none():
    assert task.numeric_summary([1, None, 3])["count"] == 2


def test_numeric_summary_empty():
    assert task.numeric_summary([]) == {
        "count": 0,
        "min": None,
        "max": None,
        "mean": None,
        "median": None,
        "p90": None,
        "skewed": False,
    }
    assert task.numeric_summary([None, None])["count"] == 0


def test_numeric_summary_single_value():
    summary = task.numeric_summary([7])
    assert summary["count"] == 1
    assert summary["mean"] == summary["median"] == summary["p90"] == 7


def test_numeric_summary_p90_nearest_rank():
    assert task.numeric_summary(list(range(1, 11)))["p90"] == 10
    assert task.numeric_summary([1, 2, 3, 4, 5])["p90"] == 5


def test_numeric_summary_detects_skew():
    assert task.numeric_summary([1, 1, 1, 1, 100])["skewed"] is True
    assert task.numeric_summary([10, 10, 10])["skewed"] is False


def test_numeric_summary_rounds_to_2dp():
    assert task.numeric_summary([1, 2])["mean"] == 1.5
    assert task.numeric_summary([1, 1, 2])["mean"] == 1.33


# --------------------------------------------------------------------------
# group_stats
# --------------------------------------------------------------------------


def test_group_stats():
    records = [{"g": "a", "v": 1}, {"g": "a", "v": 3}, {"g": "b", "v": 10}]
    stats = task.group_stats(records, "g", "v")
    assert set(stats) == {"a", "b"}
    assert stats["a"]["count"] == 2
    assert stats["a"]["mean"] == 2.0
    assert stats["b"]["max"] == 10


def test_group_stats_keeps_empty_groups():
    stats = task.group_stats([{"g": "b"}], "g", "v")
    assert stats["b"]["count"] == 0
    assert stats["b"]["mean"] is None


def test_group_stats_missing_group_key():
    stats = task.group_stats([{"v": 5}], "g", "v")
    assert stats["unknown"]["count"] == 1


def test_group_stats_empty():
    assert task.group_stats([], "g", "v") == {}


# --------------------------------------------------------------------------
# top_n_by
# --------------------------------------------------------------------------


def test_top_n_by_records():
    records = [{"n": 1}, {"n": 9}, {"n": 5}]
    assert task.top_n_by(records, "n", 2) == [{"n": 9}, {"n": 5}]


def test_top_n_by_labels():
    records = [{"t": "a", "n": 1}, {"t": "b", "n": 9}]
    assert task.top_n_by(records, "n", 2, label_field="t") == [("b", 9), ("a", 1)]


def test_top_n_by_tie_breaks_on_label():
    records = [{"t": "z", "n": 5}, {"t": "a", "n": 5}]
    assert task.top_n_by(records, "n", 2, label_field="t") == [("a", 5), ("z", 5)]


def test_top_n_by_missing_values_are_zero():
    records = [{"t": "a"}, {"t": "b", "n": 1}]
    assert task.top_n_by(records, "n", 2, label_field="t") == [("b", 1), ("a", 0)]


def test_top_n_by_empty():
    assert task.top_n_by([], "n", 3) == []


# --------------------------------------------------------------------------
# bucket_by_month
# --------------------------------------------------------------------------


def test_bucket_by_month():
    records = [{"d": "2024-01-05"}, {"d": "2024-01-31"}, {"d": "2024-03-01"}]
    assert task.bucket_by_month(records, "d") == {"2024-01": 2, "2024-03": 1}


def test_bucket_by_month_sorted_ascending():
    records = [{"d": "2024-03-01"}, {"d": "2023-12-01"}]
    assert list(task.bucket_by_month(records, "d")) == ["2023-12", "2024-03"]


def test_bucket_by_month_skips_unparseable():
    assert task.bucket_by_month([{"d": "nope"}, {"d": None}, {}], "d") == {}


def test_bucket_by_month_on_real_data():
    hits = task.load("hn_search_python")["hits"]
    buckets = task.bucket_by_month(hits, "created_at")
    assert sum(buckets.values()) == 50
    assert list(buckets) == sorted(buckets)


# --------------------------------------------------------------------------
# join_records
# --------------------------------------------------------------------------


def test_join_records():
    left = [{"userId": 1, "title": "t"}]
    right = [{"id": 1, "name": "Leanne", "email": "l@x.com"}]
    assert task.join_records(left, right, "userId", "id", ["name"], prefix="user_") == [
        {"userId": 1, "title": "t", "user_name": "Leanne"}
    ]


def test_join_records_keeps_unmatched():
    left = [{"userId": 99, "title": "t"}]
    right = [{"id": 1, "name": "x"}]
    assert task.join_records(left, right, "userId", "id", ["name"]) == [
        {"userId": 99, "title": "t"}
    ]


def test_join_records_does_not_mutate_left():
    left = [{"userId": 1}]
    right = [{"id": 1, "name": "x"}]
    task.join_records(left, right, "userId", "id", ["name"])
    assert left == [{"userId": 1}]


def test_join_records_on_real_data():
    posts = task.load("placeholder_posts")
    users = task.load("placeholder_users")
    joined = task.join_records(posts, users, "userId", "id", ["name", "username"], "user_")
    assert len(joined) == 100
    assert all("user_name" in row for row in joined)
    assert joined[0]["user_name"] == "Leanne Graham"

    per_user = task.count_by(joined, "user_name")
    assert len(per_user) == 10
    assert set(per_user.values()) == {10}


# --------------------------------------------------------------------------
# analyze_hn
# --------------------------------------------------------------------------


@pytest.fixture
def report():
    return task.analyze_hn(task.load("hn_search_python")["hits"])


def test_analyze_hn_counts(report):
    assert report["count"] == 50
    assert report["points"]["count"] == 50
    assert report["comments"]["count"] == 50


def test_analyze_hn_points_stats(report):
    assert report["points"]["mean"] == 828.44
    assert report["points"]["median"] == 744.5
    assert report["points"]["max"] == 2214
    assert report["points"]["min"] == 634


def test_analyze_hn_top_stories(report):
    top = report["top_stories"]
    assert len(top) == 5
    assert top[0][1] == 2214
    assert isinstance(top[0][0], str)
    assert [t[1] for t in top] == sorted([t[1] for t in top], reverse=True)


def test_analyze_hn_authors(report):
    assert len(report["by_author"]) == 5
    assert report["distinct_authors"] <= 50
    assert all(isinstance(count, int) for _, count in report["by_author"])


def test_analyze_hn_months(report):
    assert sum(report["by_month"].values()) == 50
    assert list(report["by_month"]) == sorted(report["by_month"])


# --------------------------------------------------------------------------
# format_table
# --------------------------------------------------------------------------


def test_format_table():
    assert task.format_table([("a", 1), ("bbb", 22)], ["name", "n"]) == (
        "name   n\na      1\nbbb   22"
    )


def test_format_table_header_only():
    assert task.format_table([], ["name", "n"]) == "name  n"


def test_format_table_no_trailing_whitespace():
    rendered = task.format_table([("long-label", 1)], ["a", "b"])
    for line in rendered.splitlines():
        assert line == line.rstrip()


def test_format_table_three_columns():
    rendered = task.format_table([("x", 1, 2)], ["a", "b", "c"])
    assert rendered.splitlines()[1] == "x  1  2"
