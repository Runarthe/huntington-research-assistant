import tempfile
from pathlib import Path
from uuid import uuid4

from hra.cache import SearchCache, default_cache_path, fallback_cache_path
from hra.models import Paper


def temp_cache_dir() -> Path:
    path = Path(tempfile.gettempdir()) / "hra-test-cache" / uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_default_cache_path_respects_env_override(monkeypatch) -> None:
    cache_path = temp_cache_dir() / "custom" / "cache.sqlite3"
    monkeypatch.setenv("HRA_CACHE_PATH", str(cache_path))

    assert default_cache_path() == cache_path


def test_search_cache_creates_parent_directory() -> None:
    cache_path = temp_cache_dir() / "nested" / "cache.sqlite3"

    cache = SearchCache(cache_path)
    cache.record_search("gene silencing", "expanded query")
    recent = cache.recent_searches()

    assert cache_path.exists()
    assert recent[0]["query"] == "gene silencing"


def test_search_cache_stores_papers() -> None:
    cache = SearchCache(temp_cache_dir() / "cache.sqlite3")
    paper = Paper(id="p1", title="A biomarker paper")

    cache.upsert_papers([paper])
    cached = cache.get_paper("p1")

    assert cached is not None
    assert cached.title == "A biomarker paper"


def test_search_cache_manages_reading_list() -> None:
    cache = SearchCache(temp_cache_dir() / "cache.sqlite3")
    first = Paper(id="p1", title="A biomarker paper")
    second = Paper(id="p2", title="A gene silencing paper")

    cache.add_to_reading_list(first)
    cache.add_to_reading_list(second)
    cache.add_to_reading_list(first)

    assert cache.reading_list_ids() == {"p1", "p2"}
    assert [paper.id for paper in cache.reading_list_papers()] == ["p2", "p1"]

    cache.remove_from_reading_list("p1")

    assert cache.reading_list_ids() == {"p2"}
    assert [paper.id for paper in cache.reading_list_papers()] == ["p2"]


def test_search_cache_manages_explicit_seen_state() -> None:
    cache = SearchCache(temp_cache_dir() / "cache.sqlite3")

    cache.mark_paper_seen("p1")
    cache.mark_paper_seen("p2")
    cache.mark_paper_seen("p1")

    assert cache.seen_paper_ids() == {"p1", "p2"}

    cache.mark_paper_unseen("p1")

    assert cache.seen_paper_ids() == {"p2"}


def test_search_cache_falls_back_when_default_dir_is_unusable(monkeypatch) -> None:
    blocker = temp_cache_dir() / "not-a-directory"
    blocker.write_text("blocks mkdir", encoding="utf-8")
    monkeypatch.delenv("HRA_CACHE_PATH", raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(blocker))
    monkeypatch.setenv("XDG_CACHE_HOME", str(blocker))

    cache = SearchCache()

    assert cache.path == fallback_cache_path()
