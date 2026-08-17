# Unit 14 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `find_records`

Start by writing the test as its own tiny function, because you are going to need it in three different places and repeating it three times is how you end up with three subtly different versions:

```python
def is_record_list(value):
    return isinstance(value, list) and value and isinstance(value[0], dict)
```

Read that as three conditions in a row: it has to be a list, it has to be non-empty (an empty list is falsy, so plain `value` covers it), and its first element has to be a dictionary. Checking only the first element rather than all of them is a deliberate shortcut — it is right often enough and it costs nothing on a list of ten thousand.

Now the structure. There are three cases, decided by what `data` itself is:

```python
if isinstance(data, list):
    inner = [v for v in data if is_record_list(v)]      # array envelope
    if inner:
        return max(inner, key=len)
    return data if is_record_list(data) else []
if isinstance(data, dict):
    candidates = [v for v in data.values() if is_record_list(v)]
    return max(candidates, key=len) if candidates else []
return []
```

The last line is doing more than it looks like. Anything that is neither a list nor a dict — `None`, a number, a string — falls straight through to `return []`, so all the odd inputs in the edge-case test are handled by that one line without a single special case.

The ordering inside the list branch is the thing worth staring at. The array-envelope check has to come **before** "is `data` itself a record list", because `[{"page": 1}, [...]]` satisfies both descriptions and the inner list is the one you want. Swap those two and the World Bank test hands you back 2 records instead of 295, with no error to tell you why.

`max(..., key=len)` is how you implement "prefer the longest": it compares candidates by their length and returns the actual list, not the length. That is the same `key=` idea as unit 07's sorting.

---

### `profile_fields`

One pass over the records, building the result dictionary as you go. For each record, loop over its `.items()` so you get the key and the value together, and for each key either create its entry or update the existing one.

Three things to track per field, and the trick is to track types in a `set` while you are looping and convert it with `sorted()` only at the end. A set collapses duplicates for you, so seeing `"str"` four hundred times costs you nothing, and sorting at the end makes the output stable enough to compare against a test.

`type(value).__name__` is what turns a value into the name of its type as plain text — `"int"`, `"str"`, `"dict"`, `"list"`. Without `.__name__` you get the noisier `<class 'int'>`.

Two ordering details that the tests check directly. Increment `present` for every key you meet, whether or not its value is `None` — presence is about the key existing. Then, if the value *is* `None`, increment `null` and record no type at all; if it isn't, add its type name to the set. Getting that branch backwards gives you `"NoneType"` in the types list and makes almost every optional field look inconsistent.

Records with no fields, and an empty list of records, both need to produce `{}` — which they will do on their own if you start from an empty dictionary and only ever add to it.

---

### `inconsistent_fields`

Do not write a second pass. Call `profile_fields(records)` and filter its output: keep the field names whose `present` is less than `len(records)`, and return them `sorted()`.

The empty-input case works out by itself — `profile_fields([])` is `{}`, so there is nothing to filter and you return `[]`.

---

### `walk_paths`

Recursive, and returning a list rather than using `yield`, so the whole thing is ordinary code you can `print()` in the middle of:

```python
if isinstance(data, dict) and data:
    out = []
    for key, value in data.items():
        child = f"{prefix}.{key}" if prefix else key
        out.extend(walk_paths(value, child))
    return out
if isinstance(data, list) and data:
    out = []
    for i, value in enumerate(data):
        out.extend(walk_paths(value, f"{prefix}[{i}]"))
    return out
return [(prefix, data)]
```

Take that in three pieces.

The last line is the base case — the thing that stops the recursion. If you got here, `data` is not a container worth descending into, so you report exactly one pair: the path you travelled to get here, and the value you found. Every recursive function needs a line like this or it never terminates.

The two branches above it each do the same thing in different clothing: they cannot answer the question themselves, so they break it into smaller questions and hand each one back to `walk_paths`. `out.extend(...)` rather than `out.append(...)` is important — each nested call returns a *list* of pairs, and you want those pairs added individually rather than added as one nested item. That is unit 03's `append` versus `extend` distinction showing up again.

