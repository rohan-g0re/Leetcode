# 17 — pandas Basics

*About thirty minutes to read and thirty to do the task. This is the unit where the course stops treating data as "a list of dictionaries you loop over" and starts treating it as a table you ask questions of. If you know SQL — and you do — this lesson is mostly a translation exercise, and I'm going to lean on that translation hard, because it is by a distance the fastest route into pandas for someone with your background. Nothing here assumes you've seen pandas before. Every term is defined the first time it shows up.*

---

## 1. First, the honest question: should you even use this?

Let's get the sales pitch out of the way, because there isn't one.

**pandas earns its keep above a few thousand rows, or when you need grouping, joining, and time series in the same breath. Below that, unit 16's tools are faster to write and easier to explain.**

That's the real rule and it's worth saying before you learn anything else, because it will come up in your interview. You already know how to count things with `Counter`, group things with `defaultdict`, and sort things with `sorted(..., key=...)`. For forty records, that code is shorter than the pandas equivalent, has no import, and you can explain every line of it out loud without hedging. Reaching for a heavyweight library to count forty things is a small mark against you, not a point in your favour.

But the moment the question becomes "group these by region, work out the mean of one column and the count of another *within* each group, then rank the groups" — that's three nested loops in plain Python and one line in pandas. And at fifty thousand rows the plain-Python version starts to be slow enough that you notice. That's the crossover.

So the skill isn't "know pandas." The skill is knowing which side of that line you're on and saying so. If an interviewer hands you a hundred-row endpoint and you say *"this is small enough that I'd just use `Counter` — pandas would be overkill, though I'll switch if you want to see the grouping"* — that is a better answer than silently importing pandas.

With that settled: here's pandas.

---

## 2. The two objects, and what they are in SQL

pandas gives you exactly two things to hold data in, and everything else in the library is an operation on one of them.

A **Series** is a single labelled column of values. Think of one column of a result set, lifted out on its own, with the row identifiers still attached to it.

A **DataFrame** is a table: several Series lined up side by side, all sharing the same row labels. That's it. A DataFrame is a result set that didn't disappear after you printed it — you can keep filtering it, sorting it, adding columns to it, and it stays a table the whole way.

```python
import pandas as pd

s = pd.Series([1, 2, 3], name="stars")
df = pd.DataFrame([{"name": "flask", "stars": 66000},
                   {"name": "click", "stars": 15000}])
```

Everybody writes `import pandas as pd`. It's not a rule, but it is universal enough that writing `import pandas` and then `pandas.DataFrame(...)` will look faintly odd to a reviewer.

The word you'll trip over is **index**. The index is the set of row labels — the names pandas has given each row. When you build a frame from scratch like the one above, pandas invents an index for you: the whole numbers `0, 1, 2, ...`, called a `RangeIndex`. It looks like a row number, and while the frame is fresh it *is* a row number, which is why the distinction I'm about to make in section 7 seems like pedantry until suddenly it isn't.

The SQL mapping, which I'll keep coming back to:

| SQL | pandas |
| --- | ------ |
| a result set | a `DataFrame` |
| one column of it | a `Series` |
| `WHERE` | a boolean mask, section 6 |
| `ORDER BY` | `.sort_values()` |
| `GROUP BY ... aggregate` | `.groupby().agg()` |
| `SELECT a, b` | `df[["a", "b"]]` |
| `LIMIT 5` | `.head(5)` |
| `IS NULL` | `.isna()` |
| a computed column in the `SELECT` list | `df["new"] = ...` |

The one row of that table with no SQL equivalent is the index, and that's genuinely the piece that has no counterpart in your existing mental model. A SQL result set has no notion of a row keeping its identity from the previous query. A pandas row does. Hold that thought.

**Mental model for this section: a DataFrame is a result set that stays on the table after the query finishes, so you can run the next query on it directly.**

---

## 3. Where DataFrames come from — and why unit 14 was aiming here all along

You build a DataFrame from a list of flat dictionaries:

```python
df = pd.DataFrame([{"name": "flask", "stars": 66000},
                   {"name": "click", "stars": 15000}])
```

Each dictionary becomes a row, each key becomes a column, and the column order comes from the key order of the first dictionary. That's the constructor you'll use for about ninety percent of the frames you ever build.

