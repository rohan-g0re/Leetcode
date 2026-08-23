# 10 — Classes and Type Hints

*This is the last lesson of Part 1, and it is the one that makes Part 4 stop looking like magic. About twenty-five minutes to read, twenty to do the task. Nothing here is assumed — every term is defined the first time it appears, including the ones that sound like they should be obvious.*

*Be warned that this unit has a slightly odd relationship with the rest of the course. You will not write many classes in a data interview; dictionaries and functions do almost all the real work, and I'll say so again in section 7 when I tell you honestly when to skip all of this. But there are two things you cannot do without it, and both of them arrive in Part 4.*

---

## 1. Why this unit exists at all

Here is the whole justification, stated plainly so you can hold it in your head while you read the rest.

**First: a Pydantic model is a class.** Pydantic is the library FastAPI uses for every request body and every response shape. When you get to unit 21 you will write something that looks like this:

```python
class RepoIn(BaseModel):
    name: str
    stars: int = 0
```

That is a class. If `class`, `self`, and attributes are unfamiliar noise to you, that block is unreadable, and you will end up copying FastAPI examples without knowing which parts you're allowed to change. Half of this lesson exists so that block reads as ordinary Python.

**Second: FastAPI reads your type hints and actually enforces them.** In normal Python, writing `def f(x: int)` and then calling `f("hello")` works fine — Python does not check. Inside FastAPI, that same annotation becomes a real gate: a request carrying `"abc"` where an `int` was declared gets rejected with an automatic error response, and your function is never even called. That contrast — *hints are decoration everywhere except here, where they are the program* — is the thesis of this unit. If you take one idea away, take that one.

Everything else below is the machinery you need for those two sentences to make sense.

---

## 2. What a class actually is

**What it is.** A **class** is a template that describes what a certain kind of thing has and what it can do. An **instance** is one particular thing built from that template. You have met this shape before: in SQL, a `CREATE TABLE` statement describes what columns a customer has, and each row is one actual customer. A class is the `CREATE TABLE`; an instance is the row.

That's the mental model for this whole lesson: **the class is the table definition, the instance is the row, and the difference between them is the difference between "what a repository is" and "this particular repository."**

Here is one, complete, with everything it can contain:

```python
class Repo:
    def __init__(self, name, stars=0):
        self.name = name
        self.stars = stars

    def is_popular(self, threshold=1000):
        return self.stars >= threshold

    def __repr__(self):
        return f"Repo(name={self.name!r}, stars={self.stars})"
```

Take that apart one piece at a time.

The word `class` followed by a name defines the template. The naming convention is `CapWords` — `Repo`, `ApiClient`, `HttpError` — as opposed to the `snake_case` you use for functions and variables from unit 01. This is not enforced by Python, but it is followed universally, and mixing it up reads as inexperience.

Everything indented under the `class` line belongs to it. The `def` blocks inside a class are called **methods** — a method is just a function that lives on a class and gets called on an instance rather than on its own. `repo.is_popular()` is a method call; `len(x)` is a plain function call. Same idea, different attachment point.

To build an instance you call the class as though it were a function:

```python
repo = Repo("flask", 66000)
repo.name            # 'flask'
repo.stars           # 66000
repo.is_popular()    # True
```

`repo` is now an instance. Its `name` and `stars` are **attributes** — named pieces of data stored on that particular instance, reached with a dot. If dictionaries are your reference point, an attribute is very nearly a key: `repo.name` is doing the same job as `repo["name"]`, just with different punctuation and the requirement that the field was declared in advance.

---

## 3. `__init__`, and what `self` really is

Two pieces of the block above need their own section, because they're where every beginner stalls.

**`__init__` is the setup method.** When you write `Repo("flask", 66000)`, Python creates a blank instance and then immediately calls `__init__` on it, handing over the arguments you passed. The job of `__init__` is to take those arguments and store them on the instance. People call it the **constructor**, which is slightly misleading — the object already exists by the time `__init__` runs; `__init__` only fills it in. It is the setup crew, not the builder.

**`self` is the instance the method was called on.** That's the entire definition, and it is simpler than it looks. When you write `repo.is_popular()`, Python quietly rewrites it into `Repo.is_popular(repo)` — it passes the instance in as the first argument. That first argument is what `self` catches. So inside the method, `self` *is* `repo`. Writing `self.stars` means "the stars of whichever instance I was called on."

Two consequences follow, and the second one is the thing that will actually bite you.

