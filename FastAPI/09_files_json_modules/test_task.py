import json

import pytest

from task import (
    append_jsonl,
    language_report,
    load_repos,
    read_json,
    read_jsonl,
    repo_field_names,
    slim_repos,
    write_csv,
    write_json,
)


def test_write_then_read_json(tmp_path):
    path = tmp_path / "out.json"
    data = {"a": 1, "b": [1, 2], "c": None}
    write_json(path, data)
    assert read_json(path) == data


def test_write_json_is_pretty_and_unicode_safe(tmp_path):
    path = tmp_path / "out.json"
    write_json(path, {"city": "Zürich"})
    text = path.read_text(encoding="utf-8")
    assert "\n" in text, "should be indented, not one line"
    assert "Zürich" in text, "should not escape non-ASCII"


def test_write_json_creates_parent_dirs(tmp_path):
    path = tmp_path / "nested" / "deeper" / "out.json"
    write_json(path, [1, 2])
    assert path.exists()
    assert read_json(path) == [1, 2]


def test_read_json_accepts_string_path(tmp_path):
    path = tmp_path / "out.json"
    write_json(path, {"x": 1})
    assert read_json(str(path)) == {"x": 1}


def test_read_json_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_json(tmp_path / "nope.json")


def test_jsonl_roundtrip(tmp_path):
    path = tmp_path / "log.jsonl"
    assert read_jsonl(path) == []
    assert append_jsonl(path, {"i": 1}) == 1
    assert append_jsonl(path, {"i": 2}) == 2
    assert read_jsonl(path) == [{"i": 1}, {"i": 2}]


def test_jsonl_appends_rather_than_overwrites(tmp_path):
    path = tmp_path / "log.jsonl"
    for i in range(5):
        append_jsonl(path, {"i": i})
    assert [r["i"] for r in read_jsonl(path)] == [0, 1, 2, 3, 4]


def test_read_jsonl_skips_blank_lines(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text('{"a": 1}\n\n{"a": 2}\n\n', encoding="utf-8")
    assert read_jsonl(path) == [{"a": 1}, {"a": 2}]


def test_write_csv(tmp_path):
    path = tmp_path / "out.csv"
    rows = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    assert write_csv(path, rows) == 2
    text = path.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line]
    assert lines[0] == "id,name"
    assert lines[1] == "1,a"
    assert len(lines) == 3


def test_write_csv_explicit_fieldnames_and_gaps(tmp_path):
    path = tmp_path / "out.csv"
    rows = [{"id": 1, "extra": "ignored"}, {"id": 2, "name": "b"}]
    assert write_csv(path, rows, fieldnames=["id", "name"]) == 2
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line]
    assert lines == ["id,name", "1,", "2,b"]


def test_write_csv_empty_rows(tmp_path):
    path = tmp_path / "out.csv"
    assert write_csv(path, [], fieldnames=["a", "b"]) == 0
    assert path.read_text(encoding="utf-8").strip() == "a,b"


def test_load_repos():
    repos = load_repos()
    assert isinstance(repos, list)
    assert len(repos) == 17
    assert isinstance(repos[0], dict)


def test_repo_field_names():
    names = repo_field_names(load_repos())
    assert isinstance(names, list)
    assert names == sorted(names)
    assert "stargazers_count" in names
    assert "owner" in names
    assert len(names) == 81


def test_slim_repos_shape():
    slim = slim_repos(load_repos())
    assert len(slim) == 17
    assert set(slim[0]) == {"name", "owner", "language", "stars", "forks", "license"}
    assert all(r["owner"] == "pallets" for r in slim)


def test_slim_repos_handles_null_license():
    slim = slim_repos(load_repos())
    assert sum(1 for r in slim if r["license"] is None) == 3
    assert any(isinstance(r["license"], str) for r in slim)


def test_slim_repos_handles_null_language():
    slim = slim_repos(load_repos())
    assert sum(1 for r in slim if r["language"] is None) == 2


def test_language_report():
    report = language_report(load_repos())
    assert report["total_repos"] == 17
    assert report["total_stars"] == 117631
    assert report["top_repo"] == "flask"
    assert report["languages"]["Python"] == 13
    assert report["languages"]["unknown"] == 2
    assert sum(report["languages"].values()) == 17


def test_language_report_is_json_serializable():
    json.dumps(language_report(load_repos()))
