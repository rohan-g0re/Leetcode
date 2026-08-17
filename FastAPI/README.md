# Zero → Interview-Ready: Python, Real APIs, Data, FastAPI

A compressed, task-driven course. You start knowing **no Python**. You finish able to be
handed a URL you have never seen, pull the data, reason about it, analyze it, and wrap it
in your own API — while talking through what you're doing.

This is built for the specific interview format: *"here is a real API endpoint, do
something useful with it."*

---

## The deal

Every unit has three parts, always in this order:

1. **`LESSON.md`** — read it. It teaches the *mechanism*: what the thing is, why it exists,
   what it does under the hood. It gives you the vocabulary and the mental model.
2. **`task.py`** — a file with function stubs and `TODO`s. You write the code.
3. **`test_task.py`** — run it to check yourself. Green = you actually understood it.

**The lessons deliberately do not contain the answer to the task.** They teach the
concept and show *different* examples. Every lesson ends with a section called
**"Look this up yourself"** listing the exact functions/methods you will need but which
I have not demonstrated. That gap is the point. Reading docs under mild pressure is the
single most transferable interview skill there is, and it is the one thing a
copy-paste-able tutorial can never train.

If you get stuck for more than ~10 minutes, open `hints.md` in that unit. If still stuck,
`solutions/` at the repo root has the full worked answer. Using the solution is not
cheating — *reading it without first fighting the problem* is, because you learn nothing.

---

## Time budget

You said time is tight. Here is the honest cost. Do not skip Part 1; everything else
collapses without it.

| Part | Units | What you get | Est. time |
|------|-------|--------------|-----------|
| 0. Setup | — | Working Python, venv, packages, how to run things | 30 min |
| 1. Python core | 01–10 | The language itself, from zero | 6–8 h |
| 2. HTTP & real APIs | 11–15 | The actual interview skill | 4–5 h |
| 3. Data analysis | 16–19 | Pure Python stats + pandas | 4–5 h |
| 4. FastAPI | 20–23 | Building your own API | 3–4 h |
| 5. Capstones + drills | 24–26 | Full end-to-end under time pressure | 4–6 h |

**Total: roughly 22–30 hours.** That is genuinely the floor for "never written Python" →
"can be handed a live endpoint and perform."

### If you have less time than that

