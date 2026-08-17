# 16 — Analysis Without Any Dependencies

**Time: ~25 min lesson + ~30 min task.**

*This is the unit where the whole first half of the course finally pays off. Units 11 to 15 were about getting data out of a live API and into a sane shape — unit 14 in particular ended with a list of flat dictionaries, one dictionary per record. That was the plumbing. This unit is what you do with the water. When an interviewer says "now tell me something useful about this," what follows is the toolkit you answer with.*

*You know SQL, and this is the unit where that helps most. Almost everything here — counting, grouping, aggregating, joining — is something you have already done a hundred times in a query. The difference is that here you can see the machinery. Where you'd write `GROUP BY`, you'll write the loop the database writes for you. That turns out to be a good thing to have seen once, and I'll point at the SQL equivalent every time one exists.*

---

## 1. Why you would do this without pandas at all

There is a real temptation, the moment somebody says the word "analysis," to reach for pandas. Resist it for a moment and think about the size of the problem in front of you.

Here is the framing that should govern the whole lesson: **for anything under a few thousand records, the standard library is faster to write, easier to explain, and produces output you can read without a viewer.** No import that takes two seconds to load. No `DataFrame` you have to `.head()` at to see what's in it. No column-dtype surprises. Just dictionaries and loops, and answers that print as plain text.

The interview angle is worth saying plainly, because nobody usually does. Reaching for pandas on a forty-row problem is a *mild negative signal*. It suggests you know one hammer. Doing the same job cleanly in the standard library — a `Counter`, a grouped loop, a formatted table — is a positive one, because it shows you understand what pandas is doing rather than only how to call it.

That is not an argument against pandas, which is units 17 to 19 and is genuinely the right tool at scale. It is an argument that **knowing which to reach for is itself part of the skill.** Rough boundary: under a few thousand rows and a handful of questions, plain Python. Tens of thousands of rows, wide tables, repeated reshaping, or anything you want to write to Excel — pandas. Say the boundary out loud when you choose, and the choice reads as deliberate rather than defaulted.

---

## 2. `Counter` — because counting is most of analysis

Sit with that heading for a second, because it's more true than it sounds. "How many per language?" "How many per author?" "How many per status code?" "Which value shows up most?" A startling proportion of every real analytical question is a count with a `GROUP BY` bolted onto it, and Python ships a tool that does exactly that in one line.

**What it is.** `Counter` lives in the `collections` module. You hand it a sequence of values and it hands you back a tally — each distinct value paired with how many times it appeared.

```python
from collections import Counter

languages = Counter(r["language"] for r in repos)

languages["Python"]              # 13
languages.most_common(3)         # [('Python', 13), ('HTML', 1), ('CSS', 1)]
languages.total()                # 17   (Python 3.10+; sum(counts.values()) otherwise)
len(languages)                   # number of distinct languages
```

That first line is the whole of `SELECT language, COUNT(*) FROM repos GROUP BY language` and it does not need a database. The thing inside the parentheses is a generator expression from unit 07 — it produces the language of each repo one at a time, and `Counter` tallies them as they arrive.

**The mental model to carry:** a `Counter` is *a tally sheet where every possible line already exists and starts at zero.* You never have to create a row before you increment it, and you never have to check whether a row exists before you read it.

**Three things about it that actually matter.**

First, **a missing key returns `0` rather than raising.** Compare that to unit 04, where `d["nope"]` on a plain dictionary raises `KeyError` and stops your program dead. On a `Counter`, `languages["COBOL"]` is simply `0`, which is the honest answer — you counted zero of them. This is why you can write `counts["Python"] - counts["Ruby"]` without first checking that both are present, and it removes a whole category of defensive code.

Second, **`Counter` is a `dict` subclass.** You met the word *subclass* in unit 08, when exceptions turned out to be arranged in a family tree — a subclass is a type built on top of another type, inheriting everything it does and adding a little more. Here it means every single thing you learned in unit 04 still applies unchanged: `.get()`, `.items()`, `in`, `len()`, looping, dictionary comprehensions. `Counter` is a dictionary that has learned two new tricks, not a new thing to learn from scratch.

Third, **`most_common` sorts for you.** `most_common(3)` gives the top three; `most_common()` with no argument gives *everything*, in descending order. That single call replaces a `sorted(counts.items(), key=lambda kv: kv[1], reverse=True)` that you would otherwise have to get right under pressure, including remembering which element of the pair to sort on.

