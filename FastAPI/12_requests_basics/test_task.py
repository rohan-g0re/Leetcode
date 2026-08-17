import json

import pytest
import requests

import task


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code=200, json_body=None, text=None, content_type="application/json"):
        self.status_code = status_code
        self._json_body = json_body
        self.text = text if text is not None else json.dumps(json_body)
        self.headers = {"Content-Type": content_type} if content_type else {}
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
def fake_get(monkeypatch):
    """Patch task's requests.get with a routing table you fill in per test."""
    routes = {}
    calls = []

    def _get(url, params=None, headers=None, timeout=None, **kwargs):
        calls.append({"url": url, "params": params, "headers": headers, "timeout": timeout})
        for prefix, response in routes.items():
            if url.startswith(prefix):
                if isinstance(response, Exception):
                    raise response
                return response
        return FakeResponse(404, {"message": "Not Found"})

    monkeypatch.setattr(task.requests, "get", _get)
    return {"routes": routes, "calls": calls}


# --------------------------------------------------------------------------
# fetch_json
# --------------------------------------------------------------------------


def test_fetch_json_returns_parsed_body(fake_get):
    fake_get["routes"]["https://x.com"] = FakeResponse(200, {"a": 1})
    assert task.fetch_json("https://x.com/thing") == {"a": 1}


def test_fetch_json_passes_params_headers_timeout(fake_get):
    fake_get["routes"]["https://x.com"] = FakeResponse(200, [])
    task.fetch_json("https://x.com/thing", params={"q": "py"})
    call = fake_get["calls"][0]
    assert call["params"] == {"q": "py"}, "params must go through requests, not the url"
    assert call["timeout"], "you must pass a timeout"
    assert call["headers"], "you must send headers"


def test_fetch_json_raises_on_error_status(fake_get):
    fake_get["routes"]["https://x.com"] = FakeResponse(500, {"message": "boom"})
    with pytest.raises(requests.HTTPError):
        task.fetch_json("https://x.com/thing")


# --------------------------------------------------------------------------
# safe_fetch
# --------------------------------------------------------------------------


def test_safe_fetch_success(fake_get):
    fake_get["routes"]["https://x.com"] = FakeResponse(200, {"a": 1})
    assert task.safe_fetch("https://x.com/a") == ({"a": 1}, None)


def test_safe_fetch_http_error(fake_get):
    fake_get["routes"]["https://x.com"] = FakeResponse(404, {"message": "nope"})
    data, error = task.safe_fetch("https://x.com/a")
    assert data is None
    assert error.startswith("HTTPError")


def test_safe_fetch_connection_error(fake_get):
    fake_get["routes"]["https://x.com"] = requests.ConnectionError("dns failed")
    data, error = task.safe_fetch("https://x.com/a")
    assert data is None
    assert error.startswith("ConnectionError")


def test_safe_fetch_bad_json(fake_get):
    fake_get["routes"]["https://x.com"] = FakeResponse(200, None, text="<html>oops</html>")
    data, error = task.safe_fetch("https://x.com/a")
    assert data is None
    assert error.startswith("JSONDecodeError")


# --------------------------------------------------------------------------
# describe_response
# --------------------------------------------------------------------------


def test_describe_response_list_of_dicts():
    response = FakeResponse(200, [{"b": 1, "a": 2}, {"a": 3}])
    assert task.describe_response(response) == {
        "status": 200,
        "ok": True,
        "content_type": "application/json",
        "is_json": True,
        "shape": "list",
        "size": 2,
        "keys": ["a", "b"],
    }


def test_describe_response_dict():
    described = task.describe_response(FakeResponse(200, {"z": 1, "a": 2}))
    assert described["shape"] == "dict"
    assert described["size"] == 2
    assert described["keys"] == ["a", "z"]


def test_describe_response_html_error_page():
    response = FakeResponse(500, None, text="<html>500</html>", content_type="text/html")
    described = task.describe_response(response)
    assert described["ok"] is False
    assert described["is_json"] is False
    assert described["shape"] == "invalid"
    assert described["size"] == 0
    assert described["keys"] == []
    assert described["content_type"] == "text/html"


def test_describe_response_missing_content_type():
    response = FakeResponse(200, [1, 2, 3], content_type=None)
    described = task.describe_response(response)
    assert described["content_type"] == ""
    assert described["shape"] == "list"
    assert described["keys"] == [], "a list of non-dicts has no keys"


def test_describe_response_scalar_json():
    described = task.describe_response(FakeResponse(200, 42))
    assert described["shape"] == "other"
    assert described["size"] == 0


# --------------------------------------------------------------------------
# get_user / get_repos
# --------------------------------------------------------------------------


def test_get_user_found(fake_get):
    fake_get["routes"][task.BASE] = FakeResponse(200, {"login": "x"})
    assert task.get_user("x") == {"login": "x"}


def test_get_user_missing_returns_none(fake_get):
    fake_get["routes"][task.BASE] = FakeResponse(404, {"message": "Not Found"})
    assert task.get_user("nope") is None


