import json

import pytest
import requests

import task


class FakeResponse:
    def __init__(self, status_code=200, json_body=None, text=None):
        self.status_code = status_code
        self._json_body = json_body
        self.text = text if text is not None else json.dumps(json_body)
        self.headers = {"Content-Type": "application/json"}
        self.url = "https://fake/"

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        if self._json_body is None:
            raise requests.exceptions.JSONDecodeError("no json", self.text or "", 0)
        return self._json_body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error", response=self)


@pytest.fixture
def fake_http(monkeypatch):
    state = {"response": FakeResponse(200, {}), "calls": []}

    def _record(method):
        def _call(url, params=None, headers=None, timeout=None, json=None, data=None, **kw):
            state["calls"].append(
                {
                    "method": method,
                    "url": url,
                    "params": params,
                    "headers": headers,
                    "timeout": timeout,
                    "json": json,
                    "data": data,
                }
            )
            response = state["response"]
            if isinstance(response, Exception):
                raise response
            return response

        return _call

    monkeypatch.setattr(task.requests, "get", _record("GET"))
    monkeypatch.setattr(task.requests, "post", _record("POST"))
    return state


# --------------------------------------------------------------------------
# build_headers
# --------------------------------------------------------------------------


def test_build_headers_without_token(monkeypatch):
    monkeypatch.delenv("API_TOKEN", raising=False)
    assert task.build_headers() == {
        "Accept": "application/json",
        "User-Agent": "python-api-course/1.0",
    }


def test_build_headers_with_token(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "secret123")
    headers = task.build_headers()
    assert headers["Authorization"] == "Bearer secret123"


def test_build_headers_empty_token_ignored(monkeypatch):
    monkeypatch.setenv("API_TOKEN", "")
    assert "Authorization" not in task.build_headers()


def test_build_headers_custom_env_var(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "gh")
    headers = task.build_headers(token_env="GITHUB_TOKEN")
    assert headers["Authorization"] == "Bearer gh"


def test_build_headers_custom_agent(monkeypatch):
    monkeypatch.delenv("API_TOKEN", raising=False)
    assert task.build_headers(user_agent="mine/9")["User-Agent"] == "mine/9"


# --------------------------------------------------------------------------
# clean_params
# --------------------------------------------------------------------------


def test_clean_params_drops_empties():
    assert task.clean_params(q="py", page=None, sort="", tags=[]) == {"q": "py"}
    assert task.clean_params(x="   ") == {}


def test_clean_params_joins_lists():
    assert task.clean_params(daily=["a", "b"]) == {"daily": "a,b"}
    assert task.clean_params(ids=[1, 2, 3]) == {"ids": "1,2,3"}


def test_clean_params_lowercases_bools():
    assert task.clean_params(current=True, past=False) == {
        "current": "true",
        "past": "false",
    }


def test_clean_params_keeps_zero():
    assert task.clean_params(page=0, offset=0.0) == {"page": 0, "offset": 0.0}


def test_clean_params_empty():
    assert task.clean_params() == {}


# --------------------------------------------------------------------------
# get_json / post_json
# --------------------------------------------------------------------------


def test_get_json(fake_http):
    fake_http["response"] = FakeResponse(200, {"a": 1})
    assert task.get_json("https://x.com", params={"q": 1}) == {"a": 1}
    call = fake_http["calls"][0]
    assert call["params"] == {"q": 1}
    assert call["timeout"]


def test_get_json_raises(fake_http):
    fake_http["response"] = FakeResponse(404, {"message": "no"})
    with pytest.raises(requests.HTTPError):
        task.get_json("https://x.com")


def test_post_json_sends_json_body(fake_http):
    fake_http["response"] = FakeResponse(201, {"id": 101})
    status, body = task.post_json("https://x.com", {"title": "hi"})
    assert (status, body) == (201, {"id": 101})
    call = fake_http["calls"][0]
    assert call["method"] == "POST"
    assert call["json"] == {"title": "hi"}, "use json=, not data="
    assert call["data"] is None


