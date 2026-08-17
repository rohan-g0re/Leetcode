"""Scratch paper for the drills.

Nothing in this file is graded and nothing depends on it. Delete it, overwrite
it, start it again from nothing for each drill -- that is exactly what it is
for. Run it with:

    python scratch.py

What `peek` is for
------------------

`peek` is the opening move. You point it at a URL you have never seen and it
answers, in about one second, the four questions you always need answered
before you can write a single useful line: did the request work, is the reply
actually JSON, what shape is the top level, and what does one record look
like. It is unit 14's exploration procedure with the first four steps already
typed out.

Read what it does, in order, because you want to be able to reproduce this from
memory rather than from this file. It fetches the URL with a timeout, so a
server that never answers cannot hang you in front of an interviewer. It prints
the status code and the content type -- a 401 is an authentication problem
rather than a data problem, and those are solved completely differently, so you
want to know which one you have before you start. If the status is 400 or
above it prints the first bit of the body and gives up, because failing
responses usually say what is wrong in plain text.

Otherwise it parses the JSON and reports the top-level type, since that single
fact decides everything you do next. If the top level is a dictionary it is
probably an envelope -- packaging wrapped around the records -- so `peek`
prints the keys and then hunts for the one whose value is a non-empty list of
dictionaries. That is unit 14's central trick: find the data by its *shape*,
not by guessing that somebody called it `results` or `docs` or `hits`. If the
top level is already a list, the records are right there and it takes the
first one.

Finally it prints that one record as three aligned columns -- field name, type,
and the first fifty characters of the value -- which is the view you actually
want. Types get a column of their own because the type of a field is what
decides whether you can sum it, group by it, or bucket it by time. Read those
three columns and you can classify every field as identifier, numeric,
categorical, temporal, or nested, which is the whole of "what analysis is
possible here."

It returns the parsed data, so you can keep working with it instead of
fetching again.

If you cannot type something like this from memory yet, that is the single
highest-value thing to practise before your interview. The point is not this
exact code -- it is that your first sixty minutes shouldn't be spent on your
first sixty seconds.
"""

import json

import requests

HEADERS = {"Accept": "application/json", "User-Agent": "python-api-course/1.0"}


def peek(url, **params):
    """Fetch one response and describe it. The first 60 seconds, every time."""
    response = requests.get(url, params=params or None, headers=HEADERS, timeout=15)
    print(f"{response.status_code}  {response.headers.get('content-type')}")

    if response.status_code >= 400:
        print(response.text[:300])
        return None

    data = response.json()
    print(f"top level: {type(data).__name__}")

    if isinstance(data, dict):
        print("keys:", list(data.keys()))
        record = None
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                print(f"records look like they live under {key!r} ({len(value)} of them)")
                record = value[0]
                break
    elif isinstance(data, list):
        print(f"{len(data)} items")
        record = data[0] if data else None
    else:
        record = None

    if isinstance(record, dict):
        print("\none record:")
        for key, value in record.items():
            print(f"  {key:>20}  {type(value).__name__:10} {str(value)[:50]}")

    return data


if __name__ == "__main__":
    # Drill 1 starts here. Change the URL for each drill -- any keyword
    # arguments you add become query parameters on the request.
    data = peek("https://api.openbrewerydb.org/v1/breweries", per_page=50)

    # `peek` shows you one record. This next bit answers a different and
    # equally important question: across *all* the records, how many actually
    # have each field filled in? Record zero lying about the schema is the
    # worst failure mode in this whole business -- a field that looks reliable
    # because the first record has it, and then turns up missing or empty on
    # record 700 and kills the run. This counts, for every field name, how many
    # records carry it with something non-empty in it, so anything that prints
    # a number lower than the total is a field you must read with `.get()` and
    # cannot trust to be there. Uncomment it once you have looked at a record.
    # from collections import Counter
    # present = Counter()
    # for record in data:
    #     present.update(k for k, v in record.items() if v not in (None, ""))
    # for field, count in present.most_common():
    #     print(f"{field:>20} {count:>4}/{len(data)}")
