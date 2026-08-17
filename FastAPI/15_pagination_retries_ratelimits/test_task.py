import json

import pytest
import requests

import task


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, headers=None, links=None):
        self.status_code = status_code
        self._json_body = json_body
        self.headers = headers or {}
        self.links = links or {}
        self.text = json.dumps(json_body)

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return self._json_body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)


class FakeSession:
    """Returns queued responses in order; records every call."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None, **kwargs):
        self.calls.append({"url": url, "params": params, "timeout": timeout})
        if not self.responses:
            raise AssertionError(f"unexpected extra request to {url}")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture
def sleeps():
    """A fake sleeper that records requested delays instead of waiting."""
    recorded = []
    return recorded, recorded.append


def page(n, per_page=100, start=0):
    return [{"i": start + i} for i in range(n)]


# --------------------------------------------------------------------------
# make_session
# --------------------------------------------------------------------------


def test_make_session_headers():
    session = task.make_session()
    assert isinstance(session, requests.Session)
    assert session.headers["Accept"] == "application/json"
    assert session.headers["User-Agent"] == task.USER_AGENT
    assert "Authorization" not in session.headers


def test_make_session_with_token():
    session = task.make_session(token="abc")
    assert session.headers["Authorization"] == "Bearer abc"


# --------------------------------------------------------------------------
# retry_delay
# --------------------------------------------------------------------------


def test_retry_delay_backoff():
    response = FakeResponse(500)
    assert task.retry_delay(response, 0) == 1
    assert task.retry_delay(response, 1) == 2
    assert task.retry_delay(response, 2) == 4


def test_retry_delay_uses_retry_after():
    response = FakeResponse(429, headers={"Retry-After": "30"})
    assert task.retry_delay(response, 0) == 30


def test_retry_delay_unparseable_retry_after():
    response = FakeResponse(429, headers={"Retry-After": "soon"})
    assert task.retry_delay(response, 1) == 2


def test_retry_delay_no_response():
    assert task.retry_delay(None, 2) == 4


# --------------------------------------------------------------------------
# fetch_with_retry
# --------------------------------------------------------------------------


def test_fetch_with_retry_success_first_time(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(200, {"a": 1})])
    assert task.fetch_with_retry(session, "https://x.com", sleeper=sleeper) == {"a": 1}
    assert recorded == [], "no sleeping when it works first time"
    assert len(session.calls) == 1


def test_fetch_with_retry_recovers_from_500(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(500), FakeResponse(200, {"ok": True})])
    assert task.fetch_with_retry(session, "https://x.com", sleeper=sleeper) == {"ok": True}
    assert recorded == [1]


def test_fetch_with_retry_recovers_from_timeout(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([requests.Timeout("slow"), FakeResponse(200, [1])])
    assert task.fetch_with_retry(session, "https://x.com", sleeper=sleeper) == [1]
    assert recorded == [1]


def test_fetch_with_retry_honours_retry_after(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession(
        [FakeResponse(429, headers={"Retry-After": "7"}), FakeResponse(200, {})]
    )
    task.fetch_with_retry(session, "https://x.com", sleeper=sleeper)
    assert recorded == [7]


def test_fetch_with_retry_gives_up_after_attempts(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(503) for _ in range(3)])
    with pytest.raises(requests.HTTPError):
        task.fetch_with_retry(session, "https://x.com", attempts=3, sleeper=sleeper)
    assert len(session.calls) == 3
    assert recorded == [1, 2], "no sleep after the final attempt"


def test_fetch_with_retry_does_not_retry_404(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(404, {"message": "no"})])
    with pytest.raises(requests.HTTPError):
        task.fetch_with_retry(session, "https://x.com", sleeper=sleeper)
    assert len(session.calls) == 1, "a 404 must not be retried"
    assert recorded == []


def test_fetch_with_retry_reraises_network_error(sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([requests.ConnectionError("no dns")] * 2)
    with pytest.raises(requests.ConnectionError):
        task.fetch_with_retry(session, "https://x.com", attempts=2, sleeper=sleeper)
    assert recorded == [1]


def test_fetch_with_retry_passes_params_and_timeout(sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, {})])
    task.fetch_with_retry(session, "https://x.com", params={"q": 1}, sleeper=sleeper)
    assert session.calls[0]["params"] == {"q": 1}
    assert session.calls[0]["timeout"]


# --------------------------------------------------------------------------
# rate limit helpers
# --------------------------------------------------------------------------


def test_rate_limit_status():
    response = FakeResponse(
        200,
        headers={
            "X-RateLimit-Limit": "60",
            "X-RateLimit-Remaining": "42",
            "X-RateLimit-Reset": "1700000000",
        },
    )
    assert task.rate_limit_status(response) == {
        "limit": 60,
        "remaining": 42,
        "reset": 1700000000,
    }


def test_rate_limit_status_lowercase_headers():
    response = FakeResponse(200, headers={"x-ratelimit-remaining": "7"})
    assert task.rate_limit_status(response)["remaining"] == 7


def test_rate_limit_status_missing_and_garbage():
    assert task.rate_limit_status(FakeResponse(200)) == {
        "limit": None,
        "remaining": None,
        "reset": None,
    }
    response = FakeResponse(200, headers={"X-RateLimit-Remaining": "many"})
    assert task.rate_limit_status(response)["remaining"] is None


def test_should_stop_for_rate_limit():
    assert task.should_stop_for_rate_limit(
        FakeResponse(200, headers={"X-RateLimit-Remaining": "2"})
    )
    assert not task.should_stop_for_rate_limit(
        FakeResponse(200, headers={"X-RateLimit-Remaining": "50"})
    )
    assert not task.should_stop_for_rate_limit(FakeResponse(200))
    assert task.should_stop_for_rate_limit(
        FakeResponse(200, headers={"X-RateLimit-Remaining": "10"}), floor=20
    )


# --------------------------------------------------------------------------
# paginate_offset
# --------------------------------------------------------------------------


def test_paginate_offset_collects_until_short_page():
    session = FakeSession(
        [
            FakeResponse(200, page(100)),
            FakeResponse(200, page(100, start=100)),
            FakeResponse(200, page(7, start=200)),
        ]
    )
    records = task.paginate_offset(session, "https://x.com", per_page=100, max_pages=5)
    assert len(records) == 207
    assert len(session.calls) == 3, "a short page ends it -- no extra request"


def test_paginate_offset_stops_on_empty_page():
    session = FakeSession([FakeResponse(200, page(10)), FakeResponse(200, [])])
    assert len(task.paginate_offset(session, "https://x.com", per_page=10)) == 10
    assert len(session.calls) == 2


def test_paginate_offset_respects_max_pages():
    session = FakeSession([FakeResponse(200, page(10)) for _ in range(10)])
    task.paginate_offset(session, "https://x.com", per_page=10, max_pages=3)
    assert len(session.calls) == 3


def test_paginate_offset_sends_page_numbers_from_one():
    session = FakeSession([FakeResponse(200, page(2)) for _ in range(2)])
    task.paginate_offset(session, "https://x.com", per_page=2, max_pages=2)
    assert [c["params"]["page"] for c in session.calls] == [1, 2]
    assert session.calls[0]["params"]["per_page"] == 2


def test_paginate_offset_merges_extra_params():
    session = FakeSession([FakeResponse(200, [])])
    task.paginate_offset(session, "https://x.com", params={"sort": "stars"}, per_page=5)
    assert session.calls[0]["params"]["sort"] == "stars"


def test_paginate_offset_custom_page_param():
    session = FakeSession([FakeResponse(200, [])])
    task.paginate_offset(session, "https://x.com", page_param="pagina")
    assert "pagina" in session.calls[0]["params"]


def test_paginate_offset_stops_on_low_rate_limit():
    session = FakeSession(
        [
            FakeResponse(200, page(10), headers={"X-RateLimit-Remaining": "50"}),
            FakeResponse(200, page(10), headers={"X-RateLimit-Remaining": "1"}),
            FakeResponse(200, page(10)),
        ]
    )
    records = task.paginate_offset(session, "https://x.com", per_page=10, max_pages=5)
    assert len(records) == 20, "keeps the page it already fetched"
    assert len(session.calls) == 2


# --------------------------------------------------------------------------
# paginate_hn
# --------------------------------------------------------------------------


def envelope(hits, page_no, n_pages):
    return {"hits": hits, "page": page_no, "nbPages": n_pages, "nbHits": len(hits)}


def test_paginate_hn_pages_from_zero():
    session = FakeSession(
        [
            FakeResponse(200, envelope(page(50), 0, 3)),
            FakeResponse(200, envelope(page(50, start=50), 1, 3)),
        ]
    )
    hits = task.paginate_hn(session, "python", max_pages=2)
    assert len(hits) == 100
    assert [c["params"]["page"] for c in session.calls] == [0, 1]
    assert session.calls[0]["params"]["query"] == "python"
    assert session.calls[0]["params"]["tags"] == "story"
    assert session.calls[0]["params"]["hitsPerPage"] == 50


def test_paginate_hn_stops_on_last_page():
    session = FakeSession([FakeResponse(200, envelope(page(5), 0, 1))])
    assert len(task.paginate_hn(session, "python", max_pages=5)) == 5
    assert len(session.calls) == 1


def test_paginate_hn_stops_on_empty_hits():
    session = FakeSession([FakeResponse(200, envelope([], 0, 10))])
    assert task.paginate_hn(session, "python") == []


def test_paginate_hn_on_recorded_envelope(load_fixture):
    recorded = load_fixture("hn_search_python")
    session = FakeSession([FakeResponse(200, recorded)])
    hits = task.paginate_hn(session, "python", max_pages=1)
    assert len(hits) == 50
    assert "objectID" in hits[0]


# --------------------------------------------------------------------------
# paginate_link_header
# --------------------------------------------------------------------------


def test_paginate_link_header_follows_next():
    session = FakeSession(
        [
            FakeResponse(200, page(3), links={"next": {"url": "https://x.com/?page=2"}}),
            FakeResponse(200, page(2, start=3)),
        ]
    )
    records = task.paginate_link_header(session, "https://x.com/", params={"per_page": 3})
    assert len(records) == 5
    assert session.calls[1]["url"] == "https://x.com/?page=2"
    assert not session.calls[1]["params"], "params must not be re-sent with an absolute next url"


def test_paginate_link_header_single_page():
    session = FakeSession([FakeResponse(200, page(4))])
    assert len(task.paginate_link_header(session, "https://x.com/")) == 4
    assert len(session.calls) == 1


def test_paginate_link_header_respects_max_pages():
    session = FakeSession(
        [FakeResponse(200, page(1), links={"next": {"url": f"https://x.com/{i}"}}) for i in range(5)]
    )
    task.paginate_link_header(session, "https://x.com/", max_pages=3)
    assert len(session.calls) == 3


# --------------------------------------------------------------------------
# caching
# --------------------------------------------------------------------------


def test_cache_key_is_order_independent():
    assert task.cache_key("https://x.com", {"b": 2, "a": 1}) == task.cache_key(
        "https://x.com", {"a": 1, "b": 2}
    )


def test_cache_key_differs_by_url_and_params():
    assert task.cache_key("https://x.com") != task.cache_key("https://y.com")
    assert task.cache_key("https://x.com", {"a": 1}) != task.cache_key(
        "https://x.com", {"a": 2}
    )


def test_cache_key_shape():
    key = task.cache_key("https://x.com", {"a": 1})
    assert len(key) == 16
    assert all(c in "0123456789abcdef" for c in key)


def test_cached_fetch_writes_then_reads(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, {"v": 1})])
    first = task.cached_fetch(
        session, "https://x.com", params={"a": 1}, cache_dir=tmp_path, sleeper=sleeper
    )
    second = task.cached_fetch(
        session, "https://x.com", params={"a": 1}, cache_dir=tmp_path, sleeper=sleeper
    )
    assert first == second == {"v": 1}
    assert len(session.calls) == 1, "second call must be served from the cache"
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_cached_fetch_different_params_miss(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, {"v": 1}), FakeResponse(200, {"v": 2})])
    a = task.cached_fetch(session, "https://x.com", {"p": 1}, cache_dir=tmp_path, sleeper=sleeper)
    b = task.cached_fetch(session, "https://x.com", {"p": 2}, cache_dir=tmp_path, sleeper=sleeper)
    assert (a, b) == ({"v": 1}, {"v": 2})
    assert len(session.calls) == 2


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_paginate_hn():
    session = task.make_session()
    hits = task.paginate_hn(session, "fastapi", hits_per_page=20, max_pages=2)
    assert len(hits) == 40
    assert len({h["objectID"] for h in hits}) == 40, "pages must not overlap"


@pytest.mark.live
def test_live_paginate_link_header():
    session = task.make_session()
    repos = task.paginate_link_header(
        session, f"{task.GITHUB}/users/pallets/repos", params={"per_page": 5}, max_pages=2
    )
    assert len(repos) == 10
    assert len({r["id"] for r in repos}) == 10


@pytest.mark.live
def test_live_rate_limit_status():
    session = task.make_session()
    response = session.get(f"{task.GITHUB}/rate_limit", timeout=task.TIMEOUT)
    status = task.rate_limit_status(response)
    assert status["limit"] is not None
    assert status["remaining"] is not None


@pytest.mark.live
def test_live_cached_fetch(tmp_path):
    session = task.make_session()
    url = f"{task.GITHUB}/users/pallets"
    first = task.cached_fetch(session, url, cache_dir=tmp_path)
    second = task.cached_fetch(session, url, cache_dir=tmp_path)
    assert first["login"] == second["login"] == "pallets"
