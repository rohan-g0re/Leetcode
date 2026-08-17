# 21 — Pydantic Models, POST, and Response Shaping

*This is the unit that pays off a promise. Back in unit 10 I told you two things and asked you to take them on trust: that a Pydantic model is just a class, and that FastAPI is the one place in Python where a type hint stops being decoration and starts being enforced. Both of those cash out here, in code you write yourself. About twenty-five minutes to read, thirty for the task.*

*Nothing is assumed beyond unit 10's vocabulary — class, instance, attribute, annotation, decorator, inheritance — and I'll lean on those words rather than redefining them. Every new term gets defined the first time it appears.*

*One more framing thought, since you're preparing for an interview. Unit 20 got you returning JSON from a function. That's a demo. What separates a demo from a service is that a service says, in advance and in writing, what it will accept and what it will return, and then holds itself to it. That statement is what this unit is about, and it is the difference an interviewer is actually listening for when they ask you to wrap an API in a service of your own.*

---

## 1. Where unit 20 left off, and what's missing

In unit 20 your endpoints returned plain dictionaries. You built a `dict`, you returned it, FastAPI turned it into JSON, and that worked fine.

It worked fine because you were the only person involved. You knew what keys you'd put in, so you knew what came out. Nothing in the code said so. If you'd typo'd a key, or if one branch of an `if` had returned five keys and another branch four, nothing anywhere would have objected — the endpoint would just quietly serve two different shapes depending on the data, and the person consuming your API would find out on a Tuesday.

The same hole exists on the way in. Unit 20 declared *parameters* — `item_id: int`, `limit: int = 50` — and those were checked. But a parameter is a single scalar value: one number, one string. The moment a caller needs to send you a whole record — a name and an owner and a star count and a list of tags — parameters run out, and you're back to receiving an untyped blob and hoping.

This unit closes both holes with the same tool. You write down the shape of what comes in, you write down the shape of what goes out, and FastAPI enforces both. Everything else in this lesson is detail on those two sentences.

---

## 2. A model is unit 10's dataclass with the enforcement switched on

A **model**, in Pydantic's sense, is a class that describes the shape of some data — which fields it has, what type each one is, what's required and what has a default. You write one by inheriting from `BaseModel`, which is exactly the inheritance line I showed you in unit 10:

```python
from pydantic import BaseModel

class Repo(BaseModel):
    name: str
    stars: int = 0
    language: str | None = None
```

Read that and notice how little of it is new. `class Repo(BaseModel)` is unit 10's inheritance — `Repo` takes on everything `BaseModel` has, and every scrap of the behaviour in this lesson arrives through that one line. The three lines underneath are unit 10's annotations: a field name, a colon, a type, and optionally a default. `str | None` is "text or nothing at all," which you met in unit 10 section 8. There is no new syntax here whatsoever.

Now put it beside unit 10's dataclass version of the same thing:

```python
@dataclass
class Repo:
    name: str
    stars: int = 0
    language: str | None = None
```

Same field names. Same types. Same defaults. Visually near-identical, and that similarity is not a coincidence — Pydantic deliberately borrowed the shape so it would look familiar. And the two behave *completely differently*, which is the single idea this entire unit exists to plant.

### The three cases

Here is the difference, made concrete. Try all three of these against the dataclass:

```python
Repo(name="flask", stars="72117")     # accepted; stars is now the STRING "72117"
Repo(name="flask", stars="lots")      # accepted; stars is now the string "lots"
Repo(stars=1)                         # TypeError -- name is a required argument
```

The dataclass took the first two without a murmur. You declared `stars: int` and handed it text, twice, and it stored the text. Unit 10 warned you about exactly this: **a dataclass is not validation.** The annotations tell `dataclass` what your fields are called; they are never checked against the values. The only thing it refused was the third case, and it refused that for a boring reason that has nothing to do with types — you didn't supply a required function argument.

Now the same three against the Pydantic model:

```python
Repo(name="flask", stars="72117")     # accepted; stars is the INTEGER 72117
Repo(name="flask", stars="lots")      # ValidationError
Repo(stars=1)                         # ValidationError: field required
```

