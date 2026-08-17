import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

import service

client = TestClient(service.app)


def make_response(status_code, json_body, url="https://fake/"):
    request = httpx.Request("GET", url)
    return httpx.Response(status_code, json=json_body, request=request)


class FakeClient:
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


@pytest.fixture(autouse=True)
def clean():
    service.reset_cache()
    yield
    service.reset_cache()
    service.app.dependency_overrides.clear()


@pytest.fixture
def upstream():
    def install(routes, delay=0.0):
        fake = FakeClient(routes, delay=delay)

        async def override():
            yield fake

        service.app.dependency_overrides[service.get_client] = override
        return fake

    return install


USER = {
    "login": "pallets",
    "name": "Pallets",
    "followers": 1200,
    "public_repos": 17,
    "created_at": "2011-09-03T15:26:22Z",
    "html_url": "https://github.com/pallets",
    "email": "secret@example.com",
}

REPOS = [
    {
        "name": "flask",
        "stargazers_count": 100,
        "forks_count": 30,
        "language": "Python",
        "archived": False,
        "license": {"name": "BSD-3-Clause"},
        "pushed_at": "2024-05-01T00:00:00Z",
    },
    {
        "name": "click",
        "stargazers_count": 60,
        "forks_count": 10,
        "language": "Python",
        "archived": False,
        "license": None,
        "pushed_at": "2024-04-01T00:00:00Z",
    },
    {
        "name": "site",
        "stargazers_count": 40,
        "forks_count": 5,
        "language": None,
        "archived": True,
        "license": {"name": "MIT"},
        "pushed_at": None,
    },
]


def routes_for(username="pallets", user=USER, repos=REPOS):
    return {
        f"{service.GITHUB}/users/{username}/repos": make_response(200, repos),
        f"{service.GITHUB}/users/{username}": make_response(200, user),
    }


# --------------------------------------------------------------------------
# exception mapping
# --------------------------------------------------------------------------


def test_upstream_error_attributes():
    exc = service.UpstreamError("timeout", context="x")
    assert exc.kind == "timeout"
    assert exc.context == "x"


@pytest.mark.parametrize(
    "status,expected", [(404, 404), (429, 429), (500, 502), (403, 502)]
)
def test_fetch_maps_statuses(status, expected, upstream):
    fake = FakeClient({service.GITHUB: make_response(status, {"m": "x"})})
    with pytest.raises(service.UpstreamError):
        asyncio.run(service.fetch(fake, "/users/x", context="x"))


def test_endpoint_status_mapping(upstream):
    upstream({service.GITHUB: make_response(500, {"m": "x"})})
    assert client.get("/users/x").status_code == 502

    upstream({service.GITHUB: httpx.TimeoutException("slow")})
    assert client.get("/users/x").status_code == 504

    upstream({service.GITHUB: httpx.ConnectError("dns")})
    assert client.get("/users/x").status_code == 503

    upstream({service.GITHUB: make_response(404, {"m": "x"})})
    response = client.get("/users/ghost")
    assert response.status_code == 404
    assert "ghost" in response.json()["detail"]
    assert response.json()["kind"] == "not_found"


# --------------------------------------------------------------------------
# caching
# --------------------------------------------------------------------------


def test_cache_prevents_second_request(upstream):
    fake = upstream(routes_for())
    client.get("/users/pallets")
    client.get("/users/pallets")
    assert len(fake.calls) == 1


def test_cache_expires(upstream):
    fake = upstream(routes_for())
    client.get("/users/pallets")
    stale = time_travel = None
    for key in list(service._CACHE):
        _, payload = service._CACHE[key]
        service._CACHE[key] = (0.0, payload)
    client.get("/users/pallets")
    assert len(fake.calls) == 2


def test_failures_are_not_cached(upstream):
    upstream({service.GITHUB: make_response(404, {"m": "x"})})
    client.get("/users/ghost")
    assert service._CACHE == {}


def test_cache_endpoint(upstream):
    upstream(routes_for())
    client.get("/users/pallets")
    assert client.get("/health").json()["cached_keys"] == 1
    assert client.delete("/cache").json() == {"cleared": 1}
    assert client.get("/health").json()["cached_keys"] == 0


# --------------------------------------------------------------------------
# pure analysis
# --------------------------------------------------------------------------


