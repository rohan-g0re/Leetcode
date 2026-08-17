import json

import pandas as pd
import pytest

import task


@pytest.fixture(scope="module")
def fx():
    return task.fx_frame(task.load_json("frankfurter_series"))


@pytest.fixture(scope="module")
def population():
    return task.population_with_regions()


# --------------------------------------------------------------------------
# fx_frame
# --------------------------------------------------------------------------


def test_fx_frame_shape(fx):
    assert list(fx.columns) == ["date", "currency", "rate"]
    assert len(fx) == 256
    assert fx["currency"].nunique() == 4
    assert fx["date"].nunique() == 64


def test_fx_frame_dtypes(fx):
    assert str(fx["date"].dtype).startswith("datetime64")
    assert fx["date"].dt.tz is not None
    assert str(fx["rate"].dtype) == "float64"


def test_fx_frame_sorted(fx):
    assert fx["date"].is_monotonic_increasing
    first_day = fx.loc[fx["date"] == fx["date"].min()]
    assert list(first_day["currency"]) == sorted(first_day["currency"])


def test_fx_frame_values(fx):
    row = fx.iloc[0]
    assert row["currency"] == "EUR"
    assert row["rate"] == pytest.approx(0.90498)


def test_fx_frame_empty():
    empty = task.fx_frame({"base": "USD"})
    assert len(empty) == 0
    assert list(empty.columns) == ["date", "currency", "rate"]


# --------------------------------------------------------------------------
# monthly_fx_stats
# --------------------------------------------------------------------------


def test_monthly_fx_stats_columns(fx):
    stats = task.monthly_fx_stats(fx)
    assert list(stats.columns) == [
        "currency",
        "month",
        "days",
        "mean_rate",
        "min_rate",
        "max_rate",
        "change_pct",
    ]
    assert len(stats) == 16
    assert list(stats.index) == list(range(16))


def test_monthly_fx_stats_values(fx):
    stats = task.monthly_fx_stats(fx)
    eur_jan = stats[(stats["currency"] == "EUR") & (stats["month"] == "2024-01")].iloc[0]
    assert eur_jan["days"] == 22
    assert eur_jan["mean_rate"] == pytest.approx(0.9170, abs=1e-4)
    # rounded to 4dp as specified: the raw values are 0.91017 and 0.92396
    assert eur_jan["min_rate"] == pytest.approx(0.9102)
    assert eur_jan["max_rate"] == pytest.approx(0.9240)
    assert eur_jan["change_pct"] == pytest.approx(1.10)


def test_monthly_fx_stats_change_uses_chronological_ends(fx):
    stats = task.monthly_fx_stats(fx)
    eur_feb = stats[(stats["currency"] == "EUR") & (stats["month"] == "2024-02")].iloc[0]
    assert eur_feb["change_pct"] == pytest.approx(-0.11)


def test_monthly_fx_stats_sorted(fx):
    stats = task.monthly_fx_stats(fx)
    assert list(stats["currency"]) == sorted(stats["currency"])
    eur = stats[stats["currency"] == "EUR"]
    assert list(eur["month"]) == sorted(eur["month"])


def test_monthly_fx_stats_days_total(fx):
    assert task.monthly_fx_stats(fx)["days"].sum() == 256


# --------------------------------------------------------------------------
# fill_missing_days
# --------------------------------------------------------------------------


def test_fill_missing_days(fx):
    filled = task.fill_missing_days(fx, "EUR")
    assert list(filled.columns) == ["date", "rate", "filled"]
    assert len(filled) == 91
    assert filled["rate"].notna().all()
    assert filled["date"].is_monotonic_increasing


def test_fill_missing_days_marks_filled(fx):
    filled = task.fill_missing_days(fx, "EUR")
    observed = len(fx[fx["currency"] == "EUR"])
    assert (~filled["filled"]).sum() == observed
    assert filled["filled"].sum() == 91 - observed
    assert filled.iloc[0]["filled"] is False or filled.iloc[0]["filled"] == False  # noqa: E712


def test_fill_missing_days_carries_forward(fx):
    filled = task.fill_missing_days(fx, "EUR").set_index("date")
    saturday = pd.Timestamp("2024-01-06", tz="UTC")
    friday = pd.Timestamp("2024-01-05", tz="UTC")
    assert filled.loc[saturday, "rate"] == filled.loc[friday, "rate"]
    assert filled.loc[saturday, "filled"]


def test_fill_missing_days_unknown_currency(fx):
    empty = task.fill_missing_days(fx, "ZZZ")
    assert len(empty) == 0
    assert list(empty.columns) == ["date", "rate", "filled"]


# --------------------------------------------------------------------------
# population_with_regions
# --------------------------------------------------------------------------


def test_population_with_regions_shape(population):
    assert list(population.columns) == [
        "country_code",
        "country_name",
        "region",
        "year",
        "population",
    ]
    assert len(population) == 970, "a left join must not change the row count"


def test_population_with_regions_all_matched(population):
    assert population["region"].isna().sum() == 0


def test_population_with_regions_sorted(population):
    codes = list(population["country_code"])
    assert codes == sorted(codes)