Now look back at unit 14. That unit spent its whole length getting you from a nested, inconsistent API response down to *a list of flat dictionaries*, and unit 04 said the same thing in its closing paragraph. This is why. That shape wasn't an arbitrary target chosen because it's tidy — it is the exact thing `pd.DataFrame` accepts, the exact thing the CSV writer accepts, and the exact thing FastAPI serialises back to JSON without complaint. Every bit of flattening you did in Part 2 was building the input to this line.

That's also the shape of the advice for this unit's task. When you have a nested response and you want a table, do **not** try to make pandas understand the nesting. Flatten it into a list of dicts in plain Python first — where `or {}` and `.get()` are readable and you can print the intermediate result — and only then hand it over. The messy part stays in the language that's good at messy parts.

There's one exception worth knowing, and the task uses it: `pd.json_normalize`. Hand it a list of nested dicts and it flattens one or more levels for you, turning `{"region": {"value": "Europe"}}` into a column literally named `region.value`. It's excellent when the nesting is regular and shallow, which the World Bank response is. It's not a substitute for thinking when the nesting is ragged.

---

## 4. The five commands you run on every new frame

Before you compute anything, look at what you've got. These five, in this order, every time:

```python
df.shape        # (rows, columns)
df.head()       # first 5 rows
df.dtypes       # the type of each column
df.info()       # dtypes + non-null counts + memory
df.describe()   # count/mean/std/min/quartiles/max for numeric columns
```

`shape` tells you whether you got the number of rows you expected — if you asked for a hundred and got twenty, stop and find out why before you build anything on it. `head` shows you the first five rows so you can see whether the values look like values. `dtypes` is section 5 and it's the important one. `info` is the two previous ones plus a count of how many non-missing values each column has, which answers "how much of this is missing?" in a single line. `describe` gives you the summary statistics of every numeric column, and its real job is catching absurdity — a maximum of 999999 in an age column, a minimum of -1 in a count.

I'm being unusually prescriptive here because this is the habit that separates people who trust their data from people who get surprised by it in front of an audience. It takes eleven seconds and it has caught something real for me more often than not.

A few more you'll reach for constantly:

```python
df.columns              # column names
df["language"].value_counts()          # counts per distinct value
df["language"].value_counts(dropna=False)   # including NaN
df["language"].unique()
df["stars"].sum() / .mean() / .median() / .min() / .max()
```

`value_counts()` is `SELECT col, COUNT(*) GROUP BY col ORDER BY 2 DESC` in one method call, and it's probably the single highest-value thing you can type at an unfamiliar column. Note its default, which is the practitioner's detail of this section: **`value_counts()` silently drops missing values.** So if a column has four hundred rows and the counts add up to three hundred and eighty, twenty were null and pandas didn't mention it. Pass `dropna=False` when you want the missing ones counted as their own category, which when you're auditing data is nearly always.

---

## 5. dtypes, and why a text dtype where you expected a number is a warning

**What a dtype is.** Every column in a DataFrame has one type that applies to the entire column — a **dtype**, short for data type. This is the biggest structural difference from a plain list of dictionaries, where every record could hold whatever it liked in a given field. In pandas, the column commits. That commitment is what makes the operations fast, and it's what makes a wrong dtype a real problem rather than a cosmetic one.

Here are the ones you'll actually meet:

| dtype | Meaning |
|-------|---------|
| `int64` | integers |
| `float64` | floats — **and any integer column containing NaN** |
| `bool` | booleans |
| `datetime64[ns]` | timestamps |
| `str` | text (pandas 3.0+; older versions show these as `object`) |
| `object` | arbitrary Python objects — lists, dicts, genuinely mixed types |

A note on that table before the two lessons in it. You are running **pandas 3.0**, where a column of text reports its dtype as `str`. On pandas 1.x and 2.x — which is what essentially every tutorial, every StackOverflow answer, and every existing codebase you'll open assumes — that same column reports `object`. You need to recognise both, because you'll be reading older material constantly and it will keep telling you to look for `object`. When it does, it means what your machine calls `str`.

**First lesson: a text dtype on a column you expected to be numeric means the numbers arrived as text.**

This is the one to actually remember. Suppose an API sends you `{"population": "1400000"}` — the right information, wrapped in quotes. pandas has no way to know you meant a number, so the column comes back as text. And then:

```python
df["population"].sum()
```