A few more operations you'll want:

```python
Counter(a) + Counter(b)          # merge two tallies, summing the counts
Counter(a) - Counter(b)          # subtract one tally from another
counts.update(more_items)        # feed in more data, adding to what's there
```

**The practitioner's detail.** Subtraction quietly drops anything that lands at zero or below. `Counter({"a": 1}) - Counter({"a": 3})` is not `Counter({"a": -2})` — it's an *empty* Counter. That's deliberate, because `Counter` is designed around multisets where negative counts are meaningless, but it will surprise you the first time you try to compute a difference between this week's numbers and last week's and the categories that shrank simply vanish from your report. When you want signed differences, do the subtraction yourself over the union of the keys.

There's also one asymmetry worth flagging now, because it's the exact opposite of the tool in the next section: **reading a missing key from a `Counter` does not create it.** `languages["COBOL"]` returns `0` and leaves the Counter the same size. Hold onto that, because `defaultdict` behaves differently and the contrast is the whole reason people get bitten.

---

## 3. `defaultdict` — grouping, tidied up

`Counter` is for when the thing you're accumulating is a count. But often you want to collect the actual records into buckets, or sum a field, rather than just tally occurrences.

You already know how to do this. In unit 04 you learned the `setdefault` idiom:

```python
groups = {}
for record in records:
    groups.setdefault(record["language"], []).append(record)
```

That works, it needs no import, and it is genuinely fine. `defaultdict` is the tidied-up version of the same idea.

**What it is.** `defaultdict` takes a *factory* — a function it calls to manufacture a value whenever you touch a key that doesn't exist yet.

```python
from collections import defaultdict

by_language = defaultdict(list)
for repo in repos:
    by_language[repo["language"]].append(repo["name"])

stars_by_language = defaultdict(int)
for repo in repos:
    stars_by_language[repo["language"]] += repo["stars"]
```

`defaultdict(list)` calls `list()` — which produces `[]` — the first time each new key is touched, so the `.append` on the very next character always has something to append to. `defaultdict(int)` calls `int()`, which produces `0`, so `+=` always has a number to add to. Without either, `by_language[key].append(...)` raises `KeyError` on the first record of every group, which is precisely the problem `setdefault` exists to solve.

**Mental model:** *a dictionary with a small factory in the basement.* Ask for a key it doesn't have and it doesn't complain — it runs down, manufactures one, files it, and hands it to you.

That second loop is worth naming, because the pattern recurs everywhere. `stars_by_language[key] += repo["stars"]` is an **accumulator** — a variable (here, one per group) that lives outside the thing being processed and carries a running total forward from one item to the next. You met a single accumulator in unit 03's `running_total`. This is the same idea, parallelised across groups.

**Two traps, and both of them are real.**

1. **Reading a missing key *creates* it.** This is the exact opposite of `Counter`. Write `by_language["Fortran"]` merely to look, and you have just inserted `"Fortran" -> []` into your data. Now `len(by_language)` is one bigger and your report has a phantom category with nothing in it. So when you want to check for presence, use `if key in d:` — the `in` operator never triggers the factory — and never bare indexing.

2. **It is still a `defaultdict` when you hand it back.** It compares equal to the plain dictionary with the same contents, so tests usually pass, but it prints as `defaultdict(<class 'list'>, {...})`, and anything downstream that receives it inherits the auto-creating behaviour without knowing. Wrap it in `dict(d)` on the way out when the thing is leaving your function. You'll do exactly that in this unit's task.

Which to use? Both are correct. `setdefault` needs no import and is what I'd type in a live coding round without hesitating. `defaultdict` reads better inside a loop that's already three lines long. Know both; the point is that neither is magic, and both are the same `GROUP BY` you'd write in SQL with the machinery visible.

---

## 4. `statistics`, and the one observation that makes you sound competent

The standard library ships summary statistics. You do not need numpy for a list of fifty numbers.

```python
import statistics as st

st.mean(xs)
st.median(xs)          # the middle value
st.mode(xs)            # the most common value
st.stdev(xs)           # sample standard deviation, needs 2+ values
st.quantiles(xs, n=4)  # [q1, q2, q3] — the three cut points of four equal groups
```

**The rule to internalise before anything else: every one of these raises `StatisticsError` on an empty list.** Not `None`, not `0` — an exception that stops your program. And an empty list is exactly what you get when a category turns out to have no data in it, which happens constantly the moment you start grouping. This is unit 01's division-by-zero guard wearing a different coat, and the fix is the same: check first.

