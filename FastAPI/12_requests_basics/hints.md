# Unit 12 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `fetch_json`

There is no trick here at all. Four requirements from the docstring become four things on one call plus two lines after it:

```python
response = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
response.raise_for_status()
return response.json()
```

Read the first line as a checklist rather than as code. The URL is the one you were given. The params go into `params=` untouched — you are not building a query string, `requests` does the percent-encoding. `HEADERS` is the module-level constant at the top of the file, which is why it exists in one place instead of being retyped. And `timeout` is the parameter with a default of `TIMEOUT`, passed straight through so a caller can shorten it if they want.

Then `raise_for_status()` turns any 4xx or 5xx into an exception before you touch the body, and `.json()` — with the parentheses — parses it. If you forget the parentheses you will get `'method' object is not subscriptable` further down the line, which is a confusing message for a trivial mistake.

Note that `params` defaults to `None`, and passing `params=None` to `requests` is perfectly fine — it just means no query string. You do not need a guard for it.

---

### `safe_fetch`

Do not repeat the request code. `fetch_json` already does everything, and everything it can go wrong with is a `RequestException`, so all this function adds is a wrapper:

```python
try:
    return fetch_json(url, params=params), None
except requests.RequestException as exc:
    return None, f"{type(exc).__name__}: {exc}"
```

The `return` inside the `try` is doing two things worth noticing. It builds a tuple — the comma is what makes it a tuple, not the parentheses — with the data first and `None` in the error slot, because on success there is no error. The failure branch mirrors it exactly: `None` where the data would have been, and a description in the error slot.

For the description, `type(exc)` gives you the exception's class and `.__name__` gives that class's name as a string, so you get `"Timeout"` or `"ConnectionError"` or `"HTTPError"`. Then `{exc}` inside an f-string calls the exception's own message. That is what produces the required `"HTTPError: 404 Client Error: ..."` shape, and the tests check that the string starts with the class name.

One handler is genuinely enough. Timeout, ConnectionError, HTTPError and JSONDecodeError are all children of `RequestException`, so catching the parent catches every one of them.

---

### `describe_response`

Do the two independent readings first, then work out the shape.

The content type is a header, and headers are missing sometimes, so read it with `.get()` and a default of empty string rather than square brackets:

```python
content_type = response.headers.get("Content-Type", "")
```

Then the parse. You are not asking the header whether the body is JSON — you are asking the body, by trying:

```python
try:
    data = response.json()
    is_json = True
except ValueError:
    data, is_json = None, False
```

That one `except` is enough because `requests`' `JSONDecodeError` subclasses `ValueError`. And that `is_json` flag is now honest in a way the header is not: it records what actually happened, so a server that claims JSON and sends an HTML error page comes out as `False`. One of the tests is precisely that.

Now branch on what you are holding, using `isinstance()` rather than guessing:

- **list** → shape `"list"`, `size = len(data)`. For the keys, only reach into the first element if there *is* one and it is a dict: `sorted(data[0])` when `data and isinstance(data[0], dict)`, otherwise `[]`. A list of plain numbers has no keys, and `sorted(3)` would raise.
- **dict** → shape `"dict"`, `size = len(data)`, `keys = sorted(data)`. Sorting a dict directly gives you its keys sorted, which is a small idiom worth knowing.
- **anything else that parsed** (a number, a string, `true`) → shape `"other"`, size `0`, keys `[]`.
- **didn't parse at all** → shape `"invalid"`, size `0`, keys `[]`.

Check the `is_json` flag before the isinstance branches, since `None` is not a list or a dict and you want `"invalid"` rather than `"other"` in that case.

The other two fields are free: `"status": response.status_code` and `"ok": response.ok`.

---

### `get_user`

The whole function is four lines, and the order of them is the entire lesson:

```python
response = requests.get(f"{BASE}/users/{username}", headers=HEADERS, timeout=TIMEOUT)
if response.status_code == 404:
    return None
response.raise_for_status()
return response.json()
```

