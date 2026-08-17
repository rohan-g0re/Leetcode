import pytest
from fastapi.testclient import TestClient

import task

client = TestClient(task.app)


@pytest.fixture(autouse=True)
def clean_store():
    task.reset_store()
    yield
    task.reset_store()


def create(**overrides):
    payload = {"name": "flask", "owner": "pallets", "stars": 72117, "language": "Python"}
    payload.update(overrides)
    return client.post("/watch", json=payload)


# --------------------------------------------------------------------------
# models
# --------------------------------------------------------------------------


def test_watch_in_defaults():
    item = task.WatchIn(name="flask", owner="pallets")
    assert item.stars == 0
    assert item.language is None
    assert item.tags == []
    assert item.notes is None


def test_watch_in_coerces_numeric_strings():
    assert task.WatchIn(name="a", owner="b", stars="42").stars == 42


def test_watch_in_lowercases_name():
    assert task.WatchIn(name="FlAsK", owner="pallets").name == "flask"


def test_watch_in_rejects_spaces_in_name():
    with pytest.raises(Exception) as info:
        task.WatchIn(name="two words", owner="pallets")
    assert "spaces" in str(info.value)


def test_watch_in_normalizes_tags():
    item = task.WatchIn(name="a", owner="b", tags=["  Web ", "web", "API", "", "  "])
    assert item.tags == ["api", "web"]


def test_watch_in_tags_default_not_shared():
    a = task.WatchIn(name="a", owner="b")
    b = task.WatchIn(name="c", owner="d")
    a.tags.append("x")
    assert b.tags == []


def test_watch_in_rejects_negative_stars():
    with pytest.raises(Exception):
        task.WatchIn(name="a", owner="b", stars=-1)


# --------------------------------------------------------------------------
# POST /watch
# --------------------------------------------------------------------------


def test_create_returns_201_and_shape():
    response = create()
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "flask"
    assert body["owner"] == "pallets"
    assert body["stars"] == 72117
    assert body["full_name"] == "pallets/flask"
    assert set(body) == {
        "id",
        "name",
        "owner",
        "stars",
        "language",
        "tags",
        "full_name",
    }


def test_create_never_leaks_notes():
    body = create(notes="private thought").json()
    assert "notes" not in body
    assert "private thought" not in str(body)


def test_create_stores_notes_internally():
    create(notes="private thought")
    assert task._STORE[1]["notes"] == "private thought"


def test_create_assigns_increasing_ids():
    assert create().json()["id"] == 1
    assert create(name="click").json()["id"] == 2


def test_create_conflict():
    create()
    response = create(name="FLASK")
    assert response.status_code == 409
    assert "pallets/flask" in response.json()["detail"]


@pytest.mark.parametrize(
    "payload",
    [
        {"owner": "pallets"},
        {"name": "flask"},
        {"name": "", "owner": "p"},
        {"name": "flask", "owner": "p", "stars": -1},
        {"name": "two words", "owner": "p"},
        {"name": "flask", "owner": "p", "notes": "x" * 501},
    ],
)
def test_create_validation_errors(payload):
    assert client.post("/watch", json=payload).status_code == 422


def test_create_validation_error_names_the_field():
    detail = client.post("/watch", json={"owner": "pallets"}).json()["detail"]
    assert any("name" in entry["loc"] for entry in detail)


# --------------------------------------------------------------------------
# GET /watch
# --------------------------------------------------------------------------


def test_list_empty():
    assert client.get("/watch").json() == []


def test_list_sorted_by_stars():
    create(name="a", stars=10)
    create(name="b", stars=90)
    create(name="c", stars=50)
    names = [item["name"] for item in client.get("/watch").json()]
    assert names == ["b", "c", "a"]


def test_list_language_filter():
    create(name="a", language="Python")
    create(name="b", language="Go")
    body = client.get("/watch", params={"language": "python"}).json()
    assert len(body) == 1
    assert body[0]["name"] == "a"


