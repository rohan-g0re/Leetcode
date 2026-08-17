# 19 — Grouping, Joining, and Time Series

*About thirty minutes to read, thirty to do the task. This is the last unit before FastAPI, and it is the one where your SQL background pays off hardest — every major idea here is something you already understand, wearing different clothes. `groupby` is `GROUP BY`. `merge` is `JOIN`. The time-series section is the part SQL makes you fight for. I will keep pointing at the correspondence, because it is genuinely the fastest way in.*

*Two threads run through everything below. The first is that unit 16 made you do all of this by hand — bucketing records with `setdefault`, building a lookup dictionary and walking the other side past it — so nothing here is a new idea, only the same idea with the machinery hidden. The second is that unit 18 made you get the dtypes right, and that was not busywork: it is the entire reason the `.dt` accessors in section 10 work at all.*

---

## 1. The three questions you already know how to ask

Almost every analytical question anyone will ever hand you is one of three shapes.

*Per category.* "Average stars by language." "Requests per endpoint." "Population per region." You split the rows into groups and summarise each group.

*Combined with.* "Posts with their authors' names." "Population joined to region." You have two tables and one of them holds a column the other one needs.

*Over time.* "Stories per month." "Is this trending up?" You bucket rows into time periods and compare each period with the one before.

In SQL those are `GROUP BY`, `JOIN`, and `DATE_TRUNC` plus a window function. In pandas they are `groupby`, `merge`, and `resample`. That is the whole unit. The reason it takes thirty minutes rather than five is not that the operations are hard — it is that three of them lose data *silently*, with no error and no warning, and section 6 and section 8 exist entirely to teach you where.

Here is the occasion to keep in mind. An interviewer hands you a live endpoint, you fetch it, you clean it. Then they ask you to say something useful about it. Sections 2 through 12 are how you say something useful. Section 13 and the task's `save_report` are how you hand it over.

---

## 2. `groupby`, and what split-apply-combine actually is

**What it is.** `groupby` takes a DataFrame and a column, and hands back an object that has quietly sorted every row into a bucket according to that column's value. Nothing is computed yet. Then you tell it what to compute per bucket, and it computes that and stitches the answers into one result.

```python
df.groupby("language")["stars"].mean()
```

Read that left to right: split the rows by language, look at the `stars` column within each group, take the mean of each. What comes back is a Series — one value per language, with the language as the index.

**The mental model is three words: split, apply, combine.** Split the rows into groups. Apply a function to each group. Combine the answers into one object. That phrase is the standard name for the pattern and it is worth saying out loud in an interview, because it describes what you are doing rather than which method you called.

You have already written this by hand. Unit 16's `group_stats` was three phases — collect into buckets with `setdefault` or `defaultdict`, compute a summary per bucket, format the result. Split, apply, combine, spelled out in a loop you could print. **pandas does not do anything different; it just hides phase one so you never see the buckets.** If you ever get confused about what a `groupby` is doing, go back to that loop and picture it.

While we are naming things: to **aggregate** is to reduce many values to one summary value — a count, a sum, a mean, a maximum. Grouped aggregation is doing that separately per bucket. That is exactly the aggregate function list in a SQL `SELECT`.

You can group by more than one column, which is SQL's `GROUP BY a, b`:

```python
df.groupby(["language", "archived"])["stars"].sum()
```

And you can ask for several aggregates at once:

```python
df.groupby("language")["stars"].agg(["count", "mean", "max"])
```

That last one works, and I am showing it to you mainly so I can tell you not to use it. Section 3 explains why.

---

## 3. Named aggregation — the one form to memorise

This is the single most load-bearing snippet in the unit. If you memorise one thing today, memorise this shape:

```python
summary = (
    df.groupby("language")
    .agg(
        repos=("name", "count"),
        total_stars=("stars", "sum"),
        mean_stars=("stars", "mean"),
        top=("stars", "max"),
    )
    .reset_index()
)
```

