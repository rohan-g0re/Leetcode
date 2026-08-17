import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

import task

client = TestClient(task.app)


def make_response(status_code, json_body, url="https://fake/"):
    request = httpx.Request("GET", url)
    return httpx.Response(status_code, json=json_body, request=request)


class FakeClient:
    def __init__(self, routes):
        self.routes = routes
        self.calls = []

    async def get(self, url, params=None, **kwargs):
        self.calls.append({"url": url, "params": params})
        for prefix, item in self.routes.items():
            if url.startswith(prefix):
                if isinstance(item, Exception):
                    raise item
                return item
        return make_response(404, {"message": "Not Found"}, url)

    async def aclose(self):
        pass


@pytest.fixture
def upstream(monkeypatch):
    """Install a fake client via dependency_overrides, and clear auth."""
    monkeypatch.delenv(task.API_KEY_ENV, raising=False)

    def install(routes):
        fake = FakeClient(routes)

        async def override():
            yield fake

        task.app.dependency_overrides[task.get_client] = override
        return fake

    yield install
    task.app.dependency_overrides.clear()


USER = {"login": "torvalds", "name": "Linus", "followers": 200000, "public_repos": 8}

REPOS = [
    {"name": "b", "stargazers_count": 5, "language": "Python", "archived": False},
    {"name": "a", "stargazers_count": 5, "language": None, "archived": True},
    {"name": "c", "stargazers_count": 100, "language": "Go", "archived": False},
]


# --------------------------------------------------------------------------
# UpstreamError + handler
# --------------------------------------------------------------------------


def test_upstream_error_carries_kind_and_context():
    exc = task.UpstreamError("not_found", context="ghost")
    assert exc.kind == "not_found"
    assert exc.context == "ghost"


@pytest.mark.parametrize(
    "kind,status",
    [
        ("not_found", 404),
        ("rate_limited", 429),
        ("timeout", 504),
        ("unavailable", 503),
        ("bad_response", 502),
        ("something_else", 502),
    ],
)
def test_exception_handler_maps_kinds(upstream, kind, status):
    upstream({})

    @task.app.get("/boom-" + kind)
    def boom():
        raise task.UpstreamError(kind, context="ctx")

    response = client.get("/boom-" + kind)
    assert response.status_code == status
    assert response.json()["kind"] == kind
    assert "detail" in response.json()


def test_exception_handler_not_found_detail(upstream):
    upstream({})

    @task.app.get("/boom-detail")
    def boom():
        raise task.UpstreamError("not_found", context="ghost")

    assert "ghost" in client.get("/boom-detail").json()["detail"]


# --------------------------------------------------------------------------
# middleware
# --------------------------------------------------------------------------


def test_timing_header_present():
    response = client.get("/health")
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0


# --------------------------------------------------------------------------
# fetch (service layer)
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,kind",
    [(404, "not_found"), (429, "rate_limited"), (500, "bad_response"), (400, "bad_response")],
)
def test_fetch_translates_statuses(status, kind):
    fake = FakeClient({task.GITHUB: make_response(status, {"message": "x"})})
    with pytest.raises(task.UpstreamError) as info:
        asyncio.run(task.fetch(fake, "/users/x", context="x"))
    assert info.value.kind == kind
    assert info.value.context == "x"


def test_fetch_translates_timeout():
    fake = FakeClient({task.GITHUB: httpx.TimeoutException("slow")})
    with pytest.raises(task.UpstreamError) as info:
        asyncio.run(task.fetch(fake, "/users/x"))
    assert info.value.kind == "timeout"


def test_fetch_translates_connection_error():
    fake = FakeClient({task.GITHUB: httpx.ConnectError("no dns")})
    with pytest.raises(task.UpstreamError) as info:
        asyncio.run(task.fetch(fake, "/users/x"))
    assert info.value.kind == "unavailable"


def test_fetch_success_and_params():
    fake = FakeClient({task.GITHUB: make_response(200, {"a": 1})})
    result = asyncio.run(task.fetch(fake, "/users/x", params={"per_page": 100}))
    assert result == {"a": 1}
    assert fake.calls[0]["url"] == f"{task.GITHUB}/users/x"
    assert fake.calls[0]["params"] == {"per_page": 100}


# --------------------------------------------------------------------------
# slim_repo
# --------------------------------------------------------------------------


def test_slim_repo():
    assert task.slim_repo(REPOS[0]) == {
        "name": "b",
        "stars": 5,
        "language": "Python",
        "archived": False,
    }


def test_slim_repo_missing_fields():
    assert task.slim_repo({"name": "x"}) == {
        "name": "x",
        "stars": 0,
        "language": None,
        "archived": False,
    }


# --------------------------------------------------------------------------
# pagination dependency
# --------------------------------------------------------------------------


def test_pagination_defaults(upstream):
    upstream({task.GITHUB: make_response(200, REPOS)})
    body = client.get("/users/x/repos").json()
    assert body["limit"] == 10
    assert body["offset"] == 0


def test_pagination_applied(upstream):
    upstream({task.GITHUB: make_response(200, REPOS)})
    body = client.get("/users/x/repos", params={"limit": 1, "offset": 1}).json()
    assert body["total"] == 3
    assert body["count"] == 1
    assert body["items"][0]["name"] == "a"