def test_slim_user():
    assert service.slim_user(USER) == {
        "login": "pallets",
        "name": "Pallets",
        "followers": 1200,
        "public_repos": 17,
        "created_year": 2011,
        "profile_url": "https://github.com/pallets",
    }


def test_slim_user_sparse():
    slim = service.slim_user({"login": "x"})
    assert slim["followers"] == 0
    assert slim["created_year"] is None
    assert slim["profile_url"] is None


def test_slim_repo():
    assert service.slim_repo(REPOS[0]) == {
        "name": "flask",
        "stars": 100,
        "forks": 30,
        "language": "Python",
        "archived": False,
        "license": "BSD-3-Clause",
        "pushed": "2024-05-01T00:00:00Z",
    }


def test_slim_repo_null_license():
    assert service.slim_repo(REPOS[1])["license"] is None
    assert service.slim_repo({"name": "x"})["stars"] == 0


def test_language_breakdown():
    slimmed = [service.slim_repo(r) for r in REPOS]
    breakdown = service.language_breakdown(slimmed)
    assert breakdown[0] == {
        "language": "Python",
        "repos": 2,
        "stars": 160,
        "share": 80.0,
    }
    assert breakdown[1] == {
        "language": "unknown",
        "repos": 1,
        "stars": 40,
        "share": 20.0,
    }


def test_language_breakdown_no_stars():
    slimmed = [{"name": "a", "stars": 0, "language": "Go"}]
    assert service.language_breakdown(slimmed)[0]["share"] == 0.0


def test_language_breakdown_empty():
    assert service.language_breakdown([]) == []


def test_build_report():
    report = service.build_report(USER, REPOS, top_n=2)
    assert report["user"]["login"] == "pallets"
    assert report["repo_count"] == 3
    assert report["total_stars"] == 200
    assert report["total_forks"] == 45
    assert report["mean_stars"] == pytest.approx(66.67)
    assert report["median_stars"] == 60
    assert report["archived"] == 1
    assert report["licensed"] == 2
    assert len(report["top_repos"]) == 2
    assert report["top_repos"][0]["name"] == "flask"
    assert report["skewed"] is False


def test_build_report_detects_skew():
    repos = [
        {"name": "big", "stargazers_count": 1000},
        {"name": "a", "stargazers_count": 1},
        {"name": "b", "stargazers_count": 1},
    ]
    assert service.build_report(USER, repos)["skewed"] is True


def test_build_report_no_repos():
    report = service.build_report(USER, [])
    assert report["repo_count"] == 0
    assert report["total_stars"] == 0
    assert report["mean_stars"] is None
    assert report["median_stars"] is None
    assert report["languages"] == []
    assert report["top_repos"] == []
    json.dumps(report)


# --------------------------------------------------------------------------
# concurrency
# --------------------------------------------------------------------------


def test_get_many_users_partial_failure():
    routes = {
        f"{service.GITHUB}/users/good": make_response(200, USER),
        f"{service.GITHUB}/users/bad": make_response(404, {"m": "x"}),
    }
    fake = FakeClient(routes)
    payloads, errors = asyncio.run(service.get_many_users(fake, ["good", "bad"]))
    assert len(payloads) == 1
    assert errors[0]["username"] == "bad"


def test_get_many_users_respects_cap():
    fake = FakeClient({service.GITHUB: make_response(200, USER)}, delay=0.02)
    names = [f"u{i}" for i in range(10)]
    asyncio.run(service.get_many_users(fake, names, concurrency=3))
    assert fake.peak_in_flight <= 3


def test_report_fetches_user_and_repos_concurrently(upstream):
    fake = upstream(routes_for(), delay=0.05)
    import time as _time

    started = _time.perf_counter()
    client.get("/users/pallets/report")
    elapsed = _time.perf_counter() - started
    assert elapsed < 0.09, f"took {elapsed:.3f}s -- the two fetches must overlap"


# --------------------------------------------------------------------------
# endpoints
# --------------------------------------------------------------------------


def test_health():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["cached_keys"] == 0


def test_user_endpoint_filters_fields(upstream):
    upstream(routes_for())
    body = client.get("/users/pallets").json()
    assert body["login"] == "pallets"
    assert body["created_year"] == 2011
    assert "email" not in body, "response_model must not leak undeclared fields"


