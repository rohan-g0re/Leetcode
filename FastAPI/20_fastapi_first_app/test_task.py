import pytest
from fastapi.testclient import TestClient

import task

client = TestClient(task.app)


# --------------------------------------------------------------------------
# health
# --------------------------------------------------------------------------


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "repos": 17}


def test_openapi_docs_exist():
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200


# --------------------------------------------------------------------------
# /repos
# --------------------------------------------------------------------------


def test_repos_default():
    body = client.get("/repos").json()
    assert body["total"] == 17
    assert body["count"] == 10
    assert body["limit"] == 10
    assert body["offset"] == 0
    assert len(body["items"]) == 10


def test_repos_sorted_by_stars_desc():
    items = client.get("/repos", params={"limit": 5}).json()["items"]
    stars = [item["stars"] for item in items]
    assert stars == sorted(stars, reverse=True)
    assert items[0]["name"] == "flask"


def test_repos_language_filter_is_case_insensitive():
    body = client.get("/repos", params={"language": "python", "limit": 100}).json()
    assert body["total"] == 13
    assert {item["language"] for item in body["items"]} == {"Python"}


def test_repos_min_stars():
    body = client.get("/repos", params={"min_stars": 10000, "limit": 100}).json()
    assert body["total"] == 3
    assert all(item["stars"] >= 10000 for item in body["items"])


def test_repos_archived_filter():
    all_repos = client.get("/repos", params={"limit": 100}).json()["total"]
    archived = client.get("/repos", params={"archived": True, "limit": 100}).json()
    active = client.get("/repos", params={"archived": False, "limit": 100}).json()
    assert archived["total"] + active["total"] == all_repos
    assert all(item["archived"] for item in archived["items"])
    assert not any(item["archived"] for item in active["items"])


def test_repos_paging():
    first = client.get("/repos", params={"limit": 5, "offset": 0}).json()
    second = client.get("/repos", params={"limit": 5, "offset": 5}).json()
    assert first["total"] == second["total"] == 17
    assert first["count"] == second["count"] == 5
    assert second["offset"] == 5
    names_first = {item["name"] for item in first["items"]}
    names_second = {item["name"] for item in second["items"]}
    assert not (names_first & names_second), "pages must not overlap"


def test_repos_offset_past_end():
    body = client.get("/repos", params={"offset": 100}).json()
    assert body["total"] == 17
    assert body["count"] == 0
    assert body["items"] == []


def test_repos_combined_filters():
    body = client.get(
        "/repos", params={"language": "Python", "min_stars": 5000, "limit": 100}
    ).json()
    assert all(item["stars"] >= 5000 for item in body["items"])
    assert all(item["language"] == "Python" for item in body["items"])


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 0},
        {"limit": 101},
        {"limit": -1},
        {"offset": -1},
        {"min_stars": -5},
        {"limit": "many"},
    ],
)
def test_repos_rejects_bad_params(params):
    assert client.get("/repos", params=params).status_code == 422


# --------------------------------------------------------------------------
# /repos/top
# --------------------------------------------------------------------------


def test_repos_top_default():
    body = client.get("/repos/top").json()
    assert isinstance(body, list)
    assert len(body) == 3
    assert body[0]["name"] == "flask"


def test_repos_top_n():
    body = client.get("/repos/top", params={"n": 5}).json()
    assert len(body) == 5
    stars = [item["stars"] for item in body]
    assert stars == sorted(stars, reverse=True)


def test_repos_top_is_not_shadowed_by_name_route():
    response = client.get("/repos/top")
    assert response.status_code == 200
    assert isinstance(response.json(), list), (
        "/repos/top must be declared before /repos/{name}"
    )


@pytest.mark.parametrize("n", [0, 21, -1])
def test_repos_top_rejects_bad_n(n):
    assert client.get("/repos/top", params={"n": n}).status_code == 422


# --------------------------------------------------------------------------
# /repos/{name}
# --------------------------------------------------------------------------


def test_repo_by_name():
    body = client.get("/repos/flask").json()
    assert body["name"] == "flask"
    assert body["stars"] == 72117
    assert body["language"] == "Python"


def test_repo_by_name_case_insensitive():
    assert client.get("/repos/FLASK").json()["name"] == "flask"


def test_repo_by_name_404():
    response = client.get("/repos/does-not-exist")
    assert response.status_code == 404
    assert "does-not-exist" in response.json()["detail"]


# --------------------------------------------------------------------------
# /languages
# --------------------------------------------------------------------------


def test_languages():
    body = client.get("/languages").json()
    assert isinstance(body, list)
    assert len(body) == 4
    assert body[0] == {"language": "Python", "repos": 13, "total_stars": 117467}
    assert [entry["language"] for entry in body] == ["Python", "HTML", "unknown", "CSS"]


def test_languages_totals():
    body = client.get("/languages").json()
    assert sum(entry["repos"] for entry in body) == 17
    assert sum(entry["total_stars"] for entry in body) == 117631


# --------------------------------------------------------------------------
# /stats
# --------------------------------------------------------------------------


def test_stats():
    body = client.get("/stats").json()
    assert body["repos"] == 17
    assert body["total_stars"] == 117631
    assert body["mean_stars"] == pytest.approx(6919.47, abs=0.01)
    assert body["archived"] == 6
    assert body["licensed"] == 14
    assert body["languages"] == 3


def test_stats_median():
    body = client.get("/stats").json()
    # mean 6919 vs median 167: heavily right-skewed, because flask alone is
    # 61% of all the stars. Worth saying out loud when you report a mean.
    assert body["median_stars"] == 167


# --------------------------------------------------------------------------
# /search
# --------------------------------------------------------------------------


def test_search():
    body = client.get("/search", params={"q": "fla"}).json()
    assert body["q"] == "fla"
    assert body["count"] >= 1
    assert all("fla" in item["name"].lower() for item in body["items"])


def test_search_is_case_insensitive():
    assert client.get("/search", params={"q": "FLASK"}).json()["count"] >= 1


def test_search_no_matches():
    body = client.get("/search", params={"q": "zzzzz"}).json()
    assert body["count"] == 0
    assert body["items"] == []


@pytest.mark.parametrize("params", [{}, {"q": "a"}, {"q": "x" * 51}])
def test_search_validates_q(params):
    assert client.get("/search", params=params).status_code == 422
