"""Unit 02 — worked solution."""

PUNCT = ".,!?:;\"'()[]"


def normalize_key(raw):
    cleaned = raw.replace("-", " ").strip().lower()
    return "_".join(cleaned.split())


def parse_iso_date(text):
    if not isinstance(text, str) or not text:
        return None
    date_part = text.split("T")[0]
    parts = date_part.split("-")
    if len(parts) != 3:
        return None
    if not all(p.isdigit() for p in parts):
        return None
    return tuple(int(p) for p in parts)


def truncate(text, limit):
    if len(text) <= limit:
        return text
    if limit <= 3:
        return "..."[:limit]
    return text[: limit - 3] + "..."


def extract_domain(url):
    if "://" not in url:
        return None
    after_scheme = url.split("://", 1)[1]
    host = after_scheme.split("?")[0].split("/")[0]
    return host.lower() or None


def build_query_string(params):
    pairs = [f"{key}={value}" for key, value in params.items() if value is not None]
    return "&".join(pairs)


def title_words(text, min_length=4):
    words = set()
    for raw in text.split():
        word = raw.strip(PUNCT).lower()
        if len(word) >= min_length:
            words.add(word)
    return sorted(words)


def format_table_row(cells, widths):
    padded = [f"{cell:<{width}}" for cell, width in zip(cells, widths)]
    return " | ".join(padded).rstrip()
