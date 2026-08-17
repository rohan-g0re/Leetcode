import pytest

from task import (
    classify_status,
    collect_pages,
    collect_until,
    find_index_of_drop,
    first_match,
    fizz_report,
    should_retry,
)


@pytest.mark.parametrize(
    "code,expected",
    [
        (200, "success"),
        (201, "success"),
        (204, "success"),
        (299, "success"),
        (301, "redirect"),
        (304, "redirect"),
        (400, "client_error"),
        (404, "client_error"),
        (422, "client_error"),
        (429, "rate_limited"),
        (500, "server_error"),
        (503, "server_error"),
        (100, "unknown"),
        (99, "unknown"),
        (600, "unknown"),
    ],
)
def test_classify_status(code, expected):
    assert classify_status(code) == expected


@pytest.mark.parametrize(
    "code,attempt,expected",
    [
        (500, 0, True),
        (500, 1, True),
        (500, 2, False),
        (429, 1, True),
        (503, 0, True),
        (404, 0, False),
        (400, 0, False),
        (200, 0, False),
        (301, 0, False),
    ],
)
def test_should_retry(code, attempt, expected):
    assert should_retry(code, attempt) is expected


def test_should_retry_respects_max_attempts():
    assert should_retry(500, 0, max_attempts=1) is False
    assert should_retry(500, 3, max_attempts=5) is True


def test_first_match():
    assert first_match([{"id": 1}, {"id": 2}], "id", 2) == {"id": 2}
    assert first_match([{"id": 1}], "id", 9) is None
    assert first_match([], "id", 1) is None
    assert first_match([{"a": 1}], "id", 1) is None


def test_first_match_returns_first_not_last():
    records = [{"id": 1, "tag": "first"}, {"id": 1, "tag": "second"}]
    assert first_match(records, "id", 1)["tag"] == "first"


@pytest.mark.parametrize(
    "values,expected",
    [
        ([1, 2, 3, 2, 5], 3),
        ([1, 2, 3], None),
        ([3, 1], 1),
        ([5], None),
        ([], None),
        ([2, 2, 1], 2),
        ([5, 4, 3], 1),
    ],
)
def test_find_index_of_drop(values, expected):
    assert find_index_of_drop(values) == expected


def test_fizz_report():
    assert fizz_report(6) == ["1", "2", "low", "4", "high", "low"]
    assert fizz_report(0) == []
    assert fizz_report(15)[14] == "both"
    assert len(fizz_report(15)) == 15


class RecordingFetcher:
    """Fake page source that remembers which pages were requested."""

    def __init__(self, pages):
        self.pages = pages  # list of lists
        self.calls = []

    def __call__(self, page):
        self.calls.append(page)
        if page - 1 < len(self.pages):
            return self.pages[page - 1]
        return []


def test_collect_pages_flattens_in_order():
    fetcher = RecordingFetcher([[1, 2], [3], [4, 5]])
    assert collect_pages(fetcher) == [1, 2, 3, 4, 5]


def test_collect_pages_starts_at_one_and_stops_after_empty():
    fetcher = RecordingFetcher([[1], [2]])
    collect_pages(fetcher)
    assert fetcher.calls == [1, 2, 3], "should stop right after the first empty page"


def test_collect_pages_respects_cap():
    fetcher = RecordingFetcher([[1]] * 100)
    result = collect_pages(fetcher, max_pages=4)
    assert len(fetcher.calls) == 4
    assert result == [1, 1, 1, 1]


def test_collect_pages_empty_source():
    fetcher = RecordingFetcher([])
    assert collect_pages(fetcher) == []
    assert fetcher.calls == [1]


def test_collect_until_stops_early():
    fetcher = RecordingFetcher([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    result = collect_until(fetcher, 5)
    assert result == [1, 2, 3, 4, 5, 6]
    assert fetcher.calls == [1, 2]


def test_collect_until_exhausted_source():
    fetcher = RecordingFetcher([[1], [2]])
    assert collect_until(fetcher, 100) == [1, 2]
    assert fetcher.calls == [1, 2, 3]


def test_collect_until_respects_cap():
    fetcher = RecordingFetcher([[1]] * 100)
    assert collect_until(fetcher, 100, max_pages=3) == [1, 1, 1]
    assert len(fetcher.calls) == 3
