"""Unit 10 — worked solution."""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


@dataclass
class Repo:
    name: str
    owner: str
    language: str | None = None
    stars: int = 0
    forks: int = 0
    license: str | None = None
    topics: list[str] = field(default_factory=list)

    def is_popular(self, threshold: int = 1000) -> bool:
        return self.stars >= threshold

    def summary(self) -> str:
        return f"{self.name} ({self.language or 'unknown'}): {self.stars} stars"


def repo_from_api(raw: dict[str, Any]) -> Repo:
    return Repo(
        name=raw.get("name"),
        owner=(raw.get("owner") or {}).get("login"),
        language=raw.get("language"),
        stars=raw.get("stargazers_count") or 0,
        forks=raw.get("forks_count") or 0,
        license=(raw.get("license") or {}).get("name"),
        topics=list(raw.get("topics") or []),
    )


def repo_to_dict(repo: Repo) -> dict[str, Any]:
    return asdict(repo)


def load_repos() -> list[Repo]:
    path = FIXTURES / "github_repos_pallets.json"
    raw_repos = json.loads(path.read_text(encoding="utf-8"))
    return [repo_from_api(raw) for raw in raw_repos]


class ApiClient:
    DEFAULT_HEADERS: dict[str, str] = {"Accept": "application/json"}

    def __init__(self, base_url: str, token: str | None = None, timeout: int = 10) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.calls = 0

    def headers(self) -> dict[str, str]:
        headers = dict(self.DEFAULT_HEADERS)
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def url(self, *parts: Any) -> str:
        url = self.base_url
        for part in parts:
            url = f"{url}/{part}"
        return url

    def request(self, path_parts: list[str]) -> dict[str, Any]:
        self.calls += 1
        return {
            "url": self.url(*path_parts),
            "timeout": self.timeout,
            "headers": self.headers(),
        }

    def __repr__(self) -> str:
        return f"ApiClient(base_url={self.base_url!r}, calls={self.calls})"
