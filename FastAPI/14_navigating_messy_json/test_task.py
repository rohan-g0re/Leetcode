import pytest
import requests

import task

# --------------------------------------------------------------------------
# find_records
# --------------------------------------------------------------------------


def test_find_records_already_a_list():
    data = [{"a": 1}, {"a": 2}]
    assert task.find_records(data) == data


def test_find_records_dict_envelope():
    data = {"hits": [{"a": 1}], "nbHits": 320, "page": 0}
    assert task.find_records(data) == [{"a": 1}]


def test_find_records_dict_envelope_prefers_longest_list():
    data = {"facets": [{"x": 1}], "results": [{"a": 1}, {"a": 2}, {"a": 3}]}
    assert task.find_records(data) == [{"a": 1}, {"a": 2}, {"a": 3}]


def test_find_records_array_envelope():
    data = [{"page": 1, "total": 295}, [{"id": "ABW"}, {"id": "AFG"}]]
    assert task.find_records(data) == [{"id": "ABW"}, {"id": "AFG"}]


def test_find_records_single_entity():
    assert task.find_records({"login": "x", "id": 1}) == []


def test_find_records_edge_cases():
    assert task.find_records(None) == []
    assert task.find_records([]) == []
    assert task.find_records({}) == []
    assert task.find_records(42) == []
    assert task.find_records([1, 2, 3]) == []
    assert task.find_records({"a": []}) == []
    assert task.find_records({"1": {"x": 1}}) == []


def test_find_records_on_real_fixtures():
    assert len(task.find_records(task.load_fixture_file("worldbank_countries"))) == 295
    assert len(task.find_records(task.load_fixture_file("hn_search_python"))) == 50
    assert len(task.find_records(task.load_fixture_file("github_repos_pallets"))) == 17
    assert len(task.find_records(task.load_fixture_file("placeholder_posts"))) == 100


# --------------------------------------------------------------------------
# profile_fields / inconsistent_fields
# --------------------------------------------------------------------------


def test_profile_fields():
    records = [{"a": 1}, {"a": None, "b": "x"}, {"a": "2"}]
    assert task.profile_fields(records) == {
        "a": {"present": 3, "null": 1, "types": ["int", "str"]},
        "b": {"present": 1, "null": 0, "types": ["str"]},
    }


def test_profile_fields_empty():
    assert task.profile_fields([]) == {}


def test_profile_fields_all_null():
    assert task.profile_fields([{"a": None}]) == {
        "a": {"present": 1, "null": 1, "types": []}
    }


def test_profile_fields_nested_types():
    profile = task.profile_fields([{"a": {"x": 1}}, {"a": [1]}])
    assert profile["a"]["types"] == ["dict", "list"]


def test_profile_fields_on_real_fixture():
    records = task.find_records(task.load_fixture_file("worldbank_countries"))
    profile = task.profile_fields(records)
    assert profile["latitude"]["present"] == 295
    assert profile["latitude"]["types"] == ["str"], "lat/long arrive as strings"
    assert profile["region"]["types"] == ["dict"]


def test_inconsistent_fields():
    assert task.inconsistent_fields([{"a": 1, "b": 2}, {"a": 3}]) == ["b"]
    assert task.inconsistent_fields([{"a": 1}, {"a": 2}]) == []
    assert task.inconsistent_fields([]) == []


def test_inconsistent_fields_on_real_fixture():
    records = task.find_records(task.load_fixture_file("hn_search_python"))
    missing = task.inconsistent_fields(records)
    assert isinstance(missing, list)
    assert missing == sorted(missing)


# --------------------------------------------------------------------------
# walk_paths / search_paths
# --------------------------------------------------------------------------


def test_walk_paths_basic():
    assert task.walk_paths({"a": 1, "b": {"c": [10, 20]}}) == [
        ("a", 1),
        ("b.c[0]", 10),
        ("b.c[1]", 20),
    ]


def test_walk_paths_empty_containers_are_leaves():
    assert task.walk_paths({"a": [], "b": {}}) == [("a", []), ("b", {})]


def test_walk_paths_scalar_root():
    assert task.walk_paths(42) == [("", 42)]


