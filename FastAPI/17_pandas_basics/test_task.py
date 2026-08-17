import json
import math

import pandas as pd
import pytest

import task

TEXT_DTYPES = {"str", "object", "string"}


@pytest.fixture(scope="module")
def repos():
    return task.repos_frame()


@pytest.fixture(scope="module")
def countries():
    return task.countries_frame()


# --------------------------------------------------------------------------
# repos_frame
# --------------------------------------------------------------------------


def test_repos_frame_shape(repos):
    assert isinstance(repos, pd.DataFrame)
    assert len(repos) == 17
    assert list(repos.columns) == [
        "name",
        "language",
        "stars",
        "forks",
        "open_issues",
        "archived",
        "license",
        "created",
    ]


def test_repos_frame_dtypes(repos):
    assert str(repos["stars"].dtype) == "int64"
    assert str(repos["forks"].dtype) == "int64"
    assert str(repos["archived"].dtype) == "bool"
    assert str(repos["name"].dtype) in TEXT_DTYPES


def test_repos_frame_values(repos):
    flask = repos.loc[repos["name"] == "flask"].iloc[0]
    assert flask["stars"] == 72117
    assert flask["language"] == "Python"
    assert repos["stars"].sum() == 117631


def test_repos_frame_nulls(repos):
    assert repos["language"].isna().sum() == 2
    assert repos["license"].isna().sum() == 3


# --------------------------------------------------------------------------
# overview
# --------------------------------------------------------------------------


def test_overview(repos):
    info = task.overview(repos)
    assert info["rows"] == 17
    assert info["columns"] == list(repos.columns)
    assert info["dtypes"]["stars"] == "int64"
    assert info["missing"]["license"] == 3
    assert info["missing"]["name"] == 0


def test_overview_is_json_serializable(repos):
    json.dumps(task.overview(repos))


def test_overview_on_empty_frame():
    info = task.overview(pd.DataFrame({"a": []}))
    assert info["rows"] == 0
    assert info["columns"] == ["a"]


# --------------------------------------------------------------------------
# filter_repos
# --------------------------------------------------------------------------


def test_filter_repos_min_stars(repos):
    filtered = task.filter_repos(repos, min_stars=10000)
    assert len(filtered) == 3
    assert (filtered["stars"] >= 10000).all()


def test_filter_repos_excludes_archived_by_default(repos):
    assert not task.filter_repos(repos)["archived"].any()
    assert task.filter_repos(repos, include_archived=True)["archived"].any()


def test_filter_repos_language(repos):
    filtered = task.filter_repos(repos, language="Python", include_archived=True)
    assert len(filtered) == 13
    assert set(filtered["language"]) == {"Python"}


def test_filter_repos_resets_index(repos):
    filtered = task.filter_repos(repos, min_stars=10000)
    assert list(filtered.index) == list(range(len(filtered)))


def test_filter_repos_does_not_mutate(repos):
    before = len(repos)
    task.filter_repos(repos, min_stars=1)
    assert len(repos) == before


def test_filter_repos_no_matches(repos):
    assert len(task.filter_repos(repos, min_stars=10**9)) == 0


# --------------------------------------------------------------------------
# add_metrics
# --------------------------------------------------------------------------


def test_add_metrics_columns(repos):
    enriched = task.add_metrics(repos)
    for column in ("fork_ratio", "popularity", "has_license"):
        assert column in enriched.columns
    assert "fork_ratio" not in repos.columns, "input frame must not be modified"


def test_add_metrics_fork_ratio(repos):
    enriched = task.add_metrics(repos)
    flask = enriched.loc[enriched["name"] == "flask"].iloc[0]
    assert flask["fork_ratio"] == round(flask["forks"] / flask["stars"], 3)


def test_add_metrics_zero_stars_is_nan(repos):
    enriched = task.add_metrics(repos)
    zero = enriched.loc[enriched["stars"] == 0]
    assert len(zero) == 2
    assert zero["fork_ratio"].isna().all(), "division by zero must not become inf"


def test_add_metrics_popularity_bands(repos):
    enriched = task.add_metrics(repos)
    assert (enriched.loc[enriched["stars"] >= 10000, "popularity"] == "high").all()
    mid = enriched.loc[(enriched["stars"] >= 1000) & (enriched["stars"] < 10000)]
    assert (mid["popularity"] == "medium").all()
    assert (enriched.loc[enriched["stars"] < 1000, "popularity"] == "low").all()


