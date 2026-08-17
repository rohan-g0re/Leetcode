import pytest

from task import (
    count_missing,
    deep_get,
    flatten_dict,
    group_by,
    index_by,
    pluck,
    rename_keys,
    select_fields,
    summarize_records,
)

NESTED = {"a": {"b": {"c": 1}}, "z": None, "lst": [{"k": 9}]}


def test_deep_get_happy_path():
    assert deep_get(NESTED, "a", "b", "c") == 1
    assert deep_get(NESTED, "a", "b") == {"c": 1}
    assert deep_get(NESTED) == NESTED


def test_deep_get_missing_and_none():
    assert deep_get(NESTED, "a", "x", "c") is None
    assert deep_get(NESTED, "z", "anything") is None
    assert deep_get(NESTED, "a", "b", "c", "d") is None
    assert deep_get(NESTED, "nope") is None


def test_deep_get_custom_default():
    assert deep_get(NESTED, "nope", default=0) == 0
    assert deep_get(NESTED, "a", "x", default="fallback") == "fallback"


def test_deep_get_does_not_descend_lists():
    assert deep_get(NESTED, "lst", "k") is None


def test_pluck():
    assert pluck([{"a": 1}, {"a": 2}, {"b": 3}], "a") == [1, 2, None]
    assert pluck([{"a": 1}, {"b": 3}], "a", default=0) == [1, 0]
    assert pluck([], "a") == []
    assert pluck([{"a": None}], "a") == [None]


def test_index_by():
    assert index_by([{"id": 1, "n": "a"}, {"id": 2, "n": "b"}], "id") == {
        1: {"id": 1, "n": "a"},
        2: {"id": 2, "n": "b"},
    }
    assert index_by([{"id": 1, "v": "old"}, {"id": 1, "v": "new"}], "id") == {
        1: {"id": 1, "v": "new"}
    }
    assert index_by([{"no_id": 1}], "id") == {}
    assert index_by([], "id") == {}


def test_group_by():
    records = [{"t": "x", "n": 1}, {"t": "y", "n": 2}, {"t": "x", "n": 3}]
    assert group_by(records, "t") == {
        "x": [{"t": "x", "n": 1}, {"t": "x", "n": 3}],
        "y": [{"t": "y", "n": 2}],
    }


def test_group_by_missing_key_bucket():
    records = [{"t": "x"}, {"other": 1}]
    grouped = group_by(records, "t")
    assert grouped["x"] == [{"t": "x"}]
    assert grouped[None] == [{"other": 1}]


def test_select_fields():
    original = {"a": 1, "b": 2, "c": 3}
    assert select_fields(original, ["a", "c", "zz"]) == {"a": 1, "c": 3}
    assert select_fields({}, ["a"]) == {}
    assert original == {"a": 1, "b": 2, "c": 3}, "input must not be mutated"


def test_select_fields_keeps_none_values():
    assert select_fields({"a": None}, ["a"]) == {"a": None}


def test_rename_keys():
    original = {"user_name": "x", "id": 1}
    assert rename_keys(original, {"user_name": "name"}) == {"name": "x", "id": 1}
    assert rename_keys(original, {}) == {"user_name": "x", "id": 1}
    assert original == {"user_name": "x", "id": 1}, "input must not be mutated"


def test_count_missing():
    records = [{"a": 1, "b": None}, {"a": None}, {"a": 3, "b": 2}]
    assert count_missing(records, ["a", "b"]) == {"a": 1, "b": 2}
    assert count_missing([], ["a"]) == {"a": 0}
    assert count_missing([{"a": 0}, {"a": ""}], ["a"]) == {"a": 0}


def test_flatten_dict():
    assert flatten_dict({"a": 1, "b": {"c": 2, "d": {"e": 3}}}) == {
        "a": 1,
        "b.c": 2,
        "b.d.e": 3,
    }
    assert flatten_dict({"a": {}}) == {}
    assert flatten_dict({}) == {}
    assert flatten_dict({"a": [1, 2], "b": None}) == {"a": [1, 2], "b": None}


def test_flatten_dict_custom_separator():
    assert flatten_dict({"a": {"b": 1}}, sep="_") == {"a_b": 1}


def test_summarize_records():
    records = [
        {"cat": "a", "n": 10},
        {"cat": "a", "n": 20},
        {"cat": "b", "n": 5},
        {"cat": "b"},
        {"n": 7},
    ]
    assert summarize_records(records, "n", "cat") == {
        "a": {"count": 2, "total": 30, "mean": 15.0},
        "b": {"count": 1, "total": 5, "mean": 5.0},
        None: {"count": 1, "total": 7, "mean": 7.0},
    }


def test_summarize_records_all_missing_numeric():
    records = [{"cat": "z"}, {"cat": "z", "n": None}]
    assert summarize_records(records, "n", "cat") == {
        "z": {"count": 0, "total": 0, "mean": None}
    }


def test_summarize_records_empty():
    assert summarize_records([], "n", "cat") == {}
