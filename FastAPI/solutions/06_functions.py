"""Unit 06 — worked solution."""


def average(values, default=None):
    usable = [v for v in values if v is not None]
    if not usable:
        return default
    return sum(usable) / len(usable)


def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


def build_url(base, *path_parts, **query):
    url = base.rstrip("/")
    for part in path_parts:
        url = f"{url}/{part}"
    pairs = [f"{key}={value}" for key, value in query.items() if value is not None]
    if pairs:
        url = f"{url}?{'&'.join(pairs)}"
    return url


def apply_to_field(records, field, func):
    out = []
    for record in records:
        copy = dict(record)
        if field in copy and copy[field] is not None:
            copy[field] = func(copy[field])
        out.append(copy)
    return out


def make_counter():
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


def retry_call(func, attempts=3, on_error=None):
    for _ in range(attempts):
        result = func()
        if result is not None:
            return result
    return on_error


def compose(*funcs):
    def composed(value):
        for func in funcs:
            value = func(value)
        return value

    return composed