**What it is.** Each keyword argument is `new_column_name=(source_column, function)`. You are saying: make me a column called `total_stars`, and fill it by summing the `stars` column within each group. This is called **named aggregation**, and it is the direct translation of the SQL you already write:

```sql
SELECT language,
       COUNT(name)  AS repos,
       SUM(stars)   AS total_stars,
       AVG(stars)   AS mean_stars,
       MAX(stars)   AS top
FROM repos
GROUP BY language
```

Line for line, that is the same statement. The `AS` clause is the keyword name.

**Why this form and not the other one.** `.agg(["count", "mean", "max"])` from section 2 gives you the right numbers with useless names. It produces a **MultiIndex** on the columns — an index with more than one level, so instead of a column called `mean_stars` you get a column identified by the *pair* `("stars", "mean")`. Everything downstream then breaks in small annoying ways: you cannot write `df["mean_stars"]`, writing it to CSV produces a two-row header, and serializing it to JSON is a mess. You end up flattening the names afterwards with a line of string-joining that nobody enjoys reading.

I am telling you what a MultiIndex is only so you understand what you are avoiding. Named aggregation gives you clean, flat, self-chosen column names in one pass, and it never creates one. Reach for it every single time.

**`.reset_index()`, and why forgetting it bites you later rather than now.** After a `groupby`, the group key is not a column — it is the *index*, the row labels down the left-hand side. That looks fine when you print it, which is exactly the problem, because nothing goes wrong until much later. Then you try to `merge` on `language` and pandas tells you there is no such column. Or you write the frame to JSON and the language disappears entirely, because `orient="records"` serializes columns and the index is not one. `.reset_index()` moves the key back into being an ordinary column and gives you plain 0, 1, 2 row numbers.

**The practitioner's habit:** put `.reset_index()` at the end of every `groupby` chain by reflex, unless you have a specific reason to keep the index. It costs nothing when you did not need it and saves you a genuinely confusing ten minutes when you did. You will do this in four of the task's functions.

---

## 4. Which functions you can name, and the `count`/`size` trap

The function in each `(column, function)` pair can be a string naming a built-in:

`"count"`, `"size"`, `"sum"`, `"mean"`, `"median"`, `"min"`, `"max"`, `"std"`, `"nunique"`, `"first"`, `"last"`.

Most behave exactly as the name says. Two pairs need a note.

**`count` versus `size`, which is the first of this unit's three silent data losses.** `count` counts *non-null* values. `size` counts *rows*, nulls included. So if a group has ten rows and three of them have a null population, `count` says 7 and `size` says 10. Neither is wrong; they answer different questions. But if your group counts come back lower than you expected and nothing errored, this is almost always why. Decide which you meant, deliberately, and prefer whichever one makes the number you print honest. In the task, `days=("rate", "size")` counts observations and `countries=("country_code", "count")` counts rows that actually contributed a value.

If SQL is your reference point: `count` is `COUNT(column)` and `size` is `COUNT(*)`. SQL has the same distinction and the same trap.

**`first` and `last` mean *positionally* first and last, not chronologically.** They hand you whatever row happens to sit at the top and bottom of the group, in whatever order the rows arrived. If your frame is not sorted, "first" is meaningless. This is a real correctness trap and the task walks you straight into it — `monthly_fx_stats` has to `sort_values("date")` *before* grouping, or its month-over-month change is computed between two arbitrary days.

You can also pass your own function instead of a string. It receives the group's Series and returns one value:

```python
.agg(pct_licensed=("license", lambda s: s.notna().mean() * 100))
```

`s.notna()` gives a column of True/False, and the mean of True/False is the proportion that are True — unit 01's "True is 1" trick, still earning its keep. A lambda is slower than a built-in because pandas cannot push it down into optimised code, but on tens of thousands of rows you will not notice.

---

## 5. `transform` versus `agg`

**What it is.** `agg` collapses each group down to one row. `transform` computes a per-group value and then *broadcasts it back out*, giving you one value per original row.

