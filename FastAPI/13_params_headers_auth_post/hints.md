# Unit 13 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `build_headers`

Start with the dictionary that is always the same — `Accept` and `User-Agent` — then decide whether to add a third key.

Read the environment with `os.environ.get(token_env)`. That returns the value if the variable is set and `None` if it isn't, which is one of the two cases you need to reject. The other case is a variable that exists but holds an empty string, and you get that one for free by testing the value with plain truthiness rather than against `None`:

```python
token = os.environ.get(token_env)
if token:
    ...
```

Unit 01's falsy list is doing the work there: both `None` and `""` are falsy, so one `if` covers both. This is one of the rare places where truthiness is exactly the right question — you genuinely want "is there a usable token here", not "is this key present" — which is the distinction unit 01 asked you to keep straight.

---

### `clean_params`

The shape is a loop over `params.items()` building a new dictionary, and the entire difficulty is the order you ask your questions in. Work down this ladder, taking the first branch that matches:

```
if value is None: skip
if isinstance(value, bool): out[key] = "true" if value else "false"
if isinstance(value, str): stripped = value.strip(); skip if empty, else keep the ORIGINAL
if isinstance(value, (list, tuple)): skip if empty, else ",".join(str(v) for v in value)
otherwise: keep as-is
```

`bool` before anything else numeric, and before the generic fallthrough. If a numeric branch or a bare `else` gets to `True` first, it goes out as the capitalised text `"True"` and the test fails with a message that points at the value rather than at your ordering.

Two details in the middle of that ladder. The string case strips only to *decide* — you check whether `value.strip()` is empty, but if it isn't you keep the original value, not the stripped one, because trimming somebody's search term for them is not your call. And `",".join(...)` refuses anything that isn't already a string, so the `str(v)` inside is what makes `ids=[1, 2, 3]` work rather than raising.

Nothing in that ladder mentions `0` or `False`, and that is correct. `0` falls through to the final branch and is kept; `False` is caught by the bool branch and becomes `"false"`. Neither is ever tested for truthiness, which is precisely why neither disappears.

---

### `get_json`

Identical to unit 12's `fetch_json`, with `headers` as a parameter rather than a module constant. Three lines: `requests.get(...)` passing through `params`, `headers` and `timeout`; `response.raise_for_status()`; `return response.json()`.

---

### `post_json`

The whole function, structurally:

```
response = requests.post(url, json=payload, headers=headers, timeout=timeout)
try:
    body = response.json()
except ValueError:
    body = response.text
return response.status_code, body
```

No `raise_for_status` — the whole point is to hand back the error body. If you find yourself reaching for it out of habit, that habit is right everywhere else in this course and wrong here.

`json=payload` rather than `data=payload` is what one of the tests checks explicitly, by asserting that the recorded call had `data` set to `None`. And catching `ValueError` is the right net for a non-JSON body: the JSON decoding error `requests` raises is a subclass of it, so this catches both that and the plain-`json`-module version without you having to name either.

---

### `create_post`

One call and one decision. Build `{"title": title, "body": body, "userId": user_id}` — note `userId`, camel-case, because that is what JSONPlaceholder's own field is called and you send what the API asks for, not what your parameter is named. Pass it to `post_json`, unpack the two returned values, and if the status isn't 201, `raise ValueError(f"create failed: {status} {body}")`. Otherwise return the body.

Putting both the status and the body into the message is the whole reason `post_json` gave them to you.

---

### `daily_weather`

Build the parameters first, and let `clean_params` do the comma joining by handing it a real Python list:

```python
params = clean_params(
    latitude=latitude,
    longitude=longitude,
    daily=["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
    timezone="UTC",
    forecast_days=days,
)
data = get_json(OPEN_METEO, params=params)
daily = data.get("daily") or {}
times = daily.get("time") or []
```

Those last two lines are unit 04's `or {}` pattern, and they are doing real work: they cover both "the key is missing" and "the key is present holding null" in one move, so the two `return []` cases in the spec need no explicit check. If `daily` is missing you end up looping over an empty list of times and returning an empty list naturally.

Now the reshape. Loop over the positions rather than the values, because a position is what ties the four arrays together — `for i in range(len(times))`. Then pull each value out defensively, because a value array may be short or absent entirely:

```python
def at(array, i):
    return array[i] if array and i < len(array) else None
```

That helper is what makes the short/missing-array test pass. Note it checks two things: that the array is truthy at all (covering missing and empty) and that `i` is within it (covering short). Define it once, then build each day's dictionary with `at(daily.get("temperature_2m_max"), i)` and its two siblings, mapping them to the output names `max_c`, `min_c` and `precip_mm`.

Call it as `get_json(...)` (a plain module-level name) — the fixture test replaces `task.get_json`, which only works if you look it up at call time rather than importing it into a local.

---

### `fx_series`

The URL and the parameters are built separately here, because the date range lives in the path:

```python
url = f"{FRANKFURTER}/{start_date}..{end_date}"
params = clean_params(base=base, symbols=symbols)
data = get_json(url, params=params)
rates = data.get("rates") or {}
out = []
for date in sorted(rates):
    for currency in sorted(rates[date]):
        out.append({"date": date, "currency": currency, "rate": rates[date][currency]})
```

`symbols` arrives as a list and `clean_params` joins it, so you do not do anything special with it.

Two things about the loops. `sorted(rates)` sorts a dictionary's *keys*, which here are the date strings — and `sorted()` on ISO date strings sorts chronologically, one of the reasons ISO-8601 is designed the way it is, so no date parsing is needed anywhere in this function. The inner `sorted(rates[date])` does the same for the currency codes, giving you the alphabetical ordering within each date that the spec asks for.

The nested loop is the entire flattening: the outer key becomes a field, the inner key becomes a field, and the value becomes a third. Once you have seen it, you can flatten any dictionary-of-dictionaries on sight.

---

### `summarize_series`

Two passes, and doing it in two is what makes the awkward case fall out for free.

First, group. Walk every row and collect its rate under its currency, using unit 04's grouping idiom — `groups.setdefault(row["currency"], []).append(...)`. Do this for *every* row, including the ones whose rate is `None`, or filter the `None`s here but make sure the currency key still gets created. Either way, the requirement is that a currency which appears at all ends up with a key, even if its list of usable rates is empty.

Then compute. For each currency, take the rates that aren't `None`. If there are none left, the answer is `{"count": 0, "min": None, "max": None, "mean": None}` — guard this before you compute anything, because the mean is `sum(values) / len(values)` and dividing by zero raises. Otherwise it's `len`, `min`, `max`, and that division, each of the last three wrapped in `round(x, 4)`.

If you group first and only then filter, both of those conditions are handled by structure rather than by special cases, which is generally the sign you have picked the right order.
