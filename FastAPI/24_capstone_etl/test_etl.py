import json

import pytest
import requests

import etl


# --------------------------------------------------------------------------
# fakes
# --------------------------------------------------------------------------


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, headers=None):
        self.status_code = status_code
        self._json_body = json_body
        self.headers = headers or {}
        self.text = json.dumps(json_body)

    def json(self):
        return self._json_body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None, **kwargs):
        self.calls.append({"url": url, "params": params})
        if not self.responses:
            raise AssertionError(f"unexpected extra request to {url}")
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def hit(object_id, points=10, comments=5, url="https://example.com/a", created="2024-05-06T12:00:00.000Z", **extra):
    payload = {
        "objectID": object_id,
        "title": f"story {object_id}",
        "author": "someone",
        "points": points,
        "num_comments": comments,
        "url": url,
        "created_at": created,
    }
    payload.update(extra)
    return payload


def envelope(hits, page=0, n_pages=3, n_hits=250):
    return {"hits": hits, "page": page, "nbPages": n_pages, "nbHits": n_hits}


@pytest.fixture
def sleeps():
    recorded = []
    return recorded, recorded.append


# --------------------------------------------------------------------------
# extract
# --------------------------------------------------------------------------


def test_make_session():
    session = etl.make_session()
    assert isinstance(session, requests.Session)
    assert session.headers["Accept"] == "application/json"
    assert "User-Agent" in session.headers


def test_cache_path_is_stable_and_order_independent(tmp_path):
    a = etl.cache_path({"query": "x", "page": 1}, cache_dir=tmp_path)
    b = etl.cache_path({"page": 1, "query": "x"}, cache_dir=tmp_path)
    c = etl.cache_path({"query": "y", "page": 1}, cache_dir=tmp_path)
    assert a == b
    assert a != c
    assert a.suffix == ".json"


def test_fetch_page_caches(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, envelope([hit("1")]))])
    params = {"query": "x", "page": 0}
    first = etl.fetch_page(session, params, cache_dir=tmp_path, sleeper=sleeper)
    second = etl.fetch_page(session, params, cache_dir=tmp_path, sleeper=sleeper)
    assert first == second
    assert len(session.calls) == 1, "second call must come from the cache"


def test_fetch_page_retries_5xx(tmp_path, sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(503), FakeResponse(200, envelope([]))])
    etl.fetch_page(session, {"q": 1}, cache_dir=tmp_path, sleeper=sleeper)
    assert len(session.calls) == 2
    assert recorded == [1]


def test_fetch_page_retries_timeout(tmp_path, sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([requests.Timeout("slow"), FakeResponse(200, envelope([]))])
    etl.fetch_page(session, {"q": 1}, cache_dir=tmp_path, sleeper=sleeper)
    assert len(session.calls) == 2


def test_fetch_page_does_not_retry_400(tmp_path, sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(400, {"message": "bad"})])
    with pytest.raises(requests.HTTPError):
        etl.fetch_page(session, {"q": 1}, cache_dir=tmp_path, sleeper=sleeper)
    assert len(session.calls) == 1
    assert recorded == []


def test_fetch_page_gives_up(tmp_path, sleeps):
    recorded, sleeper = sleeps
    session = FakeSession([FakeResponse(500) for _ in range(3)])
    with pytest.raises(requests.HTTPError):
        etl.fetch_page(session, {"q": 1}, cache_dir=tmp_path, sleeper=sleeper, attempts=3)
    assert len(session.calls) == 3
    assert recorded == [1, 2]


def test_extract_pages(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession(
        [
            FakeResponse(200, envelope([hit("1"), hit("2")], page=0, n_pages=3)),
            FakeResponse(200, envelope([hit("3")], page=1, n_pages=3)),
        ]
    )
    hits, meta = etl.extract(session, "python", pages=2, cache_dir=tmp_path, sleeper=sleeper)
    assert len(hits) == 3
    assert meta["pages_fetched"] == 2
    assert meta["total_available"] == 250
    assert meta["query"] == "python"
    assert [call["params"]["page"] for call in session.calls] == [0, 1]


def test_extract_stops_on_last_page(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, envelope([hit("1")], page=0, n_pages=1))])
    hits, meta = etl.extract(session, "x", pages=5, cache_dir=tmp_path, sleeper=sleeper)
    assert len(hits) == 1
    assert meta["pages_fetched"] == 1