def test_add_metrics_has_license(repos):
    enriched = task.add_metrics(repos)
    assert enriched["has_license"].sum() == 14
    assert enriched["has_license"].dtype == bool


# --------------------------------------------------------------------------
# language_summary
# --------------------------------------------------------------------------


def test_language_summary(repos):
    summary = task.language_summary(repos)
    assert list(summary.columns) == [
        "language",
        "repos",
        "total_stars",
        "mean_stars",
        "max_stars",
    ]
    assert len(summary) == 4
    assert list(summary.index) == list(range(4))


def test_language_summary_values(repos):
    summary = task.language_summary(repos).set_index("language")
    assert summary.loc["Python", "repos"] == 13
    assert summary.loc["Python", "total_stars"] == 117467
    assert summary.loc["Python", "mean_stars"] == 9035.9
    assert summary.loc["Python", "max_stars"] == 72117
    assert summary.loc["unknown", "repos"] == 2


def test_language_summary_sorted(repos):
    summary = task.language_summary(repos)
    assert list(summary["language"]) == ["Python", "HTML", "unknown", "CSS"]


# --------------------------------------------------------------------------
# countries_frame
# --------------------------------------------------------------------------


def test_countries_frame_shape(countries):
    assert len(countries) == 295
    assert list(countries.columns) == [
        "code",
        "name",
        "region",
        "income_level",
        "capital",
        "latitude",
        "longitude",
    ]


def test_countries_frame_numeric_coercion(countries):
    assert str(countries["latitude"].dtype) == "float64"
    assert str(countries["longitude"].dtype) == "float64"
    assert countries["latitude"].isna().sum() == 84


def test_countries_frame_blank_to_na(countries):
    assert countries["capital"].isna().sum() == 84
    assert not (countries["capital"].dropna() == "").any()


def test_countries_frame_stripped(countries):
    regions = countries["region"].dropna()
    assert (regions == regions.str.strip()).all()
    assert "Latin America & Caribbean" in set(regions)


def test_countries_frame_first_row(countries):
    aruba = countries.loc[countries["code"] == "ABW"].iloc[0]
    assert aruba["name"] == "Aruba"
    assert aruba["capital"] == "Oranjestad"
    assert aruba["latitude"] == pytest.approx(12.5167)
    assert aruba["longitude"] == pytest.approx(-70.0167)


# --------------------------------------------------------------------------
# region_stats
# --------------------------------------------------------------------------


def test_region_stats(countries):
    stats = task.region_stats(countries)
    assert list(stats.columns) == [
        "region",
        "countries",
        "with_capital",
        "mean_latitude",
    ]
    assert stats["countries"].sum() == 295
    assert list(stats.index) == list(range(len(stats)))


def test_region_stats_values(countries):
    stats = task.region_stats(countries).set_index("region")
    assert stats.loc["Aggregates", "countries"] == 78
    assert stats.loc["Aggregates", "with_capital"] == 0
    assert math.isnan(stats.loc["Aggregates", "mean_latitude"])
    assert stats.loc["Europe & Central Asia", "countries"] == 58
    assert stats.loc["Europe & Central Asia", "with_capital"] == 56
    assert stats.loc["Europe & Central Asia", "mean_latitude"] == pytest.approx(48.06)


def test_region_stats_sorted(countries):
    stats = task.region_stats(countries)
    assert stats.iloc[0]["region"] == "Aggregates"
    assert list(stats["countries"]) == sorted(stats["countries"], reverse=True)


# --------------------------------------------------------------------------
# to_records
# --------------------------------------------------------------------------


def test_to_records_basic(repos):
    records = task.to_records(repos, limit=3)
    assert len(records) == 3
    assert isinstance(records[0], dict)
    assert records[0]["name"] == repos.iloc[0]["name"]


def test_to_records_no_limit(repos):
    assert len(task.to_records(repos)) == 17


def test_to_records_nan_becomes_none(countries):
    records = task.to_records(countries)
    aggregate = next(r for r in records if r["code"] == "AFE")
    assert aggregate["capital"] is None
    assert aggregate["latitude"] is None


def test_to_records_is_json_safe(countries):
    text = json.dumps(task.to_records(countries, limit=50))
    assert "NaN" not in text
    assert json.loads(text)[0]["code"] == "ABW"
