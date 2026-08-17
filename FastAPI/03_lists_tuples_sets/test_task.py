import pytest

from task import (
    chunk,
    compare_id_sets,
    dedupe_preserving_order,
    flatten,
    merge_sorted,
    min_max,
    pair_with_next,
    running_total,
    top_n,
)


def test_dedupe_preserving_order():
    assert dedupe_preserving_order([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedupe_preserving_order([]) == []
    assert dedupe_preserving_order(["a", "a", "a"]) == ["a"]
    assert dedupe_preserving_order([1, 2, 3]) == [1, 2, 3]


def test_dedupe_does_not_mutate_input():
    original = [1, 1, 2]
    dedupe_preserving_order(original)
    assert original == [1, 1, 2]


@pytest.mark.parametrize(
    "items,size,expected",
    [
        ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
        ([1, 2, 3], 5, [[1, 2, 3]]),
        ([1, 2, 3, 4], 2, [[1, 2], [3, 4]]),
        ([], 3, []),
        ([1, 2, 3], 0, []),
        ([1, 2, 3], -1, []),
    ],
)
def test_chunk(items, size, expected):
    assert chunk(items, size) == expected


def test_flatten():
    assert flatten([[1, 2], [3], []]) == [1, 2, 3]
    assert flatten([]) == []
    assert flatten([[], []]) == []


def test_min_max():
    assert min_max([3, 1, 4]) == (1, 4)
    assert min_max([5]) == (5, 5)
    assert min_max([]) is None
    assert isinstance(min_max([1, 2]), tuple)


def test_compare_id_sets():
    assert compare_id_sets([1, 2, 3], [2, 3, 4]) == ([1], [4], [2, 3])
    assert compare_id_sets([], [1]) == ([], [1], [])
    assert compare_id_sets([1, 1, 2], [2]) == ([1], [], [2])
    assert compare_id_sets([], []) == ([], [], [])


def test_running_total():
    assert running_total([1, 2, 3]) == [1, 3, 6]
    assert running_total([]) == []
    assert running_total([5]) == [5]
    assert running_total([1, -1, 1]) == [1, 0, 1]


def test_top_n():
    assert top_n([("a", 3), ("b", 9), ("c", 5)], 2) == ["b", "c"]
    assert top_n([("a", 1)], 5) == ["a"]
    assert top_n([], 3) == []
    assert top_n([("b", 5), ("a", 5)], 2) == ["a", "b"]
    assert top_n([("a", 3), ("b", 9), ("c", 5)], 0) == []


def test_pair_with_next():
    assert pair_with_next([1, 2, 3, 4]) == [(1, 2), (2, 3), (3, 4)]
    assert pair_with_next([1]) == []
    assert pair_with_next([]) == []


def test_merge_sorted():
    assert merge_sorted([1, 3, 5], [2, 4]) == [1, 2, 3, 4, 5]
    assert merge_sorted([], [1]) == [1]
    assert merge_sorted([1], []) == [1]
    assert merge_sorted([], []) == []
    assert merge_sorted([1, 1], [1]) == [1, 1, 1]
    assert merge_sorted([1, 2, 3], [4, 5]) == [1, 2, 3, 4, 5]