```python
df["lang_mean"] = df.groupby("language")["stars"].transform("mean")
df["above_avg"] = df["stars"] > df["lang_mean"]
```

After the first line, every row carries the mean for its own language, repeated. A frame of five hundred repos stays five hundred rows long. After `agg` it would have become one row per language.

**Why you need both.** Some questions cannot be answered by collapsing. "Is *this* repo above average for its language" is a question about an individual row that requires a group-level number, so you need the group number sitting next to the row. `agg` throws away the rows; `transform` keeps them.

**The mental model: `agg` shrinks, `transform` stays the same shape.** That is the entire distinction, and it is enough to pick correctly under pressure.

If you have written SQL window functions, you have met this exactly: `AVG(stars) OVER (PARTITION BY language)` is `transform("mean")`, and `GROUP BY language` is `agg`. Same split, different combine.

---

## 6. The rows that vanish, and `value_counts`

Here is the second silent loss, and it is the one people find out about from a wrong total rather than from an error.

```python
df.groupby("language")                 # rows with a null language are DROPPED
df.groupby("language", dropna=False)   # they are kept, grouped under NaN
```

By default, **`groupby` throws away every row whose group key is missing.** No message, no warning. Your grand total simply comes out lower than the row count and nothing tells you why. This one is doubly annoying because SQL does the opposite — `GROUP BY` in SQL gives you a `NULL` group — so the instinct you brought with you is wrong here.

You have two honest options and one dishonest one. Pass `dropna=False` and let the missing rows form their own group. Or `fillna("unknown")` before grouping, so they are labelled rather than nameless. The dishonest option is to do neither and not know which happened. Whichever you pick, know that you picked it, because your totals depend on it — and being able to say "I dropped fourteen rows with no language, here they are" is the difference between an analysis and a guess.

**`value_counts`** is the shorthand for the most common grouping of all, which is counting:

```python
df["language"].value_counts()                 # counts, biggest first
df["language"].value_counts(dropna=False)     # include the missing ones
df["language"].value_counts(normalize=True)   # proportions instead of counts
```

It is exactly `groupby(col).size().sort_values(ascending=False)` with less typing. Note that it defaults to dropping nulls too, and that `dropna=False` is how you find out how many there were. Running `value_counts` on every categorical column is the fastest way to find out what is actually in a dataset someone just handed you.

---

## 7. Joining: `merge` is `JOIN`

**What it is.** `merge` takes two DataFrames and lines their rows up on a shared column, producing one wider frame.

```python
merged = df.merge(other, on="id", how="left")
merged = posts.merge(users, left_on="userId", right_on="id", how="left")
```

The column you match on is the **join key**. Use `on=` when both sides call it the same thing, and `left_on`/`right_on` when they do not — which is most of the time, because one table calls it `id` and the other calls it `user_id`.

`how` chooses which rows survive, and it means precisely what it means in SQL:

| `how` | Keeps |
|-------|-------|
| `"left"` | every left row; unmatched right columns come back NaN |
| `"inner"` | only rows that matched on both sides |
| `"right"` | every right row |
| `"outer"` | everything from both sides |

You already built the `"left"` case by hand in unit 16: index one side into a dictionary, walk the other side once, `.get()` the match. That is a hash join, and it is what `merge` runs internally. `merge` is doing your dictionary trick with a much better implementation.

**Default to `"left"`, and here is the third silent loss.** An `inner` join quietly discards every row that did not match, on both sides. If 30% of your posts have a user id that is not in the users table, an inner join hands you a perfectly clean-looking frame with 30% of your data missing and no indication that anything happened. This is a genuinely common bug and nothing warns you.

A left join preserves your left-hand row count, which means the non-matches are still *there*, marked with NaN, where you can count them:

```python
print(merged["user_name"].isna().sum(), "posts had no matching user")
```

**The mental model: join left so you can measure what didn't match, instead of losing it.** You can always filter the unmatched rows out afterwards, deliberately, once you know how many there are. You cannot recover rows an inner join already ate. The task's `population_with_regions` is built around exactly this — unmatched countries keep a null region on purpose, *so that you can count them*.