def test_extract_stops_on_empty(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, envelope([], page=0, n_pages=9))])
    hits, meta = etl.extract(session, "x", pages=5, cache_dir=tmp_path, sleeper=sleeper)
    assert hits == []
    assert meta["pages_fetched"] == 1


def test_extract_sends_query_params(tmp_path, sleeps):
    _, sleeper = sleeps
    session = FakeSession([FakeResponse(200, envelope([], n_pages=1))])
    etl.extract(session, "fastapi", pages=1, hits_per_page=50, cache_dir=tmp_path, sleeper=sleeper)
    params = session.calls[0]["params"]
    assert params["query"] == "fastapi"
    assert params["tags"] == "story"
    assert params["hitsPerPage"] == 50


# --------------------------------------------------------------------------
# transform
# --------------------------------------------------------------------------


def test_parse_timestamp_variants():
    assert etl.parse_timestamp("2024-05-06T12:00:00Z") is not None
    assert etl.parse_timestamp("2024-05-06T12:00:00.000Z").year == 2024
    assert etl.parse_timestamp("2024-05-06T12:00:00+00:00").tzinfo is not None
    assert etl.parse_timestamp("nope") is None
    assert etl.parse_timestamp(None) is None


def test_domain_of():
    assert etl.domain_of("https://Example.COM/a?b=1") == "example.com"
    assert etl.domain_of("http://sub.site.org/x") == "sub.site.org"
    assert etl.domain_of(None) is None
    assert etl.domain_of("not a url") is None


def test_transform_shape():
    records, dropped = etl.transform([hit("1")])
    assert dropped == 0
    assert set(records[0]) == {
        "id",
        "title",
        "author",
        "points",
        "comments",
        "url",
        "domain",
        "created",
        "month",
    }
    assert records[0]["id"] == "1"
    assert records[0]["domain"] == "example.com"
    assert records[0]["month"] == "2024-05"
    assert records[0]["created"].startswith("2024-05-06")


def test_transform_drops_bad_records():
    hits = [
        hit("1"),
        {"title": "no id", "created_at": "2024-01-01T00:00:00Z"},
        hit("3", created="not a date"),
    ]
    records, dropped = etl.transform(hits)
    assert len(records) == 1
    assert dropped == 2


def test_transform_handles_nulls():
    records, _ = etl.transform(
        [hit("1", points=None, comments=None, url=None, title=None)]
    )
    row = records[0]
    assert row["points"] == 0
    assert row["comments"] == 0
    assert row["url"] is None
    assert row["domain"] is None
    assert row["title"] == ""


def test_transform_on_real_fixture(load_fixture):
    hits = load_fixture("hn_search_python")["hits"]
    records, dropped = etl.transform(hits)
    assert len(records) == 50
    assert dropped == 0
    assert all(isinstance(r["points"], int) for r in records)


def test_filter_records():
    records, _ = etl.transform(
        [
            hit("1", points=100, url="https://a.com/x", created="2024-01-01T00:00:00Z"),
            hit("2", points=10, url="https://b.com/x", created="2024-06-01T00:00:00Z"),
        ]
    )
    assert len(etl.filter_records(records, min_points=50)) == 1
    assert len(etl.filter_records(records, domain="A.COM")) == 1
    assert len(etl.filter_records(records, since="2024-03-01")) == 1
    assert len(etl.filter_records(records)) == 2
    assert etl.filter_records(records, min_points=50, since="2024-03-01") == []


# --------------------------------------------------------------------------
# analyze
# --------------------------------------------------------------------------


@pytest.fixture
def sample_records():
    hits = [
        hit("1", points=100, comments=10, url="https://a.com/1", created="2024-01-05T00:00:00Z"),
        hit("2", points=50, comments=5, url="https://a.com/2", created="2024-01-20T00:00:00Z"),
        hit("3", points=10, comments=1, url="https://b.com/3", created="2024-03-01T00:00:00Z"),
        hit("4", points=5, comments=0, url=None, created="2024-03-02T00:00:00Z"),
    ]
    records, _ = etl.transform(hits)
    return records


def test_analyze_counts(sample_records):
    report = etl.analyze(sample_records, meta={"query": "q", "pages_fetched": 2, "total_available": 99})
    assert report["query"] == "q"
    assert report["pages_fetched"] == 2
    assert report["total_available"] == 99
    assert report["records"] == 4
    assert report["points"]["count"] == 4
    assert report["points"]["max"] == 100
    assert report["self_posts"] == 1