The 404 check has to come *before* `raise_for_status()`, because `raise_for_status()` would have already thrown by the time you got to look. Once the 404 is handled, `raise_for_status()` still guards everything else — a 500 or a 403 raises, exactly as it should, because those are genuine problems rather than answers.

Note that you are still sending `HEADERS` and `TIMEOUT` even though you are not going through `fetch_json`. Dropping the plumbing because you took the manual route is the easy mistake here, and the missing `User-Agent` in particular will earn you a 403 from GitHub.

---

### `get_repos`

One line, because `fetch_json` already did the work:

```python
return fetch_json(f"{BASE}/users/{username}/repos", params={"per_page": per_page, "sort": sort})
```

Build the params dictionary from the function's own parameters — do not hardcode the values, since the test calls `get_repos("x", per_page=50)` and checks that the 50 arrived.

---

### `summarize_user`

Every single line needs `.get()`, because one test hands you `{}` and expects a complete summary back rather than a `KeyError`.

For the year, you need a value before you can slice it:

```python
created = user.get("created_at")
created_year = int(created[:4]) if created else None
```

The timestamp is fixed-width ISO, so the first four characters are always the year; slicing them and converting to `int` is fine and obvious here. The `if created` guard is what stops you slicing `None` when the field is absent.

For `has_blog`, `bool(user.get("blog"))` is the whole thing — an empty string and `None` are both falsy, so both come out `False` without any special-casing.

And the trap: `user.get("public_repos", 0)` still returns `None` when the key is present holding a null. A default only fires when the key is *missing*, and the test has `"public_repos": None` sitting right there in the record. Use `user.get("public_repos") or 0` instead, which catches both the missing case and the null case because `None` is falsy. Same reasoning for `followers`, and for `name` with `or "unknown"`.

`login` is the exception — it is allowed to come back as `None`, so a plain `user.get("login")` is correct there.

---

### `top_repos`

Unit 07's sort-with-a-tuple-key, once you have defended the missing fields:

```python
ranked = sorted(repos, key=lambda r: (-(r.get("stargazers_count") or 0), r.get("name") or ""))
return [(r.get("name"), r.get("stargazers_count") or 0) for r in ranked[:n]]
```

The key function receives one repo dictionary and returns a two-item tuple, and Python compares tuples element by element — so the star count decides first and the name breaks ties. Negating the star count is what makes larger counts sort earlier, since ascending order on negative numbers is descending order on the originals. The name stays un-negated so ties fall back to alphabetical, which is the rule the docstring asks for.

Both `or` guards are load-bearing. One of the test repositories has no `stargazers_count` at all and must sort as zero; and comparing `None` against a string raises a `TypeError`, so the name needs a fallback too.

The `[:n]` slice handles `n` larger than the list for free, because slicing never runs past the end — which is why `top_repos(repos, 10)` on a four-item list quietly returns four.

---

### `user_report`

Two calls, two different failure policies. Start with the existence check and get the impossible case out of the way:

```python
user = get_user(username)
if user is None:
    return {"user": None, "repos": [], "error": "user not found"}
```

Then fetch the repositories through `safe_fetch` rather than `get_repos`, and build the report from whatever came back:

```python
repos, error = safe_fetch(f"{BASE}/users/{username}/repos", params={"per_page": 100, "sort": "updated"})
return {
    "user": summarize_user(user),
    "repos": top_repos(repos or [], 5),
    "error": error,
}
```

The `repos, error = ...` line is unit 03's tuple unpacking — one call, two names, split apart on assignment.

Using `safe_fetch` for the second call is the whole design, and it is the behaviour the test checks. `get_repos` would raise on a timeout and take the user data down with it; `safe_fetch` hands the failure back as a string, so you keep the summary you already built and simply report that the repositories are missing. That is the caller-decides principle from `safe_fetch`'s docstring actually being exercised.

Two small details. `repos or []` is there because `safe_fetch` returns `None` for the data when it failed, and `top_repos` needs something it can loop over. And `"error": error` works for both outcomes without a branch, because `safe_fetch` already puts `None` there on success — which is exactly what the success case is supposed to report.