First, `self` is written in the `def` line but not at the call site. `def is_popular(self, threshold=1000)` declares two parameters; `repo.is_popular()` passes zero. That looks like an off-by-one error and isn't — the instance is passed automatically. Once you see the `Repo.is_popular(repo)` rewrite, the asymmetry stops looking strange.

Second — and **this is the single most common error people hit when they first write classes** — if you forget `self` in the `def`, the method still receives the instance, but has nowhere to put it. You get this:

```python
class Repo:
    def is_popular():        # forgot self
        return True

Repo("x").is_popular()
# TypeError: is_popular() takes 0 positional arguments but 1 was given
```

Read that message once now so you recognise it later. "Takes 0 but 1 was given" when you passed nothing at all is nonsense until you know that Python supplied the instance for you. Every time you see that error, the fix is the same: add `self`.

The name `self` is a convention rather than a keyword. Python doesn't care what you call the first parameter. Everybody calls it `self`, and calling it anything else is the kind of thing an interviewer notices and quietly counts against you.

---

## 4. `__repr__` and the dunder methods

Method names wrapped in double underscores are called **dunder** methods — short for "double underscore." They are hooks: you don't call them yourself, Python calls them for you when something happens. `__init__` is one, called when an instance is created. There are a handful of others, and one of them is worth writing every single time.

**`__repr__` controls what your object looks like when it's printed.** Leave it out and you get this:

```python
print(repo)
# <__main__.Repo object at 0x000001F4A2B10>
```

That tells you the type and a memory address, which is useless. Now imagine printing a list of seventeen of them while debugging. Seventeen memory addresses, no data. Define `__repr__` and the same print gives you `Repo(name='flask', stars=66000)`, which is a thing you can actually read.

The practitioner's detail here is about *which* dunder to write. Python has two display hooks: `__str__` for human-facing text and `__repr__` for developer-facing detail. When you print a list, Python uses `__repr__` on each element, never `__str__` — and a list of objects is exactly the situation where the blank version hurts most. So if you're only going to define one, define `__repr__`. The convention is to make it look like the code that would rebuild the object, which is why the example writes `Repo(name=..., stars=...)`. The `!r` inside the f-string is what puts the quotes around the string values; it means "use the repr of this value rather than its plain text form."

Two more dunders worth knowing by name: `__eq__` decides what `==` means for your objects, and `__len__` decides what `len()` returns. You'll rarely write them by hand, because section 6 hands you a way to have them generated.

---

## 5. Class attributes, and the sharing trap

So far every attribute has been set inside `__init__`, which means each instance gets its own. You can also attach a value to the class itself:

```python
class ApiClient:
    BASE_URL = "https://api.github.com"      # class attribute: one, shared

    def __init__(self, token):
        self.token = token                   # instance attribute: one per client
```

`BASE_URL` is a **class attribute**. There is exactly one of it, living on the class, shared by every instance ever created. `self.token` is an **instance attribute** — a fresh one for each client you build. Back to the SQL picture: an instance attribute is a column value that varies row to row; a class attribute is a constant written on the table definition itself.

Class attributes are the right tool for genuine constants — a base URL, a default timeout, a fixed set of headers. Read one through the instance and it just works: `self.BASE_URL` finds it on the class when the instance doesn't have it.

**And here is where it goes wrong.** If the class attribute is **mutable** — a list, a dictionary, a set, using unit 01's word for "can be changed in place" — then every instance is sharing *the same object*, and one instance modifying it modifies it for all of them, retroactively and permanently, including instances that were created before and instances not created yet.

```python
class Client:
    HEADERS = {"Accept": "application/json"}

a = Client()
a.HEADERS["Authorization"] = "Bearer secret"

b = Client()
b.HEADERS      # {'Accept': ..., 'Authorization': 'Bearer secret'}
```

`b` was built after the damage and still sees it, because there was never more than one dictionary. This is unit 01's "names point at objects" lesson wearing a new costume, and it is the same trap as unit 06's mutable default argument. It is about to appear a third time in section 6, and a fourth time in this unit's task, where a test checks specifically that calling `headers()` on one client hasn't scribbled on the shared default.

The rule that falls out of this: **class attributes are for things that never change; anything mutable belongs in `__init__`.** And when you need to build on top of a shared mutable constant, you make a copy first and modify the copy. Never the original.

