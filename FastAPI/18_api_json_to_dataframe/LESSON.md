# 18 — From API JSON to a Clean DataFrame

*This is the bridge unit. Everything in Part 2 was about **getting** the data — calling the endpoint, following the pagination, surviving the retries. Everything in Part 3 is about **analysing** it. This lesson is the thing in between: taking the pile of dictionaries you fetched and turning it into a table you can actually trust. Read it straight through, about twenty-five minutes, then open `task.py`. It assumes unit 17's vocabulary — you know what a DataFrame and a Series are, you know `.dtypes` and `.isna()` and `.head()` — and nothing beyond that.*

*If SQL is your background, here's the honest framing for the whole unit: what you are doing is writing the `CREATE TABLE` and the `INSERT` for data that arrived with no schema, no types, and no guarantee that any two rows have the same columns. Nobody hands you a table. You build one.*

---

## 1. The moment this unit is about

Picture the interview. They send you a URL. You call it, you get JSON back, and you type the obvious thing:

```python
df = pd.DataFrame(records)
df.head()
```

Something prints. It has rows. It looks like a table. And now, with the clock running, you have to decide whether to believe it — because in about ninety seconds you're going to compute an average off it and say a number out loud.

That gap between "something printed" and "I believe this" is what the next twenty minutes are for. There are four things that go wrong, essentially always, and they are the four things this lesson covers: nested data that never became columns, numbers that are secretly text, timestamps that are secretly text, and rows that are duplicated or missing or impossible. Each has a standard fix, and none of the fixes are hard. The skill is knowing to look.

---

## 2. What `pd.DataFrame` does with nesting, and why it's a problem

Start with the failure, because the failure is what motivates the tool.

Real API records are nested — unit 04 spent a whole lesson on that. A GitHub repository carries its owner as a whole dictionary inside it; a World Bank observation carries its country the same way. So take the simplest possible nested record and hand it to the plain DataFrame constructor:

```python
import pandas as pd

data = [{"id": 1, "owner": {"login": "a", "type": "User"}}]

pd.DataFrame(data)
#    id                           owner
# 0   1  {'login': 'a', 'type': 'User'}
```

Look at what happened to the `owner` column. pandas didn't fail, didn't warn, and didn't unpack anything. It took the Python dictionary and put it in a cell — a whole dictionary, sitting inside one square of your table like a Russian doll that nobody opened.

That cell is dead weight. You can't filter on it (`df[df["owner"] == ...]` compares against a dictionary and does nothing useful), you can't group by it, you can't sum it, and `df.describe()` will pretend it isn't there. In SQL terms you have a column whose type is "blob" when what you wanted was two columns of text. The table looks right and roughly half of it is unusable.

**The fix is to flatten it.** To **flatten** a nested record means to pull the inner values up to the top level and give them compound names that record where they came from, so `{"owner": {"login": "a"}}` becomes the single key `owner.login` with the value `"a"`. You already wrote this by hand — it was unit 04's `flatten_dict`. pandas ships it:

```python
pd.json_normalize(data, sep=".")
#    id owner.login owner.type
# 0   1           a       User
```

Two real columns. Now you can filter on `owner.type`, count by `owner.login`, do anything a column supports. The word **normalize** in that function name is being used loosely — it doesn't mean anything like database normalization, it just means "put this into a regular, rectangular shape."

**The mental model for this section: `pd.DataFrame` puts whatever you give it into a cell; `pd.json_normalize` reaches inside first.** When your table has a column full of curly braces, that's the tell, and the fix is one function name.

**The practitioner's detail.** `json_normalize` flattens *all the way down* by default, and on a real response that can be brutal — a single GitHub repository record expands to something like eighty columns, most of them URLs you will never look at. When that happens, cap the depth:

```python
pd.json_normalize(data, max_level=1)   # flatten one level and stop
```

One level is usually the sweet spot. It gets you `owner.login` without also getting you `owner.permissions.admin` and forty of its cousins.

---

## 3. `record_path` and `meta` — when the nested thing is a list

Sometimes the nested value isn't a dictionary, it's a *list*, and each element of it deserves its own row. A search result with tags on it, a country with a list of currencies, an order with a list of line items. In SQL you'd say this data is one-to-many and belongs in a child table.

