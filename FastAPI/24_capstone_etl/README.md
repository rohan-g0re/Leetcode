# 24 — Capstone A: Live Endpoint → Clean Dataset → Report

*This is a brief rather than a lesson, and it is the first time in the whole course that Parts 1, 2 and 3 get assembled into a single thing you could hand to somebody. There are no new concepts here — every function you are about to write is a variation on something you already wrote in units 09, 14, 15 or 16. What is new is that nobody is going to tell you which piece goes where. Budget about two hours and try to do it in one sitting, because sitting down twice is how you lose the thread of your own code.*

---

## The brief

Imagine the interviewer says this, and then stops talking:

> *"Here's the Hacker News search API: `https://hn.algolia.com/api/v1/search`. Pull the stories about a topic we care about, clean them up, and tell me something useful. Save the dataset so we can look at it later."*

That is the entire brief. It is vague, and the vagueness is not an accident or an oversight on my part — it is a faithful reproduction of how these questions actually arrive. Nobody hands you a specification with field names in it. They hand you a URL and a verb like "useful," and a large part of what they are measuring is what you do in the gap between those two things. Someone who starts typing immediately is guessing. Someone who looks at one response first, says what they see, and then asks one clarifying question has already scored most of the available points before writing a line of logic.

---

## What you are building

You are building a **CLI tool** — a command-line tool, meaning a program you run by typing its name and some options into the terminal rather than by clicking anything. It looks like this when it runs:

```powershell
python etl.py "python" --pages 3 --min-points 50 --out reports/
```

The thing it does is an **ETL pipeline**. ETL stands for extract, transform, load, and it is the oldest three-word phrase in data work: go and get the data from wherever it lives, reshape it into something you can actually use, and put the result somewhere it will still be tomorrow. Your version has four stages rather than three, because the analysis step is worth naming separately.

1. **Extract** — the only part that touches the network. It walks through pages of the live API, retries the failures that are worth retrying, refuses to fetch more than a fixed number of pages, and keeps every response it has already seen in a file on disk so it never asks twice.
2. **Transform** — flattens the raw response into clean, flat records, parses the timestamps into real dates, and derives the domain a story links to.
3. **Analyze** — counts things, describes the distribution of points and comments, and aggregates by domain, by author and by month.
4. **Load** — writes `stories.csv` and `summary.json`, and prints a report a human can read.

If that split looks familiar, it should: it is `INTERVIEW_PLAYBOOK.md` §2's three-function skeleton with the analysis pulled out into its own step. The reason the playbook insists on it, and the reason this capstone is shaped around it, is that only the first stage needs a network. Everything after it is a pure function — data in, data out, nothing else — which means the whole of your logic can be tested in a fraction of a second on a laptop with the wifi off. That is exactly what `test_etl.py` does, and it is the single structural habit most worth carrying into an interview.

---

## Before you write anything

Reread [`INTERVIEW_PLAYBOOK.md`](../INTERVIEW_PLAYBOOK.md) §1, and then actually perform it rather than reading it and nodding. Open a Python prompt and fetch exactly one small response:

```python
import requests, json

r = requests.get(
    "https://hn.algolia.com/api/v1/search",
    params={"query": "python", "tags": "story", "hitsPerPage": 5},
    timeout=10,
)
print(r.status_code)
data = r.json()
print(list(data.keys()))
print(json.dumps(data["hits"][0], indent=2))
```

Five hits, not five hundred — you are looking at the *shape*, and one record tells you everything about the shape that a thousand would. Note the `timeout=10` as well. Without it `requests` will wait forever for a server that never answers, and a hung prompt in front of an interviewer is a bad minute.

Now answer four questions out loud, in words, before you touch `etl.py`. What is the **envelope**? An envelope is when the records you want are not the response itself but one field inside it, wrapped in metadata — here the response is a dictionary, the stories live under `"hits"`, and the rest of the keys are bookkeeping. Second: how does paging work, and which specific field tells you when to stop? Third: of the fields on one story, which are identifiers, which are numeric and can therefore be averaged, which are categorical and can therefore be grouped by, and which are timestamps and can therefore be bucketed into months? That four-way classification *is* the answer to "what analysis is possible here," which is why the playbook makes you say it aloud. And fourth: which fields are null often enough that you need a plan for them?

You already know all four answers from units 14 to 18. The point of doing it again is not discovery, it is rehearsal — the ritual has to be automatic enough to survive being nervous.

---

## The rules