does not raise an error. It *concatenates the strings*. You get one enormous nonsense number-shaped string, or a value so large it's obviously wrong but only if you look closely. No exception, no warning, wrong answer — and it looks plausible right up until you check. This is exactly the World Bank data you'll meet in this unit's task, where latitude and longitude arrive as text, and it's why `df.dtypes` is on the five-command list.

The fix is `pd.to_numeric(series, errors="coerce")`, which converts what it can and turns what it can't into a missing value rather than exploding on row seven hundred. You'll write it in `countries_frame`.

**Second lesson: any integer column containing a missing value becomes `float64`.**

The reason is that pandas' missing marker, `NaN`, is itself a float, and a column has one dtype for all of it, so a single missing value promotes the whole column. The visible symptom is that your integer IDs start printing as `1.0`, `2.0`, `3.0`, which looks like a formatting bug and isn't. The fix is `.astype("Int64")` — capital I, which is pandas' nullable integer type and can hold missing values without turning into floats.

**Mental model: the dtype is the column type declaration you never wrote. pandas guessed it from the data, and when its guess is wrong, arithmetic goes quietly wrong rather than loudly wrong.**

---

## 6. Selecting, and then filtering

Selection first, because it's the easy half.

```python
df["stars"]            # one column -> Series
df[["name", "stars"]]  # several columns -> DataFrame  (note the double brackets)
df.head(10)
df.iloc[0]             # first row, BY POSITION -> Series
df.loc[0]              # row with INDEX LABEL 0
df.iloc[0:3]           # first three rows
df.loc[df["stars"] > 1000]        # filter by condition
```

The double brackets on the second line catch everyone once. `df["stars"]` with a single string gives you one column as a Series. `df[["name", "stars"]]` — a *list* of names inside the brackets — gives you a DataFrame with those columns. The inner brackets are the list; the outer ones are the indexing. One column asked for as a list, `df[["stars"]]`, gives you a one-column DataFrame rather than a Series, which is occasionally exactly what you want.

**Now filtering, which is the load-bearing part of this section and possibly of the unit.**

```python
df[df["stars"] > 1000]
df[(df["stars"] > 1000) & (df["language"] == "Python")]
df[(df["language"] == "Python") | (df["language"] == "HTML")]
df[~df["archived"]]
df[df["language"].isin(["Python", "Go"])]
df[df["license"].isna()]
df[df["name"].str.startswith("fla")]
```

Look at what's actually happening in the first line, because once you see it the rest is mechanical. `df["stars"] > 1000` is not a filter. It's a comparison applied to a whole column, and it produces *another column* — one holding `True` or `False` for every row. That column of booleans is called a **mask**. Then `df[mask]` hands you back the rows where the mask says `True`.

So filtering in pandas is two steps that you usually write as one: build a column of yes/no answers, then use it to select. Once you hold that picture, everything else in this section is obvious. `WHERE stars > 1000` in SQL is a single conceptual step; in pandas the intermediate object is real and you can print it, store it in a variable, and combine it with others. That turns out to be a genuine advantage, and the task's `filter_repos` builds its mask up in stages precisely because the conditions are optional.

**The two rules that will bite you.**

First: combine masks with `&`, `|`, and `~` — **not** with `and`, `or`, and `not`. And it's worth understanding why the English keywords don't just work, because "pandas uses different symbols" is a thing you'll forget and "the keywords are asking a question that has no answer here" is a thing you won't.

`and` needs to decide whether its left-hand side is true or false so it can decide whether to bother evaluating the right. That's unit 01's short-circuiting. But the left-hand side here is a whole column of five hundred true-or-false values. Is that true? There's no honest answer — some of them are and some of them aren't — so pandas refuses and raises `ValueError: The truth value of a Series is ambiguous`. When you see that message, you wrote `and` where you meant `&`. `&` has no such problem, because it doesn't collapse anything: it lines the two masks up and computes a new true-or-false for each row independently. That word — **elementwise**, meaning "applied to each element separately, producing one result per element" — is the whole distinction.

Second: **wrap every condition in parentheses.** This is not a style preference, it's a correctness requirement, and the reason is an accident of Python's grammar. `&` binds *tighter* than `>`. So this:

```python
df[df.a > 1 & df.b < 2]
```

