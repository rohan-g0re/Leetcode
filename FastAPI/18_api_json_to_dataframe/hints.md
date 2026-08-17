# Unit 18 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `normalize_columns`

Take a copy first, then throw away the old column names and build new ones. A DataFrame's `.columns` can be assigned a plain list, so you don't need any special renaming machinery — a list comprehension over the existing names is the whole job:

```python
out = df.copy()
out.columns = [
    str(column).strip().lower().replace(".", "_")  # ...and the other two replacements
    for column in out.columns
]
```

The order of those calls matters. Strip *first*, so `" x "` loses its surrounding spaces before you start substituting; if you replace spaces first you get `"_x_"` instead of `"x"`, and one of the tests checks exactly that name. Three separate `.replace` calls handle the dot, the space, and the hyphen — they chain, since each one returns a new string.

The `str(...)` wrapper is cheap insurance: column names are usually strings but don't have to be, and calling `.strip()` on an integer raises.

Returning a copy rather than mutating in place is the other thing a test checks. `df.copy()` at the top and only ever touching `out` is all it takes.

---

### `coerce_numeric`

Loop over the requested columns, skip the ones that aren't there, and convert the rest:

```python
for column in columns:
    if column not in out.columns:
        continue
    converted = pd.to_numeric(out[column], errors="coerce")
    out[column] = converted.astype("Int64") if integer else converted
```

Two things to notice. The `continue` is what makes the function safe to call with a column list that doesn't match this particular payload — silently skipping is what the docstring asks for, not raising.

And the `.astype("Int64")` has to come *after* `to_numeric`, not instead of it. `to_numeric` is what turns the strings into numbers and the junk into NaN; `astype` only changes how the numbers are stored. Going straight to `.astype("Int64")` on a text column raises. Capital I, incidentally — lowercase `int64` is the non-nullable one and will refuse the NaN you just created.

---

### `coerce_datetime`

Same shape as `coerce_numeric` but simpler, because there's no integer branch:

```python
for column in columns:
    if column in out.columns:
        out[column] = pd.to_datetime(out[column], errors="coerce", utc=True)
```

Both keyword arguments earn their place. `errors="coerce"` turns an unparseable timestamp into `NaT` instead of raising; `utc=True` is what makes the result a genuine timezone-aware datetime column when the input mixes `Z` and `+05:30` offsets. Drop `utc=True` and the test asserting `out["d"].dt.tz is not None` fails — and so does every `.dt` call downstream in `hn_frame`.

---

### `quality_report`

Build the `missing` dictionary from `df.isna().sum()`, which gives you a Series indexed by column name. Iterate its `.items()` and keep only the non-zero entries:

```python
missing = {
    str(column): int(count)
    for column, count in df.isna().sum().items()
    if count > 0
}
```

Every number in this function needs an `int(...)` around it and the boolean needs a `bool(...)`. That isn't superstition — pandas counts in numpy, so `len(df)`, `.sum()`, and `df.empty` hand you numpy scalars, and `json.dumps` refuses to serialize them with `TypeError: Object of type int64 is not JSON serializable`. The tests call `json.dumps` on your result specifically to catch this.

The duplicates part has two conditions to get through before you count anything:

```python
duplicates = 0
if key is not None and key in df.columns:
    duplicates = int(df.duplicated(subset=[key]).sum())
```

`df.duplicated(subset=[key])` marks every row after the first occurrence of each key value, so summing it gives you the number of *extra* copies — which is why the three-row test frame with two rows sharing `id` 1 reports `1` and not `2`.

---

### `hn_frame`

Get the rows out of the envelope defensively, since the payload might be missing `hits` entirely or have it empty:

```python
hits = (payload or {}).get("hits") or []
if not hits:
    return pd.DataFrame(columns=HN_COLUMNS)
```

That `or {}` is unit 04's trick — it survives a payload that's `None` as well as one that's a dictionary without the key. Define `HN_COLUMNS` once as a module-level list of the nine final column names and use it both here and in the final selection, so the empty case and the populated case can never disagree about what the frame looks like.

The seven source fields might not all be present in a sparse payload, so create the missing ones before you select:

```python
for column in ("objectID", "title", "author", "points", "num_comments", "url", "created_at"):
    if column not in df.columns:
        df[column] = None
```

Then select those seven in order, `rename` the three that change name (`objectID` → `id`, `num_comments` → `comments`, `created_at` → `created`), and run your own helpers over the result: `coerce_numeric(df, ["points", "comments"], integer=True)` and `coerce_datetime(df, ["created"])`. The id is `.astype(str)` — the test checks every value is genuinely a Python `str`.

Domain extraction, vectorized:

```python
df["domain"] = df["url"].astype("string").str.extract(r"^[a-zA-Z]+://([^/?#]+)", expand=False).str.lower()
```