Three different outcomes, and each one is deliberate.

The first is **coercion** — Pydantic converting a value into the type you declared, when the conversion is unambiguous. The string `"72117"` can only mean one integer, so Pydantic converts it and hands you the real `int`. Note carefully what you get back: `repo.stars` is `72117`, not `"72117"`. The conversion happened, and it stuck.

The second is **validation** — Pydantic checking a value against the type you declared and refusing it when it doesn't fit. The string `"lots"` cannot be turned into an integer by any honest means, so instead of guessing, Pydantic raises a `ValidationError` and no object is created at all.

The third is validation of a different kind: `name` has no default, so it's required, and its absence is itself an error.

Coercion and validation are two halves of the same pass. Pydantic tries the conversion; if it works you get the converted value, if it doesn't you get an error. It never silently keeps the wrong type.

**The mental model for this whole unit: a Pydantic model is a `CREATE TABLE` with the constraints actually turned on.** Unit 10 gave you the first half of that picture — the class is the table definition, the instance is the row. A dataclass is that table definition with every column declared and not one constraint enforced, which is to say a comment. A Pydantic model is the same definition with `NOT NULL`, `CHECK (stars >= 0)`, and the type system doing real work at insert time. You already know exactly how much difference that makes to a database. It's the same difference here.

**The practitioner's note.** Pydantic's coercion is deliberately narrower than you might fear. It will turn `"72117"` into `72117`, and `1` into `1.0` for a `float` field, because those are lossless and unambiguous. It will not turn `"lots"` into a number, and by default it will not turn `3.7` into the integer `3`, because that would silently throw away data. This matters because the alternative design — coerce aggressively, guess when unsure — is how you get a service that accepts garbage and stores something plausible-looking. When someone asks in an interview why you'd use Pydantic over hand-written checks, "it coerces where the intent is unambiguous and refuses where it isn't, and I don't have to write either rule" is a good answer.

---

## 3. Living with an instance

Building one is a normal call, and reading fields is normal attribute access, because unit 10 already told you that's what a class gives you:

```python
repo = Repo(name="flask", stars=72117)
repo.name         # "flask"      -- a dot, not repo["name"]
repo.stars        # 72117
```

Watch that punctuation. This is an object, not a dictionary, so it's `repo.name` and not `repo["name"]`. Coming from unit 04, where everything was square brackets, this is the most common finger-slip in the unit.

Two conversions you'll use constantly. **Serialization** is the word for turning an object into plain data you can send over a wire or write to disk — and unit 04 told you what the target shape is: a flat dictionary. Pydantic gives you both directions:

```python
repo.model_dump()             # -> {"name": "flask", "stars": 72117, "language": None}
repo.model_dump_json()        # -> '{"name":"flask","stars":72117,"language":null}'

Repo.model_validate(some_dict)   # dict -> model, validating on the way in
Repo(**some_dict)                # same thing, worse error messages
```

`model_dump()` hands you unit 04's flat dictionary. `model_validate()` goes the other way and is the one to reach for when the data came from outside — it validates, and when it fails it tells you which field and why, whereas `Repo(**some_dict)` fails with a plain Python argument error that names nothing useful.

**One thing that will confuse you when you search the web for help.** Pydantic version 1 called these two methods `.dict()` and `.json()`. Version 2 renamed them to `model_dump()` and `model_dump_json()` to stop them colliding with your own field names — if you had a field called `json`, the old naming was a genuine clash. You have version 2. Plenty of tutorials, Stack Overflow answers, and blog posts still show version 1, and they'll look almost right and then fail. If you see `.dict()` on a model, you're reading v1 material; translate it and carry on.

---

## 4. `Field` — constraints you declare instead of write

Types alone only get you so far. `stars: int` says "a whole number," which still cheerfully accepts `-4000`. To say more, you attach a `Field` to the annotation:

```python
from pydantic import BaseModel, Field

class RepoIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    stars: int = Field(default=0, ge=0)
    language: str | None = Field(default=None, description="primary language")
    tags: list[str] = Field(default_factory=list)
```

