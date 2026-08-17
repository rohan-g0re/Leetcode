"""Unit 18 — worked solution."""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"

HN_COLUMNS = [
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
HOST_PATTERN = r"^[a-zA-Z]+://([^/?#]+)"


def load_json(name):
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def normalize_columns(df):
    out = df.copy()
    out.columns = [
        str(column).strip().lower().replace(".", "_").replace(" ", "_").replace("-", "_")
        for column in out.columns
    ]
    return out


def coerce_numeric(df, columns, integer=False):
    out = df.copy()
    for column in columns:
        if column not in out.columns:
            continue
        converted = pd.to_numeric(out[column], errors="coerce")
        out[column] = converted.astype("Int64") if integer else converted
    return out


def coerce_datetime(df, columns):
    out = df.copy()
    for column in columns:
        if column in out.columns:
            out[column] = pd.to_datetime(out[column], errors="coerce", utc=True)
    return out


def quality_report(df, key=None):
    missing = {
        str(column): int(count)
        for column, count in df.isna().sum().items()
        if count > 0
    }
    duplicates = 0
    if key is not None and key in df.columns:
        duplicates = int(df.duplicated(subset=[key]).sum())

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing": missing,
        "duplicates": duplicates,
        "empty": bool(df.empty),
    }


def hn_frame(payload):
    hits = (payload or {}).get("hits") or []
    if not hits:
        return pd.DataFrame(columns=HN_COLUMNS)

    df = pd.DataFrame(hits)
    for column in ("objectID", "title", "author", "points", "num_comments", "url", "created_at"):
        if column not in df.columns:
            df[column] = None

    df = df[["objectID", "title", "author", "points", "num_comments", "url", "created_at"]]
    df = df.rename(
        columns={
            "objectID": "id",
            "num_comments": "comments",
            "created_at": "created",
        }
    )

    df["id"] = df["id"].astype(str)
    df = coerce_numeric(df, ["points", "comments"], integer=True)
    df = coerce_datetime(df, ["created"])

    df["domain"] = df["url"].astype("string").str.extract(HOST_PATTERN, expand=False).str.lower()
    df["month"] = df["created"].dt.strftime("%Y-%m")

    df = df.loc[df["id"].notna() & (df["id"] != "None")]
    return df[HN_COLUMNS].reset_index(drop=True)


def population_frame(payload):
    records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    if not records:
        return pd.DataFrame(columns=["country_code", "country_name", "year", "population"])

    df = normalize_columns(pd.json_normalize(records, sep="."))
    df = df.rename(
        columns={
            "countryiso3code": "country_code",
            "country_value": "country_name",
            "date": "year",
            "value": "population",
        }
    )

    for column in ("country_code", "country_name"):
        df[column] = df[column].astype("string").str.strip().replace("", pd.NA)

    df = coerce_numeric(df, ["year", "population"], integer=True)
    df = df.loc[df["country_code"].notna()]

    return (
        df[["country_code", "country_name", "year", "population"]]
        .sort_values(["country_code", "year"])
        .reset_index(drop=True)
    )


def posts_with_users():
    posts = pd.DataFrame(load_json("placeholder_posts"))
    users = normalize_columns(pd.json_normalize(load_json("placeholder_users"), sep="."))

    users = users.rename(
        columns={
            "id": "user_id",
            "name": "user_name",
            "address_city": "user_city",
            "company_name": "company",
        }
    )[["user_id", "user_name", "user_city", "company"]]

    merged = posts.rename(columns={"id": "post_id", "userId": "user_id"}).merge(
        users, on="user_id", how="left"
    )
    merged["title_length"] = merged["title"].astype("string").str.len()

    return (
        merged[["post_id", "user_id", "user_name", "user_city", "company", "title_length"]]
        .sort_values("post_id")
        .reset_index(drop=True)
    )


def top_domains(df, n=5):
    columns = ["domain", "stories", "total_points"]
    if df.empty or "domain" not in df.columns:
        return pd.DataFrame(columns=columns)

    known = df.loc[df["domain"].notna()].copy()
    if known.empty:
        return pd.DataFrame(columns=columns)

    known["points"] = pd.to_numeric(known.get("points"), errors="coerce").fillna(0)

    grouped = (
        known.groupby("domain")
        .agg(stories=("domain", "count"), total_points=("points", "sum"))
        .reset_index()
    )
    grouped["total_points"] = grouped["total_points"].astype("int64")

    return (
        grouped.sort_values(["stories", "domain"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    hn = hn_frame(load_json("hn_search_python"))
    print(json.dumps(quality_report(hn, key="id"), indent=2))
    print()
    print(hn.head().to_string(index=False))
    print()
    print(top_domains(hn).to_string(index=False))
    print()
    pop = population_frame(load_json("worldbank_population"))
    print(pop.head().to_string(index=False))
