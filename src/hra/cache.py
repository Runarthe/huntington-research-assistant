from __future__ import annotations

import json
import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from hra.models import Paper

APP_CACHE_DIR_NAME = "huntington-research-assistant"


def default_cache_path() -> Path:
    configured_path = os.getenv("HRA_CACHE_PATH")
    if configured_path:
        return Path(configured_path).expanduser()

    if os.name == "nt" and os.getenv("LOCALAPPDATA"):
        base_dir = Path(os.environ["LOCALAPPDATA"])
    elif os.getenv("XDG_CACHE_HOME"):
        base_dir = Path(os.environ["XDG_CACHE_HOME"])
    else:
        base_dir = Path.home() / ".cache"

    return base_dir / APP_CACHE_DIR_NAME / "cache.sqlite3"


def fallback_cache_path() -> Path:
    return Path(tempfile.gettempdir()) / APP_CACHE_DIR_NAME / "cache.sqlite3"


class SearchCache:
    """Tiny SQLite cache for search history and result payloads."""

    def __init__(self, path: str | Path | None = None) -> None:
        is_default_path = path is None and not os.getenv("HRA_CACHE_PATH")
        self.path = Path(path) if path is not None else default_cache_path()
        try:
            self._ensure_schema()
        except (OSError, sqlite3.Error):
            if not is_default_path:
                raise
            self.path = fallback_cache_path()
            self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    expanded_query TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reading_list (
                    paper_id TEXT PRIMARY KEY,
                    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_papers (
                    paper_id TEXT PRIMARY KEY,
                    seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def record_search(self, query: str, expanded_query: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO searches (query, expanded_query) VALUES (?, ?)",
                (query, expanded_query),
            )

    def upsert_papers(self, papers: list[Paper]) -> None:
        rows: list[tuple[str, str]] = [
            (paper.id, paper.model_dump_json()) for paper in papers
        ]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO papers (id, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                rows,
            )

    def recent_searches(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT query, expanded_query, created_at
                FROM searches
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {"query": row[0], "expanded_query": row[1], "created_at": row[2]}
            for row in rows
        ]

    def get_paper(self, paper_id: str) -> Paper | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload FROM papers WHERE id = ?",
                (paper_id,),
            ).fetchone()
        if row is None:
            return None
        return Paper.model_validate(json.loads(row[0]))

    def add_to_reading_list(self, paper: Paper) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO papers (id, payload, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (paper.id, paper.model_dump_json()),
            )
            connection.execute(
                """
                INSERT INTO reading_list (paper_id, added_at)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(paper_id) DO NOTHING
                """,
                (paper.id,),
            )

    def remove_from_reading_list(self, paper_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM reading_list WHERE paper_id = ?",
                (paper_id,),
            )

    def reading_list_ids(self) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute("SELECT paper_id FROM reading_list").fetchall()
        return {row[0] for row in rows}

    def reading_list_papers(self) -> list[Paper]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT papers.payload
                FROM reading_list
                JOIN papers ON papers.id = reading_list.paper_id
                ORDER BY reading_list.added_at DESC, reading_list.paper_id DESC
                """
            ).fetchall()
        return [Paper.model_validate(json.loads(row[0])) for row in rows]

    def mark_paper_seen(self, paper_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO seen_papers (paper_id, seen_at)
                VALUES (?, CURRENT_TIMESTAMP)
                ON CONFLICT(paper_id) DO UPDATE SET seen_at = CURRENT_TIMESTAMP
                """,
                (paper_id,),
            )

    def mark_paper_unseen(self, paper_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "DELETE FROM seen_papers WHERE paper_id = ?",
                (paper_id,),
            )

    def seen_paper_ids(self) -> set[str]:
        with self._connect() as connection:
            rows = connection.execute("SELECT paper_id FROM seen_papers").fetchall()
        return {row[0] for row in rows}
