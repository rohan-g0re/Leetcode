import json

import pandas as pd
import pytest

import task


@pytest.fixture(scope="module")
def hn():
    return task.hn_frame(task.load_json("hn_search_python"))


@pytest.fixture(scope="module")
def population():
    return task.population_frame(task.load_json("worldbank_population"))


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def test_normalize_columns():
    df = pd.DataFrame([{"User Name": 1, "owner.login": 2, "a-b": 3, " x ": 4}])
    assert list(task.normalize_columns(df).columns) == [
        "user_name",
        "owner_login",
        "a_b",
        "x",
    ]


def test_normalize_columns_does_not_mutate():
    df = pd.DataFrame([{"A.B": 1}])
    task.normalize_columns(df)
    assert list(df.columns) == ["A.B"]


def test_coerce_numeric():
    df = pd.DataFrame([{"n": "1.5"}, {"n": "x"}, {"n": None}])
    out = task.coerce_numeric(df, ["n"])
    assert str(out["n"].dtype) == "float64"
    assert out["n"].iloc[0] == 1.5
    assert out["n"].isna().sum() == 2


def test_coerce_numeric_integer_keeps_nulls():
    df = pd.DataFrame([{"n": "10"}, {"n": None}])
    out = task.coerce_numeric(df, ["n"], integer=True)
    assert str(out["n"].dtype) == "Int64"
    assert out["n"].iloc[0] == 10
    assert pd.isna(out["n"].iloc[1])


def test_coerce_numeric_ignores_missing_columns():
    df = pd.DataFrame([{"a": 1}])
    assert list(task.coerce_numeric(df, ["nope"]).columns) == ["a"]


def test_coerce_datetime():
    df = pd.DataFrame([{"d": "2024-01-05T10:00:00Z"}, {"d": "nope"}])
    out = task.coerce_datetime(df, ["d"])
    assert str(out["d"].dtype).startswith("datetime64")
    assert out["d"].iloc[0].year == 2024
    assert pd.isna(out["d"].iloc[1])
    assert out["d"].dt.tz is not None


def test_quality_report():
    df = pd.DataFrame([{"id": 1, "v": None}, {"id": 1, "v": 2}, {"id": 3, "v": 4}])
    report = task.quality_report(df, key="id")
    assert report["rows"] == 3
    assert report["columns"] == 2
    assert report["missing"] == {"v": 1}
    assert report["duplicates"] == 1
    assert report["empty"] is False
    json.dumps(report)


def test_quality_report_no_key():
    df = pd.DataFrame([{"a": 1}])
    report = task.quality_report(df)
    assert report["duplicates"] == 0
    assert report["missing"] == {}


def test_quality_report_empty_frame():
    report = task.quality_report(pd.DataFrame({"a": []}), key="a")
    assert report["rows"] == 0
    assert report["empty"] is True
    json.dumps(report)


# --------------------------------------------------------------------------
# hn_frame
# --------------------------------------------------------------------------


def test_hn_frame_columns(hn):
    assert list(hn.columns) == [
        "id",
        "title",
        "author",
        "points",
        "comments",
        "url",
        "domain",
        "created",
        "month",
    ]
    assert len(hn) == 50


def test_hn_frame_dtypes(hn):
    assert str(hn["points"].dtype) == "Int64"
    assert str(hn["comments"].dtype) == "Int64"
    assert str(hn["created"].dtype).startswith("datetime64")
    assert hn["created"].dt.tz is not None
    assert hn["id"].map(type).eq(str).all()


def test_hn_frame_month_matches_created(hn):
    row = hn.iloc[0]
    assert row["month"] == row["created"].strftime("%Y-%m")
    assert hn["month"].notna().all()


def test_hn_frame_domain(hn):
    assert hn["domain"].notna().sum() > 0
    domains = hn["domain"].dropna()
    assert (domains == domains.str.lower()).all()
    assert not domains.str.contains("/").any()


def test_hn_frame_points_are_real(hn):
    assert hn["points"].max() == 2214
    assert hn["points"].sum() == 41422


def test_hn_frame_empty_payload():
    empty = task.hn_frame({"hits": []})
    assert len(empty) == 0
    assert list(empty.columns) == [
        "id",
        "title",
        "author",
        "points",
        "comments",
        "url",
        "domain",
        "created",
        "month",
    ]
    assert task.quality_report(empty)["empty"] is True


def test_hn_frame_missing_hits_key():
    assert len(task.hn_frame({"nbHits": 0})) == 0