def test_get_user_other_error_raises(fake_get):
    fake_get["routes"][task.BASE] = FakeResponse(500, {"message": "boom"})
    with pytest.raises(requests.HTTPError):
        task.get_user("x")


def test_get_user_builds_right_url(fake_get):
    fake_get["routes"][task.BASE] = FakeResponse(200, {})
    task.get_user("torvalds")
    assert fake_get["calls"][0]["url"] == f"{task.BASE}/users/torvalds"


def test_get_repos_sends_params(fake_get):
    fake_get["routes"][task.BASE] = FakeResponse(200, [{"name": "a"}])
    assert task.get_repos("x", per_page=50) == [{"name": "a"}]
    call = fake_get["calls"][0]
    assert call["url"] == f"{task.BASE}/users/x/repos"
    assert call["params"]["per_page"] == 50
    assert call["params"]["sort"] == "updated"


# --------------------------------------------------------------------------
# pure logic
# --------------------------------------------------------------------------


def test_summarize_user_full():
    user = {
        "login": "torvalds",
        "name": "Linus Torvalds",
        "public_repos": 8,
        "followers": 200000,
        "created_at": "2011-09-03T15:26:22Z",
        "blog": "https://example.com",
    }
    assert task.summarize_user(user) == {
        "login": "torvalds",
        "name": "Linus Torvalds",
        "public_repos": 8,
        "followers": 200000,
        "created_year": 2011,
        "has_blog": True,
    }


def test_summarize_user_nulls_everywhere():
    user = {"login": "x", "name": None, "public_repos": None, "blog": ""}
    assert task.summarize_user(user) == {
        "login": "x",
        "name": "unknown",
        "public_repos": 0,
        "followers": 0,
        "created_year": None,
        "has_blog": False,
    }


def test_summarize_user_empty_dict():
    summary = task.summarize_user({})
    assert summary["login"] is None
    assert summary["name"] == "unknown"
    assert summary["created_year"] is None


def test_top_repos():
    repos = [
        {"name": "b", "stargazers_count": 5},
        {"name": "a", "stargazers_count": 5},
        {"name": "c", "stargazers_count": 100},
        {"name": "d"},
    ]
    assert task.top_repos(repos, 3) == [("c", 100), ("a", 5), ("b", 5)]
    assert task.top_repos(repos, 1) == [("c", 100)]
    assert task.top_repos([], 3) == []
    assert task.top_repos(repos, 10)[-1] == ("d", 0)


def test_top_repos_on_real_fixture(load_fixture):
    repos = load_fixture("github_repos_pallets")
    top = task.top_repos(repos, 3)
    assert top[0][0] == "flask"
    assert top[0][1] == 72117
    assert len(top) == 3


# --------------------------------------------------------------------------
# user_report
# --------------------------------------------------------------------------


def test_user_report_success(fake_get):
    fake_get["routes"][f"{task.BASE}/users/x/repos"] = FakeResponse(
        200, [{"name": "r", "stargazers_count": 3}]
    )
    fake_get["routes"][f"{task.BASE}/users/x"] = FakeResponse(
        200, {"login": "x", "name": "X", "public_repos": 1, "followers": 2}
    )
    report = task.user_report("x")
    assert report["error"] is None
    assert report["user"]["login"] == "x"
    assert report["repos"] == [("r", 3)]


def test_user_report_unknown_user(fake_get):
    fake_get["routes"][task.BASE] = FakeResponse(404, {"message": "Not Found"})
    assert task.user_report("nope") == {
        "user": None,
        "repos": [],
        "error": "user not found",
    }


def test_user_report_repos_fail_but_user_survives(fake_get):
    fake_get["routes"][f"{task.BASE}/users/x/repos"] = requests.Timeout("too slow")
    fake_get["routes"][f"{task.BASE}/users/x"] = FakeResponse(200, {"login": "x"})
    report = task.user_report("x")
    assert report["user"]["login"] == "x"
    assert report["repos"] == []
    assert report["error"].startswith("Timeout")


# --------------------------------------------------------------------------
# live tests -- real network. python -m pytest -m live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_get_user():
    user = task.get_user("torvalds")
    assert user is not None
    assert user["login"] == "torvalds"
    assert isinstance(user["public_repos"], int)


@pytest.mark.live
def test_live_unknown_user_returns_none():
    assert task.get_user("this-user-should-not-exist-9c3f1a2b") is None


@pytest.mark.live
def test_live_get_repos():
    repos = task.get_repos("pallets", per_page=5)
    assert isinstance(repos, list)
    assert 0 < len(repos) <= 5
    assert "stargazers_count" in repos[0]


@pytest.mark.live
def test_live_describe_response():
    response = requests.get(
        f"{task.BASE}/users/pallets", headers=task.HEADERS, timeout=task.TIMEOUT
    )
    described = task.describe_response(response)
    assert described["status"] == 200
    assert described["is_json"] is True
    assert described["shape"] == "dict"
    assert "login" in described["keys"]


@pytest.mark.live
def test_live_user_report():
    report = task.user_report("pallets")
    assert report["error"] is None
    assert report["user"]["login"] == "pallets"
    assert len(report["repos"]) == 5