```python
if not values:
    return None
```

Write that line reflexively. You will write it in this unit's task more than once.

### Mean versus median

Now the part that actually matters, and I want to give it real weight, because it is the single observation that separates "computed the average" from "understood the data."

A **distribution** is just the shape of a set of numbers — where they cluster, how spread out they are, whether they're lopsided. Two numbers describe its centre and they do it differently.

The **mean** is the total divided by the count. The **median** is the value in the middle when you line every value up in order — half above, half below.

**Mental model:** *the mean is the centre of gravity; the median is the middle of the queue.* Balance the values on a see-saw and the mean is where you put the fulcrum, which means one enormously heavy value at the far end drags it a long way. Line the same values up in a queue and the median is whoever is standing in the middle, and that person doesn't move at all when the person at the back of the queue gets richer.

So when the mean and median are close, the data is roughly symmetric and the mean is a fair summary. When the mean sits far *above* the median, a small number of very large values are dragging it upward and the mean is not representative of a typical record. That lopsidedness is called **skew** — specifically, right-skew or positive skew, because the long thin tail of the distribution stretches out to the right, toward the large values.

Here is why this deserves a whole section: **essentially every real-world count is right-skewed.** GitHub stars. Follower counts. Revenue per customer. Page views per article. Comments per post. In each case a handful of monsters and a long tail of ordinary things. Reporting the mean alone on data like that is not just incomplete, it is actively misleading — you'll say "the average repository has 6,900 stars" when the typical repository has 2,100 and the average is being held up by three famous ones.

Compare these two answers to "what do the stars look like?":

> "The mean is 6,900."

> "Mean 6,900, median 2,100 — so this is heavily right-skewed. A few very large repositories are pulling the average up, and the median is the number I'd quote as typical."

The second one takes four extra seconds to say and it is a *genuinely* better answer. It also opens the obvious next question, which is "which ones are the outliers?" — and you already have `most_common` and a sort to answer that.

**The practitioner's detail.** A cheap, defensible rule of thumb for flagging this automatically is `mean > median * 1.2`. It is not a statistical test and you should not pretend it is one; it's a threshold that catches the cases worth mentioning without firing on ordinary noise. Your task implements exactly this as a `skewed` flag, and the reason it's a flag rather than something you eyeball is so that a report can say the word "skewed" without a human having to look at it. Note also that `median` of an even-length list averages the two middle values, so a list of integers can perfectly correctly produce a median of `744.5` — that is not a bug.

---

## 5. Percentiles, by nearest rank

The median is the value at the halfway point. A **percentile** generalises that to any position: the 90th percentile is the value below which 90% of your data sits.

`statistics.quantiles(xs, n=4)` handles quartiles, but for an arbitrary percentile it's clearer to do it yourself, and doing it yourself is four lines:

```python
def percentile(values, p):
    """p is 0..100. Nearest-rank method."""
    if not values:
        return None
    ordered = sorted(values)
    index = min(int(p / 100 * len(ordered)), len(ordered) - 1)
    return ordered[index]
```

**Mental model:** *sort everything, then walk 90% of the way along the line and point at whoever you're standing next to.* That's it. There's no interpolation, no averaging between neighbours — you land on an actual value that actually occurred in your data. This is called the **nearest-rank** method, and its virtue is that the answer is always a real observation rather than a computed fiction.

The `min(...)` is the only fiddly part, and it's a clamp: for `p=100`, `int(1.0 * n)` is `n`, which is one past the last valid index and would raise `IndexError`. Clamping to `n - 1` makes the 100th percentile the maximum, which is what anyone asking for it meant.

**The practitioner's detail.** There are several defensible definitions of "percentile" — nearest-rank, linear interpolation, and a couple of variants that differ in how they handle the ends. They disagree, sometimes visibly, on small datasets. Excel, numpy and pandas do not all default to the same one. None of this is a problem as long as you *say which one you used*. "p90 by nearest rank" is a complete, unambiguous statement. "p90" on its own, on a list of eleven numbers, is not.

---

## 6. Dates — the part nobody warns you about

You have not parsed a date yet in this course. That's about to change, because almost every API record carries a timestamp and almost every interesting question ("is this growing?", "when was the busy month?") is a question about time.

The basic moves:

