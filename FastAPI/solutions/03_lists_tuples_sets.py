"""Unit 03 — worked solution."""


def dedupe_preserving_order(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def chunk(items, size):
    if size <= 0:
        return []
    out = []
    for start in range(0, len(items), size):
        out.append(items[start : start + size])
    return out


def flatten(nested):
    out = []
    for inner in nested:
        out.extend(inner)
    return out


def min_max(numbers):
    if not numbers:
        return None
    return (min(numbers), max(numbers))


def compare_id_sets(left, right):
    left_set = set(left)
    right_set = set(right)
    return (
        sorted(left_set - right_set),
        sorted(right_set - left_set),
        sorted(left_set & right_set),
    )


def running_total(numbers):
    out = []
    total = 0
    for n in numbers:
        total += n
        out.append(total)
    return out


def top_n(pairs, n):
    ranked = sorted(pairs, key=lambda pair: (-pair[1], pair[0]))
    out = []
    for label, _score in ranked[:n]:
        out.append(label)
    return out


def pair_with_next(items):
    out = []
    for i in range(len(items) - 1):
        out.append((items[i], items[i + 1]))
    return out


def merge_sorted(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out
