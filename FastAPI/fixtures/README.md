# fixtures/

Recorded, unedited responses from the public APIs this course uses. Tests read these so
they pass offline and don't depend on someone else's uptime or rate limit.

**They are real.** The nulls, the missing keys, the numbers-stored-as-strings, the fields
that are an empty string instead of absent — none of that is invented. That mess is the
material.

Load one in the REPL and look around:

```python
import json
data = json.loads(open("fixtures/github_repos_pallets.json", encoding="utf-8").read())
print(type(data), len(data))
print(json.dumps(data[0], indent=2)[:1500])
```

In tests, use the `load_fixture` fixture defined in the root `conftest.py`:

```python
def test_something(load_fixture):
    repos = load_fixture("github_repos_pallets")
```

| File | Source | Shape | What's interesting about it |
|------|--------|-------|------------------------------|
| `github_user_pallets.json` | `api.github.com/users/pallets` | single dict | flat-ish; several fields are `null` |
| `github_repos_pallets.json` | `api.github.com/users/pallets/repos?per_page=100` | list of dicts | deep nesting (`owner`, `license`, `permissions`), `license` is often `null` |
| `pokemon_ditto.json` | `pokeapi.co/api/v2/pokemon/ditto` | single dict | lists of dicts of dicts; the deepest structure here |
| `hn_search_python.json` | `hn.algolia.com/api/v1/search` | envelope | real data under `hits`, pagination metadata alongside it |
| `placeholder_posts.json` | `jsonplaceholder.typicode.com/posts` | list of dicts | perfectly clean, flat. The easy case, for contrast |
| `placeholder_users.json` | `jsonplaceholder.typicode.com/users` | list of dicts | nested `address.geo` and `company`; joins to posts on `id` |
| `open_meteo_berlin.json` | `api.open-meteo.com/v1/forecast` | dict of **parallel arrays** | not records at all — dates in one array, values in another. Must be reshaped |
| `frankfurter_series.json` | `api.frankfurter.dev/v1/2024-01-01..2024-03-31` | dict keyed by date | a time series as a dict-of-dicts; weekends simply absent |
| `worldbank_countries.json` | `api.worldbank.org/v2/country` | `[metadata, records]` | two-element array envelope; nested `region`/`incomeLevel`; `""` used instead of `null`; lat/long are strings |
| `worldbank_population.json` | `api.worldbank.org/v2/.../SP.POP.TOTL` | `[metadata, records]` | same envelope; `value` is `null` for many country-years; joins to the countries file |

## Re-recording

```powershell
python fixtures/refresh.py
```

Only needed if an endpoint changes shape and you want to see what moved. Note this course
was written when `restcountries.com/v3.1` returned a deprecation stub instead of data —
which is a fair sample of what "a real API endpoint" means in practice, and why
`INTERVIEW_PLAYBOOK.md` §7 exists.
