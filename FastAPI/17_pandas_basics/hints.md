# Unit 17 — hints

*Open this once you have genuinely tried a function for ten minutes or so — long enough that you are stuck on something specific, not so long that you are demoralised. Each section explains the approach and gives you enough scaffolding to get moving; none of them hands you a finished function.*

---

### `repos_frame`

Do this in two clearly separate halves and it stops being fiddly.

The first half is plain Python and has nothing to do with pandas: loop over the raw records from `load_json`, and for each one build a small flat dictionary with your eight keys. This is the `slim_repos` shape from unit 09, and if you have that function's body in your head you already know most of this.

```python
rows = []
for repo in load_json("github_repos_pallets"):
    rows.append({
        "name": repo["name"],
        ...
    })
```

The order in which you write those keys is the order your columns come out in, because `pd.DataFrame` takes its column order from the keys of the first dictionary. So write them in the order the docstring lists and you get the column order for free rather than having to reorder afterwards.

The only awkward field is the license, because `repo["license"]` is often `null` and you cannot reach into `null` for a name. `(repo.get("license") or {}).get("name")` handles it: if the license is missing or null you ask an empty dictionary for `"name"` and get `None` back, which is what you want in the table. This is unit 04's `or {}` pattern, and it is deliberately here so you use it once more.

The second half is one line: `pd.DataFrame(rows)`. That is genuinely all of it. Resist any urge to hand the raw nested response to pandas and clean up afterwards — the whole reason for the first half is that null-handling is readable in Python and obscure in pandas.

---

### `overview`

This one is short enough to give you almost whole, because the interesting part is not the structure but the casts.

```python
{
    "rows": int(len(df)),
    "columns": list(df.columns),
    "dtypes": {c: str(t) for c, t in df.dtypes.items()},
    "missing": {c: int(n) for c, n in df.isna().sum().items()},
}
```

Three things to notice. `df.columns` is not a list — it is an `Index` object — so `list(...)` around it is what makes it something `json.dumps` will accept. `df.dtypes` is a Series mapping each column name to its dtype, and `.items()` on a Series gives you name-value pairs exactly the way it does on a dictionary, which is why the comprehension reads naturally. And `df.isna().sum()` is the count of missing values per column: `isna()` gives you a whole frame of True and False, and summing a frame sums each column, so what comes back is one number per column.

The `int(...)` and `str(...)` casts are the point of the exercise. pandas gives you `numpy.int64` and dtype objects, neither of which `json.dumps` will touch, and the failure arrives one test later than you expect, with a message about serialization that does not obviously point back to here. Convert at the boundary.

---

### `filter_repos`

Build the mask up in steps rather than trying to write one enormous condition, because two of the three conditions are optional and you cannot know at authoring time which will apply.

```python
mask = df["stars"] >= min_stars
if language is not None:
    mask = mask & (df["language"] == language)
if not include_archived:
    mask = mask & (~df["archived"])
return df.loc[mask].reset_index(drop=True)
```

Read what that is doing. `mask` starts as a column of True and False, one per row. Each `if` narrows it by combining it with another column of True and False using `&`, which is elementwise — row by row, a row survives only if it was True in both. It is exactly the same reasoning as adding another `AND` to a `WHERE` clause, except you can see the intermediate result.

Note `language is not None` rather than `if language:`, and it matters for the same reason unit 01 made a fuss about it: an empty string is falsy, and you want "no language filter was requested" to be distinguishable from "a filter was requested."

`~` is negation, so `~df["archived"]` is the not-archived rows. And `reset_index(drop=True)` renumbers the surviving rows from zero, which the tests check for explicitly.

---

### `add_metrics`

`.copy()` first, always. Make it the first line before you have thought about anything else, because the test that catches a missing copy checks the *input* frame afterwards, and the failure message will point at a function that looks fine.

The zero-star division is the piece worth thinking about. You want NaN where stars is zero, and pandas gives you `inf` if you just divide. The clean way is to turn the zeros into NaN *before* dividing:

```python
out["fork_ratio"] = (out["forks"] / out["stars"].where(out["stars"] != 0)).round(3)
```

`Series.where(cond)` keeps the value where the condition is True and replaces it with NaN where it is False — so `.where(stars != 0)` leaves the real star counts alone and blanks out the zeros. Dividing by NaN gives NaN, which is honest, whereas dividing by zero gives `inf`, which is not.

For the bands, assign the lowest first and overwrite upward:

```python
out["popularity"] = "low"
out.loc[out["stars"] >= 1000, "popularity"] = "medium"
out.loc[out["stars"] >= 10000, "popularity"] = "high"
```

The first line sets the whole column to a single value — pandas broadcasts a scalar across every row. Then each `.loc[mask, "column"] = value` overwrites only the rows the mask selects. Order matters and it is doing real work: the 50,000-star rows get set to "medium" by the second line and then corrected to "high" by the third, because the later assignment wins for the rows it touches. Write those three lines in the other order and every big repo ends up labelled "medium".