A **field constraint** is a rule about a value that goes beyond its type. `ge=0` means "greater than or equal to zero." `min_length=1` means the text can't be empty. The full set is `ge`, `gt`, `le`, `lt` for numbers, `min_length` and `max_length` for text and lists, and `pattern` for a regular expression. If those look familiar, they should — **this is the identical vocabulary you used with `Query` in unit 20.** One set of words, whether the value arrived in the URL or in the body. That consistency is deliberate and it's worth noticing, because it means learning it once covers both.

Now the thread worth pulling. Back in unit 08 you wrote this by hand:

```python
def validate_page_size(size):
    if not isinstance(size, int) or isinstance(size, bool):
        raise ValidationError(...)
    if not 1 <= size <= 100:
        raise ValidationError(...)
    return size
```

Eight or so lines, doing a type check, a range check, and raising a custom error with a decent message. That function was a good exercise and it taught you what the work consists of. Its entire content is now this:

```python
size: int = Field(default=50, ge=1, le=100)
```

That is the shift this unit is really about, and it has a name: you've gone from **imperative** validation — writing out the steps of the checking — to **declarative** validation, where you state the rule and something else performs it. The `ge=1, le=100` version is shorter, but that's the least of it. It's also automatically documented, automatically turned into an error message that names the field, and impossible to forget to call. Hand-written checks get skipped on the third endpoint because you were in a hurry. A declared constraint is part of the type; there's nothing to skip.

**The mutable default, for the third time.** `tags: list[str] = Field(default_factory=list)` is the line to look at. You cannot write `tags: list[str] = []`. Unit 06 showed you why with a function argument that quietly accumulated values across calls; unit 10 showed you the same trap as a shared class attribute and again as a dataclass field. A default written directly in the class body is created *once*, when the class is defined, so every instance would share one list, and appending a tag to one repo would append it to all of them — including ones created before, and ones not created yet.

`default_factory=list` says: don't store a list, store the *means of making* a list, and call it afresh for every instance. Note it's `list` and not `list()` — you're handing over the function itself, not the result of running it. Every model gets its own empty list and nobody shares anything. Like the dataclass version, Pydantic turns this from a silent bug into a loud one; there's a test in your task that specifically builds two models, appends to one's tags, and checks the other's are still empty.

---

## 5. How FastAPI decides something is a request body

This is the second load-bearing idea of the unit, and it's mercifully small.

A **request body** is the block of data a client sends *with* a request, as opposed to what it puts in the URL. A GET request usually has no body — everything it needs fits in the path and the query string. A POST almost always has one, and for a JSON API that body is a JSON object: the record you're creating.

Here's how you receive one:

```python
@app.post("/repos")
def create_repo(repo: RepoIn):
    return {"created": repo.name}
```

That's it. There is no `body=` argument, no decorator option, no `request.json()` call. FastAPI looks at the annotation on each parameter and applies one rule:

**A parameter annotated with a Pydantic model comes from the request body. A parameter annotated with a scalar — `int`, `str`, `float`, `bool` — comes from the path if its name matches a `{placeholder}` in the route, and from the query string otherwise.**

That single sentence is the whole routing-of-inputs story, and it's the thing to be able to say out loud in an interview. It also explains a shape you'll write in this unit's task without thinking about it:

```python
@app.patch("/watch/{item_id}")
def patch_watch(item_id: int, patch: WatchPatch):
```

Two parameters, two different sources. `item_id` is a scalar and matches the placeholder, so it comes from the path. `patch` is annotated with a model, so it comes from the body. You didn't tell FastAPI any of that; it read the annotations. This is unit 10's thesis — hints do nothing in plain Python and everything inside FastAPI — doing real work in front of you.

### What that one annotation buys you

Four things happen for free, and it's worth being precise about them because "FastAPI does a lot for you" is a vague thing to say in an interview and this list isn't.

**The body is parsed.** The raw bytes arrive, get decoded, get parsed from JSON into Python. If the body isn't valid JSON at all, the caller gets an error and your function is never entered.