One related oddity, since it confuses people who half-know this. Reading `self.calls` finds a class attribute if there's no instance attribute — but *assigning* `self.calls = 5` always creates an instance attribute, leaving the class one untouched. So a counter declared as a class attribute and incremented with `self.calls += 1` appears to work per-instance. It does, but only by accident of that rule, and it starts at whatever the class value is. Initialise your counters in `__init__` where they belong.

---

## 6. `@dataclass` — the version you'll actually write

Look back at the `Repo` class in section 2 and count how much of it was thought and how much was typing. You wrote `name` three times to store one field. Now imagine seven fields, plus a `__repr__` listing all seven, plus an `__eq__` comparing all seven. That's fifty lines of code containing roughly zero decisions.

Python has a tool that writes that for you.

```python
from dataclasses import dataclass, field

@dataclass
class Repo:
    name: str
    stars: int = 0
    topics: list[str] = field(default_factory=list)

    def is_popular(self, threshold=1000):
        return self.stars >= threshold
```

That is the whole class, and it does everything the section 2 version did and more:

```python
repo = Repo("flask", 66000)
print(repo)              # Repo(name='flask', stars=66000, topics=[])
Repo("a") == Repo("a")   # True
```

Three new things are happening there.

**The `@dataclass` line is a decorator.** A **decorator** is a line starting with `@` placed directly above a `def` or a `class`, and what it means is "take the thing defined below and hand it to this tool for modification before anyone else sees it." You met the shape in unit 06. Here, `dataclass` receives your class, looks at what you declared, and writes `__init__`, `__repr__`, and `__eq__` into it. Your class comes out the other side with methods you never typed. The mental model: **a dataclass is a code generator that reads your field list and writes the boring methods for you.**

**The `name: str` lines are annotations.** An **annotation** is a type written after a colon, saying what kind of value is expected — `str` for text, `int` for a whole number, `list[str]` for a list of text. Section 8 covers the syntax properly. What matters right now is that `dataclass` uses those lines to *find* your fields. It has no other way of knowing what the class contains. Leave the annotation off and the line is invisible to it. This is the one place in Python where an annotation genuinely changes behaviour rather than just documenting it — which makes it a useful preview of what Pydantic does at much larger scale.

**Fields with defaults must come after fields without.** `name: str` has no default, `stars: int = 0` does. Put them the other way round and Python refuses to define the class at all, because the generated `__init__` would have a required parameter sitting after an optional one, which isn't legal in any function.

### The mutable default, made into an error

`field(default_factory=list)` is the line that deserves attention. Here is what it's protecting you from.

You cannot write `topics: list[str] = []`. If you try, Python stops you:

```
ValueError: mutable default <class 'list'> for field topics is not allowed:
use default_factory
```

Think about why. A default written directly in the class body is evaluated **once**, when the class is defined — it becomes a class attribute, one single list shared by every `Repo` you ever build. Append a topic to one repo and it appears on all of them. That's section 5's trap, and it's unit 06's `add_tag` trap, which you've now met three times with three different disguises.

`default_factory=list` says: don't store a list, store the *means of making* a list, and call it fresh each time an instance is built. Note that it's `list`, not `list()` — you're handing over the function itself, not the result of calling it. Every instance gets its own empty list, and nobody shares anything.

The genuinely nice thing here, and the reason I'd flag it: **dataclasses turn a silent bug into a loud error.** Unit 06's version of this trap fails quietly — your function works fine for weeks and then produces a nonsense result. The dataclass version refuses to import. Being stopped at the door is a much better deal than being surprised in production, and it's a rare case of Python choosing strictness.

### Turning one back into a dictionary

The `dataclasses` module ships a helper that converts an instance into a plain dictionary — field names become keys, in declaration order. It's one function call, and finding it yourself is part of this unit's task, so I'll leave you to look. What matters is *why* you'd want it: your target output shape, established back in unit 04, is a list of flat dictionaries, because that's what `json.dumps` accepts, what pandas accepts, and what FastAPI returns without complaint. A dataclass is a nice thing to hold data in while you work; a dictionary is what you hand over at the end.

### The limitation that motivates the next section

Now the important part:

```python
Repo(name=5, stars="lots")
```

That runs. No error, no warning, no complaint. You declared `name: str` and passed the number 5, and Python built the object anyway. **A dataclass is not validation.** The annotations tell `dataclass` what your fields are called and in what order; they are not checked against the values.

That gap — declared types that nothing enforces — is precisely the hole Pydantic fills, and it's the bridge into the rest of this lesson.