---

## 8. Cardinality, and the two assertions worth writing every time

This section is short and it matters more than its length suggests.

**Cardinality** is the question of how many rows on each side share a given key — one-to-one, one-to-many, many-to-many. Unit 16 raised it when your lookup dictionary silently overwrote a duplicate. `merge` has the opposite failure and it is worse: where a dictionary loses a row, **a duplicate key on the right side silently multiplies your rows.** If the right frame has two rows for `id = 7`, then every left row with `id = 7` comes back *twice*. Your row count grows, your sums double, and nothing errors.

So write two lines around every merge you do. Before:

```python
assert users["id"].is_unique
```

That is the cardinality check — it asserts the right side is one-row-per-key, which is the assumption a left join quietly makes on your behalf. And after:

```python
assert len(merged) == len(posts)
```

That asserts the join did not change your row count, which for a left join against a unique key it never should.

Two cheap lines that catch the single most common merge bug in existence. And saying *"let me just confirm the join key is unique on the right before I merge"* out loud in an interview is one of the strongest short signals available to you, because it is the exact sentence someone who has been burned by this says. The task's `population_with_regions` asks you to write both, and I would say the assertions are as much the point of that exercise as the merge is.

**Overlapping column names.** If both frames have a `name` column and it is not the join key, pandas cannot keep both, so it renames them `name_x` and `name_y` — which is unreadable and easy to mix up. Either rename before merging, or say what you want:

```python
merged = posts.merge(users, on="user_id", suffixes=("", "_user"))
```

An empty first suffix leaves the left column alone and tags only the right one, so you get `name` and `name_user`. Much easier to read three functions later.

---

## 9. Stacking rather than joining: `concat`

A merge glues frames side by side. When you want them stacked *end to end* — same columns, more rows — that is `concat`:

```python
pd.concat([df1, df2], ignore_index=True)
```

This is SQL's `UNION ALL`. The overwhelmingly common use is pagination: unit 15 had you fetch page one, page two, page three, and what you are holding afterwards is a list of pages. Build a frame per page and `concat` them into one. `ignore_index=True` matters — without it each page keeps its own 0, 1, 2 row labels and you end up with a frame containing four separate rows labelled 0, which breaks the next thing you do.

---

## 10. Time series, and why unit 18 was the prerequisite

Everything below this line depends on one thing being true: your date column has to be a real datetime dtype, not text that looks like a date.

```python
df["created"] = pd.to_datetime(df["created"], errors="coerce", utc=True)
```

This is the line from unit 18, and now you find out what it was for. **Every `.dt` accessor in this section fails on a string column.** Not "gives a worse answer" — fails, with `AttributeError: Can only use .dt accessor with datetimelike values`. Getting the dtype right was not tidiness; it is the thing that unlocks the entire second half of this lesson. The same is true of `to_numeric` and your rate column, since you cannot take a mean of text.

Once the column is genuinely datetime, `.dt` gives you the parts:

```python
df["created"].dt.year
df["created"].dt.month
df["created"].dt.date
df["created"].dt.day_name()               # "Monday"
df["created"].dt.to_period("M")           # Period('2024-01', 'M')
df["created"].dt.strftime("%Y-%m")        # "2024-01", a plain string
```

**A period is a span of time rather than an instant.** `Period('2024-01', 'M')` means "the whole of January 2024" — it is not a timestamp, it is a bucket with a start and an end. That is semantically the right type for "which month is this row in", and periods sort and compare correctly as periods. Strings are the right type for handing to JSON. So the practitioner's rule is: **use periods for the analysis, `.astype(str)` at the edge** where the data leaves your program. Note that `"%Y-%m"` strings sort correctly as text too, because the year comes first and the month is zero-padded — which is why that format shows up everywhere and `"%m-%Y"` shows up nowhere.

Grouping by time is then just grouping, with a computed key:

