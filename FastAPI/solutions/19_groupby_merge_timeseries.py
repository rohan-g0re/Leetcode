"""Unit 19 — worked solution."""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"

FX_COLUMNS = ["date", "currency", "rate"]
GROWTH_COLUMNS = ["year", "total_population", "change", "change_pct"]
MONTHLY_COLUMNS = ["month", "stories", "total_points"]


def load_json(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def fx_frame(payload):
    rates = (payload or {}).get("rates") or {}
    rows = [
        {"date": date, "currency": currency, "rate": rate}
        for date, by_currency in rates.items()
        for currency, rate in (by_currency or {}).items()
    ]
    if not rows:
        return pd.DataFrame(columns=FX_COLUMNS)

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True)
    df["rate"] = pd.to_numeric(df["rate"], errors="coerce")
    return df[FX_COLUMNS].sort_values(["date", "currency"]).reset_index(drop=True)


def monthly_fx_stats(df):
    out = df.sort_values("date").copy()
    out["month"] = out["date"].dt.strftime("%Y-%m")

    stats = (
        out.groupby(["currency", "month"])
        .agg(
            days=("rate", "size"),
            mean_rate=("rate", "mean"),
            min_rate=("rate", "min"),
            max_rate=("rate", "max"),
            first_rate=("rate", "first"),
            last_rate=("rate", "last"),
        )
        .reset_index()
    )

    stats["change_pct"] = (
        (stats["last_rate"] - stats["first_rate"]) / stats["first_rate"] * 100
    ).round(2)
    for column in ("mean_rate", "min_rate", "max_rate"):
        stats[column] = stats[column].round(4)

    return (
        stats[
            ["currency", "month", "days", "mean_rate", "min_rate", "max_rate", "change_pct"]
        ]
        .sort_values(["currency", "month"])
        .reset_index(drop=True)
    )


def fill_missing_days(df, currency):
    subset = df.loc[df["currency"] == currency].sort_values("date")
    if subset.empty:
        return pd.DataFrame(columns=["date", "rate", "filled"])

    observed = set(subset["date"])

    daily = (
        subset.set_index("date")["rate"]
        .resample("D")
        .ffill()
        .reset_index()
        .rename(columns={"index": "date"})
    )
    daily["filled"] = ~daily["date"].isin(observed)
    return daily[["date", "rate", "filled"]].reset_index(drop=True)


def _population_frame():
    records = load_json("worldbank_population")[1]
    df = pd.json_normalize(records, sep=".").rename(
        columns={
            "countryiso3code": "country_code",
            "country.value": "country_name",
            "date": "year",
            "value": "population",
        }
    )
    for column in ("country_code", "country_name"):
        df[column] = df[column].astype("string").str.strip().replace("", pd.NA)

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["population"] = pd.to_numeric(df["population"], errors="coerce").astype("Int64")
    return df.loc[df["country_code"].notna()]


def _region_lookup():
    records = load_json("worldbank_countries")[1]
    df = pd.json_normalize(records, sep=".").rename(
        columns={"id": "country_code", "region.value": "region"}
    )[["country_code", "region"]]

    for column in ("country_code", "region"):
        df[column] = df[column].astype("string").str.strip().replace("", pd.NA)

    return df.loc[df["region"].notna() & df["country_code"].notna()]


def population_with_regions():
    population = _population_frame()
    lookup = _region_lookup()

    assert lookup["country_code"].is_unique, "region lookup must be one row per country"

    merged = population.merge(lookup, on="country_code", how="left")
    assert len(merged) == len(population), "left join changed the row count"

    return (
        merged[["country_code", "country_name", "region", "year", "population"]]
        .sort_values(["country_code", "year"])
        .reset_index(drop=True)
    )


def region_population_by_year(df):
    usable = df.loc[df["region"].notna() & df["population"].notna()]
    if usable.empty:
        return pd.DataFrame(columns=["region", "year", "countries", "total_population"])

    grouped = (
        usable.groupby(["region", "year"])
        .agg(countries=("country_code", "count"), total_population=("population", "sum"))
        .reset_index()
    )
    grouped["total_population"] = grouped["total_population"].astype("int64")

    return grouped.sort_values(["region", "year"]).reset_index(drop=True)


def population_growth(df, region):
    subset = df.loc[df["region"] == region].sort_values("year").reset_index(drop=True)
    if subset.empty:
        return pd.DataFrame(columns=GROWTH_COLUMNS)

    out = subset[["year", "total_population"]].copy()
    out["change"] = out["total_population"].diff()
    out["change_pct"] = (out["total_population"].pct_change() * 100).round(2)
    return out[GROWTH_COLUMNS].reset_index(drop=True)


def stories_per_month(hits):
    if not hits:
        return pd.DataFrame(columns=MONTHLY_COLUMNS)

    df = pd.DataFrame(
        [{"created": hit.get("created_at"), "points": hit.get("points")} for hit in hits]
    )
    df["created"] = pd.to_datetime(df["created"], errors="coerce", utc=True)
    df["points"] = pd.to_numeric(df["points"], errors="coerce").fillna(0)
    df = df.loc[df["created"].notna()]
    if df.empty:
        return pd.DataFrame(columns=MONTHLY_COLUMNS)

    monthly = (
        df.set_index("created")
        .resample("MS")
        .agg(stories=("points", "size"), total_points=("points", "sum"))
        .reset_index()
    )
    monthly["month"] = monthly["created"].dt.strftime("%Y-%m")
    monthly["total_points"] = monthly["total_points"].astype("int64")

    return monthly[MONTHLY_COLUMNS].reset_index(drop=True)


def save_report(df, path, fmt="csv"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "json":
        df.to_json(path, orient="records", indent=2, date_format="iso")
    else:
        raise ValueError(f"unsupported format: {fmt}")

    return len(df)


if __name__ == "__main__":
    fx = fx_frame(load_json("frankfurter_series"))
    print(monthly_fx_stats(fx).to_string(index=False))
    print()

    filled = fill_missing_days(fx, "EUR")
    print(f"EUR: {len(fx[fx.currency == 'EUR'])} observed -> {len(filled)} calendar days")
    print()

    pop = population_with_regions()
    by_region = region_population_by_year(pop)
    print(by_region.head(8).to_string(index=False))
    print()
    print(population_growth(by_region, "South Asia").to_string(index=False))