```python
from datetime import datetime, timezone, timedelta

dt = datetime.fromisoformat("2024-01-05T10:30:00+00:00")
dt.year, dt.month, dt.day
dt.strftime("%Y-%m")             # '2024-01'  — a month bucket
dt.date().isoformat()            # '2024-01-05'
dt.weekday()                     # 0 = Monday
```

`fromisoformat` reads the ISO 8601 format — the `YYYY-MM-DDTHH:MM:SS` shape that essentially every JSON API uses. `strftime` goes the other way, turning a datetime back into text using a format string of `%`-codes.

That should be the end of it. It is not, for four separate reasons.

### The `Z` problem

APIs overwhelmingly send `"2024-01-05T10:30:00Z"`. That trailing `Z` means "Zulu time," which is aviation-speak for **UTC** — Coordinated Universal Time, the single global reference clock that every timezone is defined as an offset from. It is exactly equivalent to writing `+00:00`.

Python 3.11 and later parse it fine. Every earlier version raises `ValueError` and refuses. The portable fix is a string replacement before you parse:

```python
text = text.replace("Z", "+00:00")
dt = datetime.fromisoformat(text)
```

This is unglamorous and you will write it many times. Write it anyway; the alternative is code that works on your laptop and dies on a machine running 3.9.

### Fractional seconds and epochs

Two other shapes turn up constantly. Some APIs send `"2024-01-05T10:30:00.000Z"` with fractional seconds attached — modern `fromisoformat` handles that fine once the `Z` is dealt with.

Others don't send a string at all. They send `1700000000`, which is an **epoch** timestamp: the number of seconds elapsed since midnight UTC on 1 January 1970, a moment arbitrarily chosen by Unix's designers and now baked into essentially every computer on earth. It's a plain integer, which makes it trivial to store and compare and completely unreadable to a human. Convert it explicitly:

```python
datetime.fromtimestamp(1700000000, tz=timezone.utc)
```

That `tz=` argument is not optional in any moral sense. Leave it off and Python converts into *your machine's local timezone*, which means your code produces different answers on your laptop and on a server in another region. Always pass it.

### Naive versus aware — the one that will actually bite you

This is the important one.

A datetime that carries no timezone information is **naive**. It says "10:30 on the 5th of January" and genuinely does not know whether that's in London or Tokyo. A datetime that does carry timezone information is **aware**. It says "10:30 on the 5th of January, UTC," which identifies an actual moment in the actual universe.

Python refuses to compare the two:

```
TypeError: can't compare offset-naive and offset-aware datetimes
```

And it's right to refuse, because the comparison is meaningless — you're asking whether an unlabelled clock reading is before or after a specific moment, and there's no answer. But it stops your program, usually in the middle of a sort, usually after you've already fetched a thousand records.

**The rule, and it is the single most valuable thing in this section: parse everything to UTC-aware at the edge of your program, and then never think about it again.** Every timestamp gets converted the moment it arrives, before it touches any of your logic. After that boundary, every datetime in your program is aware and in UTC, so comparisons, sorts and subtractions all just work.

**Mental model:** *a customs desk.* Nothing enters the country without being stamped. Once everything inside is stamped identically, nothing inside ever has to check again.

The mechanics of stamping something that arrived naive:

```python
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
```

`.replace(tzinfo=...)` attaches the label without shifting the clock — which is what you want when the source *meant* UTC but didn't say so. A date-only string like `"2024-01-05"` parses to a naive midnight, so this line is exactly what turns it into midnight UTC, aware. Your task tests for precisely this, and it tests for it because a naive result is a bug rather than a detail.

**The practitioner's detail.** `datetime.utcnow()` looks like the obviously correct way to get the current time in UTC and it is a trap. It returns a datetime holding the UTC time with **no tzinfo attached** — a naive datetime that lies about being naive. Compare it against anything aware and you get the `TypeError`; compare it against something local and you get a silently wrong answer. It's deprecated as of Python 3.12 for exactly this reason. Use `datetime.now(timezone.utc)`, always.

### Bucketing by time

Now the payoff. Counting records per month is two lines:

```python
from collections import Counter

by_month = Counter(parse(r["created_at"]).strftime("%Y-%m") for r in records)
for month, count in sorted(by_month.items()):
    print(month, count)
```