def test_repos_endpoint(upstream):
    upstream(routes_for())
    body = client.get("/users/pallets/repos", params={"limit": 2}).json()
    assert body["username"] == "pallets"
    assert body["total"] == 3
    assert body["count"] == 2
    assert [item["name"] for item in body["items"]] == ["flask", "click"]


def test_repos_endpoint_filters(upstream):
    upstream(routes_for())
    body = client.get(
        "/users/pallets/repos", params={"language": "python", "limit": 100}
    ).json()
    assert body["total"] == 2

    body = client.get(
        "/users/pallets/repos", params={"min_stars": 50, "limit": 100}
    ).json()
    assert body["total"] == 2


def test_repos_endpoint_paging(upstream):
    upstream(routes_for())
    body = client.get("/users/pallets/repos", params={"limit": 1, "offset": 2}).json()
    assert body["count"] == 1
    assert body["items"][0]["name"] == "site"


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"min_stars": -1}])
def test_repos_endpoint_validation(upstream, params):
    upstream(routes_for())
    assert client.get("/users/pallets/repos", params=params).status_code == 422


def test_report_endpoint(upstream):
    upstream(routes_for())
    body = client.get("/users/pallets/report", params={"top": 2}).json()
    assert body["user"]["login"] == "pallets"
    assert body["repo_count"] == 3
    assert body["total_stars"] == 200
    assert body["languages"][0]["language"] == "Python"
    assert len(body["top_repos"]) == 2


def test_report_endpoint_404(upstream):
    upstream({service.GITHUB: make_response(404, {"m": "x"})})
    assert client.get("/users/ghost/report").status_code == 404


@pytest.mark.parametrize("top", [0, 21])
def test_report_endpoint_validates_top(upstream, top):
    upstream(routes_for())
    assert client.get("/users/pallets/report", params={"top": top}).status_code == 422


def test_compare_endpoint(upstream):
    routes = {
        f"{service.GITHUB}/users/a": make_response(
            200, {"login": "a", "followers": 10, "public_repos": 1}
        ),
        f"{service.GITHUB}/users/b": make_response(
            200, {"login": "b", "followers": 90, "public_repos": 2}
        ),
    }
    upstream(routes)
    body = client.get("/compare", params={"users": "a,b"}).json()
    assert body["requested"] == 2
    assert body["found"] == 2
    assert body["failed"] == []
    assert [u["login"] for u in body["users"]] == ["b", "a"]
    assert [u["rank"] for u in body["users"]] == [1, 2]
    assert body["total_followers"] == 100


def test_compare_endpoint_partial(upstream):
    routes = {
        f"{service.GITHUB}/users/a": make_response(
            200, {"login": "a", "followers": 10, "public_repos": 1}
        ),
        f"{service.GITHUB}/users/ghost": make_response(404, {"m": "x"}),
    }
    upstream(routes)
    body = client.get("/compare", params={"users": "a,ghost"}).json()
    assert body["found"] == 1
    assert body["failed"][0]["username"] == "ghost"


def test_compare_endpoint_limits(upstream):
    upstream(routes_for())
    names = ",".join(f"u{i}" for i in range(11))
    response = client.get("/compare", params={"users": names})
    assert response.status_code == 400
    assert "10" in response.json()["detail"]
    assert client.get("/compare", params={"users": " , "}).status_code == 400


# --------------------------------------------------------------------------
# docs
# --------------------------------------------------------------------------


def test_openapi_declares_models():
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    for name in ("UserOut", "RepoOut", "RepoPage", "UserReport", "CompareOut"):
        assert name in schemas
    assert "email" not in schemas["UserOut"]["properties"]


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_report():
    service.app.dependency_overrides.clear()
    body = client.get("/users/pallets/report").json()
    assert body["user"]["login"] == "pallets"
    assert body["repo_count"] > 0
    assert body["total_stars"] > 1000
    assert body["languages"][0]["language"] == "Python"


@pytest.mark.live
def test_live_repos():
    service.app.dependency_overrides.clear()
    body = client.get("/users/pallets/repos", params={"limit": 3}).json()
    assert body["count"] == 3
    assert body["items"][0]["name"] == "flask"


@pytest.mark.live
def test_live_compare():
    service.app.dependency_overrides.clear()
    body = client.get("/compare", params={"users": "pallets,torvalds"}).json()
    assert body["found"] == 2
    assert body["users"][0]["rank"] == 1
