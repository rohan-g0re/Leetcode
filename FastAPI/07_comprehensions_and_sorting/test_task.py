from task import (
    REPOS,
    active_python_repos,
    distinct_languages,
    group_names_by_language,
    label_sizes,
    names_of,
    rank_by_stars,
    sort_with_missing_last,
    stars_by_name,
    stars_summary,
    total_forks,
)


def test_names_of():
    assert names_of(REPOS)[:3] == ["flask", "jinja", "click"]
    assert len(names_of(REPOS)) == len(REPOS)
    assert names_of([]) == []


def test_active_python_repos():
    assert active_python_repos(REPOS) == ["flask", "jinja", "click", "werkzeug"]


def test_active_python_repos_excludes_missing_language():
    records = [{"name": "x", "archived": False}]
    assert active_python_repos(records) == []


def test_stars_by_name():
    mapping = stars_by_name(REPOS)
    assert mapping["flask"] == 66000
    assert mapping["meta"] == 100
    assert len(mapping) == 7


def test_distinct_languages():
    assert distinct_languages(REPOS) == ["HTML", "Python"]
    assert distinct_languages([]) == []


def test_total_forks():
    assert total_forks(REPOS) == 20950
    assert total_forks([]) == 0


def test_rank_by_stars():
    assert rank_by_stars(REPOS, 3) == ["flask", "click", "jinja"]
    assert rank_by_stars(REPOS)[0] == "flask"
    assert len(rank_by_stars(REPOS)) == 7
    assert rank_by_stars([], 3) == []


def test_rank_by_stars_tie_breaks_on_name():
    records = [{"name": "b", "stars": 5}, {"name": "a", "stars": 5}]
    assert rank_by_stars(records) == ["a", "b"]


def test_sort_with_missing_last():
    records = [{"n": 3}, {"n": None}, {"n": 1}, {}]
    assert sort_with_missing_last(records, "n") == [{"n": 1}, {"n": 3}, {"n": None}, {}]
    assert records == [{"n": 3}, {"n": None}, {"n": 1}, {}], "input must not change"


def test_sort_with_missing_last_all_present():
    assert sort_with_missing_last([{"n": 2}, {"n": 1}], "n") == [{"n": 1}, {"n": 2}]


def test_group_names_by_language():
    grouped = group_names_by_language(REPOS)
    assert grouped["Python"] == ["flask", "jinja", "click", "werkzeug", "itsdangerous"]
    assert grouped["HTML"] == ["flask-website"]
    assert grouped[None] == ["meta"]


def test_stars_summary():
    summary = stars_summary(REPOS)
    assert summary["count"] == 7
    assert summary["total"] == 100600
    assert summary["mean"] == 14371.43
    assert summary["max_name"] == "flask"


def test_stars_summary_empty():
    assert stars_summary([]) == {
        "count": 0,
        "total": 0,
        "mean": None,
        "max_name": None,
    }


def test_label_sizes():
    labelled = label_sizes(REPOS)
    assert labelled[:2] == [("flask", "big"), ("jinja", "big")]
    assert ("meta", "small") in labelled
    assert len(labelled) == len(REPOS)


def test_label_sizes_threshold():
    assert label_sizes([{"name": "x", "stars": 10}], threshold=10) == [("x", "big")]
    assert label_sizes([{"name": "x"}], threshold=1) == [("x", "small")]