---

## 7. When to use a dict instead — an honest answer

Before going further, let me say the thing a Python tutorial usually won't.

| Reach for a dict when                        | Reach for a class or dataclass when             |
| -------------------------------------------- | ----------------------------------------------- |
| The shape comes straight out of JSON         | You've defined a stable internal shape yourself |
| Different records carry different keys       | Every instance has the same fields              |
| You're handing it to pandas or`json.dumps` | You want behaviour attached to the data         |
| It's a throwaway intermediate step           | It's a concept used in several places           |

**For an interview data task, a dict is usually the right answer.** It's what `json.loads` hands you, it's what pandas eats, it's what you can print and inspect without ceremony, and it costs you nothing to create. Wrapping API data in classes because classes feel more professional is a way to spend ten minutes producing less capability than you started with.

Reach for a dataclass when one of two things happens. Either you catch yourself writing `record["owner"]["login"]` in six different places and want the shape written down in one, or the data has grown behaviour — a `summary()`, an `is_popular()` — that belongs next to it rather than scattered across your script.

The reason this unit still matters despite all that is section 1: Pydantic models are classes whether you like classes or not, and FastAPI's request layer is built entirely out of them. You're learning this to *read* Part 4 fluently, not because your ETL script needs an object model.

---

## 8. Type hints: the syntax

A **type hint** (or annotation — the words are used interchangeably) is a note in your code saying what kind of value something is expected to hold.

```python
def average(values: list[float], default: float | None = None) -> float | None:
    ...

name: str = "rohan"
counts: dict[str, int] = {}
```

The rules are short:

- `x: T` annotates a parameter or a variable — read the colon as "is a."
- `-> T` after the parameter list annotates what the function gives back.
- Containers say what's inside them: `list[str]`, `dict[str, int]`, `tuple[int, int]`, `set[str]`. For a dictionary, the first slot is the key type and the second is the value type.
- `A | B` means "either one." The overwhelmingly common case is `X | None`, meaning "an `X`, or nothing at all" — which is how you write down unit 01's `None` in the type system. You will also see this spelled `Optional[X]`, which is the older syntax for the identical idea. Both are current in real codebases; recognise both, write the `|` form.
- `Any` means "I'm not going to say," and switches checking off for that slot.

That last one gets more use than you'd expect, because of what parsed JSON looks like:

```python
from typing import Any

def process(raw: dict[str, Any]) -> list[dict[str, Any]]:
    ...
```

`dict[str, Any]` is the **honest** annotation for an API response. The keys are text — unit 04's translation table guarantees that — but the values could be text, numbers, `None`, lists, or further dictionaries, and pretending otherwise would be a lie you'd have to maintain. You'll write `dict[str, Any]` constantly from here to the end of the course.

---

## 9. Hints are not enforced — except where they are

This is the section the unit is built around.

```python
def f(x: int) -> int:
    return x

f("not an int")      # runs fine, returns "not an int"
```

No error. Python read your annotation, stored it on the function so tools can find it later, and then completely ignored it. It does not check arguments against their hints, it does not check the return value, and it will never stop your program because a type was wrong. Annotations are **not enforced at runtime**.

The distinction has a name worth learning, because it comes up in interviews. **Runtime** means "while the program is actually running." **Static** means "by reading the source code, without running it." Type hints are a *static* feature: they exist for three audiences, none of which is the running program. Human readers, who learn what a function expects without reading its body. Your editor, which uses them for autocomplete and to underline mistakes as you type. And type checkers like `mypy`, a separate tool you run over your code that reports every place the types don't line up. All three work by reading; none of them intervenes while your code runs.

**And then there is the exception, which is the whole reason you're here.**

Pydantic and FastAPI read your annotations at runtime and act on them. Write this in a FastAPI app:

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    ...
```

and a request for `/items/abc` never reaches your function. FastAPI has already looked at `item_id: int`, tried to convert `"abc"`, failed, and sent back an automatic error response explaining exactly which field was wrong and why. Send `/items/42` and your function receives the integer `42`, not the string `"42"` — the conversion happened for you. The same annotation that was pure decoration two paragraphs ago is now doing parsing, validation, error reporting, and — because FastAPI generates interactive documentation from the same information — documentation.

Hold both halves of that at once, because it's the thing to be able to say out loud: **type hints do nothing in plain Python and everything inside FastAPI, and the difference is that FastAPI bothers to read them.** That sentence is unit 21 in advance. When you get there and Pydantic seems to be doing something uncanny, it isn't — it's reading annotations you wrote and enforcing them, which is a thing any library is allowed to do and almost none do.

---

## 10. Inheritance, in one paragraph, for one reason

**Inheritance** is a class taking on everything another class has, then adding to or overriding it. You write it by naming the other class in parentheses:

```python
class HttpError(Exception):
    ...