def test_walk_paths_list_root():
    assert task.walk_paths([{"a": 1}]) == [("[0].a", 1)]


def test_walk_paths_on_pokemon():
    payload = task.load_fixture_file("pokemon_ditto")
    paths = task.walk_paths(payload)
    assert len(paths) > 500
    lookup = dict(paths)
    assert lookup["name"] == "ditto"
    assert lookup["types[0].type.name"] == "normal"


def test_search_paths():
    assert task.search_paths({"user": {"name": "x"}, "id": 1}, "name") == [
        ("user.name", "x")
    ]
    assert task.search_paths({"a": 1}, "zz") == []


def test_search_paths_is_case_insensitive():
    assert task.search_paths({"userName": "x"}, "username") == [("userName", "x")]


def test_search_paths_on_pokemon():
    payload = task.load_fixture_file("pokemon_ditto")
    hits = task.search_paths(payload, "stat.name")
    # 6 from stats[] -- plus one from past_stats[], which you would not have
    # known was in there. That is exactly why you search instead of guessing.
    assert len(hits) == 7
    assert ("stats[0].stat.name", "hp") in hits
    assert any(path.startswith("past_stats") for path, _ in hits)


# --------------------------------------------------------------------------
# World Bank
# --------------------------------------------------------------------------


@pytest.fixture
def countries():
    return task.flatten_worldbank_countries(task.load_fixture_file("worldbank_countries"))


def test_flatten_worldbank_shape(countries):
    assert len(countries) == 295
    assert set(countries[0]) == {
        "code",
        "name",
        "region",
        "income_level",
        "capital",
        "latitude",
        "longitude",
    }


def test_flatten_worldbank_first_record(countries):
    aruba = next(c for c in countries if c["code"] == "ABW")
    assert aruba == {
        "code": "ABW",
        "name": "Aruba",
        "region": "Latin America & Caribbean",
        "income_level": "High income",
        "capital": "Oranjestad",
        "latitude": 12.5167,
        "longitude": -70.0167,
    }


def test_flatten_worldbank_strips_trailing_space(countries):
    assert all(
        c["region"] is None or c["region"] == c["region"].strip() for c in countries
    )


def test_flatten_worldbank_numbers_are_floats(countries):
    numeric = [c for c in countries if c["latitude"] is not None]
    assert len(numeric) == 211
    assert all(isinstance(c["latitude"], float) for c in numeric)


def test_flatten_worldbank_blank_becomes_none(countries):
    assert sum(1 for c in countries if c["capital"] is None) == 84


def test_flatten_worldbank_handles_synthetic_input():
    payload = [
        {"page": 1},
        [
            {
                "id": "X",
                "name": " Xland ",
                "region": {"value": "  Somewhere  "},
                "incomeLevel": {"value": ""},
                "capitalCity": "",
                "latitude": "",
                "longitude": "1.5",
            }
        ],
    ]
    assert task.flatten_worldbank_countries(payload) == [
        {
            "code": "X",
            "name": "Xland",
            "region": "Somewhere",
            "income_level": None,
            "capital": None,
            "latitude": None,
            "longitude": 1.5,
        }
    ]


def test_summarize_by_region(countries):
    summary = task.summarize_by_region(countries)
    assert summary[0] == ("Aggregates", 78)
    assert summary[1] == ("Europe & Central Asia", 58)
    assert sum(count for _, count in summary) == 295


def test_summarize_by_region_sorting_rules():
    rows = [
        {"region": "b"},
        {"region": "a"},
        {"region": "c"},
        {"region": "c"},
        {"region": None},
    ]
    assert task.summarize_by_region(rows) == [("c", 2), ("a", 1), ("b", 1)]


# --------------------------------------------------------------------------
# Hacker News
# --------------------------------------------------------------------------


@pytest.fixture
def hits():
    return task.flatten_hn_hits(task.load_fixture_file("hn_search_python"))


def test_flatten_hn_shape(hits):
    assert len(hits) == 50
    assert set(hits[0]) == {
        "id",
        "title",
        "author",
        "points",
        "comments",
        "domain",
        "date",
    }


