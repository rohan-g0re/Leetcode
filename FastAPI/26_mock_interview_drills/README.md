# 26 — Mock Interview Drills

*This is the last unit, and it is the only one that doesn't teach you anything new. Everything before it built skills. This one builds **speed under pressure**, which is a genuinely different thing, and it is the thing that actually decides the interview. Budget three to five hours, but split it across days — doing all seven drills in one sitting measures your stamina rather than your ability. Nothing here is auto-graded and there is no reference solution, because there isn't a right answer to check you against. There's just you, a URL you have never seen, and a clock.*

*If you are reading this the night before, don't try to do all seven. Do drill 1, do drill 7, and reread the [Interview Playbook](../INTERVIEW_PLAYBOOK.md) §1. Those three things are ninety percent of the value and take about forty minutes.*

---

## What these drills are

Seven drills against endpoints the course has deliberately never used. You have not seen these responses, you don't know what fields they contain, and there is no fixture file waiting for you. That is the entire point. Every earlier unit gave you a task with a known shape and a test that told you when you were right. A real interview gives you neither, and the gap between "I can do this with a test telling me the answer" and "I can do this cold" is the gap these drills close.

What you are rehearsing is the procedure from unit 14 — check the top-level type, find the records by shape rather than by name, inventory one record and classify its fields, take the register of which fields are actually present, then flatten to a list of flat dictionaries — running on data that has never been arranged for your convenience. The Playbook is the same procedure written as a script for what to *say* while you do it. Keep it open in another tab; using it is not cheating, it's what your own notes would be.

---

## How to run a drill

Four rules, and each one exists for a reason worth understanding rather than just obeying.

**Set a timer, and stop when it goes off.** The stated limit on each drill is not a suggestion or a target — it is the constraint that makes the drill a drill. Without a clock you will keep going until the thing is finished, which teaches you nothing about what to do when it isn't. The single most valuable skill an interview measures is deciding what to *drop*, and you cannot practise that with unlimited time. When the timer goes, stop mid-line if you have to.

**Talk out loud the whole time, even though you are alone.** This feels ridiculous and you should do it anyway. Narrating your reasoning while your hands are typing is a separate motor skill from either one on its own, it degrades badly if you have never practised it, and it is a large fraction of what an interviewer is actually scoring. The person who says "I'm checking the type first because that decides everything downstream" and then does it beats the person who silently does the identical thing. If you cannot bring yourself to speak, type your narration as comments — it's a weaker version of the exercise but it's not nothing. Playbook §8 has the specific sentences.

**Do not open the lesson files.** `CHEATSHEET.md` is fine, and so is anything you wrote yourself, because in a real interview you would have your own notes on screen and nobody minds. Reading official documentation online is not just allowed but expected — looking something up quickly in front of an interviewer reads as competence. What you are avoiding is the lessons, because rereading unit 14 mid-drill converts a test of recall into a comprehension exercise and quietly tells you nothing about whether you can do this cold.

**When the timer stops, write down what you'd have done with more time.** This is not a consolation prize for not finishing. "With more time I'd add caching, retry with backoff, and a test for the transform" is a real answer to a real question, it converts an unfinished piece of work into evidence of judgment, and it is the sentence Playbook §8 tells you to always end on. Practising it here means it comes out naturally there.

Then — and only then — read that drill's section in [`DEBRIEF.md`](DEBRIEF.md). Never before. The debrief tells you what is actually in the data, so reading it in advance turns the drill into a tutorial and destroys the one thing it was for.

Work in [`scratch.py`](scratch.py). Delete it, rewrite it, start fresh each drill; it is scratch paper, not a deliverable.

**Which of these matter most, since you may not get to all of them.** Drill 1 and drill 6 are the two that most closely resemble what will actually happen to you, and drill 7 is a ten-minute inoculation against the one situation that makes people freeze completely. If you have one evening, do those three. Drills 2 through 5 are each rehearsing one specific skill — aggregation, pagination, joining, and service-building — and are worth doing properly when you have the time, but they are more predictable than the interview will be.