There is a small piece of cleverness hiding in `sorted` there and it's worth seeing. Those keys are *strings* — `"2024-01"`, `"2023-12"` — and `sorted` is comparing them as plain text, character by character. It nonetheless produces correct chronological order, because the format is fixed-width and goes largest unit to smallest: the year dominates, and within a year the zero-padded month sorts correctly too. **`"%Y-%m"` strings sort chronologically as text.** That's not a coincidence, it's why ISO 8601 puts the year first, and it means you can bucket and order time without any datetime objects surviving into your output.

---

## 7. The three-step shape of grouped aggregation

Everything in section 3 and section 4 combines into one pattern, and once you see it you'll see it everywhere.

To **aggregate** is to reduce many values to one summary value — a count, a total, a mean, a maximum. Grouped aggregation is doing that separately for each category. In SQL you write it in a single statement and the engine handles the rest. Here it's a function you can read:

```python
def group_stats(records, group_field, value_field):
    groups = defaultdict(list)
    for record in records:
        value = record.get(value_field)
        if value is not None:
            groups[record.get(group_field)].append(value)

    return {
        key: {
            "count": len(values),
            "total": sum(values),
            "mean": round(sum(values) / len(values), 2),
            "max": max(values),
        }
        for key, values in groups.items()
    }
```

Read it as three distinct phases, because that separation is the actual lesson.

**One: collect into groups.** Walk the records once, and for each one work out which bucket it belongs in and drop its value there. Nothing is computed yet — you're only sorting the mail. Note `.get()` on both fields, which is unit 04's habit: real records are missing fields and one absent key should not kill a job that has processed four hundred records already.

**Two: aggregate each group.** Now every bucket holds a plain list of numbers, and you compute whatever summary you want from it. This phase never has to think about grouping at all, which is why it's easy.

**Three: format.** Round the numbers, name the keys, decide what the output dictionary looks like.

**Mental model, and the one thing to memorise from this lesson: collect, aggregate, format.** Whatever the question, that's the shape. "Average points per author." "Busiest month per category." "Error rate per endpoint." Every one of them is the same three phases with different fields plugged in. When an interviewer asks you something you haven't seen before and your mind goes blank, start typing `groups = defaultdict(list)` and the rest follows.

If you're coming from SQL, notice what phase one and two correspond to: phase one is the `GROUP BY`, phase two is the aggregate functions in the `SELECT` list. The database does them together and never shows you the intermediate buckets. Here you can print them, which is why bugs in this pattern are much easier to find in Python than in SQL.

---

## 8. Joining two datasets

Unit 04 showed you how to turn a list of records into a lookup table. Here's what it was for.

```python
users_by_id = {u["id"]: u for u in users}          # index once

joined = [
    {**post, "user_name": users_by_id.get(post["userId"], {}).get("name")}
    for post in posts
]
```

Two lines, and they are a `LEFT JOIN`. Build a dictionary keyed by the thing you'll match on, then make one pass over the other side and look each match up.

The alternative — for each post, scan the entire user list looking for a match — is what everybody writes first, and it works, and it is quadratic. That's the notation `O(n × m)`, read "order n times m": **big-O notation describes how the work grows as the inputs grow**, ignoring constants. A nested scan over a hundred posts and ten users is a thousand comparisons, which is nothing. The same code over ten thousand posts and ten thousand users is a hundred million comparisons, which is a coffee break. The lookup version is `O(n + m)` — one pass to build the index, one pass to use it — and a hundred million becomes twenty thousand.

**This is a hash join.** That's the actual name for it, and it's the same algorithm your database picks internally when it joins two tables and neither is usefully indexed: build a hash table from the smaller side, stream the larger side past it. Saying "I'll hash-join on user id" out loud in an interview is a nice, short, precise sentence that tells the interviewer you know what the database has been doing for you.

**Mental model:** *index one side, walk the other.* Never both.

Two details. `{**post, "user_name": ...}` builds a *new* dictionary containing everything from `post` plus the extra key — it does not modify `post`. Mutating your input is how you end up with a function that gives different answers the second time you call it, so prefer this form. And `.get(key, {}).get("name")` is unit 04's chaining trick, so an unmatched post yields `None` rather than an explosion.