**Every field is validated.** Types checked, coercion applied, constraints enforced, defaults filled in for anything absent. By the time your function's first line runs, `repo` is a fully-formed, fully-checked object. There is no defensive code at the top of your handler, because there is nothing left to defend against.

**A bad body produces a 422 with per-field detail.** `422 Unprocessable Entity` is the status code meaning "I understood the request, and the data in it is wrong." Here's what the caller actually receives:

```json
{"detail": [
  {"type": "missing", "loc": ["body", "name"], "msg": "Field required"}
]}
```

The important part is `loc`, short for location — it names exactly where the problem is. `["body", "name"]` means "in the request body, in the field called `name`." For a nested model it would be `["body", "owner", "login"]`, walking down to the precise leaf that failed. A caller debugging against your API can read that and fix their request without asking you a single question. Note also that `detail` is a *list* — if three fields are wrong, you get three entries, not just the first one. **You wrote none of this**, and writing it by hand well is a genuinely tedious afternoon.

**The shape appears in `/docs`.** FastAPI reads the same model to generate the interactive documentation page, complete with an example body you can edit in the browser and send. In an interview, opening `/docs`, editing the example, hitting Execute and showing a real 201 come back is a much better demo than anything you can say.

One thing worth internalising about that list: **every item on it came from the annotation.** You didn't configure four features. You wrote `repo: RepoIn` and got parsing, validation, error reporting, and documentation, because all four are downstream of knowing the shape.

---

## 6. `response_model` — putting a contract on the way out

Everything so far has been about what comes in. The way out gets the same treatment, and the mechanism is an argument on the route decorator.

```python
class RepoOut(BaseModel):
    name: str
    stars: int


@app.get("/repos/{name}", response_model=RepoOut)
def get_repo(name: str):
    return {"name": "flask", "stars": 72117, "internal_note": "do not leak"}
```

**`response_model`** tells FastAPI what the response is supposed to look like. Your function returned three keys. The caller receives two. `internal_note` was **filtered out** — not renamed, not nulled, absent. It never left the process.

Sit with that for a second, because it's the behaviour people are most surprised by. `response_model` does not merely *describe* your output; it *rewrites* it. Anything you return that the model doesn't declare is dropped, and anything the model declares that you didn't return is an error you find out about immediately.

That gives you three distinct things.

**A contract.** The `/docs` page now shows exactly what a caller gets, field by field, with types. That's a promise, written in code, that you can be held to — which is what makes it a service rather than a function that happens to be reachable over HTTP.

**Safety, which is the one that matters.** Internal fields cannot leak by accident. The textbook version of this bug is an endpoint that fetches a user row from the database and returns it — and the row includes `password_hash`, because of course it does, it's a column on the table. The endpoint works. The tests pass. The password hashes are on the public internet. With a `response_model` listing `id`, `username`, and `email`, that leak is structurally impossible: the hash isn't declared, so it isn't sent, and no amount of carelessness downstream can change that.

This is the framing to use out loud: **filtering is a safety property, not tidiness.** It's not that the extra key is untidy. It's that the set of fields you return is now a decision made once, in one place, deliberately, rather than an accident of whatever your data layer happened to hand back.

**Validation of your own output.** If your function returns a record missing `stars`, `response_model` catches it in development, on your machine, with a clear error — instead of a consumer catching it in production and emailing you. You are, in effect, running your own API's tests on every response.

It composes the way you'd hope, too:

```python
@app.get("/repos", response_model=list[RepoOut])
def list_repos(): ...
```

`list[RepoOut]` means every element of the returned list gets validated and filtered individually. One annotation, applied down the whole list.

And note what you're allowed to *return*. In the example above the function returned a plain `dict`, not a `RepoOut` instance, and that's completely fine — `response_model` validates whatever you hand back. Returning dicts is often simpler, especially when you're assembling a shape out of stored data, and you lose nothing by doing it. Your task takes exactly this route: a helper builds a dict with the right keys and `response_model` checks it.

---

## 7. In-models and out-models, and why collapsing them is the classic mistake

You have now seen two models describing the same concept — `RepoIn` and `RepoOut`. Your instinct, reasonably, is that this is duplication and you should merge them into one `Repo` and use it for both directions.