@pytest.mark.parametrize(
    "params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"limit": "x"}]
)
def test_pagination_validation(upstream, params):
    upstream({task.GITHUB: make_response(200, REPOS)})
    assert client.get("/users/x/repos", params=params).status_code == 422


# --------------------------------------------------------------------------
# auth dependency
# --------------------------------------------------------------------------


def test_auth_disabled_when_env_unset(upstream):
    upstream({task.GITHUB: make_response(200, USER)})
    assert client.get("/users/torvalds").status_code == 200
    assert client.get("/health").json()["auth_required"] is False


def test_auth_required_when_env_set(upstream, monkeypatch):
    upstream({task.GITHUB: make_response(200, USER)})
    monkeypatch.setenv(task.API_KEY_ENV, "s3cret")

    assert client.get("/users/torvalds").status_code == 401
    assert client.get("/users/torvalds", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/users/torvalds", headers={"X-API-Key": "s3cret"}).status_code == 200


def test_health_never_requires_auth(upstream, monkeypatch):
    upstream({})
    monkeypatch.setenv(task.API_KEY_ENV, "s3cret")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["auth_required"] is True


def test_auth_error_detail(upstream, monkeypatch):
    upstream({})
    monkeypatch.setenv(task.API_KEY_ENV, "s3cret")
    assert "api key" in client.get("/users/x").json()["detail"].lower()


# --------------------------------------------------------------------------
# endpoints
# --------------------------------------------------------------------------


def test_user_endpoint(upstream):
    upstream({task.GITHUB: make_response(200, USER)})
    body = client.get("/users/torvalds").json()
    assert body == {
        "login": "torvalds",
        "name": "Linus",
        "followers": 200000,
        "public_repos": 8,
    }


def test_user_endpoint_missing_numbers(upstream):
    upstream({task.GITHUB: make_response(200, {"login": "x", "name": None})})
    body = client.get("/users/x").json()
    assert body["followers"] == 0
    assert body["public_repos"] == 0


def test_user_endpoint_404(upstream):
    upstream({task.GITHUB: make_response(404, {"message": "Not Found"})})
    response = client.get("/users/ghost")
    assert response.status_code == 404
    assert "ghost" in response.json()["detail"]
    assert response.json()["kind"] == "not_found"


def test_user_endpoint_502(upstream):
    upstream({task.GITHUB: make_response(500, {"message": "boom"})})
    assert client.get("/users/x").status_code == 502


def test_user_endpoint_504(upstream):
    upstream({task.GITHUB: httpx.TimeoutException("slow")})
    assert client.get("/users/x").status_code == 504


def test_repos_endpoint(upstream):
    fake = upstream({task.GITHUB: make_response(200, REPOS)})
    body = client.get("/users/x/repos", params={"limit": 3}).json()
    assert body["username"] == "x"
    assert body["total"] == 3
    assert body["count"] == 3
    assert [item["name"] for item in body["items"]] == ["c", "a", "b"]
    assert fake.calls[0]["params"]["per_page"] == 100


def test_search_endpoint(upstream):
    envelope = {"total_count": 4321, "items": REPOS}
    upstream({task.GITHUB: make_response(200, envelope)})
    body = client.get("/search/repos", params={"q": "fastapi", "limit": 2}).json()
    assert body["q"] == "fastapi"
    assert body["total"] == 4321, "total must come from the upstream count"
    assert body["count"] == 2
    assert [item["name"] for item in body["items"]] == ["c", "a"]


def test_search_endpoint_sends_q(upstream):
    fake = upstream({task.GITHUB: make_response(200, {"total_count": 0, "items": []})})
    client.get("/search/repos", params={"q": "fastapi"})
    assert fake.calls[0]["params"]["q"] == "fastapi"
    assert fake.calls[0]["url"].endswith("/search/repositories")


@pytest.mark.parametrize("params", [{}, {"q": "a"}, {"q": "x" * 101}])
def test_search_endpoint_validates_q(upstream, params):
    upstream({task.GITHUB: make_response(200, {"total_count": 0, "items": []})})
    assert client.get("/search/repos", params=params).status_code == 422


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_user(monkeypatch):
    monkeypatch.delenv(task.API_KEY_ENV, raising=False)
    task.app.dependency_overrides.clear()
    body = client.get("/users/torvalds").json()
    assert body["login"] == "torvalds"


@pytest.mark.live
def test_live_repos(monkeypatch):
    monkeypatch.delenv(task.API_KEY_ENV, raising=False)
    task.app.dependency_overrides.clear()
    body = client.get("/users/pallets/repos", params={"limit": 3}).json()
    assert body["count"] == 3
    assert body["items"][0]["name"] == "flask"


@pytest.mark.live
def test_live_search(monkeypatch):
    monkeypatch.delenv(task.API_KEY_ENV, raising=False)
    task.app.dependency_overrides.clear()
    body = client.get("/search/repos", params={"q": "fastapi", "limit": 5}).json()
    assert body["total"] > 100
    assert body["count"] == 5
