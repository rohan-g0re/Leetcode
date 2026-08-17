"""Unit 01 — worked solution.

Copy over 01_values_and_types/task.py only AFTER you have fought the problem.
"""


def describe_type(value):
    return type(value).__name__.lower()


def safe_divide(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator


def is_missing(value):
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False


def _looks_numeric(text):
    """True if `text` is a plain decimal number, optionally signed."""
    if text.startswith("-") or text.startswith("+"):
        text = text[1:]
    if text.count(".") > 1:
        return False
    digits = text.replace(".", "")
    return digits.isdigit()


def coerce_number(value):
    if value is None:
        return None
    # bool must be tested before int: isinstance(True, int) is True
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if _looks_numeric(text):
            return float(text)
        return None
    return None


def bucket(n, size):
    if size <= 0:
        return None
    return n // size


def percent_change(old, new):
    if old == 0:
        return None
    return round((new - old) / old * 100, 2)


def clamp(value, low, high):
    return max(low, min(value, high))


def format_summary(name, count, average):
    avg_text = "n/a" if average is None else f"{average:.2f}"
    return f"{name}: {count} items, avg {avg_text}"