Don't. This is the most common design mistake in FastAPI codebases, and being able to name why is a real interview signal.

The reason is that **the shapes genuinely differ**, and not by accident — they differ for structural reasons that show up in every service you'll ever write.

*The input has no id.* A caller creating a repository cannot supply its id, because the server assigns it. Put `id: int` on the model you accept and you've either made it required — so callers must invent ids, which is absurd — or optional, in which case callers can send one and now you have to remember to ignore it, forever, in every endpoint.

*The output has no secrets.* `password_hash`, an internal `notes` field, a raw upstream payload you cached: things you accept and store and must never return. If one model serves both directions, every one of those fields is either sent to callers or unstorable.

*Server-set fields only exist on the way out.* `created_at`, `updated_at`, a computed `full_name` — the caller never sends them and always receives them.

Two models, then, and they are not duplicates; they're two different statements. One says "here is what I will accept from you." The other says "here is what I will give you." The fact that they overlap in the middle is incidental.

```python
class RepoIn(BaseModel):        # what callers may send
    name: str
    stars: int = 0

class RepoOut(BaseModel):       # what callers get back
    id: int
    name: str
    stars: int

@app.post("/repos", response_model=RepoOut, status_code=201)
def create_repo(repo: RepoIn):
    stored = save(repo.model_dump())
    return stored
```

Read the handler. It accepts an in-model, converts it to a plain dict with `model_dump()`, saves it, and returns the stored record — which contains the server-assigned id, and possibly other internal fields too. `response_model=RepoOut` decides what actually goes out. The store keeps everything; the caller sees a curated subset. That's the pattern, and it's the pattern your task implements: `notes` is accepted by `WatchIn`, kept in `_STORE`, and absent from `WatchOut`, so it is never returned by any endpoint. Several tests exist purely to prove that, including one that inspects the generated OpenAPI schema to check `notes` isn't even *documented* as an output field.

---

## 8. Nested models

A field's type can be another model, and validation follows it down:

```python
class Owner(BaseModel):
    login: str
    type: str = "User"


class RepoDetail(BaseModel):
    name: str
    owner: Owner
    topics: list[str] = Field(default_factory=list)
```

Send `{"name": "flask", "owner": {"login": "pallets"}}` and Pydantic validates the outer object, sees that `owner` should be an `Owner`, and validates the inner object against that — **recursively**, meaning it applies the same process at every level of depth. `/docs` shows the whole tree. If the inner object is wrong, `loc` walks down to it: `["body", "owner", "login"]`.

Worth pausing on what this replaces. Unit 04 was largely about surviving nested data you didn't control — `or {}` chains, `deep_get`, the whole apparatus of defending against a `None` where a dictionary was expected. All of that was necessary because nobody had ever written the shape down. Here you write it down once, and every request is checked against it at the door. **You are still doing unit 04's work; you're just doing it declaratively and in one place rather than defensively and in fifty.**

Your task uses this in a small but real way: `WatchStats` has a field `top: WatchOut | None`, a model nested inside another model. The most-starred entry comes back as a fully-shaped `WatchOut` inside the stats response — which means the `notes`-filtering applies there too, automatically, and there's a test that checks it.

---

## 9. Validators — and the one rule you must not forget

Types and constraints handle "is this the right kind of thing, in the right range." Sometimes you need a rule they can't express: this name must not contain a space; these tags should be lowercased and de-duplicated. For that you write a **validator** — a function attached to a model that runs on a specific field after the type check has passed.

```python
from pydantic import field_validator

class RepoIn(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def no_spaces(cls, value: str) -> str:
        if " " in value:
            raise ValueError("name must not contain spaces")
        return value.lower()
```

Take the pieces apart. `@field_validator("name")` is unit 10's decorator syntax — it hands the function below to Pydantic, saying "run this on the `name` field." `@classmethod` sits underneath it because the method belongs to the class rather than to any instance; there's no instance yet, since the whole point is that we're deciding whether to build one. The parameter `cls` is the class, playing the role `self` played for instance methods. You can copy that two-line stack verbatim every time; it's the same shape for every validator you'll ever write.

