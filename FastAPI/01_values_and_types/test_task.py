import pytest

from task import (
    bucket,
    clamp,
    coerce_number,
    describe_type,
    format_summary,
    is_missing,
    percent_change,
    safe_divide,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        (5, "int"),
        (5.0, "float"),
        ("x", "str"),
        (True, "bool"),
        (None, "nonetype"),
        ([], "list"),
        ({}, "dict"),
    ],
)
def test_describe_type(value, expected):
    assert describe_type(value) == expected


def test_safe_divide():
    assert safe_divide(10, 4) == 2.5
    assert safe_divide(0, 5) == 0.0
    assert safe_divide(10, 0) is None
    assert safe_divide(-9, 3) == -3.0


@pytest.mark.parametrize(
    "value,expected",
    [
        (None, True),
        ("", True),
        ("   ", True),
        ("\t\n", True),
        (0, False),
        (0.0, False),
        (False, False),
        ([], False),
        ("0", False),
        ("hello", False),
    ],
)
def test_is_missing(value, expected):
    assert is_missing(value) is expected


@pytest.mark.parametrize(
    "value,expected",
    [
        (42, 42.0),
        (42.5, 42.5),
        ("42", 42.0),
        ("3.5", 3.5),
        ("  7 ", 7.0),
        ("-12", -12.0),
        ("abc", None),
        ("", None),
        ("   ", None),
        (None, None),
        (True, None),
        (False, None),
        ([], None),
    ],
)
def test_coerce_number(value, expected):
    result = coerce_number(value)
    assert result == expected
    if expected is not None:
        assert isinstance(result, float), "must return a float, not an int"


@pytest.mark.parametrize(
    "n,size,expected",
    [
        (0, 10, 0),
        (7, 10, 0),
        (10, 10, 1),
        (19, 10, 1),
        (37, 10, 3),
        (37, 25, 1),
        (5, 0, None),
        (5, -1, None),
    ],
)
def test_bucket(n, size, expected):
    assert bucket(n, size) == expected


def test_percent_change():
    assert percent_change(100, 150) == 50.0
    assert percent_change(100, 50) == -50.0
    assert percent_change(80, 80) == 0.0
    assert percent_change(50, 0) == -100.0
    assert percent_change(0, 10) is None
    assert percent_change(3, 4) == 33.33


def test_clamp():
    assert clamp(5, 1, 10) == 5
    assert clamp(-3, 1, 10) == 1
    assert clamp(99, 1, 10) == 10
    assert clamp(1, 1, 10) == 1
    assert clamp(10, 1, 10) == 10


def test_format_summary():
    assert format_summary("torvalds", 8, 1234.5678) == "torvalds: 8 items, avg 1234.57"
    assert format_summary("empty", 0, None) == "empty: 0 items, avg n/a"
    assert format_summary("a", 1, 2.0) == "a: 1 items, avg 2.00"
