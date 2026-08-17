# Unit 19 — hints

*Open this once you have genuinely been stuck on a particular function for about ten minutes — long enough that you know what is confusing you, not long enough to give up on it. Each section talks through the approach and gives you partial scaffolding. None of them is a finished function.*

---

### `fx_frame`

You have a dictionary of dictionaries and you want a flat list of rows, so build the rows first and hand them to pandas at the end. Two nested loops do it, and in a comprehension they read as one thing — the outer loop walks the dates, the inner one walks that date's currencies:

```python
rows = [
    {"date": date, "currency": currency, "rate": rate}
    for date, by_currency in rates.items()
    for currency, rate in (by_currency or {}).items()
]
```

Read the two `for` clauses top to bottom, in the same order you would write the nested loops. The `or {}` is unit 04's habit again: if a date maps to `null` instead of a dictionary, `.items()` on `None` would blow up, and an empty dictionary contributes no rows and no complaint.

Once you have `rows`, build the frame and then fix the two dtypes. `pd.to_datetime(..., utc=True)` on the date column and `pd.to_numeric(...)` on the rate column — the first is what makes `.dt` work in the next two functions, and the second is what makes `mean` mean anything. Then `sort_values` by date and currency, and `reset_index(drop=True)` so the row numbers run 0, 1, 2 rather than keeping whatever order they had before the sort.

For the empty case, return `pd.DataFrame(columns=["date", "currency", "rate"])`. Check for it early, because building a frame from an empty list of rows gives you a frame with no columns at all, and the test checks the columns.

---

### `monthly_fx_stats`

Call `sort_values("date")` **before** the groupby. This is the one line that decides whether the function is right, because `"first"` and `"last"` take the top and bottom row of each group as the rows happen to be arranged, not as the calendar arranges them. Sort first and they mean chronologically first and last.

Then group by currency and the month string together, and aggregate everything you need in one pass — including the two values you only want in order to compute something else:

```python
.agg(
    days=("rate", "size"),
    mean_rate=("rate", "mean"),
    min_rate=("rate", "min"),
    max_rate=("rate", "max"),
    first_rate=("rate", "first"),
    last_rate=("rate", "last"),
)
```

Now `change_pct` is ordinary arithmetic between two columns: last minus first, over first, times a hundred. Round it to 2dp and round the three rate columns to 4dp.

Finish by selecting the seven output columns in the order the docstring lists them. That selection is doing two jobs — it fixes the column order, and it drops `first_rate` and `last_rate` without you having to write a `drop` call. And put `.reset_index()` after the `agg` so `currency` and `month` come back as real columns rather than staying in the index, which is what the test checks when it looks at `list(stats.index)`.

---

### `fill_missing_days`

Order of operations is everything here. Capture the dates you actually observed **before** you resample, because afterwards the invented rows are indistinguishable from the real ones:

```python
observed = set(subset["date"])
daily = subset.set_index("date")["rate"].resample("D").ffill().reset_index()
daily["filled"] = ~daily["date"].isin(observed)
```

Walking that middle line: `set_index("date")` gives you the DatetimeIndex that `resample` requires; `resample("D")` creates a bucket for every calendar day in the range including the ones with nothing in them; `ffill` carries the last real rate forward into each empty day; `reset_index` turns the date back into a column.

The last line reads as "filled is true where this date was *not* one of the ones we saw." The `~` is elementwise `not` for a column of True/False — Python's `not` keyword does not work on a Series, which is a small annoyance you meet once and then remember.

Filter to the currency first, and if the filtered frame is empty, return the empty three-column frame straight away rather than resampling nothing.

---

### `population_with_regions`

Write two small helper functions rather than doing this inline — one that builds the population frame (which is essentially unit 18's, again) and one that builds the `country_code -> region` lookup. Being able to print each side separately is worth the extra six lines when the join count comes out wrong.

Then the merge itself is three lines, two of which are assertions:

```python
assert lookup["country_code"].is_unique
merged = population.merge(lookup, on="country_code", how="left")
assert len(merged) == len(population)
```

Those two assertions are the point of the exercise as much as the merge is. The first says the right side is one row per key, which is the assumption a left join silently makes for you; if it were false, every population row for the duplicated country would come back twice and nothing would tell you. The second says the join did not change your row count, which for a left join against a unique key it never should. The test for this function asserts exactly the same thing, with the message "a left join must not change the row count."

Drop the rows with a blank country code from the population frame and the ones with a blank region from the lookup, before merging. Then sort by country code and year, reset the index, and select the five columns in the documented order.

---

### `region_population_by_year`

Filter first, group second. Drop the rows where the region is null and the rows where the population is null, explicitly, at the top of the function — `groupby` would drop the null-region ones for you, but doing it yourself makes the choice visible and takes care of the null populations at the same time, which `groupby` would not.

Once only good rows remain, it is a two-key named aggregation on region and year. `("country_code", "count")` gives you `countries`, which is a count of the rows that survived the filter — which is what `countries` means here. `("population", "sum")` gives you the total.

One last step: cast the sum to `int64`. If the population column came through as pandas' nullable `Int64` (capital I), the sum stays nullable and does not compare equal to a plain integer the way the test expects. There are no nulls left at that point, so the cast is safe.

---

### `population_growth`

Filter to the region, sort by year, and then two one-line calls do the arithmetic:

```python
out["change"] = out["total_population"].diff()
out["change_pct"] = (out["total_population"].pct_change() * 100).round(2)
```

Both produce NaN for the first row on their own, because there is no earlier row to compare with — you do not need a special case for it and you should not fill it in. `pct_change` returns a fraction, so the `* 100` is what turns 0.0102 into 1.02; without it, rounding to 2dp would flatten every value to 0.01 or 0.0.

The sort matters as much as it did in `monthly_fx_stats`: both methods compare each row with the row physically above it, so on an unsorted frame they produce confident nonsense rather than an error.

Guard the unknown-region case at the top and return an empty frame carrying the four documented column names. The danger is not a crash — it is silently returning a frame with the wrong columns.

---

### `stories_per_month`

`resample("MS")` — month **start** — is what makes the labels line up with `"YYYY-MM"` strings. `"ME"` would give you the last day of each month, which formats to the same string but is a different index, and the test builds a `pd.period_range` and compares against it.

Parse `created_at` with `utc=True`, `set_index` on it, and resample. Then aggregate with named aggregation so both columns come out as numbers rather than NaN in the empty months:

```python
.agg(stories=("points", "size"), total_points=("points", "sum"))
```

`size` counts rows, so an empty month gives 0. `sum` over nothing is also 0 in pandas, which is what you want here. Finally, `strftime("%Y-%m")` the index into the `month` column and reset the index.

The empty-input case needs its own early return with the three column names — resampling an empty frame has no range to work over.

---

### `save_report`

Three steps and nothing subtle, but each step is a thing people forget.

`Path(path).parent.mkdir(parents=True, exist_ok=True)` first. `parents=True` creates intermediate folders, `exist_ok=True` means running it twice is not an error.

Then branch on `fmt`. For CSV, pass `index=False` — without it you get an unnamed leading column of row numbers, and the test's first assertion is that the header line is exactly `a,b`. For JSON, pass `orient="records", indent=2, date_format="iso"` to get the readable list-of-objects shape. Anything else, `raise ValueError(f"unsupported format: {fmt}")` — with the bad value actually in the message, since the test checks that `"parquet"` appears in it.

Then `return len(df)`.