is parsed by Python as `df.a > (1 & df.b) < 2` — it does the `&` first, on `1` and the column, and produces something baffling and an error message that points nowhere useful. Written with the parentheses, `df[(df.a > 1) & (df.b < 2)]`, it does what it reads as. Put them in every time, including when there's only one condition and you don't need them yet, because you'll add a second condition later.

The rest of that code block is worth a sentence each. `~` is "not" — it flips a mask, so `df[~df["archived"]]` is the non-archived rows. `.isin([...])` is SQL's `IN`. `.isna()` is `IS NULL`, and section 9 explains why you must never write `== None` here. `.str.startswith(...)` is section 8.

**Sorting** is `ORDER BY` and behaves how you'd hope:

```python
df.sort_values("stars", ascending=False)
df.sort_values(["language", "stars"], ascending=[True, False])
df.nlargest(5, "stars")        # faster and clearer than sort + head
```

The list form sorts by several columns in order, and `ascending` takes a matching list so you can mix directions — exactly `ORDER BY language ASC, stars DESC`. `nlargest` is the one people don't know about: it's `sort_values(...).head(n)` but it doesn't sort the whole frame to get the top five, and it reads better.

---

## 7. `.loc` versus `.iloc`, and why this is the confusion

Here's the one I promised in section 2, and it is fairly comfortably the single most common source of pandas bewilderment.

**`.loc` selects by index label. `.iloc` selects by integer position.**

On a fresh frame those are the same thing, because the labels pandas invented *are* `0, 1, 2, ...` in order. `df.loc[0]` and `df.iloc[0]` both give you the first row and you could be forgiven for concluding they're synonyms.

They diverge the instant you filter or sort — because **the original row labels travel with the rows.** Filtering a frame down to rows 4, 9 and 12 gives you a three-row frame whose index is still `[4, 9, 12]`. Now:

- `result.iloc[0]` gives the first row of the new frame. That's the one that was row 4.
- `result.loc[0]` raises a `KeyError`, because there is no longer any row labelled 0.

And the sneakier version: after a `sort_values`, `df.iloc[0]` is the top-ranked row while `df.loc[0]` is whichever row happened to be first *before* you sorted. Both work, neither errors, one of them is silently answering a different question than you asked.

This behaviour is deliberate and it's occasionally invaluable — it's what lets you filter a frame, compute something, and line the answer back up against the original rows. But when you don't want it, say so explicitly:

```python
result = df[df["stars"] > 1000].reset_index(drop=True)
```

`.reset_index(drop=True)` throws away the old labels and renumbers from zero. The `drop=True` matters: without it, pandas politely keeps your old index by turning it into a new column called `index`, which is almost never what you meant and will show up unexpectedly in your output. Every function in this unit's task that returns a frame asks for `reset_index(drop=True)`, and now you know it's not bookkeeping — it's the difference between a result you can index positionally and one you can't.

**Mental model: labels are names, positions are seat numbers. Filtering removes people from the room without renaming anyone, so seat three is now occupied by someone still called Twelve.**

---

## 8. Vectorization — the idiom, and why a reviewer looks for it

Adding a column is assignment, and it operates on the whole column at once:

```python
df["ratio"] = df["forks"] / df["stars"]              # vectorized: whole column at once
df["big"] = df["stars"] > 10000
df["name_upper"] = df["name"].str.upper()
```

That first line divides every value in `forks` by the value in `stars` on the same row, all in one go, and stores the resulting column. There's no loop. In SQL you'd write it as an expression in the `SELECT` list and think nothing of it; the pandas version is the same idea, and the same instinct serves you.

**Vectorized** is the word for this, and here is what it actually means rather than what it vaguely gestures at. A pandas column isn't a Python list — it's a contiguous block of memory holding raw numbers, and the arithmetic is performed by compiled C code looping over that block. Python isn't involved in the loop at all. So `df["forks"] / df["stars"]` is one instruction from Python's point of view, and somewhere between ten and a hundred times faster than doing it a row at a time.

The row-at-a-time version has a name and you should recognise it so you can avoid it:

```python
# don't
df["ratio"] = [row["forks"] / row["stars"] for _, row in df.iterrows()]

# do
df["ratio"] = df["forks"] / df["stars"]
```

`.iterrows()` walks the frame one row at a time, and each row it hands you is constructed as a fresh Series object — which is expensive, and does it once per row. It is not merely slower; it signals to anyone reading that you're thinking in loops rather than in columns. This is the idiom an interviewer is watching for. Writing the vectorized version, unprompted, is a small clear signal that you've used the library rather than read about it.