def test_list_min_stars():
    create(name="a", stars=10)
    create(name="b", stars=1000)
    body = client.get("/watch", params={"min_stars": 100}).json()
    assert [item["name"] for item in body] == ["b"]


def test_list_limit():
    for i in range(5):
        create(name=f"r{i}", stars=i)
    assert len(client.get("/watch", params={"limit": 2}).json()) == 2


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 201}, {"min_stars": -1}])
def test_list_rejects_bad_params(params):
    assert client.get("/watch", params=params).status_code == 422


def test_list_never_leaks_notes():
    create(notes="secret")
    assert "notes" not in client.get("/watch").json()[0]


# --------------------------------------------------------------------------
# GET /watch/{id}
# --------------------------------------------------------------------------


def test_get_one():
    create()
    body = client.get("/watch/1").json()
    assert body["name"] == "flask"
    assert body["full_name"] == "pallets/flask"


def test_get_one_404():
    response = client.get("/watch/99")
    assert response.status_code == 404
    assert "99" in response.json()["detail"]


def test_get_one_bad_id_type():
    assert client.get("/watch/abc").status_code == 422


# --------------------------------------------------------------------------
# PATCH
# --------------------------------------------------------------------------


def test_patch_single_field():
    create()
    body = client.patch("/watch/1", json={"stars": 99}).json()
    assert body["stars"] == 99
    assert body["language"] == "Python", "omitted fields must be untouched"
    assert body["name"] == "flask"


def test_patch_omitted_fields_do_not_become_null():
    create(language="Python", tags=["web"])
    body = client.patch("/watch/1", json={"stars": 5}).json()
    assert body["language"] == "Python"
    assert body["tags"] == ["web"]


def test_patch_can_set_null_explicitly():
    create(language="Python")
    body = client.patch("/watch/1", json={"language": None}).json()
    assert body["language"] is None


def test_patch_empty_body_is_a_noop():
    create()
    before = client.get("/watch/1").json()
    assert client.patch("/watch/1", json={}).json() == before


def test_patch_notes_still_hidden():
    create()
    body = client.patch("/watch/1", json={"notes": "new"}).json()
    assert "notes" not in body
    assert task._STORE[1]["notes"] == "new"


def test_patch_404():
    assert client.patch("/watch/99", json={"stars": 1}).status_code == 404


def test_patch_validates():
    create()
    assert client.patch("/watch/1", json={"stars": -5}).status_code == 422


# --------------------------------------------------------------------------
# DELETE
# --------------------------------------------------------------------------


def test_delete():
    create()
    response = client.delete("/watch/1")
    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/watch/1").status_code == 404


def test_delete_404():
    assert client.delete("/watch/99").status_code == 404


# --------------------------------------------------------------------------
# stats
# --------------------------------------------------------------------------


def test_stats_empty():
    body = client.get("/watch-stats").json()
    assert body == {
        "count": 0,
        "total_stars": 0,
        "mean_stars": None,
        "languages": {},
        "top": None,
    }


def test_stats_populated():
    create(name="a", stars=10, language="Python")
    create(name="b", stars=90, language="Python")
    create(name="c", stars=50, language=None)
    body = client.get("/watch-stats").json()
    assert body["count"] == 3
    assert body["total_stars"] == 150
    assert body["mean_stars"] == 50.0
    assert body["languages"] == {"Python": 2, "unknown": 1}
    assert body["top"]["name"] == "b"
    assert body["top"]["full_name"] == "pallets/b"


def test_stats_top_never_leaks_notes():
    create(notes="secret")
    assert "notes" not in client.get("/watch-stats").json()["top"]


# --------------------------------------------------------------------------
# docs
# --------------------------------------------------------------------------


def test_openapi_documents_the_models():
    schema = client.get("/openapi.json").json()
    assert "WatchIn" in schema["components"]["schemas"]
    assert "WatchOut" in schema["components"]["schemas"]
    assert "notes" not in schema["components"]["schemas"]["WatchOut"]["properties"]