```python
data = [
    {"id": 1, "name": "a", "tags": [{"t": "x"}, {"t": "y"}]},
    {"id": 2, "name": "b", "tags": [{"t": "z"}]},
]

pd.json_normalize(data, record_path="tags", meta=["id", "name"])
#    t  id name
# 0  x   1    a
# 1  y   1    a
# 2  z   2    b
```

Two arguments are doing all the work here, and they're worth reading as a sentence. `record_path="tags"` says *"the rows I actually want are in here — explode this list so each element becomes its own row."* `meta=["id", "name"]` says *"and carry these fields down from the parent onto every row that came out of it."* Notice that `id` 1 appears twice, once per tag, exactly as a join against a child table would give you.

Written by hand that's a nested loop with bookkeeping. Here it's one line.

**The caveat, and I want to give it real weight because the one-liner is seductive.** `json_normalize` with a `record_path` is brittle. If even one record in your list is missing the `tags` key entirely — which is the *normal* state of real data, per unit 04 — it raises a `KeyError` and you get nothing at all. The `meta` columns also come back typed as generic objects rather than as proper types, so you'll be converting them anyway.

So here's the honest guidance, and it's guidance an interviewer will respect: for clean, uniform data, use `record_path` and `meta` and enjoy the one-liner. For genuinely messy data, do the flattening yourself in plain Python — unit 14's `find_records` and a `for` loop that builds a list of flat dictionaries with `.get()` on every field — and then hand *that* to `pd.DataFrame`. It is more code, it is more robust, and critically it is far easier to explain out loud when someone asks why row seventeen looks odd. A pipeline you can narrate beats a pipeline that's short.

---

## 4. `errors="coerce"`, and the thing that must always follow it

This is the most load-bearing idea in the unit. Read it twice.

Unit 17 told you that a text dtype on a column of numbers means the numbers arrived as strings, and that summing such a column concatenates instead of adding. The World Bank data you're about to work with does exactly this. So you convert. The tool is `pd.to_numeric`, and it has one argument that changes everything:

```python
df["population"] = pd.to_numeric(df["population"], errors="coerce")
```

To **coerce** a value means to force it into a type it wasn't in. The `errors="coerce"` part says what to do when the forcing fails — when a cell contains `"n/a"` or `""` or `"1,400,000"` with a comma in it. Without that argument, `to_numeric` raises an exception on the first bad value and your whole job dies on row seven of nine thousand. With it, the bad value quietly becomes `NaN` — pandas' missing marker from unit 17 — and every other row survives.

That is unit 04's `.get()` argument in a new outfit: one bad record must not kill a job that has already processed six hundred good ones.

**And now the part that nobody warns you about.** `errors="coerce"` is silent by construction. That's the whole point of it. Which means the following is entirely possible: your date column looked like `"05/06/2024"`, pandas couldn't parse it, forty percent of your rows became `NaN`, your code ran without a single complaint, and you computed a mean over the surviving sixty percent and said it out loud with confidence.

So the coercion is never one move. It's two, and they are welded together:

```python
df["population"] = pd.to_numeric(df["population"], errors="coerce")
print(df["population"].isna().sum(), "values failed to parse")
```

**The mental model: `errors="coerce"` doesn't delete your problem, it converts your problem into nulls. Counting the nulls is how you find out how big the problem was.** Say this out loud in an interview — *"I coerced, and I'm checking what I lost: three of nine hundred, so I'm comfortable"* — and you have just demonstrated the single habit that separates people who have shipped data code from people who have written it.

If the count comes back large, don't shrug. Look at the values that failed. Usually it's one fixable thing: a thousands separator, a currency symbol, the string `"None"`, a stray unit suffix.

---

## 5. `utc=True` — timestamps that are secretly text

Same story, different type. Timestamps arrive as strings, always, because JSON has no date type at all. So you convert:

```python
df["created"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
```

The `errors="coerce"` is there for the same reason as before: unparseable timestamps become `NaT` rather than raising. **`NaT`** stands for "Not a Time" — it's the missing marker specifically for datetime columns, the datetime equivalent of `NaN`, and `.isna()` catches it just the same.