```python
df.groupby(df["created"].dt.to_period("M")).size()
df.groupby(df["created"].dt.strftime("%Y-%m")).size()
```

You can pass an expression to `groupby`, not only a column name, as long as it lines up row for row with the frame. This is `GROUP BY DATE_TRUNC('month', created)`.

**Timezones, briefly, because it is a `TypeError` you will otherwise spend twenty minutes on.** A datetime is either *aware* (it knows its offset from UTC) or *naive* (it does not). Comparing one of each raises `TypeError: Cannot compare tz-naive and tz-aware timestamps`, and it raises it in the middle of a filter you thought was trivial. The fix is a policy, not a debugging technique: parse with `utc=True` at the boundary where data enters, so everything inside your program is aware and in UTC, and never think about it again. Convert only for display:

```python
df["created"].dt.tz_convert("America/New_York")
```

---

## 11. `resample`, and the difference between a missing bar and a zero bar

This is the most important idea in the time-series half of the unit, and it is the one most often got wrong in real reports.

**What it is.** `resample` buckets rows into fixed time periods. It needs a DatetimeIndex, so you `set_index` on your date column first:

```python
counts  = df.set_index("created").resample("D").size()
monthly = df.set_index("created").resample("MS")["value"].mean()
```

That looks like a `groupby` on a month string, and for most rows it gives the same answer. Here is the difference, and it is not cosmetic.

**`resample` emits a row for every period in the range, including the empty ones.** Group on a month string and a month with no records simply does not appear in the output — it vanishes, and your chart draws a line from March straight to May as though April never happened. `resample` gives you April with a count of zero.

**A missing bar and a zero bar mean different things.** Missing means "we have no information about this period." Zero means "we looked, and there was nothing." Reporting the first as though it were the second — or worse, silently skipping it so the reader never sees either — is the single most commonly mis-reported property of a sparse time series. If you take one habit from this section: when the answer is a count over time, use `resample`, because the zeros are part of the answer. The task's `stories_per_month` is built on this. Its test expects 143 months, 103 of which are empty, and a `groupby` on a month string would return 40.

**Frequency aliases** are the short codes naming the bucket size: `"D"` daily, `"W"` weekly, `"h"` hourly, `"MS"` month start, `"ME"` month end, `"QE"` quarter end, `"YE"` year end.

Two notes on those. First, `"M"` and `"Y"` were renamed to `"ME"` and `"YE"` in pandas 2.2 — the old short forms still work but now emit a deprecation warning, so any example you find online written before that will warn at you. That is the code being old, not you being wrong.

Second, **`"MS"` versus `"ME"` is a real choice, not a detail.** Month *start* labels each bucket with the first day of the month; month *end* labels it with the last. Both bucket the same rows. But if you are going to format those labels as `"YYYY-MM"` strings and line them up against a period range, `"MS"` is what you want, because the index it produces is the first-of-month timestamps that correspond one-to-one with the months. `"ME"` formats to the same string but is a different index underneath, and the mismatch shows up later as an off-by-one you cannot see. `stories_per_month` uses `"MS"` for exactly this reason.

`resample` also gives you a way to fill gaps rather than count them:

```python
daily = df.set_index("date")["rate"].resample("D").ffill()
```

`ffill` is forward fill: carry the most recent observed value forward into each empty day. The FX data in the task has no weekend rows because markets are shut, so this turns roughly 64 trading days into roughly 90 calendar days. **Whether you should do that is an analytical decision, not a technical one** — it changes the answer to "average rate per month", because you have just added weight to Fridays. There is no universally right choice, which is why `fill_missing_days` returns a `filled` column: the caller gets to know which rows were observed and which were invented.

---

## 12. Rolling windows, and change over time

A **rolling window** is a fixed-width span that slides along the series, computing a summary at each position from the last N values.

```python
counts.rolling(7).mean()      # seven-period moving average
```

Each output value is the mean of that point and the six before it. This is what smooths a noisy daily count into a readable trend, and it is SQL's `AVG(x) OVER (ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)`.