When you genuinely need arbitrary Python for each value, `.apply()` is the escape hatch:

```python
df["label"] = df["stars"].apply(lambda s: "big" if s > 10000 else "small")
```

Be honest about what that is: `.apply` is a Python-level loop wearing a pandas coat. It's correct, it's readable, and on a frame of a few thousand rows it's completely fine. On a frame of a few million it's the bottleneck. Reach for a vectorized expression or `np.where(cond, a, b)` — which is a vectorized if/else — when you can, and use `.apply` when the logic genuinely doesn't fit into column arithmetic.

**Mental model: stop thinking "for each row" and start thinking "one instruction to the whole column." Every time you catch yourself writing a loop over a frame, there's a column operation you haven't found yet.**

### String methods live under `.str`

A column of text doesn't have `.upper()` directly, because the column is a Series and `.upper()` is a string method. You reach the string methods through the `.str` **accessor** — a small doorway on a Series that applies a string operation to every value:

```python
df["name"].str.lower()
df["name"].str.contains("api", case=False, na=False)
df["name"].str.split("-").str[0]
df["url"].str.replace("http://", "https://", regex=False)
```

Note `.str[0]` in the third line: after `.split("-")` each value is a list, and `.str[0]` reaches into position zero of every one of them.

The practitioner's detail here is `na=False` on `.str.contains`, and it's a real trap. If the column has any missing values, `.str.contains` returns `NaN` for those rows rather than `True` or `False` — because it honestly can't tell you whether a value that doesn't exist contains "api". You now have a mask with three possible values, and using it to filter raises `ValueError: Cannot mask with non-boolean array`. Passing `na=False` says "treat missing as not-a-match," which is almost always what you meant. Get in the habit of typing it every time, the same way you type the parentheses.

---

## 9. Missing data, and why `==` is the wrong tool

pandas marks a missing value with **`NaN`**, which stands for "not a number" and is a special float value borrowed from the IEEE floating-point standard. When you build a frame from dictionaries, Python's `None` becomes `NaN` in a numeric column. In text columns you may also see `None` or `pd.NA` depending on the dtype, and pandas' missing-value functions treat all three the same, which is the mercy that makes this workable.

```python
df.isna().sum()                    # missing count per column -- run this early
df["license"].fillna("none")
df.dropna(subset=["stars"])        # drop rows missing a specific column
df.dropna()                        # drop rows missing ANYTHING -- usually too aggressive
```

`df.isna()` gives you a frame of `True`/`False` the same shape as the original, and summing it collapses that to a count per column — because summing booleans counts the `True`s, which is unit 01's trick showing up again. Run it early. It's the same information `df.info()` gives you, arranged so you can act on it.

**The rule with teeth: `NaN` is not equal to itself.** `float("nan") == float("nan")` is `False`, and that's not a pandas quirk — it's in the floating-point standard, on the reasoning that two unknown values can't be asserted to be the same. The consequence for you is that `df[df["license"] == None]` matches nothing at all, silently, and you go looking for a bug in your data that isn't there. **Always use `.isna()` and `.notna()`.** Never `==`.

There's a judgment call buried in this section that's worth narrating out loud when you hit it. Filling missing values before you aggregate changes your means. Dropping rows before you aggregate changes your counts. Neither is right in general — filling ratings with zero drags the average down, dropping them throws away the information that they were missing — and the useful thing in an interview is not picking correctly but saying which you picked and why. *"I dropped rather than filled here because a missing latitude isn't a latitude of zero, and zero would drag the mean toward the equator"* is the sentence that demonstrates you understand your own output.

---

## 10. Grouping — `GROUP BY`, with the parts named differently

This is the operation pandas is genuinely, obviously better at than plain Python, and it's the reason the crossover in section 1 exists at all.

```python
summary = df.groupby("language").agg(
    repos=("name", "count"),
    total_stars=("stars", "sum"),
    mean_stars=("stars", "mean"),
    max_stars=("stars", "max"),
).reset_index()
```

Read that against the SQL you'd write for the same thing and the mapping is one-to-one:

```sql
SELECT language,
       COUNT(name)  AS repos,
       SUM(stars)   AS total_stars,
       AVG(stars)   AS mean_stars,
       MAX(stars)   AS max_stars
FROM repos
GROUP BY language
```