def test_analyze_top_lists(sample_records):
    report = etl.analyze(sample_records, top_n=2)
    assert [s["points"] for s in report["top_stories"]] == [100, 50]
    assert report["top_domains"][0] == {
        "domain": "a.com",
        "stories": 2,
        "total_points": 150,
    }
    assert all("author" in entry for entry in report["top_authors"])


def test_analyze_by_month(sample_records):
    report = etl.analyze(sample_records)
    assert report["by_month"] == {"2024-01": 2, "2024-03": 2}
    assert list(report["by_month"]) == sorted(report["by_month"])


def test_analyze_date_range(sample_records):
    report = etl.analyze(sample_records)
    assert report["date_range"]["first"].startswith("2024-01-05")
    assert report["date_range"]["last"].startswith("2024-03-02")


def test_analyze_empty():
    report = etl.analyze([])
    assert report["records"] == 0
    assert report["points"]["count"] == 0
    assert report["top_stories"] == []
    assert report["by_month"] == {}
    assert report["date_range"] == {"first": None, "last": None}
    json.dumps(report)


def test_analyze_is_json_serializable(sample_records):
    json.dumps(etl.analyze(sample_records))


# --------------------------------------------------------------------------
# load
# --------------------------------------------------------------------------


def test_save_csv(tmp_path, sample_records):
    path = tmp_path / "out" / "stories.csv"
    assert etl.save_csv(sample_records, path) == 4
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert lines[0] == "id,title,author,points,comments,domain,url,created,month"
    assert len(lines) == 5


def test_save_json(tmp_path, sample_records):
    path = tmp_path / "summary.json"
    etl.save_json(etl.analyze(sample_records), path)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["records"] == 4


def test_format_report(sample_records):
    report = etl.analyze(sample_records, meta={"query": "python", "pages_fetched": 1, "total_available": 4})
    text = etl.format_report(report)
    assert isinstance(text, str)
    assert "python" in text
    assert "stories: 4" in text
    assert "points" in text.lower()
    assert "domains" in text.lower()
    assert "a.com" in text
    assert "b.com" in text


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_parser_defaults():
    args = build = etl.build_parser().parse_args(["python"])
    assert args.query == "python"
    assert args.pages == 3
    assert args.min_points == 0
    assert args.domain is None
    assert args.since is None
    assert args.out == "reports"
    assert args.no_cache is False


def test_parser_flags():
    args = etl.build_parser().parse_args(
        ["python", "--pages", "5", "--min-points", "50", "--domain", "a.com", "--out", "x", "--no-cache"]
    )
    assert args.pages == 5
    assert args.min_points == 50
    assert args.domain == "a.com"
    assert args.out == "x"
    assert args.no_cache is True


def test_run_end_to_end(tmp_path, monkeypatch, capsys):
    session = FakeSession(
        [FakeResponse(200, envelope([hit("1", points=100), hit("2", points=5)], page=0, n_pages=1))]
    )
    monkeypatch.setattr(etl, "make_session", lambda: session)
    monkeypatch.setattr(etl, "CACHE_DIR", tmp_path / "cache")

    out_dir = tmp_path / "reports"
    report = etl.run(["python", "--pages", "1", "--min-points", "50", "--out", str(out_dir)])

    assert report["records"] == 1
    assert (out_dir / "stories.csv").exists()
    assert (out_dir / "summary.json").exists()
    assert "python" in capsys.readouterr().out


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_extract(tmp_path):
    session = etl.make_session()
    hits, meta = etl.extract(session, "fastapi", pages=1, hits_per_page=20, cache_dir=tmp_path)
    assert len(hits) == 20
    assert meta["total_available"] > 0


@pytest.mark.live
def test_live_full_pipeline(tmp_path, capsys):
    session = etl.make_session()
    hits, meta = etl.extract(session, "python", pages=2, hits_per_page=50, cache_dir=tmp_path)
    records, dropped = etl.transform(hits)
    report = etl.analyze(records, meta=meta)
    assert report["records"] > 50
    assert report["points"]["count"] > 0
    text = etl.format_report(report)
    assert "python" in text
    json.dumps(report)