The first six values come back NaN, because there are not yet seven values to average. That is correct rather than broken — pandas is refusing to show you a "7-day average" computed from three days. If you would rather have partial windows at the start, `rolling(7, min_periods=1)` says so explicitly.

For period-over-period change, two methods do the arithmetic for you:

```python
monthly = df.set_index("created").resample("MS").size()
monthly.diff()          # absolute change from the previous period
monthly.pct_change()    # fractional change: 0.25 means +25%
```

Both give NaN for the first row, because there is no previous period to compare against — and that NaN is the honest answer, not a gap to fill. `pct_change` returns a *fraction*, so multiply by 100 when you want the number a human reads. You will do exactly this in `population_growth`.

---

## 13. Pivoting, as a final step only

```python
df.pivot_table(index="month", columns="language", values="stars",
               aggfunc="sum", fill_value=0)
```

This turns long data into a matrix: one row per month, one column per language, the summed stars in the cells. It is what you want when a human is going to *look* at the table.

It is a bad intermediate format, though, and this is worth knowing before you reach for it too early. Almost every pandas operation — `groupby`, `merge`, plotting — expects long format, one row per observation. The moment you pivot, your categories become column *names*, and filtering or joining on a column name is awkward in a way that filtering on a value is not. So pivot at the very end, for presentation, and keep everything upstream long. (`df.melt()` unpivots if you need to get back.)

---

## 14. Look this up yourself

The habit of reading documentation under mild pressure is the transferable skill here, so these are deliberately left for you.

- `pd.Grouper(key="created", freq="MS")` — grouping by time without `set_index`.
- `df.merge(..., indicator=True)` — adds a column telling you which side each row came from, which turns "how many didn't match" into one `value_counts`.
- `df.merge(..., validate="one_to_one")` — pandas will assert your cardinality for you.
- `series.rolling(7, min_periods=1)` versus plain `rolling(7)`.
- `df.sort_index()` after grouping on a period, and why the order might not already be what you want.
- `df.melt()` — the inverse of pivot.

---

## 15. Check yourself

1. What does named aggregation give you that `.agg(["mean", "max"])` does not?
2. What is the difference between `count` and `size` in a groupby?
3. What happens by default to rows whose group key is null?
4. Why default to a left join rather than an inner one?
5. Which two assertions belong around every merge?
6. What does `resample` do that a `groupby` on a month string does not?
7. `agg` or `transform` — which one answers "is this row above its group's average"?

*(Answers: 1. clean flat column names of your own choosing in one pass, instead of a MultiIndex you then have to flatten. 2. `count` skips nulls, `size` counts every row — `COUNT(col)` versus `COUNT(*)`. 3. they are dropped silently, unless you pass `dropna=False`. 4. it preserves the left row count, so you can measure what failed to match instead of losing it. 5. the join key is unique on the right side, and the row count is unchanged afterwards. 6. it emits rows for empty periods, so a gap shows as 0 instead of disappearing. 7. `transform` — `agg` has already collapsed the rows you wanted to compare.)*

---

*Four things to carry out of here. Named aggregation with `.reset_index()` is the form to type without thinking, because it is the only one that leaves you with a frame you can immediately merge or serialize. Three operations in this unit lose data with no error at all — `groupby` drops null keys, `count` skips nulls where `size` does not, and an inner join eats non-matches — so default to the choices that let you *count* what you lost rather than the ones that hide it. Cardinality is checkable in one line and worth checking every single time, because a duplicate key on the right multiplies rows and looks like a successful join. And `resample` exists because the zeros in a sparse time series are part of the answer.*

*This is the last unit before FastAPI, and with it you can now run the whole pipeline: fetch a live endpoint (units 12 to 15), flatten and clean it (units 17 and 18), group it, join it, put it on a time axis, and write it to disk. That is the entirety of Capstone A. Unit 20 turns the pipeline around and puts an endpoint of your own on the front of it.*

*Now open [`task.py`](task.py).*