The `if prefix else key` on the child path is a small detail with a visible effect. At the very top level `prefix` is `""`, and joining with a dot would give you `".name"` with a leading dot on every single path. The conditional says "put a dot between them only if there is something on the left."

The `and data` on both container checks is what makes an empty dict or list fall through to the leaf case at the bottom, which is the specified behaviour. Without it, an empty container enters the loop, the loop body never runs, and it returns an empty list — so the path disappears from the output entirely instead of appearing as `("a", [])`.

---

### `search_paths`

One line, built on the function you just wrote rather than on a second traversal:

```python
[(p, v) for p, v in walk_paths(data) if needle.lower() in p.lower()]
```

Lowercasing both sides is what makes the match case-insensitive, and `in` on two strings is a substring test — so `"name"` matches `"user.name"` and `"userName"` alike.

---

### `flatten_worldbank_countries`

Two small helper functions make this readable, and writing them separately is worth it because you use each of them several times:

```python
def clean(value):
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    return stripped or None

def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
```

`clean` handles two of the quirks at once. It strips the trailing spaces the API sends, and then `stripped or None` turns anything that was blank — or was only whitespace — into `None`, because an empty string is falsy. The `isinstance` guard at the top means you can pass it anything without thinking; non-strings come back untouched.

`as_float` is unit 08's `try`/`except` doing exactly what it exists for. `float("")` and `float(None)` both raise, one with `ValueError` and one with `TypeError`, and catching both means the caller never has to check what it is passing in.

With those in hand, the body is a loop over `find_records(payload)` building one dictionary per country. For the nested fields, `(record.get("region") or {}).get("value")` gets you the label safely, and then you run it through `clean`. The `or {}` matters here rather than being belt-and-braces, because these nested dicts are genuinely absent on some rows.

---

### `summarize_by_region`

`Counter` over the regions that are not `None`, then sort its items with a two-part key:

```python
sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
```

`kv` is one `(region, count)` pair, so `kv[1]` is the count and `kv[0]` is the region. Negating the count makes larger counts sort first, since ascending order on negative numbers is descending order on the originals, and the un-negated region name breaks ties alphabetically. Same trick as unit 03's `top_n`.

---

### `flatten_hn_hits`

Use `find_records(payload)` to get the hits rather than `payload["hits"]` — the tests feed it both real fixture data and small synthetic payloads, and going through your own function is the point of having written it.

For the id, `str(hit.get("objectID"))`. It arrives as a string from the real API but as an int in one of the synthetic tests, and `str()` flattens that difference without you having to care which you got.

For the domain, `urlparse(url).netloc.lower()` — `netloc` is the host part, everything between the `//` and the next `/`. Guard the whole thing with `if url`, because `url` is `None` on Ask HN posts and `urlparse(None)` raises.

For the date, `created[:10] if created else None`. The first ten characters of an ISO timestamp are exactly the `YYYY-MM-DD` part, which is why the test checks the length is 10.

For the numbers, remember that the field can be missing *or* present holding `None`, and both have to become `0`. `hit.get("points") or 0` covers both in one expression — though notice it also turns a genuine `0` into `0`, which is harmless here, and would not be if the field were something where zero and missing meant different things.

---

### `pokemon_profile`

Handle the lists first, because types and abilities follow identical shapes:

```python
types = sorted(payload.get("types") or [], key=lambda t: t.get("slot", 0))
type_names = [(t.get("type") or {}).get("name") for t in types]
```

Read the first line right to left: get the types list, substitute an empty list if it is missing or `None`, then sort what you have by each entry's slot number, defaulting to `0` if an entry has no slot. Sorting an empty list is fine and gives you an empty list, so the empty-payload case needs no special handling.

The second line is the four-level reach, done in two safe steps rather than one risky one. Abilities are the same pattern with `"abilities"` and `"ability"` swapped in.

For stats, loop over `payload.get("stats") or []` and build the dictionary as you go, taking the name from `(s.get("stat") or {}).get("name")` and the value from `s.get("base_stat")`. Then `total_stats` is `sum(...)` over the values you collected — and summing an empty dictionary's values gives `0` for free, which is what the empty-payload test expects. If you want to be thorough, filter out any `None` values before summing, since `sum` will raise on them.