Reading that left to right: `.astype("string")` puts the column into pandas' nullable text type so the `.str` methods behave predictably around nulls. `.str.extract` runs the regex over every value and returns what the parentheses captured — the scheme and `://` have to match but are discarded, and `[^/?#]+` takes everything up to the first slash, question mark, or hash, which is the host. `expand=False` asks for a Series back rather than a one-column DataFrame. Rows where the pattern doesn't match, including the null urls of text-only stories, come out as NA with no error, which is exactly the behaviour you want. `.str.lower()` at the end stops `Example.com` and `example.com` counting as two sources.

For the month, `df["created"].dt.strftime("%Y-%m")` formats the whole column at once and gives NA rather than the string `"NaT"` where the timestamp didn't parse.

One last wrinkle on dropping rows with no id: because you called `.astype(str)` on the id column, a genuinely missing id has already become the literal four-character string `"None"`. So the filter needs to catch both shapes — `df["id"].notna() & (df["id"] != "None")` — and then `.reset_index(drop=True)` so the row labels are 0..n again.

---

### `population_frame`

The records are the second element of the payload, and the first is metadata you don't want:

```python
records = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
```

`pd.json_normalize(records, sep=".")` flattens the nested `country` dictionary into `country.value`; `normalize_columns` then turns that into `country_value`. Do all four renames in a single `df.rename(columns={...})` call — `countryiso3code` → `country_code`, `country_value` → `country_name`, `date` → `year`, `value` → `population` — so the whole mapping reads as one table.

Now the trap. This API sends `""` rather than `null` for aggregate regions with no ISO code, and an empty string is not missing as far as pandas is concerned, so `.dropna()` walks straight past it. Convert it explicitly before you filter:

```python
for column in ("country_code", "country_name"):
    df[column] = df[column].astype("string").str.strip().replace("", pd.NA)
```

Strip first, then replace, so a code of `"  "` also becomes NA. If you drop on `country_code` before doing this, the blank-coded rows survive and your row count comes out well above the 970 the test expects.

Then `coerce_numeric(df, ["year", "population"], integer=True)` for both nullable integer columns, filter to `df["country_code"].notna()`, select the four columns in order, and finish with `.sort_values(["country_code", "year"]).reset_index(drop=True)`. The `reset_index` is not optional decoration — sorting carries the original row labels along with the rows, and the test checks the index is a clean sequence.

---

### `posts_with_users`

Posts are already flat, so `pd.DataFrame(load_json("placeholder_posts"))` is enough. Users are not — `address` and `company` are nested — so they need `pd.json_normalize` plus `normalize_columns`, which gives you `address_city` and `company_name`.

Rename the users frame to the target names and narrow it to just what you need, in one expression:

```python
users = users.rename(
    columns={"id": "user_id", "name": "user_name",
             "address_city": "user_city", "company_name": "company"}
)[["user_id", "user_name", "user_city", "company"]]
```

Then rename on the posts side *before* merging, which is the detail that matters:

```python
merged = posts.rename(columns={"id": "post_id", "userId": "user_id"}).merge(
    users, on="user_id", how="left"
)
```

Both frames arrive with a column called `id`. If you merge without renaming, pandas appends suffixes and you get `id_x` and `id_y`, and you then have to work out which one is the post — easy to get backwards under pressure. Renaming first means the ambiguity never exists.

Worth doing even though the tests don't force it: check `users["user_id"].is_unique` before the merge and `len(merged) == len(posts)` after it. A duplicated key on the right-hand side of a left join silently multiplies rows, and those two lines are how you find out. Saying that out loud in an interview lands well.

Title length is `merged["title"].astype("string").str.len()`, then select the six columns in order and `.sort_values("post_id").reset_index(drop=True)`.

---

### `top_domains`

The guard comes first, before you touch any column at all:

```python
columns = ["domain", "stories", "total_points"]
if df.empty or "domain" not in df.columns:
    return pd.DataFrame(columns=columns)
```

Grouping an empty frame gives you back something with neither the rows nor the columns you promised, and the caller then fails somewhere unhelpful. Returning the right-shaped empty frame means the answer always has the same shape.

Then drop the null domains — take a `.copy()` of the filtered frame so assigning to it doesn't set off `SettingWithCopyWarning` — coerce the points with `.fillna(0)` so a missing score counts as zero rather than poisoning the sum, and aggregate:

```python
grouped = (
    known.groupby("domain")
    .agg(stories=("domain", "count"), total_points=("points", "sum"))
    .reset_index()
)
```

Each keyword to `.agg` names an output column and takes a `(input_column, how)` pair, which is the readable form and worth preferring over the dictionary syntax you'll see in older code. `reset_index()` — without `drop=True` here — turns the grouping key back into an ordinary `domain` column, which is what the expected output needs.

Finish with `.sort_values(["stories", "domain"], ascending=[False, True])`, then `.head(n)`, then `.reset_index(drop=True)`. Two sort keys with two different directions: most stories first, and alphabetical order as the tiebreaker so the output is the same on every run.

If your `total_points` comes out as `10.0` instead of `10`, that's the `fillna(0)` having made it a float — `.astype("int64")` on that column after the aggregation puts it back.