def test_population_with_regions_values(population):
    row = population[
        (population["country_code"] == "AFE") & (population["year"] == 2023)
    ].iloc[0]
    assert row["population"] == 750491370
    assert row["region"] == "Aggregates"


# --------------------------------------------------------------------------
# region_population_by_year
# --------------------------------------------------------------------------


def test_region_population_by_year(population):
    by_year = task.region_population_by_year(population)
    assert list(by_year.columns) == [
        "region",
        "year",
        "countries",
        "total_population",
    ]
    assert len(by_year) == 48
    assert list(by_year.index) == list(range(48))


def test_region_population_by_year_values(population):
    by_year = task.region_population_by_year(population)
    row = by_year[(by_year["region"] == "South Asia") & (by_year["year"] == 2018)].iloc[0]
    assert row["countries"] == 3
    assert row["total_population"] == 1538941926


def test_region_population_by_year_sorted(population):
    by_year = task.region_population_by_year(population)
    assert list(by_year["region"]) == sorted(by_year["region"])
    south = by_year[by_year["region"] == "South Asia"]
    assert list(south["year"]) == sorted(south["year"])


def test_region_population_by_year_excludes_nulls():
    df = pd.DataFrame(
        [
            {"region": None, "year": 2020, "population": 5, "country_code": "A"},
            {"region": "R", "year": 2020, "population": None, "country_code": "B"},
            {"region": "R", "year": 2020, "population": 7, "country_code": "C"},
        ]
    )
    out = task.region_population_by_year(df)
    assert len(out) == 1
    assert out.iloc[0]["countries"] == 1
    assert out.iloc[0]["total_population"] == 7


# --------------------------------------------------------------------------
# population_growth
# --------------------------------------------------------------------------


def test_population_growth(population):
    by_year = task.region_population_by_year(population)
    growth = task.population_growth(by_year, "South Asia")
    assert list(growth.columns) == ["year", "total_population", "change", "change_pct"]
    assert len(growth) == 6
    assert pd.isna(growth.iloc[0]["change"])
    assert pd.isna(growth.iloc[0]["change_pct"])
    assert growth.iloc[1]["change"] == 1554708191 - 1538941926
    assert growth.iloc[1]["change_pct"] == pytest.approx(1.02, abs=0.01)


def test_population_growth_sorted(population):
    by_year = task.region_population_by_year(population)
    growth = task.population_growth(by_year, "South Asia")
    assert list(growth["year"]) == sorted(growth["year"])
    assert list(growth.index) == list(range(len(growth)))


def test_population_growth_unknown_region(population):
    by_year = task.region_population_by_year(population)
    empty = task.population_growth(by_year, "Atlantis")
    assert len(empty) == 0
    assert list(empty.columns) == ["year", "total_population", "change", "change_pct"]


# --------------------------------------------------------------------------
# stories_per_month
# --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def monthly():
    return task.stories_per_month(task.load_json("hn_search_python")["hits"])


def test_stories_per_month_columns(monthly):
    assert list(monthly.columns) == ["month", "stories", "total_points"]
    assert list(monthly.index) == list(range(len(monthly)))


def test_stories_per_month_totals(monthly):
    assert monthly["stories"].sum() == 50
    assert monthly["total_points"].sum() == 41422


def test_stories_per_month_fills_gaps(monthly):
    assert len(monthly) == 143, "every month in the range must appear"
    assert (monthly["stories"] == 0).sum() == 103
    assert monthly.iloc[0]["month"] == "2014-07"
    assert monthly.iloc[0]["stories"] == 1


def test_stories_per_month_is_continuous(monthly):
    months = list(monthly["month"])
    assert months == sorted(months)
    periods = pd.period_range(months[0], months[-1], freq="M")
    assert months == [str(p) for p in periods]


def test_stories_per_month_single_story():
    hits = [{"created_at": "2024-03-05T00:00:00Z", "points": 10}]
    out = task.stories_per_month(hits)
    assert len(out) == 1
    assert out.iloc[0]["month"] == "2024-03"
    assert out.iloc[0]["total_points"] == 10


def test_stories_per_month_empty():
    out = task.stories_per_month([])
    assert len(out) == 0
    assert list(out.columns) == ["month", "stories", "total_points"]


# --------------------------------------------------------------------------
# save_report
# --------------------------------------------------------------------------


def test_save_report_csv(tmp_path):
    df = pd.DataFrame([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
    path = tmp_path / "out" / "report.csv"
    assert task.save_report(df, path) == 2
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert lines[0] == "a,b", "index=False -- no leading unnamed column"
    assert lines[1] == "1,x"


def test_save_report_json(tmp_path):
    df = pd.DataFrame([{"a": 1}])
    path = tmp_path / "report.json"
    assert task.save_report(df, path, fmt="json") == 1
    assert json.loads(path.read_text(encoding="utf-8")) == [{"a": 1}]


def test_save_report_bad_format(tmp_path):
    with pytest.raises(ValueError) as info:
        task.save_report(pd.DataFrame(), tmp_path / "x.parquet", fmt="parquet")
    assert "parquet" in str(info.value)
