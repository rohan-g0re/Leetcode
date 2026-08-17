import pytest

from task import (
    add_tag,
    apply_to_field,
    average,
    build_url,
    compose,
    make_counter,
    retry_call,
)


def test_average():
    assert average([1, 2, 3]) == 2.0
    assert average([2]) == 2.0
    assert average([]) is None
    assert average([], default=0) == 0
    assert average([1, None, 3]) == 2.0
    assert average([None], default=0) == 0


def test_add_tag_fresh_list_each_call():
    assert add_tag("a") == ["a"]
    assert add_tag("b") == ["b"], "mutable default leaked between calls"
    assert add_tag("c") == ["c"]


def test_add_tag_uses_caller_list():
    given = ["x"]
    result = add_tag("c", given)
    assert result == ["x", "c"]
    assert result is given


@pytest.mark.parametrize(
    "args,kwargs,expected",
    [
        (("https://api.x.com", "users", "torvalds"), {}, "https://api.x.com/users/torvalds"),
        (("https://api.x.com/", "users"), {}, "https://api.x.com/users"),
        (("https://api.x.com", "users", 42), {}, "https://api.x.com/users/42"),
        (("https://api.x.com",), {}, "https://api.x.com"),
        (("https://api.x.com/",), {}, "https://api.x.com"),
        (
            ("https://api.x.com", "search"),
            {"q": "python", "page": 2},
            "https://api.x.com/search?q=python&page=2",
        ),
        (("https://api.x.com",), {"q": "a", "empty": None}, "https://api.x.com?q=a"),
        (("https://api.x.com",), {"empty": None}, "https://api.x.com"),
    ],
)
def test_build_url(args, kwargs, expected):
    assert build_url(*args, **kwargs) == expected


def test_apply_to_field():
    records = [{"n": "  A "}, {"n": "b"}]
    assert apply_to_field(records, "n", str.strip) == [{"n": "A"}, {"n": "b"}]
    assert records == [{"n": "  A "}, {"n": "b"}], "originals must not change"


def test_apply_to_field_skips_missing_and_none():
    records = [{"other": 1}, {"n": None}, {"n": "x"}]
    assert apply_to_field(records, "n", str.upper) == [
        {"other": 1},
        {"n": None},
        {"n": "X"},
    ]


def test_apply_to_field_keeps_other_fields():
    assert apply_to_field([{"n": 2, "keep": "yes"}], "n", lambda v: v * 10) == [
        {"n": 20, "keep": "yes"}
    ]


def test_make_counter():
    c = make_counter()
    assert c() == 1
    assert c() == 2
    assert c() == 3


def test_make_counter_instances_are_independent():
    c = make_counter()
    d = make_counter()
    c()
    c()
    assert d() == 1
    assert c() == 3


def test_retry_call_returns_first_non_none():
    calls = []

    def flaky():
        calls.append(1)
        return "ok" if len(calls) == 2 else None

    assert retry_call(flaky) == "ok"
    assert len(calls) == 2


def test_retry_call_gives_up():
    calls = []

    def always_none():
        calls.append(1)
        return None

    assert retry_call(always_none, attempts=3) is None
    assert len(calls) == 3
    assert retry_call(always_none, attempts=2, on_error="!") == "!"


def test_retry_call_zero_attempts():
    calls = []
    assert retry_call(lambda: calls.append(1), attempts=0, on_error="x") == "x"
    assert calls == []


def test_compose():
    pipeline = compose(str.strip, str.lower)
    assert pipeline("  ABC ") == "abc"
    assert compose()("x") == "x"
    assert compose(lambda x: x + 1, lambda x: x * 2)(3) == 8
