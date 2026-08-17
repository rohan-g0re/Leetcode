import asyncio
import time

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import task

client = TestClient(task.app)


@pytest.fixture(autouse=True)
def clean_cache():
    task.reset_cache()
    yield
    task.reset_cache()


# --------------------------------------------------------------------------
# fake upstream
# --------------------------------------------------------------------------


def make_response(status_code, json_body, url="https://fake/"):
    request = httpx.Request("GET", url)
    return httpx.Response(status_code, json=json_body, request=request)


class FakeClient:
    """Stands in for httpx.AsyncClient. Records calls, tracks concurrency."""

    def __init__(self, routes, delay=0.0):
        self.routes = routes
        self.delay = delay
        self.calls = []
        self.in_flight = 0
        self.peak_in_flight = 0

    async def get(self, url, params=None, **kwargs):
        self.calls.append({"url": url, "params": params})
        self.in_flight += 1
        self.peak_in_flight = max(self.peak_in_flight, self.in_flight)
        try:
            if self.delay:
                await asyncio.sleep(self.delay)
            for prefix, item in self.routes.items():
                if url.startswith(prefix):
                    if isinstance(item, Exception):
                        raise item
                    return item
            return make_response(404, {"message": "Not Found"}, url)
        finally:
            self.in_flight -= 1

    async def aclose(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


@pytest.fixture
def fake_upstream(monkeypatch):
    holder = {"client": FakeClient({})}

    def install(routes, delay=0.0):
        holder["client"] = FakeClient(routes, delay=delay)
        monkeypatch.setattr(task, "get_client", lambda: holder["client"])
        return holder["client"]

    return install


USER_PAYLOAD = {
    "login": "torvalds",
    "name": "Linus Torvalds",
    "followers": 200000,
    "public_repos": 8,
    "created_at": "2011-09-03T15:26:22Z",
}


# --------------------------------------------------------------------------
# fetch_json
# --------------------------------------------------------------------------


def test_fetch_json_ok():
    fake = FakeClient({"https://x": make_response(200, {"a": 1})})
    assert asyncio.run(task.fetch_json(fake, "https://x/y")) == {"a": 1}


def test_fetch_json_raises_on_status():
    fake = FakeClient({"https://x": make_response(500, {"m": "boom"})})
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(task.fetch_json(fake, "https://x/y"))


def test_fetch_json_passes_params():
    fake = FakeClient({"https://x": make_response(200, [])})
    asyncio.run(task.fetch_json(fake, "https://x/y", params={"per_page": 100}))
    assert fake.calls[0]["params"] == {"per_page": 100}


# --------------------------------------------------------------------------
# upstream_error
# --------------------------------------------------------------------------


def status_error(code):
    response = make_response(code, {"message": "x"})
    return httpx.HTTPStatusError("boom", request=response.request, response=response)


@pytest.mark.parametrize(
    "code,expected_status",
    [(404, 404), (429, 429), (400, 502), (403, 502), (500, 502), (503, 502)],
)
def test_upstream_error_status_mapping(code, expected_status):
    result = task.upstream_error(status_error(code), context="torvalds")
    assert isinstance(result, HTTPException)
    assert result.status_code == expected_status


def test_upstream_error_404_detail():
    result = task.upstream_error(status_error(404), context="ghost")
    assert "ghost" in result.detail


def test_upstream_error_429_detail():
    assert "rate limited" in task.upstream_error(status_error(429)).detail


def test_upstream_error_timeout():
    result = task.upstream_error(httpx.TimeoutException("slow"))
    assert result.status_code == 504
    assert "timeout" in result.detail


def test_upstream_error_connection():
    result = task.upstream_error(httpx.ConnectError("no dns"))
    assert result.status_code == 502
    assert "unreachable" in result.detail


# --------------------------------------------------------------------------
# get_user + cache
# --------------------------------------------------------------------------


def test_get_user_fetches_and_caches():
    fake = FakeClient({task.GITHUB: make_response(200, USER_PAYLOAD)})
    first = asyncio.run(task.get_user(fake, "torvalds"))
    second = asyncio.run(task.get_user(fake, "torvalds"))
    assert first == second == USER_PAYLOAD
    assert len(fake.calls) == 1, "second call must be served from the cache"


def test_get_user_cache_expires(monkeypatch):
    fake = FakeClient({task.GITHUB: make_response(200, USER_PAYLOAD)})
    asyncio.run(task.get_user(fake, "torvalds"))
    stale = time.time() - task.CACHE_TTL_SECONDS - 1
    task._CACHE["torvalds"] = (stale, USER_PAYLOAD)
    asyncio.run(task.get_user(fake, "torvalds"))
    assert len(fake.calls) == 2


def test_get_user_does_not_cache_failures():
    fake = FakeClient({task.GITHUB: make_response(404, {"message": "Not Found"})})
    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(task.get_user(fake, "ghost"))
    assert "ghost" not in task._CACHE


def test_get_user_builds_the_right_url():
    fake = FakeClient({task.GITHUB: make_response(200, USER_PAYLOAD)})
    asyncio.run(task.get_user(fake, "torvalds"))
    assert fake.calls[0]["url"] == f"{task.GITHUB}/users/torvalds"


# --------------------------------------------------------------------------
# summarize_user
# --------------------------------------------------------------------------


def test_summarize_user():
    assert task.summarize_user(USER_PAYLOAD) == {
        "login": "torvalds",
        "name": "Linus Torvalds",
        "followers": 200000,
        "public_repos": 8,
        "created_year": 2011,
    }


def test_summarize_user_sparse():
    assert task.summarize_user({"login": "x"}) == {
        "login": "x",
        "name": None,
        "followers": 0,
        "public_repos": 0,
        "created_year": None,
    }


# --------------------------------------------------------------------------
# get_many_users
# --------------------------------------------------------------------------


def test_get_many_users_success():
    fake = FakeClient({task.GITHUB: make_response(200, USER_PAYLOAD)})
    results, errors = asyncio.run(task.get_many_users(fake, ["a", "b", "c"]))
    assert len(results) == 3
    assert errors == []
    assert all(r["login"] == "torvalds" for r in results)


def test_get_many_users_partial_failure():
    routes = {
        f"{task.GITHUB}/users/good": make_response(200, USER_PAYLOAD),
        f"{task.GITHUB}/users/bad": make_response(404, {"message": "Not Found"}),
    }
    fake = FakeClient(routes)
    results, errors = asyncio.run(task.get_many_users(fake, ["good", "bad"]))
    assert len(results) == 1, "one failure must not discard the successes"
    assert len(errors) == 1
    assert errors[0]["username"] == "bad"
    assert "HTTPStatusError" in errors[0]["error"]


def test_get_many_users_is_concurrent():
    fake = FakeClient({task.GITHUB: make_response(200, USER_PAYLOAD)}, delay=0.05)
    names = [f"u{i}" for i in range(8)]
    started = time.perf_counter()
    results, _ = asyncio.run(task.get_many_users(fake, names, concurrency=8))
    elapsed = time.perf_counter() - started
    assert len(results) == 8
    assert elapsed < 0.25, f"took {elapsed:.2f}s -- requests must overlap, not run in series"


def test_get_many_users_respects_concurrency_cap():
    fake = FakeClient({task.GITHUB: make_response(200, USER_PAYLOAD)}, delay=0.02)
    names = [f"u{i}" for i in range(10)]
    asyncio.run(task.get_many_users(fake, names, concurrency=3))
    assert fake.peak_in_flight <= 3, f"peak was {fake.peak_in_flight}"


def test_get_many_users_preserves_order():
    routes = {
        f"{task.GITHUB}/users/{name}": make_response(200, {"login": name})
        for name in ("a", "b", "c")
    }
    fake = FakeClient(routes)
    results, _ = asyncio.run(task.get_many_users(fake, ["c", "a", "b"]))
    assert [r["login"] for r in results] == ["c", "a", "b"]


# --------------------------------------------------------------------------
# endpoints
# --------------------------------------------------------------------------


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["cached_users"] == 0


def test_user_endpoint(fake_upstream):
    fake_upstream({task.GITHUB: make_response(200, USER_PAYLOAD)})
    body = client.get("/users/torvalds").json()
    assert body["login"] == "torvalds"
    assert body["created_year"] == 2011
    assert "avatar_url" not in body


def test_user_endpoint_404(fake_upstream):
    fake_upstream({task.GITHUB: make_response(404, {"message": "Not Found"})})
    response = client.get("/users/ghost")
    assert response.status_code == 404
    assert "ghost" in response.json()["detail"]


def test_user_endpoint_upstream_500_becomes_502(fake_upstream):
    fake_upstream({task.GITHUB: make_response(500, {"message": "boom"})})
    assert client.get("/users/x").status_code == 502


def test_user_endpoint_timeout_becomes_504(fake_upstream):
    fake_upstream({task.GITHUB: httpx.TimeoutException("slow")})
    assert client.get("/users/x").status_code == 504


REPOS = [
    {"name": "b", "stargazers_count": 5, "language": "Python", "archived": False},
    {"name": "a", "stargazers_count": 5, "language": None, "archived": True},
    {"name": "c", "stargazers_count": 100, "language": "Go", "archived": False},
]


def test_repos_endpoint(fake_upstream):
    fake_upstream({task.GITHUB: make_response(200, REPOS)})
    body = client.get("/users/x/repos", params={"limit": 2}).json()
    assert body["username"] == "x"
    assert body["count"] == 2
    assert [item["name"] for item in body["items"]] == ["c", "a"]
    assert body["items"][0] == {
        "name": "c",
        "stars": 100,
        "language": "Go",
        "archived": False,
    }


def test_repos_endpoint_sort_by_name(fake_upstream):
    fake_upstream({task.GITHUB: make_response(200, REPOS)})
    body = client.get("/users/x/repos", params={"sort": "name", "limit": 3}).json()
    assert [item["name"] for item in body["items"]] == ["a", "b", "c"]


def test_repos_endpoint_sends_per_page(fake_upstream):
    fake = fake_upstream({task.GITHUB: make_response(200, REPOS)})
    client.get("/users/x/repos")
    assert fake.calls[0]["params"]["per_page"] == 100


@pytest.mark.parametrize(
    "params", [{"limit": 0}, {"limit": 101}, {"sort": "followers"}]
)
def test_repos_endpoint_validation(fake_upstream, params):
    fake_upstream({task.GITHUB: make_response(200, REPOS)})
    assert client.get("/users/x/repos", params=params).status_code == 422


def test_compare_endpoint(fake_upstream):
    routes = {
        f"{task.GITHUB}/users/a": make_response(200, {"login": "a", "followers": 10}),
        f"{task.GITHUB}/users/b": make_response(200, {"login": "b", "followers": 90}),
    }
    fake_upstream(routes)
    body = client.get("/compare", params={"users": "a,b"}).json()
    assert body["requested"] == 2
    assert body["found"] == 2
    assert body["failed"] == []
    assert [u["login"] for u in body["users"]] == ["b", "a"]
    assert body["total_followers"] == 100


def test_compare_endpoint_partial_failure(fake_upstream):
    routes = {
        f"{task.GITHUB}/users/a": make_response(200, {"login": "a", "followers": 10}),
        f"{task.GITHUB}/users/ghost": make_response(404, {"message": "Not Found"}),
    }
    fake_upstream(routes)
    body = client.get("/compare", params={"users": "a,ghost"}).json()
    assert body["requested"] == 2
    assert body["found"] == 1
    assert body["failed"][0]["username"] == "ghost"
    assert body["total_followers"] == 10


def test_compare_endpoint_drops_empty_names(fake_upstream):
    fake_upstream({task.GITHUB: make_response(200, {"login": "a", "followers": 1})})
    body = client.get("/compare", params={"users": "a,,  ,"}).json()
    assert body["requested"] == 1


def test_compare_endpoint_too_many(fake_upstream):
    fake_upstream({task.GITHUB: make_response(200, USER_PAYLOAD)})
    names = ",".join(f"u{i}" for i in range(11))
    response = client.get("/compare", params={"users": names})
    assert response.status_code == 400
    assert "10" in response.json()["detail"]


def test_compare_endpoint_empty(fake_upstream):
    fake_upstream({})
    assert client.get("/compare", params={"users": " , "}).status_code == 400


def test_compare_endpoint_requires_users():
    assert client.get("/compare").status_code == 422


def test_cache_endpoint(fake_upstream):
    fake_upstream({task.GITHUB: make_response(200, USER_PAYLOAD)})
    client.get("/users/torvalds")
    assert client.get("/health").json()["cached_users"] == 1
    assert client.delete("/cache").json() == {"cleared": 1}
    assert client.get("/health").json()["cached_users"] == 0


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_user_endpoint():
    body = client.get("/users/torvalds").json()
    assert body["login"] == "torvalds"
    assert body["public_repos"] > 0


@pytest.mark.live
def test_live_user_404():
    assert client.get("/users/this-user-should-not-exist-9c3f1a2b").status_code == 404


@pytest.mark.live
def test_live_repos_endpoint():
    body = client.get("/users/pallets/repos", params={"limit": 3}).json()
    assert body["count"] == 3
    assert body["items"][0]["name"] == "flask"


@pytest.mark.live
def test_live_compare():
    body = client.get("/compare", params={"users": "pallets,torvalds"}).json()
    assert body["found"] == 2
    assert body["total_followers"] > 0