`.groupby("language")` is the `GROUP BY` clause. Each keyword argument to `.agg` is one line of the `SELECT` list, written backwards: the name you want comes first, and the `(column, function)` tuple says which column to aggregate and how. This form is called **named aggregation** and it's the one to learn, because it hands you back a frame with the column names you asked for rather than a two-level column structure you then have to flatten.

The `.reset_index()` at the end is there because `groupby` puts the grouping column into the *index* rather than leaving it as a column — which is section 7 biting again. `reset_index()` moves it back out into an ordinary column, which is what you want if the next thing you do is sort or serialise.

Two aggregation functions behave in ways worth knowing before they surprise you, and both matter in this unit's task. **`"count"` ignores nulls** — it counts how many non-missing values there were in that column within the group, not how many rows the group has. That sounds like a footnote until you realise it's exactly how you answer "how many of these countries have a capital city": count the capital column, and the missing ones don't count themselves. And **`"mean"` skips `NaN`** rather than being poisoned by it, so a group where four of five values are present gives you the mean of those four, and you only get `NaN` back when *every* value in the group is missing. Both of these are the behaviour you want; they just aren't the behaviour you'd get from writing the loop yourself, which is why they're worth knowing you're relying on.

---

## 11. Chaining

Every operation you've seen returns a *new* DataFrame rather than modifying the one you called it on. That means you can write a whole pipeline as one expression:

```python
result = (
    df[df["language"] == "Python"]
    .sort_values("stars", ascending=False)
    .head(10)
    [["name", "stars"]]
    .reset_index(drop=True)
)
```

**Chaining** is the name for stringing operations together like that, one after another, each one taking the previous one's output. The outer parentheses are what let you break it across lines — without them Python reaches the end of the first line and thinks the statement is finished.

It's worth writing this way for two reasons. It reads top to bottom as a description of what happened, in the order it happened, which a nest of function calls does not. And it's easy to debug: comment out the last line and run it, then the last two, and you can see exactly which step went wrong. That's a considerably nicer debugging story than a single dense expression.

The one thing to watch is length. A chain of four or five steps is clear; a chain of twelve is a wall. Break it into two named intermediates when the thing it's doing changes character — cleaning, then summarising.

---

## 12. Copies and views, and the warning you'll definitely see

This one is confusing on purpose, in the sense that even pandas finds it confusing.

```python
subset = df[df["stars"] > 1000]
subset["new"] = 1        # may warn: SettingWithCopyWarning
```

When you slice a frame, pandas sometimes hands you a **view** — a window onto the original data, sharing the same memory, so writing through it changes the original — and sometimes a **copy**, an independent snapshot where writing changes nothing but itself. Which one you get depends on details of the slice you almost certainly don't want to reason about. This is unit 01's names-not-boxes idea in its most annoying form: you have a second name, and you can't easily tell whether it's a second name for the same thing or a name for a new thing.

pandas can't reliably tell either, so when you assign into something that might be a view it raises `SettingWithCopyWarning` — which is a warning, not an error, so your program continues and may or may not have done what you intended.

The fix is to stop leaving it ambiguous:

```python
subset = df[df["stars"] > 1000].copy()
subset["new"] = 1
```

`.copy()` says explicitly: give me an independent frame, I intend to modify it, and I do not want the original touched. The rule to carry: **when you see `SettingWithCopyWarning`, add `.copy()` at the point where the subset was created** — not at the point where the warning appeared. The warning fires at the assignment, but the ambiguity was born at the slice.

This is exactly what `add_metrics` in the task requires. It's handed a frame, it adds three columns, and the tests check that the frame it was handed came back unchanged. `.copy()` on the first line is the whole answer, and doing it habitually — copy first, then modify — costs nothing and removes an entire category of bug.

---

## 13. Getting the data back out

You built the frame from a list of dicts. You get it back out the same way:

```python
df.to_dict("records")     # list of dicts -- the inverse of how you built it
df.to_csv("out.csv", index=False)
df.to_json("out.json", orient="records", indent=2)
df.to_string()            # full text, no truncation
```

`to_dict("records")` is the exact inverse of `pd.DataFrame(list_of_dicts)` — one dictionary per row, keys from the columns. That symmetry is the whole architecture of how pandas fits into your program: plain Python at the edges where the data is messy and you need `.get()` and `or {}`, pandas in the middle where the data is rectangular and you want grouping. `to_dict("records")` is the exit door.

