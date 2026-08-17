"""Unit 04 — worked solution."""


def deep_get(data, *keys, default=None):
    current = data
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def pluck(records, key, default=None):
    return [record.get(key, default) for record in records]


def index_by(records, key):
    out = {}
    for record in records:
        if key in record:
            out[record[key]] = record
    return out


def group_by(records, key):
    out = {}
    for record in records:
        out.setdefault(record.get(key), []).append(record)
    return out


def select_fields(record, fields):
    return {field: record[field] for field in fields if field in record}


def rename_keys(record, mapping):
    return {mapping.get(key, key): value for key, value in record.items()}


def count_missing(records, fields):
    counts = {field: 0 for field in fields}
    for record in records:
        for field in fields:
            if field not in record or record[field] is None:
                counts[field] += 1
    return counts


def flatten_dict(data, prefix="", sep="."):
    out = {}
    for key, value in data.items():
        full_key = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flatten_dict(value, full_key + sep, sep))
        else:
            out[full_key] = value
    return out


def summarize_records(records, numeric_field, category_field):
    grouped = group_by(records, category_field)
    summary = {}
    for category, group in grouped.items():
        values = [
            r[numeric_field]
            for r in group
            if numeric_field in r and r[numeric_field] is not None
        ]
        total = sum(values)
        summary[category] = {
            "count": len(values),
            "total": total,
            "mean": round(total / len(values), 2) if values else None,
        }
    return summary
