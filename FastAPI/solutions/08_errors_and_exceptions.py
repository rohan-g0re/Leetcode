"""Unit 08 — worked solution."""


class ValidationError(Exception):
    """Raised when input data fails a check we care about."""


def to_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_field(record, *keys, default=None):
    current = record
    try:
        for key in keys:
            current = current[key]
    except (KeyError, TypeError, IndexError):
        return default
    return current


def parse_records(raw_records):
    good = []
    failures = []
    for record in raw_records:
        if "id" not in record:
            failures.append({"id": None, "error": "missing id"})
            continue
        if "amount" not in record:
            failures.append({"id": record["id"], "error": "missing amount"})
            continue
        amount = to_float(record["amount"])
        if amount is None:
            failures.append({"id": record["id"], "error": "bad amount"})
            continue
        good.append({"id": record["id"], "amount": amount})
    return good, failures


def validate_page_size(size):
    if isinstance(size, bool) or not isinstance(size, int) or not 1 <= size <= 100:
        raise ValidationError(f"page_size must be an int in 1..100, got {size!r}")
    return size


def first_successful(funcs, default=None):
    for func in funcs:
        try:
            return func()
        except Exception:
            continue
    return default


def describe_exception(func):
    try:
        func()
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return "ok"


def divide_all(pairs):
    out = []
    for a, b in pairs:
        try:
            out.append(a / b)
        except (ZeroDivisionError, TypeError):
            out.append(None)
    return out
