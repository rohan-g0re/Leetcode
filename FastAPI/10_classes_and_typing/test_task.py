import dataclasses
import json

import pytest

from task import ApiClient, Repo, load_repos, repo_from_api, repo_to_dict


def test_repo_is_a_dataclass():
    assert dataclasses.is_dataclass(Repo)


def test_repo_construction_and_defaults():
    repo = Repo(name="flask", owner="pallets")
    assert repo.name == "flask"
    assert repo.owner == "pallets"
    assert repo.language is None
    assert repo.stars == 0
    assert repo.forks == 0
    assert repo.license is None
    assert repo.topics == []


def test_repo_topics_not_shared_between_instances():
    a = Repo(name="a", owner="o")
    b = Repo(name="b", owner="o")
    a.topics.append("x")
    assert b.topics == [], "mutable default leaked across instances"


def test_repo_equality_and_repr():
    assert Repo(name="a", owner="o") == Repo(name="a", owner="o")
    assert "flask" in repr(Repo(name="flask", owner="pallets"))


def test_repo_is_popular():
    assert Repo(name="a", owner="o", stars=1000).is_popular() is True
    assert Repo(name="a", owner="o", stars=999).is_popular() is False
    assert Repo(name="a", owner="o", stars=50).is_popular(threshold=10) is True


def test_repo_summary():
    assert Repo(name="flask", owner="p", language="Python", stars=66000).summary() == (
        "flask (Python): 66000 stars"
    )
    assert Repo(name="meta", owner="p", stars=100).summary() == "meta (unknown): 100 stars"


def test_repo_from_api_full_record():
    raw = {
        "name": "flask",
        "owner": {"login": "pallets"},
        "language": "Python",
        "stargazers_count": 66000,
        "forks_count": 16000,
        "license": {"name": "BSD-3-Clause"},
        "topics": ["python", "web"],
    }
    repo = repo_from_api(raw)
    assert repo == Repo(
        name="flask",
        owner="pallets",
        language="Python",
        stars=66000,
        forks=16000,
        license="BSD-3-Clause",
        topics=["python", "web"],
    )


def test_repo_from_api_sparse_record():
    repo = repo_from_api({"name": "x", "license": None, "topics": None})
    assert repo.name == "x"
    assert repo.owner is None
    assert repo.stars == 0
    assert repo.license is None
    assert repo.topics == []


def test_repo_to_dict():
    repo = Repo(name="a", owner="o", stars=5)
    as_dict = repo_to_dict(repo)
    assert as_dict == {
        "name": "a",
        "owner": "o",
        "language": None,
        "stars": 5,
        "forks": 0,
        "license": None,
        "topics": [],
    }
    json.dumps(as_dict)


def test_load_repos():
    repos = load_repos()
    assert len(repos) == 17
    assert all(isinstance(r, Repo) for r in repos)
    assert all(r.owner == "pallets" for r in repos)
    assert sum(r.stars for r in repos) == 117631
    assert sum(1 for r in repos if r.license is None) == 3


def test_client_init_strips_trailing_slash():
    assert ApiClient("https://api.github.com/").base_url == "https://api.github.com"
    assert ApiClient("https://api.github.com").base_url == "https://api.github.com"


def test_client_defaults():
    client = ApiClient("https://x.com")
    assert client.token is None
    assert client.timeout == 10
    assert client.calls == 0


def test_client_headers_without_token():
    client = ApiClient("https://x.com")
    assert client.headers() == {"Accept": "application/json"}


def test_client_headers_with_token():
    client = ApiClient("https://x.com", token="abc")
    assert client.headers() == {
        "Accept": "application/json",
        "Authorization": "Bearer abc",
    }


def test_client_headers_does_not_mutate_class_attribute():
    ApiClient("https://x.com", token="abc").headers()
    assert ApiClient.DEFAULT_HEADERS == {"Accept": "application/json"}


def test_client_url():
    client = ApiClient("https://api.github.com")
    assert client.url("users", "torvalds") == "https://api.github.com/users/torvalds"
    assert client.url() == "https://api.github.com"
    assert client.url("repos") == "https://api.github.com/repos"


def test_client_request_counts_calls():
    client = ApiClient("https://api.github.com", token="t", timeout=5)
    result = client.request(["users", "torvalds"])
    assert result == {
        "url": "https://api.github.com/users/torvalds",
        "timeout": 5,
        "headers": {"Accept": "application/json", "Authorization": "Bearer t"},
    }
    assert client.calls == 1
    client.request(["x"])
    assert client.calls == 2


def test_client_instances_have_independent_counters():
    a = ApiClient("https://x.com")
    b = ApiClient("https://x.com")
    a.request(["y"])
    assert b.calls == 0


def test_client_repr():
    assert repr(ApiClient("https://api.github.com")) == (
        "ApiClient(base_url='https://api.github.com', calls=0)"
    )