Now the important part, which is the body.

**Raise `ValueError` to reject. `return` the value to accept.** Those are the only two things a validator may do, and the second one is where people come unstuck.

The `raise` half is intuitive. `ValueError` is Python's ordinary "that value is wrong" exception from unit 08, and Pydantic catches it and folds your message into the 422 response, next to the right `loc`. You don't raise `HTTPException` here and you don't build a response — you raise a plain `ValueError` and the framework does the translating.

The `return` half is the one to burn in. A validator must return the value, and **what it returns becomes the field's value.** That's a feature, not an obligation: the example above returns `value.lower()`, so the field is stored lowercased. A validator is therefore a normalization hook as much as a gate — the natural place to trim whitespace, fold case, canonicalise, sort. Cleaning data at the boundary means nothing downstream has to wonder whether it's clean.

And here is the mistake, which is common enough that I'd bet money you make it at least once today:

```python
    @field_validator("name")
    @classmethod
    def no_spaces(cls, value: str) -> str:
        if " " in value:
            raise ValueError("name must not contain spaces")
        value.lower()          # no return
```

A Python function that falls off the end without returning gives back `None`. So this validator "passes" and sets `name` to `None`. No error, no warning. If the field is `str | None`, that's accepted and stored, and you now have a record with a null name that you can't explain. **Forgetting the `return` doesn't break loudly; it corrupts quietly.** When a field mysteriously comes out as `None` after you've added a validator, this is always why.

The mental model: **a validator is a checkpoint on a conveyor belt. Either you stop the belt, or you put something back on it — and if you put nothing back, the belt keeps moving with an empty space where the value was.**

Your task has two validators and both have to return. `name` rejects spaces and returns lowercased. `tags` returns a cleaned list — lowercased, stripped, de-duplicated, sorted — which is a pure normalization validator that rejects nothing at all.

---

## 10. Partial updates, and telling "omitted" from "null"

This is the subtlest idea in the unit and it takes about four minutes to get. It's worth them.

A PATCH request means "change some fields, leave the rest alone." So the model describing a PATCH body has *every* field optional:

```python
class RepoPatch(BaseModel):
    stars: int | None = Field(default=None, ge=0)
    language: str | None = None
```

Note that the constraints still apply when a value *is* supplied — `stars: int | None = Field(default=None, ge=0)` still rejects `-5`. Optional means "you may omit it," not "anything goes."

Now the problem. Consider two requests to the same endpoint:

```json
{"stars": 99}
{"stars": 99, "language": null}
```

The first says "set stars to 99, don't touch the language." The second says "set stars to 99, *and clear the language*." Those are different intentions and your service must honour both.

But look at what your handler receives. In both cases, `patch.language` is `None`. In the first because that's the default and nothing overrode it; in the second because the caller explicitly asked for null. Reading the attribute cannot tell them apart. And `model_dump()` is no help either — it dumps every field, defaults included, so the naive implementation:

```python
stored.update(patch.model_dump())      # wrong
```

writes `language: None` over a perfectly good stored value on the first request. Every field the caller left out gets wiped. This is a real bug that ships regularly, and the tests in your task check for it directly.

So you need to distinguish "the caller did not mention this field" from "the caller sent null for this field." Pydantic tracks that — it remembers which fields were actually present in the incoming data, separately from which fields ended up with values. `model_dump` takes an argument that filters the dump down to just those, and finding it is a two-minute job in the Pydantic documentation. Look for the option on `model_dump` about fields that were never set. Once you have the right call, the whole of PATCH is a single `update` line, and both requests above do exactly the right thing without a single `if`.

I'm leaving you to find it rather than handing it over, because knowing that this problem *exists* is the hard part and you now do. The method name is the easy part.

---

## 11. Status codes, and the one that returns nothing

You set the success status code on the decorator:

```python
@app.post("/repos", response_model=RepoOut, status_code=201)
def create_repo(repo: RepoIn):
    ...
```