It's also the door to FastAPI, which is where this course is heading. FastAPI serialises lists of dictionaries perfectly well and does not know what a DataFrame is. So when your endpoint's job is "fetch this, summarise it, return it", the last line of the function is `to_dict("records")`.

Two smaller notes. `index=False` on `to_csv` stops pandas writing your row labels as a nameless leading column, which is section 7's index sneaking into your output file and confusing whoever opens it. And `to_string()` prints the frame without the `...` truncation you get from a normal `print`, which matters the first time you have twenty columns and pandas shows you six of them.

There's a real trap on the way out, and the task makes you handle it: **`json.dumps` will happily write the literal token `NaN` into your JSON, and `NaN` is not valid JSON.** Python's own `json.loads` accepts it back, because Python is being permissive, so you can round-trip it in your own tests and never notice. Every other consumer — a JavaScript front end, a strict parser, FastAPI's response validation — rejects it. So before serialising, convert missing values to `None`, which becomes a proper `null`. That's the entire reason `to_records` in the task is more than a one-liner.

---

## 14. Look this up yourself

The task needs a few things I've deliberately left out. Reading documentation under time pressure is the transferable skill; go find these.

- `pd.set_option("display.max_columns", None)` and `display.width` — for when pandas truncates your frame in the terminal.
- `df.query("stars > 1000 and language == 'Python'")` — filtering with a string, where `and` *does* work. Note why that isn't a contradiction.
- `np.where(cond, a, b)` — vectorized if/else.
- `df.assign(ratio=lambda d: d.forks / d.stars)` — adding a column inside a chain, without breaking it.
- `pd.to_numeric(series, errors="coerce")` — you need this one for `countries_frame`.
- `Series.where(cond)` — what happens to the values where the condition is false. This is how you turn zeros into `NaN` before dividing.
- `df.memory_usage(deep=True)` — the honest answer to "how big is this actually".

---

## 15. Check yourself

Answer these before opening the task. If one isn't obvious, reread that section — it's cheaper than getting stuck.

1. What does a `str` (or `object`) dtype on a "population" column tell you, and what goes wrong if you ignore it?
2. Why does an integer column become `float64`?
3. What's the difference between `.loc` and `.iloc`, and when do they stop agreeing?
4. Why `&` instead of `and` when filtering, and why the parentheses?
5. Why is `df["a"] / df["b"]` preferred over `.iterrows()`?
6. What does `SettingWithCopyWarning` mean and where do you put the fix?
7. Why can't you find missing values with `df[df["x"] == None]`?

*(Answers: 1. the values arrived as strings, so `.sum()` concatenates them instead of adding — no error, wrong answer. 2. `NaN` is a float and a column has one dtype, so one missing value promotes the whole column. 3. `.loc` selects by index label, `.iloc` by position; they agree on a fresh frame and diverge as soon as you filter or sort, because the old labels travel with the rows. 4. `and` needs a single true-or-false and you've handed it a whole column of them; `&` works elementwise. The parentheses are needed because `&` binds tighter than `>`. 5. it runs in compiled C over the whole column instead of constructing a Series per row in Python — faster, and the idiom a reviewer expects. 6. pandas can't tell whether your slice is a view onto the original or an independent copy; add `.copy()` where the subset is created, not where the warning appears. 7. `NaN` is not equal to itself, so the comparison matches nothing; use `.isna()`.)*

---

*Four things to carry out of this unit. First, the decision itself: pandas above a few thousand rows or when grouping, joining and time series show up together, and unit 16's `Counter` and `defaultdict` below that — and saying which you chose is worth more than either choice. Second, `df.dtypes` is the first thing you look at, because a text dtype on a numeric column produces a wrong answer rather than an error, and wrong answers that look plausible are the expensive kind. Third, filtering is a mask — a column of true and false that you build with `&`, `|`, `~` and a lot of parentheses, and that you can print and inspect like any other column. Fourth, the shape at both ends is a list of flat dictionaries: that's what unit 14 was building toward, it's what `pd.DataFrame` eats, and `to_dict("records")` is how you hand it back to FastAPI. Unit 18 points all of this at a real, dirty World Bank response, and unit 19 adds the time-series half.*

*Now open [`task.py`](task.py).*