---

## Drill 1 — Cold open (15 min)

**Endpoint:** `https://api.openbrewerydb.org/v1/breweries?per_page=50`

This is the purest version of the exercise and the one to do first. You have never seen this API, there is no context, and you have a quarter of an hour. It exercises unit 14 almost exclusively, plus unit 12's fetching and unit 01's `type()`.

In fifteen minutes, do these five things in order:

1. Fetch one page. Print the status code and the content type.
2. Determine the shape and print one full record.
3. Classify every field: identifier / numeric / categorical / temporal / nested.
4. Report: how many records, how many have a `state`, how many have coordinates.
5. Say aloud three analyses this data would support.

**Grading: did you get to step 5?** That's the whole score. Most people are still staring at raw JSON at minute twelve, having never got past step 2, and step 5 is the one that would actually have impressed anybody. If you find yourself scrolling printed JSON, stop — that's the failure mode, and the fix is mechanical rather than clever.

---

## Drill 2 — Aggregate and rank (25 min)

**Endpoint:** `https://api.openbrewerydb.org/v1/breweries?per_page=200`

Same API, but now with a question attached, phrased the way an interviewer phrases things:

> *"Which states have the most breweries, and what's the mix of brewery types?"*

This is Playbook §6's ladder — counts first, then a distribution, then a group-and-aggregate — running on units 07 and 16. Deliver:

- breweries per state, top 10, printed as an aligned table
- per state, the share that are `micro`
- a count of records with missing coordinates
- one sentence about data quality

**Grading:** aligned output rather than a dumped `Counter`, `Counter`/`groupby` rather than hand-rolled tally loops, and — the one that carries the most weight — you mentioned the missing data *unprompted*. Nobody asked you about coordinates. Volunteering a data-quality observation is what separates a junior answer from a senior one, and it costs one sentence.

Two things to hold in mind while you write it. Grouping by a field means deciding what to do with the records where that field is null, and whatever you decide, say it. And computing a share means dividing by a count, which means the guard from unit 01 — a division whose denominator could be zero.

---

## Drill 3 — Paginate everything (30 min)

**Endpoint:** `https://api.openbrewerydb.org/v1/breweries?page=N&per_page=200`

> *"Pull all of them, not just the first page."*

This is unit 15's whole subject, and it's the drill where the mistake is invisible. A pagination bug doesn't crash; it just hands you a fraction of the data, and every number you compute afterwards is confidently wrong. Deliver:

- a paginating fetch with a hard cap and a stop condition
- caching, so a rerun does no network I/O
- total count, and a per-country breakdown
- saved to `breweries.csv`

Two terms, since they carry the drill. A **stop condition** is how the loop knows it has reached the end — with no total in the response, you find the end by the page you get back rather than by arithmetic. A **hard cap** is a maximum number of pages you refuse to go beyond regardless of what the API says, and it exists because an unbounded loop against an API you have misread is how you send forty thousand requests during an interview. Playbook §4 is the reference.

**Grading:** did you cap the loop, and did you say *why* out loud? And did you handle the last page correctly — a **short page**, one that comes back with fewer records than you asked for, is the last page, and checking only for an *empty* page means one wasted round trip every run. Both conditions, not one.

The caching requirement is not busywork either. Saving each page's JSON to disk and reading it back on a rerun means your second run through this drill is instant, and in a real interview it means a mistake at minute twenty doesn't cost you another two minutes of waiting on requests you already made. That's unit 09.

---

## Drill 4 — Join two sources (35 min)

**Endpoints:**
- `https://openlibrary.org/search.json?q=python+programming&limit=50`
- `https://openlibrary.org/subjects/programming.json?limit=50`

> *"Combine these and tell me something neither one tells you alone."*

A **join** is what you already know from SQL — matching records from two sources on a shared key so you can see fields from both at once. What SQL never makes you do is the part that is hard here, because in SQL both tables already have columns. Deliver:

- a flat record set from each (they have **different shapes** — that's the exercise)
- a join on a sensible key
- how many matched, how many didn't — **report both**
- one genuine finding

**Grading:** the two responses are shaped differently in an annoying, real way, and you will want to give up somewhere around minute ten. That moment is the actual content of this drill. Did you narrate the mismatch instead of going quiet? Saying "these two represent authors differently, so I'm normalising both to a plain list of names before I join" is a better performance than silently producing a working join, because it shows the interviewer the thinking they cannot otherwise see.

One steer that isn't a spoiler: normalise each side into your own flat record shape *first*, separately, and only then join. Attempting to join the two raw responses directly is what makes this feel impossible, and it's the trap most people fall into. Unit 14 §8 is exactly this move.

---

## Drill 5 — Wrap it in an API (40 min)

**Endpoint:** `https://api.openbrewerydb.org/v1/breweries`

> *"Expose this as our own service."*

This one is Part 4 — units 20 through 23 and the capstone in 25 — compressed into forty minutes. **Upstream** is the word for the service you are calling; you are sitting in front of it, and your callers only ever talk to you. Deliver a FastAPI app with:

- `GET /health`
- `GET /breweries` — filter by state and type, paged
- `GET /breweries/{id}` — 404 when absent
- `GET /stats` — per-state counts
- response models, one upstream error translated, and **one test**

**Grading:** does `/docs` open and show the shapes you meant? Is there a timeout on the upstream call? And does a dead upstream produce a **502** rather than a 500 — because a 500 from your service means *you* are broken, while a 502 means you are fine and the thing behind you isn't, and those are different messages to whoever is paged at 3am.

Forty minutes is not much for five endpoints plus a test, which is deliberate. Build the smallest thing that runs, get `/docs` open, and then add. A working app with two endpoints beats a half-written app with five.

---

## Drill 6 — Full take-home (60 min)

**Endpoint:** `https://api.tvmaze.com/shows?page=0`

> *"Analyse this. Give us a report and a clean dataset."*

That is all the instruction you get, exactly as it would arrive in your inbox. Nobody will tell you what "useful" means, which fields matter, or what the report should contain. Deciding those things *is* the task, and the vagueness is not an oversight on my part.

Deliver whatever you judge to be right. Then, afterwards, check yourself against these:

- Did you look at one record before writing code?
- Did you ask (or state) what "useful" means here?
- Is fetch/transform/analyse separated?
- Did you handle the nested fields? (`network`, `rating`, `schedule`, `image`, `externals` and `_links` are all nested objects, and `genres` is a list — several are `null` on plenty of records.)
- Did you produce something a non-programmer could read?
- Did you say what you'd do with more time?

**This drill is the closest thing here to the real interview. Do it last, do it timed, and record yourself talking if you can bear it.** Watching yourself back is unpleasant and unusually informative — you will hear the silences, and the silences are the thing to fix.

The parenthetical about nested fields is a warning rather than a hint. Every one of those is a place where unit 04's `.get()` and `or {}` are the difference between a report and a `TypeError` at record 90. Reaching for them by reflex, before you have been bitten, is the habit this drill is checking for.

---

## Drill 7 — The dead endpoint (10 min, do it once)

**Endpoint:** `https://api.spacexdata.com/v4/launches`

Do this one whenever you like — it is not part of the sequence and it takes ten minutes. It is also, per unit of time, probably the most valuable thing in this unit.

**This drill is not about fetching the data. There is no data. You are rehearsing the recovery.** The endpoint is expected to be broken, and the entire exercise is what you say and do in the sixty seconds after it breaks.

Run this:

```python
import requests
r = requests.get("https://api.spacexdata.com/v4/launches", timeout=20)
print(r.status_code, r.headers.get("content-type"))
print(r.text[:200])
r.json()      # watch what happens
```

At the time this course was written that endpoint returned **525** with an HTML body, and `.json()` raised `JSONDecodeError` — which looks exactly like your bug and isn't. A `JSONDecodeError` means "the text I was handed is not JSON", and when the server has sent you an HTML error page, that is a completely truthful message about a problem you did not cause. It may be back up by the time you read this; if so, find another broken endpoint, they are genuinely not rare.

Now practise the recovery, out loud, in these three beats:

1. *"I'm getting a 525 and an HTML body — that's Cloudflare, server-side, not my code."*
2. Confirm it independently, in a browser or with `curl`, so it isn't just your assertion.
3. *"I'll work from a saved response so we can keep going, and wire the live fetch back in at the end."*

Why this is worth ten minutes: a dependency dying mid-interview is the single most common thing that makes an otherwise-competent candidate freeze, because it feels like being caught not knowing something. It isn't. Carrying on productively past a broken dependency is one of the strongest signals you can send, and it is entirely a rehearsed reflex rather than a skill. Do it once, deliberately, and you will never freeze on it. Playbook §7 is the same three beats in reference form.

---

## After every drill

Score yourself 1–5, honestly. The honesty is the part that makes this work — a rubric you grade generously is a rubric that tells you nothing.

| Dimension | 1 | 5 |
|-----------|---|---|
| Time to first successful fetch | > 5 min | < 1 min |
| Explored before coding | dived straight in | full inventory first |
| Structure | one long script | clean fetch/transform/analyse |
| Error handling | crashed on a null | handled and reported |
| Communication | silent | narrated throughout |
| Output quality | raw dict dump | readable report |

Write the six numbers down somewhere and keep them across drills. The improvement curve on these is genuinely steep — the first-fetch time in particular tends to fall from four minutes to under one within three drills — and watching it move is both motivating and the only real evidence you have that this is working.

---

## Common failure modes

These are the specific things that go wrong, and the specific replacement habit for each. If your score on some dimension isn't moving, the fix is almost certainly one line of this table.

| You did | Do instead |
|---------|------------|
| Stared at raw JSON for 5 minutes | `json.dumps(data[0], indent=2)` immediately |
| Wrote 50 lines before running | Run after every 5 |
| Crashed on a null field | `.get()` and `or {}` from the start |
| Went silent when stuck | "I'm deciding whether to group first or filter first" |
| Ran out of time mid-refactor | Ship the working version, then improve |
| Forgot the timeout | Muscle memory: `timeout=10` in the same keystroke as `requests.get` |
| Printed a raw dict | 30 seconds of f-string alignment |

The pattern across all seven is the same, and it's worth naming: none of them is a gap in your Python. They are all habits, which means they are all fixable by repetition rather than by study. That is genuinely good news this close to an interview.

---

## The endpoints, for reference

All public, all free, none of them needs an API key or any registration.

| API | Base | Notes |
|-----|------|-------|
| Open Brewery DB | `https://api.openbrewerydb.org/v1/breweries` | flat records, page/per_page, lots of nulls |
| Open Library search | `https://openlibrary.org/search.json` | envelope under `docs`, list-valued fields |
| Open Library subjects | `https://openlibrary.org/subjects/{name}.json` | different shape entirely |
| TVmaze | `https://api.tvmaze.com/shows?page=0` | 240 records, deeply nested, temporal, nulls everywhere |

---

*Here is the thing to carry out of this unit and into the room. The bar is much lower than you think it is, and it is not the bar you have been revising for. Nobody is going to ask you to recall a pandas method or reproduce FastAPI's dependency syntax from memory; they are going to hand you a URL and watch what you do with the first five minutes. What they are looking for is that you look before you code, that you say what you are doing while you do it, that you notice when the data is dirty and mention it without being asked, and that when something breaks you say so plainly and keep going. Every one of those is a habit, and you have just spent this unit rehearsing all four.*

*You already know more than enough Python for this. What these drills gave you is the thing that knowledge alone doesn't: the first four minutes, running on rails, while you think about their problem instead of your own. Go and do the drills, then close the laptop. You're ready.*