`utc=True` is the argument that deserves the explanation. Unit 16 introduced the distinction between a **naive** timestamp, which is just a wall-clock reading with no idea where on earth it was taken, and an **aware** one, which carries its offset from UTC so it can be compared to any other aware timestamp unambiguously. **Timezone-aware** means exactly that: the value knows its own offset.

Here's why it matters in pandas specifically. Real feeds are inconsistent about offsets — some rows end in `Z` (meaning UTC), others in `+05:30`, and once in a while one has no offset at all. If you parse that mixture without `utc=True`, pandas can't find a single datetime type that fits all of them, so it gives up and hands you back a column of Python datetime objects typed as generic objects. It looks converted. It isn't. And then:

```python
df["created"].dt.year
# AttributeError: Can only use .dt accessor with datetimelike values
```

Every `.dt` accessor fails, which means every piece of time analysis you were about to do fails, and the error message points at the accessor rather than at the parse that actually caused it.

With `utc=True`, pandas converts every value to the same instant expressed in UTC, and you get one clean timezone-aware column that all the `.dt` tooling works on:

```python
df["created"].dt.year
df["created"].dt.month
df["created"].dt.day_name()
df["created"].dt.strftime("%Y-%m")     # "2024-05" — a string, great for labels
df["created"].dt.to_period("M")        # a monthly period, great for grouping
```

**The mental model: `utc=True` is not a formatting preference, it's what makes the column a datetime column at all when the offsets disagree.** Put it on every `to_datetime` call you write against API data. There is essentially no case where you regret it.

One nicety worth noticing: `.dt.strftime` propagates missing values correctly. A row whose timestamp was `NaT` gets a missing month rather than the string `"NaT"`, which is what you want and is not what naive string formatting would give you.

---

## 6. Nullable `Int64`, with a capital I

Unit 17 mentioned this and it's worth ten more sentences here, because the task turns on it.

A plain `int64` column in pandas is a block of machine integers, and there is no bit pattern in there that means "missing." So the moment one value goes missing, pandas has to put `NaN` in that slot — and `NaN` is a float. The only way to keep floats and integers in one column is for the whole column to become floats. It happens silently. Your IDs, which were `1`, `2`, `3`, are now `1.0`, `2.0`, `3.0`, and when you print them or write them to CSV or use them as a join key, they don't match anything anymore.

The fix is a **nullable dtype** — a pandas type that stores the values *and* a separate mask marking which slots are missing, so missing-ness doesn't have to be smuggled in as a float:

```python
df["count"] = pd.to_numeric(df["count"], errors="coerce").astype("Int64")
```

Capital `Int64` is the nullable one; lowercase `int64` is the plain machine one. One letter, entirely different behaviour. The missing values in a nullable column show up as `pd.NA`, `.isna()` finds them, arithmetic skips them, and your integers stay integers.

Reach for `Int64` on anything that is conceptually a whole number and might be missing: counts, years, IDs, points, comment totals. That's most of them.

---

## 7. The five-check cleaning ritual

Here is the two-minute routine. Run it, in this order, on every fresh dataset you ever touch. It is not sophisticated and it catches nearly everything.

```python
df.isna().sum()                              # 1. how much is missing?
df.dtypes                                    # 2. are the types right?
df.duplicated(subset=["id"]).sum()           # 3. any duplicates?
df.describe()                                # 4. do the numbers make sense?
df["region"].value_counts(dropna=False)      # 5. what are the categories?
```

Taking them one at a time, because each answers a different question and each has a standard response.