```

`HttpError` now *is* an `Exception` and has everything one has, without you writing any of it. Inside a subclass, `super()` refers to the class you inherited from, so `super().__init__(...)` means "run the parent's setup as well as mine."

I'm giving this one paragraph rather than a section because for data work you genuinely don't need more, and beginners who discover inheritance tend to overuse it badly. But you do need to *recognise* it, because of exactly one line you're going to meet:

```python
class RepoIn(BaseModel):
    name: str
```

That's a Pydantic model. It inherits from `BaseModel`, and every bit of the validation magic — the type enforcement, the error messages, the JSON conversion — arrives through that inheritance. `BaseModel` is where the behaviour lives; your class just declares fields. When you see it in unit 21, this paragraph is the whole explanation.

---

## 11. Where hints are worth the keystrokes

A practical note, since you're time-constrained and annotating everything is a real cost.

Annotate **function signatures** — parameters and return type. That's where a reader looks to find out how to call something, and it's where a type checker gets the most leverage. Don't bother annotating local variables inside a function; the value is usually obvious from the line that creates it, and the annotations become noise you have to maintain.

In an interview, putting hints on your three or four top-level functions signals care and costs you about fifteen seconds. Annotating every intermediate variable signals that you're padding.

---

## 12. Look this up yourself

Same principle as every unit: reading documentation quickly is the most transferable skill here, so a few things are deliberately left for you.

- The `dataclasses` function that converts an instance into a plain dictionary. You need it for the task.
- `@dataclass(frozen=True)` — instances that can't be modified after creation, and why that makes them usable as dictionary keys (unit 03's hashability rule is the reason).
- `typing.Optional[X]` against `X | None` — confirm for yourself that they mean the same thing.
- `TypedDict` — annotating the shape of a dictionary without replacing it with a class. Given section 7's advice, this is often the best of both.
- `isinstance(x, Repo)` with a class you defined yourself.
- `dict(some_dict)` and `some_dict.copy()` — two ways to make the copy section 5 said you'd need.

---

## 13. Check yourself

1. What is `self`, and why does it appear in the `def` line but not at the call site?
2. What exact error do you get if you forget `self`, and why does the number in it look wrong?
3. What three methods does `@dataclass` generate for you?
4. Why is `topics: list[str] = []` in a dataclass an outright error rather than a bug?
5. Does Python check `def f(x: int)` while your program runs? What is the exception?
6. Why should you write `__repr__` rather than `__str__`?
7. When would you keep API data in dictionaries instead of a dataclass?

*(Answers: 1. the instance the method was called on — Python passes it automatically, because `repo.method()` is really `Repo.method(repo)`. 2. `TypeError: is_popular() takes 0 positional arguments but 1 was given`; the 1 is the instance Python supplied for you. 3. `__init__`, `__repr__`, `__eq__`. 4. because the single list would be created once and shared by every instance, so dataclasses refuse it and demand `default_factory`. 5. no, never — except in Pydantic and FastAPI, which read the annotations and validate against them. 6. because printing a list uses `__repr__` on each element, and a list of objects is exactly when the default is most useless. 7. when the shape comes straight from JSON, when keys vary between records, when it's a throwaway, or when it's heading into pandas.)*

---

*Three things to carry out of this lesson. A class is a table definition and an instance is a row, `self` is the row a method is standing on, and the moment that clicks, Pydantic models stop being mysterious. `@dataclass` writes the boring methods for you by reading your annotations, which is the first time in this course an annotation has changed what your code does — and its refusal to accept `= []` is unit 06's mutable-default trap finally being caught at the door instead of in production. And type hints do nothing at runtime in ordinary Python, which makes the fact that FastAPI enforces them the entire point of Part 4: when you write `item_id: int` there, you have written a validator.*

*That's the end of Part 1. From unit 11 onward the data stops being fixtures on disk and starts arriving over the network. Everything you've built — `.get()` and `or {}`, the list of flat dictionaries, the comprehension, the try/except — is about to be pointed at things you don't control.*

*Now open [`task.py`](task.py).*
