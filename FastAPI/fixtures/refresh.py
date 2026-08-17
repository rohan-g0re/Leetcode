"""Re-record the fixture files from the live APIs.

    python fixtures/refresh.py

The course ships with these already recorded, so you never need to run this. It
exists for two reasons:

1. If an endpoint changes shape, you can re-record and see the diff.
2. Reading it is a decent worked example of the fetch-and-save pattern before
   you get to unit 12.

Each entry says where the data came from and how much of it we keep. Responses
are trimmed so the repo stays small -- the SHAPE is untouched, which is the part
that matters for practice.
"""

import json
from pathlib import Path

import requests

HERE = Path(__file__).parent
TIMEOUT = 20
HEADERS = {"Accept": "application/json", "User-Agent": "python-api-course/1.0"}


def get(url, **params):
    response = requests.get(url, params=params or None, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def save(name, data):
    path = HERE / f"{name}.json"
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    size = path.stat().st_size
    print(f"  wrote {path.name:32} {size / 1024:6.1f} KB")


def main():
    print("recording fixtures...")

    # A single entity: one GitHub organisation account.
    save("github_user_pallets", get("https://api.github.com/users/pallets"))

    # A list of entities, each deeply nested (owner, license, permissions...).
    repos = get("https://api.github.com/users/pallets/repos", per_page=100)
    save("github_repos_pallets", repos)

    # Deeply nested single entity with several inner arrays.
    save("pokemon_ditto", get("https://pokeapi.co/api/v2/pokemon/ditto"))

    # An envelope: metadata keys wrapped around the actual list.
    save(
        "hn_search_python",
        get(
            "https://hn.algolia.com/api/v1/search",
            query="python",
            tags="story",
            hitsPerPage=50,
        ),
    )

    # Flat, well-behaved records. The friendly case.
    save("placeholder_posts", get("https://jsonplaceholder.typicode.com/posts"))
    save("placeholder_users", get("https://jsonplaceholder.typicode.com/users"))

    # Parallel arrays instead of records -- a shape that needs reshaping.
    save(
        "open_meteo_berlin",
        get(
            "https://api.open-meteo.com/v1/forecast",
            latitude=52.52,
            longitude=13.41,
            daily="temperature_2m_max,temperature_2m_min,precipitation_sum",
            timezone="UTC",
            forecast_days=16,
        ),
    )

    # A dict-of-dicts time series keyed by date string.
    save(
        "frankfurter_series",
        get(
            "https://api.frankfurter.dev/v1/2024-01-01..2024-03-31",
            base="USD",
            symbols="EUR,GBP,INR,JPY",
        ),
    )

    # World Bank: a two-element array envelope -- [metadata, records]. Also
    # full of numbers-as-strings and empty-string-instead-of-null, which is
    # exactly the mess you want practice on.
    countries = get("https://api.worldbank.org/v2/country", format="json", per_page=400)
    save("worldbank_countries", countries)

    # A time series from the same API: population per country per year.
    population = get(
        "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL",
        format="json",
        per_page=1000,
        date="2018:2023",
    )
    save("worldbank_population", population)

    print("done")


if __name__ == "__main__":
    main()