**Keep the four stages in separate functions, and let only `fetch` touch the network.** This is the rule everything else hangs off. If `transform` reaches out to the internet, or `analyze` quietly fetches one more page, then nothing downstream can be tested without a live connection and nothing can be debugged by printing intermediate values. Once the boundary is clean you can hand `transform` a saved response and check its output in milliseconds, which is precisely what the tests do.

**Cache while you are developing.** You are going to run this thing thirty times before the logic is right, and there is no reason for thirty identical round trips over the network. The first run fetches and writes the response to a file; every run after that reads the file. This is unit 15's `cached_fetch` doing exactly the job it was written for, and the difference it makes to your development loop is not small — it turns a two-second edit-run cycle into an instant one, and it means an API that starts rate-limiting you at the worst moment cannot stop your work.

**Cap the pages, always.** The `--pages` option has a default and the default is small. An unbounded loop against an API you have misread is how a five-minute exercise becomes forty thousand requests against somebody else's service, and the failure mode is that you do not notice until it is embarrassing. Saying "I capped this at three pages so a misunderstanding on my side can't turn into thousands of requests" out loud is one of the cheapest credibility wins in `INTERVIEW_PLAYBOOK.md` §8.

**Report what you dropped.** If you fetched three hundred hits, kept two hundred and eighty-seven, and threw away thirteen because their timestamps would not parse, then "fetched 300, kept 287, dropped 13 with no timestamp" is part of your answer rather than a footnote to it. A quiet loss is how a dataset becomes wrong without anyone finding out, and volunteering the number is the one-sentence move that §6 of the playbook calls out as separating a junior answer from a senior one.

**Make the printed output readable.** Aligned columns, thousands separators, no raw dictionary dumped to the terminal. This feels cosmetic and is not: the report is the only part of your work the interviewer actually reads, and the gap between "here are the numbers" and "here is the answer" is entirely in the formatting. Unit 16 gave you the f-string format codes for this; use them.

---

## The deliverable

`etl.py` in this folder, with every function filled in and the tests passing.

```powershell
python -m pytest test_etl.py -v -m "not live"     # the logic, no network
python -m pytest test_etl.py -v                   # the same plus real requests
python etl.py "fastapi" --pages 2                 # the actual tool
```

Run the first command constantly and the second one occasionally. The `-m "not live"` part deselects the two tests marked as needing the real API, so the first command works on a train.

The stubs and the full specification are in the docstrings of [`etl.py`](etl.py) — start there and work top to bottom, since each stage feeds the next. Some of the tests lean on a **fixture**, which is a saved copy of a real API response kept in a file so the test can run against genuine, messy data without a network; you will see one referred to as `hn_search_python`.

There is deliberately no `hints.md` for the capstones. Every function here is a variation on something you have already written in units 09, 14, 15 and 16, and going back to find your own earlier answer is the exercise rather than a detour from it. The worked solution sits at [`solutions/24_capstone_etl.py`](../solutions/24_capstone_etl.py) if you get genuinely stuck, but spend twenty minutes stuck first — that is where the learning is.

---

## Self-assessment

When the tests pass, go back through and score yourself honestly against these. This one stays a checklist because it is genuinely a list of separate things to check.

| | |
|---|---|
| ☐ | Would this run if the API returned an extra field tomorrow? |
| ☐ | Would it survive a null in every single field? |
| ☐ | If the network dies on page 2, do you keep page 1? |
| ☐ | Can someone read the printed report without asking you what it means? |
| ☐ | Can you explain every line, including why you chose median over mean? |
| ☐ | Did you cap the pages *and* say why? |

The last two are what interviews actually turn on, and they are the two that no test can check for you.

---

## If you have extra time

Once the base version passes, there are four natural directions. You could add `--since 2024-01-01` and filter by date, which the stubs already anticipate. You could add a second source — `https://api.github.com/search/repositories` is the obvious one — and reconcile the two datasets by domain, which is unit 19's join wearing different clothes. You could write the summary as Markdown instead of JSON, so it can be pasted straight into a document. Or you could add a `--format table|json|csv` flag and let the caller choose how the output arrives.

Do none of these before the base version is passing. Finished-and-plain beats ambitious-and-broken every time, in this exercise and much more so in the interview, where a half-built second data source is indistinguishable from not knowing how to finish the first one.

---

*What makes this a capstone rather than another task is that nothing in it is new and everything in it is yours to place. Unit 15 gave you the retries and the file cache, unit 14 gave you the procedure for reading an unfamiliar response, unit 16 gave you the statistics and the formatting, unit 09 gave you the file writing — and this is the first time you decide which of them goes where, in what order, behind which function name. That decision is the actual skill being tested, both here and in the room. Now open [`etl.py`](etl.py) and read the docstrings top to bottom before you write anything.*