`201 Created` is the correct response to a request that made something new. FastAPI's default is `200 OK`, which isn't wrong exactly, but `201` tells the caller a resource now exists, and using it is a small signal that you know the vocabulary. Errors are separate: raising `HTTPException(status_code=409, detail="...")` inside the handler overrides the decorator's code entirely, and `detail` is what lands in the response body under the key `detail`.

`204 No Content` is the one with a quirk. It means "done, and there is deliberately no body" — the right answer to a successful DELETE. The quirk is that a 204 response must have a genuinely *empty* body, not `null`, not `{}`. In recent FastAPI, returning nothing from the handler does the right thing; returning `Response(status_code=204)` explicitly is unambiguous and works everywhere. The test in your task asserts `response.content == b""`, so an empty-string body is being checked literally.

---

## 12. Look this up yourself

Same principle as every unit — reading documentation quickly under mild time pressure is the most transferable skill in this course, so a few useful things are left for you. The first one is needed for the task.

- The `model_dump` argument from section 10 that keeps only the fields the caller actually sent. **You need this.**
- `model_config = ConfigDict(extra="forbid")` — reject unknown fields in a body instead of silently ignoring them. Think about when you'd want each.
- `Field(examples=[...])` — populates the example body shown in `/docs`, which makes your API pleasant to try.
- `@model_validator(mode="after")` — validating across several fields at once, for rules like "end date must be after start date" that no single-field validator can express.
- `Annotated[int, Field(ge=0)]` — the modern way to write the same constraint, which you'll see in newer codebases.
- `pydantic.EmailStr`, `HttpUrl`, `PositiveInt` — ready-made types that carry their own validation.
- `response_model_exclude_none=True` — drops null fields from responses. Nice for sparse data, and a breaking change for any consumer expecting a stable set of keys. Choose deliberately.

---

## 13. Check yourself

Answer these before you open the task. If one isn't obvious, reread the section rather than getting stuck later and not knowing why.

1. What are the three different outcomes of passing `"72117"`, `"lots"`, and nothing at all to a Pydantic `stars: int` field, and how does a dataclass differ on each?
2. What's the difference between coercion and validation?
3. How does FastAPI decide that a parameter comes from the request body rather than the path or the query string?
4. What status code does an invalid body produce, and what does `loc` contain?
5. Give two structural reasons an in-model and an out-model genuinely differ.
6. Besides not raising, what must a `field_validator` do — and what happens if you forget?
7. Why can't you tell "field omitted" from "field explicitly null" by reading the attribute?

*(Answers: 1. `"72117"` is coerced to the integer `72117`; `"lots"` raises `ValidationError`; the missing field raises `ValidationError` for a required field. A dataclass accepts both strings unchanged and only rejects the third, for the unrelated reason that a required argument was missing. 2. Coercion converts a value into the declared type when that's unambiguous; validation refuses it when it isn't. They're two outcomes of the same pass. 3. The parameter is annotated with a Pydantic model; scalars come from the path when the name matches a placeholder and from the query string otherwise. 4. 422, and `loc` names the exact path to the failing field, like `["body", "name"]`. 5. The input has no server-assigned id; the output has no secrets. Also: server-set fields like timestamps only exist on the way out. 6. Return the value — and what it returns becomes the field's value. Forget it and the field is silently set to `None`. 7. Because in both cases the attribute holds `None`; only the record of which keys were actually present distinguishes them.)*

---

*Three things to carry out of this lesson. First, a Pydantic model is unit 10's dataclass with the enforcement switched on — same syntax, completely different behaviour — and everything else here follows from Pydantic reading annotations that plain Python ignores. Second, one annotation on a parameter turns a function into a validated endpoint: body parsing, per-field checking, a 422 that names the failing field, and a documented, editable example in `/docs`, none of which you wrote. Third, `response_model` is not documentation, it's a filter, and separating the model you accept from the model you return is what stops internal fields leaking — the thing you should say out loud when an interviewer asks how you'd design the endpoint.*

*Now open [`task.py`](task.py). You're building a small watchlist service: four models and six endpoints. Write the models first and run the model tests before you touch a single route — the whole point of this unit is that if the models are right, the endpoints turn out to be almost nothing.*
