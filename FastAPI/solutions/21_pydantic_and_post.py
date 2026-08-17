"""Unit 21 — worked solution."""

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Watchlist", version="1.0.0")

_STORE: dict[int, dict] = {}
_NEXT_ID = {"value": 1}


def reset_store():
    _STORE.clear()
    _NEXT_ID["value"] = 1


def _new_id():
    value = _NEXT_ID["value"]
    _NEXT_ID["value"] += 1
    return value


class WatchIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=100)
    stars: int = Field(default=0, ge=0)
    language: str | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if " " in value:
            raise ValueError("name must not contain spaces")
        return value.lower()

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: list[str]) -> list[str]:
        cleaned = {tag.strip().lower() for tag in value if tag and tag.strip()}
        return sorted(cleaned)


class WatchOut(BaseModel):
    id: int
    name: str
    owner: str
    stars: int
    language: str | None = None
    tags: list[str] = Field(default_factory=list)
    full_name: str


class WatchPatch(BaseModel):
    stars: int | None = Field(default=None, ge=0)
    language: str | None = None
    tags: list[str] | None = None
    notes: str | None = Field(default=None, max_length=500)


class WatchStats(BaseModel):
    count: int
    total_stars: int
    mean_stars: float | None = None
    languages: dict[str, int] = Field(default_factory=dict)
    top: WatchOut | None = None


def to_out(stored):
    return {
        "id": stored["id"],
        "name": stored["name"],
        "owner": stored["owner"],
        "stars": stored["stars"],
        "language": stored.get("language"),
        "tags": stored.get("tags", []),
        "full_name": f"{stored['owner']}/{stored['name']}",
    }


def _ranked(records):
    return sorted(records, key=lambda r: (-r["stars"], r["name"]))


@app.post("/watch", response_model=WatchOut, status_code=201)
def create_watch(item: WatchIn):
    key = (item.owner.lower(), item.name.lower())
    for stored in _STORE.values():
        if (stored["owner"].lower(), stored["name"].lower()) == key:
            raise HTTPException(
                status_code=409,
                detail=f"already watching: {item.owner}/{item.name}",
            )

    stored = item.model_dump()
    stored["id"] = _new_id()
    _STORE[stored["id"]] = stored
    return to_out(stored)


@app.get("/watch", response_model=list[WatchOut])
def list_watch(
    language: str | None = None,
    min_stars: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    matches = list(_STORE.values())

    if language is not None:
        wanted = language.lower()
        matches = [r for r in matches if (r.get("language") or "").lower() == wanted]
    if min_stars:
        matches = [r for r in matches if r["stars"] >= min_stars]

    return [to_out(record) for record in _ranked(matches)[:limit]]


@app.get("/watch/{item_id}", response_model=WatchOut)
def get_watch(item_id: int):
    stored = _STORE.get(item_id)
    if stored is None:
        raise HTTPException(status_code=404, detail=f"not found: {item_id}")
    return to_out(stored)


@app.patch("/watch/{item_id}", response_model=WatchOut)
def patch_watch(item_id: int, patch: WatchPatch):
    stored = _STORE.get(item_id)
    if stored is None:
        raise HTTPException(status_code=404, detail=f"not found: {item_id}")

    # exclude_unset is what distinguishes "omitted" from "explicitly null"
    stored.update(patch.model_dump(exclude_unset=True))
    return to_out(stored)


@app.delete("/watch/{item_id}", status_code=204)
def delete_watch(item_id: int):
    if item_id not in _STORE:
        raise HTTPException(status_code=404, detail=f"not found: {item_id}")
    del _STORE[item_id]
    return Response(status_code=204)


@app.get("/watch-stats", response_model=WatchStats)
def watch_stats():
    records = list(_STORE.values())
    if not records:
        return {
            "count": 0,
            "total_stars": 0,
            "mean_stars": None,
            "languages": {},
            "top": None,
        }

    languages: dict[str, int] = {}
    for record in records:
        key = record.get("language") or "unknown"
        languages[key] = languages.get(key, 0) + 1

    total = sum(record["stars"] for record in records)
    return {
        "count": len(records),
        "total_stars": total,
        "mean_stars": round(total / len(records), 2),
        "languages": languages,
        "top": to_out(_ranked(records)[0]),
    }
