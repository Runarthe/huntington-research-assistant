from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Author(BaseModel):
    """A lightweight publication author representation."""

    full_name: str


class Paper(BaseModel):
    """Normalized literature metadata used by the app."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., min_length=1)
    title: str = Field(default="Untitled")
    authors: list[Author] = Field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    doi: str | None = None
    pmid: str | None = None
    abstract: str | None = None
    source_url: HttpUrl | None = None
    citation_count: int | None = None
    is_open_access: bool | None = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: Any) -> str:
        if value is None or str(value).strip() == "":
            return "Untitled"
        return str(value).strip()

    @field_validator("year", mode="before")
    @classmethod
    def parse_year(cls, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            year = int(str(value)[:4])
        except ValueError:
            return None
        if 1800 <= year <= 2200:
            return year
        return None

    @field_validator("citation_count", mode="before")
    @classmethod
    def parse_citation_count(cls, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @field_validator("is_open_access", mode="before")
    @classmethod
    def parse_open_access(cls, value: Any) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        return str(value).strip().upper() in {"Y", "YES", "TRUE", "1"}

    @property
    def author_display(self) -> str:
        if not self.authors:
            return "Authors not listed"
        if len(self.authors) <= 3:
            return ", ".join(author.full_name for author in self.authors)
        first_authors = ", ".join(author.full_name for author in self.authors[:3])
        return f"{first_authors}, et al."

    @property
    def abstract_snippet(self) -> str:
        if not self.abstract:
            return "No abstract available."
        snippet = " ".join(self.abstract.split())
        if len(snippet) <= 350:
            return snippet
        return f"{snippet[:347].rstrip()}..."


class SearchResponse(BaseModel):
    """A normalized provider search response."""

    query: str
    page: int
    page_size: int
    total_results: int | None = None
    papers: list[Paper] = Field(default_factory=list)