def test_post_json_does_not_raise_on_error(fake_http):
    fake_http["response"] = FakeResponse(400, {"error": "bad title"})
    status, body = task.post_json("https://x.com", {})
    assert status == 400
    assert body == {"error": "bad title"}


def test_post_json_non_json_body(fake_http):
    fake_http["response"] = FakeResponse(500, None, text="<html>boom</html>")
    status, body = task.post_json("https://x.com", {})
    assert status == 500
    assert body == "<html>boom</html>"


def test_create_post_success(fake_http):
    fake_http["response"] = FakeResponse(201, {"id": 101, "title": "hi"})
    assert task.create_post("hi", "there") == {"id": 101, "title": "hi"}
    assert fake_http["calls"][0]["json"] == {"title": "hi", "body": "there", "userId": 1}


def test_create_post_failure(fake_http):
    fake_http["response"] = FakeResponse(422, {"message": "nope"})
    with pytest.raises(ValueError) as info:
        task.create_post("hi", "there")
    assert "422" in str(info.value)


# --------------------------------------------------------------------------
# daily_weather
# --------------------------------------------------------------------------


def test_daily_weather_reshapes_parallel_arrays(fake_http):
    fake_http["response"] = FakeResponse(
        200,
        {
            "daily": {
                "time": ["2024-01-01", "2024-01-02"],
                "temperature_2m_max": [4.1, 5.2],
                "temperature_2m_min": [-1.0, 0.4],
                "precipitation_sum": [0.0, 2.3],
            }
        },
    )
    assert task.daily_weather(52.52, 13.41, days=2) == [
        {"date": "2024-01-01", "max_c": 4.1, "min_c": -1.0, "precip_mm": 0.0},
        {"date": "2024-01-02", "max_c": 5.2, "min_c": 0.4, "precip_mm": 2.3},
    ]


def test_daily_weather_handles_short_and_missing_arrays(fake_http):
    fake_http["response"] = FakeResponse(
        200, {"daily": {"time": ["a", "b"], "temperature_2m_max": [1.0]}}
    )
    assert task.daily_weather(0, 0) == [
        {"date": "a", "max_c": 1.0, "min_c": None, "precip_mm": None},
        {"date": "b", "max_c": None, "min_c": None, "precip_mm": None},
    ]


def test_daily_weather_missing_daily_key(fake_http):
    fake_http["response"] = FakeResponse(200, {"error": True})
    assert task.daily_weather(0, 0) == []
    fake_http["response"] = FakeResponse(200, {"daily": {}})
    assert task.daily_weather(0, 0) == []


def test_daily_weather_sends_clean_params(fake_http):
    fake_http["response"] = FakeResponse(200, {"daily": {"time": []}})
    task.daily_weather(52.52, 13.41, days=3)
    params = fake_http["calls"][0]["params"]
    assert params["latitude"] == 52.52
    assert params["forecast_days"] == 3
    assert params["timezone"] == "UTC"
    assert params["daily"] == (
        "temperature_2m_max,temperature_2m_min,precipitation_sum"
    ), "daily must be one comma-joined string"


def test_daily_weather_on_recorded_response(load_fixture, monkeypatch):
    recorded = load_fixture("open_meteo_berlin")
    monkeypatch.setattr(task, "get_json", lambda *a, **k: recorded)
    rows = task.daily_weather(52.52, 13.41, days=16)
    assert len(rows) == 16
    assert set(rows[0]) == {"date", "max_c", "min_c", "precip_mm"}
    assert all(isinstance(r["date"], str) for r in rows)


# --------------------------------------------------------------------------
# fx_series
# --------------------------------------------------------------------------