def test_flatten_hn_types(hits):
    assert all(isinstance(h["id"], str) for h in hits)
    assert all(isinstance(h["points"], int) for h in hits)
    assert all(isinstance(h["comments"], int) for h in hits)
    assert all(h["date"] is None or len(h["date"]) == 10 for h in hits)


def test_flatten_hn_drops_search_internals(hits):
    assert "_highlightResult" not in hits[0]
    assert "_tags" not in hits[0]


def test_flatten_hn_handles_nulls():
    payload = {
        "hits": [
            {
                "objectID": "1",
                "title": None,
                "author": None,
                "points": None,
                "num_comments": None,
                "url": None,
                "created_at": None,
            }
        ]
    }
    assert task.flatten_hn_hits(payload) == [
        {
            "id": "1",
            "title": "",
            "author": None,
            "points": 0,
            "comments": 0,
            "domain": None,
            "date": None,
        }
    ]


def test_flatten_hn_domain():
    payload = {
        "hits": [
            {"objectID": 7, "url": "https://Example.COM/a/b?c=1", "created_at": "2024-05-06T00:00:00.000Z"}
        ]
    }
    row = task.flatten_hn_hits(payload)[0]
    assert row["domain"] == "example.com"
    assert row["date"] == "2024-05-06"
    assert row["id"] == "7"


# --------------------------------------------------------------------------
# PokeAPI
# --------------------------------------------------------------------------


def test_pokemon_profile():
    profile = task.pokemon_profile(task.load_fixture_file("pokemon_ditto"))
    assert profile["name"] == "ditto"
    assert profile["id"] == 132
    assert profile["types"] == ["normal"]
    assert profile["abilities"] == ["limber", "imposter"]
    assert profile["stats"]["hp"] == 48
    assert len(profile["stats"]) == 6
    assert profile["total_stats"] == sum(profile["stats"].values())


def test_pokemon_profile_respects_slot_order():
    payload = {
        "name": "x",
        "id": 1,
        "height": 1,
        "weight": 1,
        "types": [
            {"slot": 2, "type": {"name": "flying"}},
            {"slot": 1, "type": {"name": "normal"}},
        ],
        "abilities": [
            {"slot": 3, "ability": {"name": "c"}},
            {"slot": 1, "ability": {"name": "a"}},
        ],
        "stats": [{"base_stat": 10, "stat": {"name": "hp"}}],
    }
    profile = task.pokemon_profile(payload)
    assert profile["types"] == ["normal", "flying"]
    assert profile["abilities"] == ["a", "c"]
    assert profile["total_stats"] == 10


def test_pokemon_profile_empty_payload():
    assert task.pokemon_profile({}) == {
        "name": None,
        "id": None,
        "height": None,
        "weight": None,
        "types": [],
        "abilities": [],
        "stats": {},
        "total_stats": 0,
    }


# --------------------------------------------------------------------------
# live
# --------------------------------------------------------------------------


@pytest.mark.live
def test_live_worldbank():
    response = requests.get(
        "https://api.worldbank.org/v2/country",
        params={"format": "json", "per_page": 20},
        headers=task.HEADERS,
        timeout=task.TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    records = task.find_records(payload)
    assert len(records) == 20
    countries = task.flatten_worldbank_countries(payload)
    assert countries[0]["code"]


@pytest.mark.live
def test_live_hn_search():
    response = requests.get(
        "https://hn.algolia.com/api/v1/search",
        params={"query": "fastapi", "tags": "story", "hitsPerPage": 10},
        headers=task.HEADERS,
        timeout=task.TIMEOUT,
    )
    response.raise_for_status()
    rows = task.flatten_hn_hits(response.json())
    assert len(rows) == 10
    assert all(isinstance(r["points"], int) for r in rows)


@pytest.mark.live
def test_live_pokemon():
    response = requests.get(
        "https://pokeapi.co/api/v2/pokemon/pikachu",
        headers=task.HEADERS,
        timeout=task.TIMEOUT,
    )
    response.raise_for_status()
    profile = task.pokemon_profile(response.json())
    assert profile["name"] == "pikachu"
    assert "electric" in profile["types"]
    assert profile["total_stats"] > 0