**One, missing counts.** `.isna().sum()` gives you a per-column tally of nulls. What you're looking for is a column that's mostly empty (probably not worth using), or a key column with any nulls at all (those rows are unusable — you can't join or group on a missing key).

**Two, dtypes.** You're scanning for the unit 17 tell: a column you expect to be numeric that isn't. On your pandas 3.0 a text column reports its dtype as `str`; on pandas 1.x and 2.x — which is what nearly every tutorial and StackOverflow answer and existing codebase you'll read assumes — the identical column reports `object`. Learn to see both as the same signal. A genuine `object` dtype on pandas 3.0 means something stronger: an actual Python object in there, a list or a dict, which sends you back to section 2.

**Three, duplicates.** A **duplicate** here means two rows that agree on whatever you're treating as the primary key — the same record arriving twice. This is not rare. Paginated APIs hand you an overlapping page routinely, especially if rows were inserted while you were paging. Duplicates are nasty precisely because they don't error; they just quietly inflate every count and skew every average. `subset=["id"]` is the important part — you almost never care about rows being identical across *all* columns, you care about the key repeating.

**Four, `describe()`.** This is your sanity pass on the numbers. Look at the min and the max of each column and ask whether they are physically possible. A latitude of 999, a population of -1, a comment count of four billion. This is how you find the garbage.

**Five, `value_counts`.** For any text column that behaves like a category, this shows you the actual vocabulary. You're looking for the same thing spelled two ways — `"Python"` and `"python"` and `" Python"` — which is exactly the kind of thing that splits one group into three in a `GROUP BY` and makes your top-five list wrong. Pass `dropna=False` so nulls appear in the tally instead of vanishing from it.

And the standard fixes, roughly in the order you'd apply them:

```python
df = df.drop_duplicates(subset=["id"], keep="last")
df = df.dropna(subset=["id"])                       # a row with no key is unusable
df["language"] = df["language"].fillna("unknown")
df["name"] = df["name"].str.strip()
df.columns = [c.lower().replace(".", "_") for c in df.columns]
```

`keep="last"` on the deduplication is a decision, not a default — it says the later copy is the fresher one. Sometimes `keep="first"` is right instead. Either way, *pick* one and be ready to say why.

---

## 8. Tidying column names, which matters more than it sounds

That last line above deserves its own moment, because it's the cheapest habit in this lesson.

`json_normalize` gives you dotted names — `owner.login`, `country.value`. Dots are legal as column names but they break two conveniences. Attribute access stops working, so `df.owner.login` doesn't mean what it looks like it means. And `df.query("owner.login == 'a'")`, which is the pleasant SQL-ish way to filter, can't parse it at all.

So on every frame you build, immediately after normalizing:

```python
df.columns = [c.strip().lower().replace(".", "_").replace(" ", "_") for c in df.columns]
```

Lowercase, underscores, no surrounding whitespace. It takes one line and it means nothing downstream has to remember whether this particular API spelled it `userName` or `user_name` or `User Name`. This is unit 04's key-normalizing comprehension, applied to columns instead of dictionary keys — same idea, same payoff: normalize at the boundary so the inside of your program only ever sees one convention.

---

## 9. Outliers and sanity checks

An **outlier** is a value far outside the plausible range for its column. Some outliers are real and interesting; many are junk — a sentinel value someone used to mean "missing," a unit mix-up, a broken sensor.

The checks are one-liners and you should run them on any column whose real-world range you know:

```python
df[df["latitude"].abs() > 90]                     # impossible coordinates
df[df["created"] > pd.Timestamp.now(tz="UTC")]    # timestamps in the future
df[df["count"] < 0]                               # negative counts
```

Note the `tz="UTC"` on that middle one — comparing an aware column against a naive timestamp raises, which is section 5 coming back around. Once your column is aware, everything you compare it to must be too.

Here's the part worth internalising for the interview. Finding an outlier and *mentioning it unprompted* — *"three rows have a latitude of 999, which isn't a real coordinate; I'm dropping them and here's the count"* — is one of the strongest signals you can send in a data conversation. It says you looked. Real data has these; nobody expects you to have prevented them, and nobody wants you to quietly delete them either. Name it, decide, move on.

---

## 10. The empty frame is a normal case

An API returning zero rows is not an error. A search that matched nothing, a date range with no activity, a filter that was too narrow — all ordinary. But aggregations over an empty DataFrame behave badly: means come back as `NaN`, some operations raise, and a `groupby` on nothing can give you a frame with no columns at all, which then breaks whatever you do next.

So guard at the top of any function that summarises:

```python
if df.empty:
    return {"count": 0, "mean": None}
```

There's a stronger version of this that the task makes you write, and it's a genuinely good habit: when a function returns a DataFrame and there's no data, return an **empty frame that still has the correct columns**.

```python
if not hits:
    return pd.DataFrame(columns=HN_COLUMNS)
```

That way every caller downstream can do `df["points"].sum()` or `df.columns` without a special case, and gets `0` rather than a `KeyError`. The shape of the answer stays the same whether there were fifty rows or none. That's a deliberate design choice and it's worth naming as one.

---

## 11. The whole pipeline, in one place

Everything above, assembled. This is roughly the shape of the function you'll write in the task, and roughly the shape of what you'd type in front of an interviewer.

```python
def build_frame(raw):
    records = find_records(raw)             # unit 14 — locate the rows in the envelope
    if not records:
        return pd.DataFrame()

    df = pd.json_normalize(records, sep=".")
    df.columns = [c.lower().replace(".", "_") for c in df.columns]

    df["created"] = pd.to_datetime(df["created_at"], errors="coerce", utc=True)
    df["stars"] = pd.to_numeric(df["stargazers_count"], errors="coerce").fillna(0).astype("Int64")

    df = df.drop_duplicates(subset=["id"]).dropna(subset=["id"])
    return df[["id", "name", "stars", "created"]]
```

Read it as five moves: find the records, flatten them, tidy the names, fix the types, drop the bad rows. Then one more move that people skip — **narrow to the columns you actually need, at the very end.** A seven-column frame prints in your terminal and you can read it at a glance. An eighty-column frame wraps into a wall of text that tells you nothing, and you will waste minutes squinting at it. Selecting columns is not tidiness for its own sake; it's what makes the rest of your session possible.

---

## 12. Look these up yourself

Same reason as always: finding an argument in the docs under mild pressure is a skill, and it's the one a tutorial can't hand you.

- `pd.json_normalize(..., errors="ignore")` — what it does about missing `meta` keys.
- `df.convert_dtypes()` — a one-shot "guess better types for everything," and when it's too clever.
- `df.rename(columns=str.lower)` — you can pass a *function* to `rename`.
- `pd.NA` versus `np.nan` versus `None` — three flavours of missing, and which shows up where.
- `df.duplicated(keep="first" | "last" | False)` — especially what `False` does.
- `df.explode("column")` — the other way to turn a list column into rows, and how it differs from `record_path`.

---

## 13. Check yourself

1. What does `pd.DataFrame` do with a nested dictionary that `json_normalize` doesn't?
2. What do `record_path` and `meta` each do, and when would you avoid them?
3. Why `errors="coerce"`, and what must you *always* do immediately afterwards?
4. Why `utc=True` on `to_datetime`, and what breaks without it?
5. Why `Int64` rather than `int64`?
6. What are the five checks you run on a fresh dataset, and what is each one looking for?

*(Answers: 1. it leaves the dictionary sitting inside a cell, where you can't filter or aggregate on it; `json_normalize` flattens it into dotted columns. 2. `record_path` explodes a nested list so each element becomes a row, `meta` carries parent fields down onto those rows — avoid them when records inconsistently have the key, since that raises a `KeyError`. 3. bad values become `NaN` instead of raising, so one broken row can't kill the job — then count the nulls, because the failure is otherwise silent. 4. mixed offsets otherwise leave the column as generic objects and every `.dt` accessor fails; `utc=True` gives one timezone-aware column. 5. `Int64` is nullable, so a missing value doesn't force the whole column to float and turn your IDs into `1.0`. 6. missing counts, dtypes, duplicates, describe, value_counts — looking for empty columns, text-where-numbers-should-be, repeated keys, impossible ranges, and the same category spelled two ways.)*

---

*Three things to carry out of this unit. First, `pd.DataFrame` accepts anything and `json_normalize` reaches inside — so a column full of curly braces is a tell, not a table. Second, `errors="coerce"` plus counting the nulls is one move, not two; the coercion is what keeps you alive and the count is what keeps you honest, and doing only the first is how people confidently report an average over the fraction of their data that happened to parse. Third, the five-check ritual takes two minutes and is the entire difference between a table you printed and a table you trust. Unit 19 takes that trustworthy table and does the interesting work — grouping, joining, and resampling over time — which is only interesting because this unit made the types real.*

*Now open [`task.py`](task.py).*