`has_license` is a single expression — `.notna()` on the license column gives you exactly the boolean column asked for.

---

### `language_summary`

Fill the nulls first, on a copy, then group:

```python
out = df.copy()
out["language"] = out["language"].fillna("unknown")
summary = out.groupby("language").agg(
    repos=("name", "count"),
    total_stars=("stars", "sum"),
    mean_stars=("stars", "mean"),
    max_stars=("stars", "max"),
).reset_index()
```

The `fillna` has to come before the `groupby`, not after, because `groupby` silently drops rows whose key is null. Do it afterwards and those two repos are already gone and there is nothing left to rename.

Each keyword argument to `.agg` reads as `output_name=(input_column, function)`. That form is called named aggregation and it hands you back tidy single-level column names, which is why it is worth learning over the older `agg({"stars": ["sum", "mean"]})` style that produces a two-level column structure you then have to flatten.

`.reset_index()` — without `drop=True` here — moves `language` out of the index and back into being a column, which is where the tests look for it.

Then round `mean_stars` to 1dp and finish with `sort_values([...], ascending=[False, True]).reset_index(drop=True)`. That second `reset_index` *does* take `drop=True`, because at that point the index is just leftover numbering you want to throw away rather than data you want to keep.

---

### `countries_frame`

Remember the payload is `[metadata, records]`, so the data you want is the second element.

`pd.json_normalize(records, sep=".")` flattens the nesting and gives you columns named `region.value` and `incomeLevel.value` alongside the flat ones. From there it is a rename and a select:

```python
df = pd.json_normalize(records, sep=".")
df = df.rename(columns={"id": "code", "region.value": "region", ...})
df = df[["code", "name", "region", "income_level", "capital", "latitude", "longitude"]]
```

Selecting with a list of column names is what fixes the order — the frame comes out in exactly the order you list them, which is what the test checks. Note the double brackets: the inner ones are the list, the outer ones are the indexing.

Then the three cleaning steps, in order. For the text columns:

```python
df[col] = df[col].str.strip().replace("", pd.NA)
```

`.str.strip()` goes through the `.str` accessor because it is a string operation applied to every value; `.replace("", pd.NA)` is a plain Series method, no `.str`, because it is comparing whole values rather than manipulating text inside them. Getting those two the wrong way round is the usual stumble here.

Then the coordinates:

```python
df[col] = pd.to_numeric(df[col], errors="coerce")
```

`errors="coerce"` is what turns an unparseable value into NaN instead of raising, and since the blanks have already become `pd.NA` by this point they land as NaN cleanly. Check `df.dtypes` afterwards — you should see `float64` on both, and if you see `str` or `object` the conversion did not take.

---

### `region_stats`

Drop the null regions before you do anything else, with `df.loc[df["region"].notna()]`. Use `.notna()` rather than any comparison against `None` or `NaN`; NaN is not equal to itself, so a comparison quietly matches nothing.

Then group and aggregate. The two functions do most of the work for you, but only if you point them at the right columns:

- `"count"` ignores nulls, so `with_capital=("capital", "count")` counts exactly the rows that have a capital city. That is the whole answer, no boolean trickery needed.
- `countries` wants every row in the group regardless of nulls, so point `"count"` at a column that is never missing — `code` is a safe bet — or use `"size"`, which counts rows rather than values.
- `"mean"` skips NaN by default, so `mean_latitude=("latitude", "mean")` averages the latitudes that exist and returns NaN only when a whole region has none. The "Aggregates" region is exactly that case, and the test asserts the NaN, so do not fill it with zero.

Round `mean_latitude` to 2dp, then `sort_values(["countries", "region"], ascending=[False, True]).reset_index(drop=True)`.

---

### `to_records`

```python
subset = df if limit is None else df.head(limit)
cleaned = subset.astype(object).where(subset.notna(), None)
return cleaned.to_dict("records")
```

The middle line is the one doing something non-obvious, so read it in two parts.

`.astype(object)` loosens every column so it will hold arbitrary Python objects. Without it, a float column can only contain floats, so the `None` you carefully put in gets converted straight back to `NaN` and you have achieved nothing — which is a genuinely maddening bug to look at, because your code plainly says `None` and the output plainly says `NaN`.

`.where(subset.notna(), None)` then keeps each value where it is not missing and substitutes `None` everywhere it is. It is the frame-level version of the `Series.where` you used in `add_metrics`, with the second argument saying what to put in place of the values that fail the condition.

`limit is None` rather than `if limit:` for the guard, so that a `limit` of 0 means zero rows rather than being mistaken for no limit at all.

Verify it yourself the way the tests do: `json.dumps(to_records(countries))` should succeed, and the resulting text should not contain the string `NaN` anywhere.