**The practitioner's detail: check your cardinality.** **Cardinality** is the question of how many records on each side share a key — one-to-one, one-to-many, many-to-many. That dictionary comprehension assumes the right side's key is *unique*: if two users somehow share an id, the later one silently overwrites the earlier one and you lose a row with no warning at all. Before joining, `len(users) == len(users_by_id)` tells you in one line whether that assumption holds. If it doesn't, you don't want a lookup of records, you want a lookup of *lists* of records — which is section 3's `defaultdict(list)`, and the join becomes one-to-many. Getting this wrong is how join results end up with mysteriously too few or too many rows, and it's the first thing to check when a joined count doesn't match what you expected.

---

## 9. Formatting the output

Your analysis is worth nothing if it prints as an unreadable blob. This is not a nicety and I'd rather overstate it than have you skip the section.

```python
for name, count in counts.most_common(5):
    print(f"{name:<20} {count:>6,}")

print(f"{'total':<20} {total:>6,}")
```

Those format codes inside the f-string braces come from unit 02. `:<20` means "pad this out to twenty characters, aligned left." `:>6` means "pad to six, aligned right." The `,` adds thousands separators, so `1234567` prints as `1,234,567`.

The **convention is labels left, numbers right**, and there's a real reason for it rather than aesthetics. Text is easiest to scan when all the words start at the same column, so labels go left. Numbers are easiest to *compare* when their digits line up by place value — units above units, tens above tens — because then a longer number is visibly a bigger number and you can see the magnitudes at a glance without reading a single digit. Right-alignment is what produces that. Left-align a column of numbers and `9` and `1000` start in the same place, and the column tells you nothing until you actually read it.

**Mental model:** *measure, then render.* Every table renderer is two passes — one to find how wide each column needs to be, one to lay the cells out at those widths. You'll write exactly that in `format_table`.

Ten seconds of formatting is the difference between output that looks dumped and output that looks considered. In an interview where you're screen-sharing, it's also the difference between the interviewer being able to follow your result and the interviewer squinting.

---

## 10. Look this up yourself

Reading documentation quickly is the most transferable skill in this course, so here are the things I've deliberately not covered. Ten minutes at the interactive prompt.

- `Counter.total()` (3.10+) versus `sum(counter.values())` — and why you might prefer the second for portability.
- `statistics.quantiles(..., method="inclusive")` — and how it differs from the default.
- `itertools.groupby` — and, crucially, why it needs its input sorted first. This is a genuine trap: it groups *consecutive* equal items, so unsorted input silently produces the same key several times.
- `datetime.strptime` — for the timestamps that aren't ISO 8601 at all.
- `dateutil.parser.parse` — a third-party parser that handles almost anything, already installed for you here.
- `zoneinfo.ZoneInfo("America/New_York")` — for genuine timezone conversion, once you need more than UTC.

---

## 11. Check yourself

1. What does `counts["missing"]` return on a `Counter`, and what does it do to the Counter?
2. Why does `defaultdict(list)` beat a plain dict for grouping — and what's the one thing you must never do to a `defaultdict`?
3. What does it tell you when the mean is far above the median, and what should you say about it?
4. What breaks when you compare a naive and an aware datetime, and what's the rule that prevents it?
5. Why does `sorted` put `"%Y-%m"` strings in chronological order?
6. Why index one side of a join into a dictionary first, and what assumption does that make?

*(Answers: 1. `0`, and it leaves the Counter unchanged — unlike a `defaultdict`, which would insert the key. 2. it manufactures the empty list automatically, so `.append` works on a key's first appearance; never read a missing key just to look, because that creates it. 3. the distribution is right-skewed — a few large values are dragging the mean, so it isn't representative and you should quote the median as typical. 4. `TypeError` — the rule is to parse everything to UTC-aware at the edge of your program. 5. because the format is fixed-width and largest-unit-first, so text order and time order coincide. 6. it turns an O(n×m) nested scan into an O(n+m) hash join; it assumes the indexed side's key is unique, and silently drops rows if it isn't.)*

---

*Four things to carry out of this unit. Counting is most of analysis, and `Counter` is a dictionary that starts every key at zero, so everything from unit 04 still applies. Mean versus median is the observation that turns a number into an insight, and on real-world counts the answer is almost always "right-skewed, quote the median." Every timestamp gets parsed to UTC-aware at the border and never thought about again. And every grouped question, whatever it is, has the same three-phase shape: collect, aggregate, format. Unit 14 got your data into a list of flat dictionaries; this unit is what you finally do with it; units 17 to 19 hand the same jobs to pandas, and you'll recognise every one of them because you built them by hand first.*

*Now open [`task.py`](task.py).*
