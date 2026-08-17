"""Unit 13 — worked solution."""

import json
import os

import requests

TIMEOUT = 25
PLACEHOLDER = "https://jsonplaceholder.typicode.com"
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
FRANKFURTER = "https://api.frankfurter.dev/v1"

DAILY_FIELDS = ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"]


def build_headers(user_agent="python-api-course/1.0", token_env="API_TOKEN"):
    headers = {"Accept": "application/json", "User-Agent": user_agent}
    token = os.environ.get(token_env)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def clean_params(**params):
    cleaned = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            cleaned[key] = "true" if value else "false"
        elif isinstance(value, str):
            if value.strip():
                cleaned[key] = value
        elif isinstance(value, (list, tuple)):
            if value:
                cleaned[key] = ",".join(str(item) for item in value)
        else:
            cleaned[key] = value
    return cleaned


def get_json(url, params=None, headers=None, timeout=TIMEOUT):
    response = requests.get(url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def post_json(url, payload, headers=None, timeout=TIMEOUT):
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return response.status_code, body


def create_post(title, body, user_id=1):
    status, response_body = post_json(
        f"{PLACEHOLDER}/posts",
        {"title": title, "body": body, "userId": user_id},
        headers=build_headers(),
    )
    if status != 201:
        raise ValueError(f"create failed: {status} {response_body}")
    return response_body


def _at(array, index):
    """Element `index` of `array`, or None when it isn't there."""
    if not array or index >= len(array):
        return None
    return array[index]


def daily_weather(latitude, longitude, days=7):
    params = clean_params(
        latitude=latitude,
        longitude=longitude,
        daily=DAILY_FIELDS,
        timezone="UTC",
        forecast_days=days,
    )
    data = get_json(OPEN_METEO, params=params, headers=build_headers())

    daily = data.get("daily") or {}
    times = daily.get("time") or []
    highs = daily.get("temperature_2m_max") or []
    lows = daily.get("temperature_2m_min") or []
    precip = daily.get("precipitation_sum") or []

    return [
        {
            "date": times[i],
            "max_c": _at(highs, i),
            "min_c": _at(lows, i),
            "precip_mm": _at(precip, i),
        }
        for i in range(len(times))
    ]


def fx_series(base, symbols, start_date, end_date):
    url = f"{FRANKFURTER}/{start_date}..{end_date}"
    params = clean_params(base=base, symbols=symbols)
    data = get_json(url, params=params, headers=build_headers())

    rates = data.get("rates") or {}
    rows = []
    for date in sorted(rates):
        by_currency = rates[date] or {}
        for currency in sorted(by_currency):
            rows.append(
                {"date": date, "currency": currency, "rate": by_currency[currency]}
            )
    return rows


def summarize_series(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["currency"], []).append(row.get("rate"))

    summary = {}
    for currency, rates in grouped.items():
        usable = [rate for rate in rates if rate is not None]
        if usable:
            summary[currency] = {
                "count": len(usable),
                "min": round(min(usable), 4),
                "max": round(max(usable), 4),
                "mean": round(sum(usable) / len(usable), 4),
            }
        else:
            summary[currency] = {"count": 0, "min": None, "max": None, "mean": None}
    return summary


if __name__ == "__main__":
    print("headers:", build_headers())
    print("\nweather in Berlin:")
    for day in daily_weather(52.52, 13.41, days=3):
        print(" ", day)
    print("\nUSD rates:")
    rows = fx_series("USD", ["EUR", "GBP"], "2024-01-02", "2024-01-05")
    print(json.dumps(summarize_series(rows), indent=2))