- **~15 hours:** Do 01–10 fast (skim what's obvious, but *do every task*), then 11–15,
  then 20–23, then Capstone B. Skip Part 3 except unit 16.
- **~8 hours (emergency):** 01, 03, 04, 05, 06, 08, 09 → 11, 12, 13, 14 → 20, 21, 22 →
  read `INTERVIEW_PLAYBOOK.md` twice. You will be shaky but functional.

Do not read ahead without doing tasks. Reading Python feels like understanding Python and
it is not the same thing; that illusion is exactly what breaks people in live interviews.

---

## Course map

### Part 0 — Setup
- [`SETUP.md`](SETUP.md) — install, virtual environments, packages, running files, running tests.

### Part 1 — Python core (from absolute zero)
| # | Unit | Core idea |
|---|------|-----------|
| 01 | [`01_values_and_types`](01_values_and_types/) | Values, types, variables, operators, truthiness |
| 02 | [`02_strings`](02_strings/) | Text, indexing, slicing, f-strings, immutability |
| 03 | [`03_lists_tuples_sets`](03_lists_tuples_sets/) | Ordered collections, mutation, references |
| 04 | [`04_dicts_and_nested_data`](04_dicts_and_nested_data/) | Key→value, nesting — the shape of all JSON |
| 05 | [`05_control_flow`](05_control_flow/) | `if`, `for`, `while`, `break`, iteration protocol |
| 06 | [`06_functions`](06_functions/) | Parameters, defaults, `*args`/`**kwargs`, scope, returns |
| 07 | [`07_comprehensions_and_sorting`](07_comprehensions_and_sorting/) | Comprehensions, `sorted` + `key`, `lambda` |
| 08 | [`08_errors_and_exceptions`](08_errors_and_exceptions/) | Tracebacks, `try`/`except`, raising, defensive code |
| 09 | [`09_files_json_modules`](09_files_json_modules/) | Reading/writing files, the `json` module, imports, `__main__` |
| 10 | [`10_classes_and_typing`](10_classes_and_typing/) | Classes, `dataclass`, type hints — prerequisites for Pydantic |

### Part 2 — HTTP and real API endpoints
| # | Unit | Core idea |
|---|------|-----------|
| 11 | [`11_http_fundamentals`](11_http_fundamentals/) | URLs, methods, status codes, headers, bodies — no code |
| 12 | [`12_requests_basics`](12_requests_basics/) | `requests`, `.json()`, status handling, live GitHub API |
| 13 | [`13_params_headers_auth_post`](13_params_headers_auth_post/) | Query params, headers, auth schemes, sending JSON |
| 14 | [`14_navigating_messy_json`](14_navigating_messy_json/) | Exploring an unknown response, safe traversal, flattening |
| 15 | [`15_pagination_retries_ratelimits`](15_pagination_retries_ratelimits/) | Paging, timeouts, retries/backoff, sessions, caching |

### Part 3 — Doing something useful with the data
| # | Unit | Core idea |
|---|------|-----------|
| 16 | [`16_pure_python_analysis`](16_pure_python_analysis/) | Aggregation, grouping, stats with zero dependencies |
| 17 | [`17_pandas_basics`](17_pandas_basics/) | Series, DataFrame, selection, filtering, vectorization |
| 18 | [`18_api_json_to_dataframe`](18_api_json_to_dataframe/) | `json_normalize`, dtypes, missing data, cleaning |
| 19 | [`19_groupby_merge_timeseries`](19_groupby_merge_timeseries/) | `groupby`, `merge`, datetimes, resampling, export |

### Part 4 — FastAPI
| # | Unit | Core idea |
|---|------|-----------|
| 20 | [`20_fastapi_first_app`](20_fastapi_first_app/) | Routes, `uvicorn`, auto docs, path & query params |
| 21 | [`21_pydantic_and_post`](21_pydantic_and_post/) | Request/response models, validation, `response_model` |
| 22 | [`22_async_and_upstream_calls`](22_async_and_upstream_calls/) | `async`/`await`, `httpx`, calling other APIs concurrently |
| 23 | [`23_errors_deps_testing`](23_errors_deps_testing/) | `HTTPException`, dependency injection, `TestClient` |

### Part 5 — Interview simulation
| # | Unit | Core idea |
|---|------|-----------|
| 24 | [`24_capstone_etl`](24_capstone_etl/) | Live endpoint → clean dataset → report, as a CLI |
| 25 | [`25_capstone_api_service`](25_capstone_api_service/) | Build a FastAPI service on top of a live upstream API |
| 26 | [`26_mock_interview_drills`](26_mock_interview_drills/) | Seven timed drills against endpoints this course never used |

### Supporting files
- [`fixtures/`](fixtures/) — recorded real API responses the offline tests run against,
  with a table describing what's awkward about each one.
- [`solutions/`](solutions/) — one worked solution per unit. Read `solutions/README.md`
  before you open any of them.
- `_verify_solutions.py` — runs every solution against its unit's tests. A good way to
  confirm your environment works before you start:
  ```powershell
  python _verify_solutions.py
  ```

### Reference (read anytime)
- [`INTERVIEW_PLAYBOOK.md`](INTERVIEW_PLAYBOOK.md) — **the money document.** Exactly what to
  do, in order, when someone hands you a URL. Read it after Part 2 and again before the interview.
- [`GLOSSARY.md`](GLOSSARY.md) — every term used in this course, defined plainly.
- [`CHEATSHEET.md`](CHEATSHEET.md) — one-page syntax recall for the last 20 minutes before the call.

---

## How to work a unit

```powershell
cd 01_values_and_types
#  1. read LESSON.md end to end (don't skim the "Look this up yourself" section)
#  2. open task.py, fill in the TODOs
#  3. run the tests:
python -m pytest test_task.py -v
#  4. all green? move on. red? read the failure message — it tells you exactly what was expected
```

**Run tests per unit, from inside that unit's folder.** Running bare `pytest` at the course
root collects every unit at once, including the ones you haven't started, so you get a wall
of `NotImplementedError`. That's expected, not a broken setup.

The two capstones use their own filenames — `etl.py` / `test_etl.py` in unit 24 and
`service.py` / `test_service.py` in unit 25 — because they're meant to look like real
deliverables rather than exercises.

Tests that need the internet are marked and can be skipped:

```bash
python -m pytest -v -m "not live"     # offline only
python -m pytest -v                   # everything, including real network calls
```

Every unit's offline tests run against **recorded real API responses** stored in
[`fixtures/`](fixtures/). So the data you practice on is genuinely what those endpoints
return — you get real-world mess without depending on a network connection or on someone
else's rate limit.

---

## The APIs you will actually use

All are public, free, and need **no API key**. You will hit them for real.

| API | Base URL | Used in |
|-----|----------|---------|
| GitHub REST | `https://api.github.com` | 12, 13, 14, 15, 25 |
| PokéAPI | `https://pokeapi.co/api/v2` | 12, 14, 22 |
| Open-Meteo (weather) | `https://api.open-meteo.com/v1` | 13, 19, 24 |
| Frankfurter (FX rates) | `https://api.frankfurter.dev/v1` | 13, 19 |
| JSONPlaceholder (fake CRUD) | `https://jsonplaceholder.typicode.com` | 13, 16, 18 |
| Hacker News (Algolia) | `https://hn.algolia.com/api/v1` | 15, 18, 24, 26 |
| World Bank | `https://api.worldbank.org/v2` | 14, 17, 19, 26 |
| Open Library | `https://openlibrary.org` | 26 |

If one of these is down or has changed shape on the day you're working: **good.** That is
the real job. `INTERVIEW_PLAYBOOK.md` §7 covers what to do about it.

---

## Start here

1. Do [`SETUP.md`](SETUP.md) right now. Don't read on until `python -m pytest --version` works.
2. Then [`01_values_and_types/LESSON.md`](01_values_and_types/LESSON.md).