def test_fx_series_flattens(fake_http):
    fake_http["response"] = FakeResponse(
        200,
        {
            "base": "USD",
            "rates": {
                "2024-01-03": {"GBP": 0.79, "EUR": 0.91},
                "2024-01-02": {"EUR": 0.90, "GBP": 0.78},
            },
        },
    )
    assert task.fx_series("USD", ["EUR", "GBP"], "2024-01-02", "2024-01-03") == [
        {"date": "2024-01-02", "currency": "EUR", "rate": 0.90},
        {"date": "2024-01-02", "currency": "GBP", "rate": 0.78},
        {"date": "2024-01-03", "currency": "EUR", "rate": 0.91},
        {"date": "2024-01-03", "currency": "GBP", "rate": 0.79},
    ]


def test_fx_series_uses_range_in_path(fake_http):
    fake_http["response"] = FakeResponse(200, {"rates": {}})
    task.fx_series("USD", ["EUR"], "2024-01-01", "2024-01-31")
    call = fake_http["calls"][0]
    assert call["url"].endswith("/2024-01-01..2024-01-31")
    assert call["params"]["symbols"] == "EUR"
    assert call["params"]["base"] == "USD"


def test_fx_series_missing_rates(fake_http):
    fake_http["response"] = FakeResponse(200, {"base": "USD"})
    assert task.fx_series("USD", ["EUR"], "a", "b") == []


def test_fx_series_on_recorded_response(load_fixture, monkeypatch):
    recorded = load_fixture("frankfurter_series")
    monkeypatch.setattr(task, "get_json", lambda *a, **k: recorded)
    rows = task.fx_series("USD", ["EUR", "GBP", "INR", "JPY"], "x", "y")
    assert len(rows) == len(recorded["rates"]) * 4
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates)


# --------------------------------------------------------------------------
# summarize_series
# --------------------------------------------------------------------------


def test_summarize_series():
    rows = [
        {"date": "d1", "currency": "EUR", "rate": 0.90},
        {"date": "d2", "currency": "EUR", "rate": 0.92},
        {"date": "d1", "currency": "GBP", "rate": 0.78},
    ]
    assert task.summarize_series(rows) == {
        "EUR": {"count": 2, "min": 0.9, "max": 0.92, "mean": 0.91},
        "GBP": {"count": 1, "min": 0.78, "max": 0.78, "mean": 0.78},
    }


def test_summarize_series_ignores_none_rates():
    rows = [
        {"date": "d1", "currency": "EUR", "rate": None},
        {"date": "d2", "currency": "EUR", "rate": 1.0},
    ]
    assert task.summarize_series(rows)["EUR"] == {
        "count": 1,
        "min": 1.0,
        "max": 1.0,
        "mean": 1.0,
    }


def test_summarize_series_all_none():
    rows = [{"date": "d1", "currency": "JPY", "rate": None}]
    assert task.summarize_series(rows) == {
        "JPY": {"count": 0, "min": None, "max": None, "mean": None}
    }


def test_summarize_series_empty():
    assert task.summarize_series([]) == {}


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_create_post():
    created = task.create_post("interview practice", "hello world")
    assert created["title"] == "interview practice"
    assert "id" in created


@pytest.mark.live
def test_live_post_json_status():
    status, body = task.post_json(f"{task.PLACEHOLDER}/posts", {"title": "x"})
    assert status == 201
    assert isinstance(body, dict)


@pytest.mark.live
def test_live_daily_weather():
    rows = task.daily_weather(52.52, 13.41, days=3)
    assert len(rows) == 3
    assert set(rows[0]) == {"date", "max_c", "min_c", "precip_mm"}
    assert isinstance(rows[0]["max_c"], (int, float))


@pytest.mark.live
def test_live_fx_series():
    # frankfurter.dev cold-starts: the first hit after an idle period can 522
    # or time out, then answers instantly. Retry once rather than fail on it.
    try:
        rows = task.fx_series("USD", ["EUR", "GBP"], "2024-01-02", "2024-01-10")
    except requests.RequestException:
        rows = task.fx_series("USD", ["EUR", "GBP"], "2024-01-02", "2024-01-10")
    assert rows
    assert {r["currency"] for r in rows} == {"EUR", "GBP"}
    summary = task.summarize_series(rows)
    assert summary["EUR"]["count"] > 0
