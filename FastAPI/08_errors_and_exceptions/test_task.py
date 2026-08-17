import pytest

from task import (
    ValidationError,
    describe_exception,
    divide_all,
    first_successful,
    parse_records,
    safe_field,
    to_float,
    validate_page_size,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("3.5", 3.5),
        (" 7 ", 7.0),
        (42, 42.0),
        ("1e3", 1000.0),
        ("-2", -2.0),
        ("abc", None),
        ("", None),
        (None, None),
        ([], None),
        ({}, None),
    ],
)
def test_to_float(value, expected):
    assert to_float(value) == expected


def test_to_float_default():
    assert to_float("nope", default=0.0) == 0.0
    assert to_float(None, default=-1) == -1


def test_safe_field():
    assert safe_field({"a": {"b": 1}}, "a", "b") == 1
    assert safe_field({"a": None}, "a", "b") is None
    assert safe_field({}, "x", default=0) == 0
    assert safe_field({"a": 1}, "a", "b") is None
    assert safe_field({"a": {"b": 1}}) == {"a": {"b": 1}}


def test_parse_records():
    good, failures = parse_records(
        [
            {"id": 1, "amount": "10.5"},
            {"id": 2},
            {"amount": 5},
            {"id": 4, "amount": "abc"},
        ]
    )
    assert good == [{"id": 1, "amount": 10.5}]
    assert failures == [
        {"id": 2, "error": "missing amount"},
        {"id": None, "error": "missing id"},
        {"id": 4, "error": "bad amount"},
    ]


def test_parse_records_all_good():
    good, failures = parse_records([{"id": "a", "amount": 1}, {"id": "b", "amount": 2.5}])
    assert good == [{"id": "a", "amount": 1.0}, {"id": "b", "amount": 2.5}]
    assert failures == []


def test_parse_records_empty():
    assert parse_records([]) == ([], [])


def test_parse_records_missing_id_takes_priority():
    _, failures = parse_records([{"nothing": 1}])
    assert failures == [{"id": None, "error": "missing id"}]


def test_validate_page_size_accepts():
    assert validate_page_size(50) == 50
    assert validate_page_size(1) == 1
    assert validate_page_size(100) == 100


@pytest.mark.parametrize("bad", [0, -1, 101, "50", 1.5, True, None])
def test_validate_page_size_rejects(bad):
    with pytest.raises(ValidationError) as info:
        validate_page_size(bad)
    assert str(bad) in str(info.value)


def test_first_successful():
    assert first_successful([lambda: 1 / 0, lambda: "ok"]) == "ok"
    assert first_successful([lambda: 1 / 0], default="fallback") == "fallback"
    assert first_successful([], default="fallback") == "fallback"
    assert first_successful([lambda: None]) is None


def test_first_successful_stops_at_first_win():
    calls = []

    def first():
        calls.append("first")
        return "a"

    def second():
        calls.append("second")
        return "b"

    assert first_successful([first, second]) == "a"
    assert calls == ["first"]


def test_describe_exception():
    assert describe_exception(lambda: 1) == "ok"
    assert describe_exception(lambda: 1 / 0) == "ZeroDivisionError: division by zero"
    assert describe_exception(lambda: {}["x"]) == "KeyError: 'x'"
    assert describe_exception(lambda: int("x")).startswith("ValueError: ")


def test_divide_all():
    assert divide_all([(10, 2), (1, 0), (9, 3)]) == [5.0, None, 3.0]
    assert divide_all([("a", 2)]) == [None]
    assert divide_all([]) == []