def test_hn_frame_handles_null_url_and_title():
    payload = {
        "hits": [
            {
                "objectID": "1",
                "title": None,
                "author": "a",
                "points": None,
                "num_comments": None,
                "url": None,
                "created_at": "2024-05-06T00:00:00.000Z",
            }
        ]
    }
    row = task.hn_frame(payload).iloc[0]
    assert row["id"] == "1"
    assert pd.isna(row["domain"])
    assert pd.isna(row["points"])
    assert row["month"] == "2024-05"


# --------------------------------------------------------------------------
# population_frame
# --------------------------------------------------------------------------


def test_population_frame_columns(population):
    assert list(population.columns) == [
        "country_code",
        "country_name",
        "year",
        "population",
    ]


def test_population_frame_drops_blank_codes(population):
    assert len(population) == 970
    assert population["country_code"].notna().all()


def test_population_frame_dtypes(population):
    assert str(population["year"].dtype) == "Int64"
    assert str(population["population"].dtype) == "Int64"


def test_population_frame_keeps_null_populations():
    # In this fixture every null population happens to sit on a row with a
    # blank country code, so those rows are dropped. The nullable dtype still
    # has to survive a null that does NOT get dropped -- that is what plain
    # int64 cannot do.
    payload = [
        {"page": 1},
        [
            {"countryiso3code": "AAA", "country": {"value": "A"}, "date": "2020", "value": None},
            {"countryiso3code": "AAA", "country": {"value": "A"}, "date": "2021", "value": 5},
        ],
    ]
    frame = task.population_frame(payload)
    assert len(frame) == 2
    assert frame["population"].isna().sum() == 1
    assert frame["population"].dropna().iloc[0] == 5


def test_population_frame_sorted(population):
    codes = list(population["country_code"])
    assert codes == sorted(codes)
    first = population.loc[population["country_code"] == codes[0]]
    assert list(first["year"]) == sorted(first["year"])


def test_population_frame_values(population):
    row = population[
        (population["country_code"] == "AFE") & (population["year"] == 2023)
    ].iloc[0]
    assert row["population"] == 750491370
    assert row["country_name"] == "Africa Eastern and Southern"


def test_population_frame_years(population):
    assert set(population["year"].dropna()) == {2018, 2019, 2020, 2021, 2022, 2023}


# --------------------------------------------------------------------------
# posts_with_users
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def posts():
    return task.posts_with_users()


def test_posts_with_users_columns(posts):
    assert list(posts.columns) == [
        "post_id",
        "user_id",
        "user_name",
        "user_city",
        "company",
        "title_length",
    ]
    assert len(posts) == 100


def test_posts_with_users_joined_values(posts):
    first = posts.iloc[0]
    assert first["post_id"] == 1
    assert first["user_id"] == 1
    assert first["user_name"] == "Leanne Graham"
    assert first["user_city"] == "Gwenborough"
    assert first["company"] == "Romaguera-Crona"


def test_posts_with_users_title_length(posts):
    raw = task.load_json("placeholder_posts")
    assert posts.iloc[0]["title_length"] == len(raw[0]["title"])
    assert (posts["title_length"] > 0).all()


def test_posts_with_users_all_matched(posts):
    assert posts["user_name"].notna().all()
    assert posts["user_id"].nunique() == 10


def test_posts_with_users_sorted(posts):
    assert list(posts["post_id"]) == sorted(posts["post_id"])
    assert list(posts.index) == list(range(100))


# --------------------------------------------------------------------------
# top_domains
# --------------------------------------------------------------------------


def test_top_domains(hn):
    top = task.top_domains(hn, n=3)
    assert list(top.columns) == ["domain", "stories", "total_points"]
    assert len(top) == 3
    assert list(top["stories"]) == sorted(top["stories"], reverse=True)
    assert top["domain"].notna().all()


def test_top_domains_counts():
    df = pd.DataFrame(
        [
            {"domain": "a.com", "points": 10},
            {"domain": "a.com", "points": 5},
            {"domain": "b.com", "points": 100},
            {"domain": None, "points": 1},
        ]
    )
    top = task.top_domains(df)
    assert list(top["domain"]) == ["a.com", "b.com"]
    assert list(top["stories"]) == [2, 1]
    assert list(top["total_points"]) == [15, 100]


def test_top_domains_empty():
    empty = task.top_domains(pd.DataFrame({"domain": [], "points": []}))
    assert len(empty) == 0
    assert list(empty.columns) == ["domain", "stories", "total_points"]
