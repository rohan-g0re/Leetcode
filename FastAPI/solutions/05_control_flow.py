"""Unit 05 — worked solution."""


def classify_status(code):
    if code == 429:
        return "rate_limited"
    if 200 <= code < 300:
        return "success"
    if 300 <= code < 400:
        return "redirect"
    if 400 <= code < 500:
        return "client_error"
    if 500 <= code < 600:
        return "server_error"
    return "unknown"


def should_retry(code, attempt, max_attempts=3):
    retryable = code == 429 or code >= 500
    return retryable and attempt < max_attempts - 1


def first_match(records, field, value):
    for record in records:
        if record.get(field) == value:
            return record
    return None


def find_index_of_drop(values):
    for i in range(1, len(values)):
        if values[i] < values[i - 1]:
            return i
    return None


def fizz_report(n):
    out = []
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            out.append("both")
        elif i % 3 == 0:
            out.append("low")
        elif i % 5 == 0:
            out.append("high")
        else:
            out.append(str(i))
    return out


def collect_pages(fetch_page, max_pages=10):
    out = []
    page = 1
    while page <= max_pages:
        batch = fetch_page(page)
        if not batch:
            break
        out.extend(batch)
        page += 1
    return out


def collect_until(fetch_page, target_count, max_pages=10):
    out = []
    page = 1
    while page <= max_pages:
        batch = fetch_page(page)
        if not batch:
            break
        out.extend(batch)
        if len(out) >= target_count:
            break
        page += 1
    return out
