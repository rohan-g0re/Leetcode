"""Unit 17 — worked solution."""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"

TEXT_COLUMNS = ["code", "name", "region", "income_level", "capital"]


def load_json(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def repos_frame():
    rows = []
    for repo in load_json("github_repos_pallets"):
        rows.append(
            {
                "name": repo.get("name"),
                "language": repo.get("language"),
                "stars": repo.get("stargazers_count") or 0,
                "forks": repo.get("forks_count") or 0,
                "open_issues": repo.get("open_issues_count") or 0,
                "archived": bool(repo.get("archived")),
                "license": (repo.get("license") or {}).get("name"),
                "created": repo.get("created_at"),
            }
        )
    return pd.DataFrame(rows)


def overview(df):
    return {
        "rows": int(len(df)),
        "columns": list(df.columns),
        "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
        "missing": {column: int(count) for column, count in df.isna().sum().items()},
    }


def filter_repos(df, min_stars=0, language=None, include_archived=False):
    mask = df["stars"] >= min_stars
    if language is not None:
        mask = mask & (df["language"] == language)
    if not include_archived:
        mask = mask & (~df["archived"])
    return df.loc[mask].reset_index(drop=True)


def add_metrics(df):
    out = df.copy()

    ratio = out["forks"] / out["stars"].where(out["stars"] != 0)
    out["fork_ratio"] = ratio.round(3)

    out["popularity"] = "low"
    out.loc[out["stars"] >= 1000, "popularity"] = "medium"
    out.loc[out["stars"] >= 10000, "popularity"] = "high"

    out["has_license"] = out["license"].notna()
    return out


def language_summary(df):
    out = df.copy()
    out["language"] = out["language"].fillna("unknown")

    summary = (
        out.groupby("language")
        .agg(
            repos=("name", "count"),
            total_stars=("stars", "sum"),
            mean_stars=("stars", "mean"),
            max_stars=("stars", "max"),
        )
        .reset_index()
    )
    summary["mean_stars"] = summary["mean_stars"].round(1)
    return summary.sort_values(
        ["total_stars", "language"], ascending=[False, True]
    ).reset_index(drop=True)


def countries_frame():
    records = load_json("worldbank_countries")[1]
    df = pd.json_normalize(records, sep=".")

    df = df.rename(
        columns={
            "id": "code",
            "region.value": "region",
            "incomeLevel.value": "income_level",
            "capitalCity": "capital",
        }
    )[["code", "name", "region", "income_level", "capital", "latitude", "longitude"]]

    for column in TEXT_COLUMNS:
        df[column] = df[column].str.strip().replace("", pd.NA)

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    return df


def region_stats(df):
    known = df.loc[df["region"].notna()]

    stats = (
        known.groupby("region")
        .agg(
            countries=("code", "count"),
            with_capital=("capital", "count"),
            mean_latitude=("latitude", "mean"),
        )
        .reset_index()
    )
    stats["mean_latitude"] = stats["mean_latitude"].round(2)
    return stats.sort_values(
        ["countries", "region"], ascending=[False, True]
    ).reset_index(drop=True)


def to_records(df, limit=None):
    subset = df if limit is None else df.head(limit)
    cleaned = subset.astype(object).where(subset.notna(), None)
    return cleaned.to_dict("records")


if __name__ == "__main__":
    repos = repos_frame()
    print(json.dumps(overview(repos), indent=2))
    print()
    print(language_summary(repos).to_string(index=False))
    print()
    countries = countries_frame()
    print(region_stats(countries).to_string(index=False))
