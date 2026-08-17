# Cheatsheet

For the last 20 minutes before the interview. Nothing new here — pure recall.

## Data structures

```python
xs = [1, 2, 3]                # list  - ordered, mutable
t  = (1, 2)                   # tuple - ordered, immutable
s  = {1, 2, 3}                # set   - unordered, unique
d  = {"a": 1, "b": 2}         # dict  - key -> value

xs[0]; xs[-1]; xs[1:3]        # index, last, slice [start:stop) 
xs.append(4); xs.extend([5])  # add one / add many
xs.sort(); sorted(xs)         # in place (returns None) / new list
len(xs); 3 in xs

d["a"]                        # KeyError if missing
d.get("z")                    # None if missing
d.get("z", 0)                 # default if missing
d.keys(); d.values(); d.items()
for k, v in d.items(): ...
d.setdefault("k", []).append(1)
{**d1, **d2}                  # merge, right wins
```

## Strings

```python
f"{name} has {n} items"
f"{x:.2f}"  f"{x:,}"  f"{name:>10}"      # 2dp / thousands / right-pad
s.strip().lower().upper().title()
s.split(","); ",".join(parts)
s.replace("a", "b"); s.startswith("x"); "sub" in s
```

## Control flow

```python
if a and b: ...
elif not c: ...
else: ...

for i, x in enumerate(xs): ...
for a, b in zip(xs, ys): ...
for i in range(5): ...          # 0..4
while cond: ...  break / continue

value = x if cond else y        # ternary
```

## Comprehensions & sorting

```python
[f(x) for x in xs]
[x for x in xs if x > 0]
{k: v for k, v in pairs}
{x.type for x in xs}                       # set
sum(x["n"] for x in xs)                    # generator, no list built

sorted(rows, key=lambda r: r["age"])
sorted(rows, key=lambda r: r["age"], reverse=True)
sorted(rows, key=lambda r: (-r["score"], r["name"]))   # multi-key
max(rows, key=lambda r: r["n"])
```

## Functions

```python
def f(a, b=10, *args, **kwargs) -> int:
    """docstring"""
    return a + b

f(1, b=2)
```

## Errors

```python
try:
    ...
except KeyError as e:
    print("missing", e)
except (ValueError, TypeError):
    ...
else:      # ran without exception
    ...
finally:   # always
    ...

raise ValueError("message")
```

## Useful stdlib

```python
from collections import Counter, defaultdict
Counter(names).most_common(3)
d = defaultdict(list); d["k"].append(1)

import statistics as st
st.mean(xs); st.median(xs); st.stdev(xs)

from datetime import datetime, timedelta, timezone
datetime.fromisoformat("2024-01-05T10:00:00+00:00")
dt.strftime("%Y-%m")
datetime.now(timezone.utc)

import json
json.loads(text); json.dumps(obj, indent=2)
```

## Files

```python
with open("out.json", "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)

import csv
with open("out.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["a", "b"])
    w.writeheader(); w.writerows(rows)
```

## requests

```python
import requests

r = requests.get(url, params={"q": "x", "per_page": 100},
                 headers={"Accept": "application/json"}, timeout=10)
r.status_code; r.headers; r.text; r.json(); r.url
r.raise_for_status()
r.ok                              # status < 400

requests.post(url, json={"a": 1}, timeout=10)     # JSON body
requests.post(url, data={"a": 1}, timeout=10)     # form body

s = requests.Session()
s.headers.update({"User-Agent": "demo"})
```

### Status codes
`200` ok · `201` created · `204` no content · `301/302` redirect ·
`400` bad request · `401` no auth · `403` forbidden/ratelimit · `404` not found ·
`422` validation · `429` too many requests · `500` server error · `503` unavailable

### Retry skeleton
```python
import time

for attempt in range(3):
    r = requests.get(url, timeout=10)
    if r.status_code < 400:
        break
    if r.status_code == 429 or r.status_code >= 500:
        time.sleep(2 ** attempt)
        continue
    r.raise_for_status()          # 4xx that isn't 429: don't retry
```

## pandas

```python
import pandas as pd

df = pd.DataFrame(list_of_dicts)
df = pd.json_normalize(data, sep=".")
df = pd.json_normalize(data, record_path="items", meta=["id", "name"])

df.head(); df.shape; df.columns; df.dtypes; df.info(); df.describe()
df["col"]; df[["a", "b"]]
df.loc[df["age"] > 30]                    # filter rows
df.loc[(df.a > 1) & (df.b == "x")]        # & | ~  and wrap each in ()
df.sort_values("age", ascending=False).head(10)

df["new"] = df["a"] * 2
df["c"] = df["c"].fillna(0)
df = df.dropna(subset=["id"])
df["n"] = pd.to_numeric(df["n"], errors="coerce")
df["ts"] = pd.to_datetime(df["ts"], errors="coerce", utc=True)

df.groupby("cat")["val"].mean()
df.groupby("cat").agg(n=("id", "count"), avg=("val", "mean")).reset_index()
df["cat"].value_counts()
df.merge(other, on="id", how="left")
df.set_index("ts").resample("D").size()
df.to_csv("out.csv", index=False)
```

## FastAPI

```python
from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel, Field

app = FastAPI(title="demo")

class Item(BaseModel):
    name: str
    qty: int = Field(default=1, ge=1)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/items/{item_id}")
def get_item(item_id: int, q: str | None = Query(default=None, max_length=20)):
    if item_id > 100:
        raise HTTPException(status_code=404, detail="not found")
    return {"id": item_id, "q": q}

@app.post("/items", response_model=Item, status_code=201)
def create(item: Item):
    return item
```

```powershell
uvicorn main:app --reload        # docs at http://127.0.0.1:8000/docs
```

### async upstream
```python
import httpx, asyncio

@app.get("/proxy")
async def proxy():
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get("https://api.github.com/users/torvalds")
        r.raise_for_status()
        return r.json()

results = await asyncio.gather(*(client.get(u) for u in urls))
```

### test
```python
from fastapi.testclient import TestClient
client = TestClient(app)
r = client.get("/health")
assert r.status_code == 200 and r.json() == {"ok": True}
```

## pytest

```powershell
python -m pytest -v
python -m pytest test_task.py::test_name -v
python -m pytest -k "median" -v
python -m pytest -v -m "not live"
python -m pytest -v -s -x
```

## REPL rescue

```python
type(x)      # what is it
len(x)       # how big
dir(x)       # what can I call on it
help(x.foo)  # what does that do
x.keys()     # dict? what fields
print(json.dumps(x, indent=2)[:2000])
```
