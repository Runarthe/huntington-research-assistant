from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class Author(BaseModel):
    """A lightweight publication author representation."""

    full_name: str


class CorrectionNotice(BaseModel):
    """A correction or retraction relationship reported by Europe PMC."""

    id: str | None = None
    source: str | None = None
    reference: str | None = None
    notice_type: str

    @property
    def source_url(self) -> str | None:
        if not self.id or not self.source:
            return None
        return f"https://europepmc.org/article/{self.source}/{self.id}"


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
    open_access_full_text_url: HttpUrl | None = None
    open_access_pdf_url: HttpUrl | None = None
    citation_count: int | None = None
    is_open_access: bool | None = None
    tags: list[str] = Field(default_factory=list)
    publication_types: list[str] = Field(default_factory=list)
    correction_notices: list[CorrectionNotice] = Field(default_factory=list)

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

    @property
    def is_retracted(self) -> bool:
        publication_types = {item.lower() for item in self.publication_types}
        if "retracted publication" in publication_types:
            return True
        return any(
            notice.notice_type.lower().startswith("retraction in")
            for notice in self.correction_notices
        )

    @property
    def has_correction(self) -> bool:
        correction_terms = ("correction", "erratum", "corrected")
        return any(
            any(term in notice.notice_type.lower() for term in correction_terms)
            for notice in self.correction_notices
        )

    @property
    def is_review(self) -> bool:
        return any("review" in item.lower() for item in self.publication_types)


class SearchResponse(BaseModel):
    """A normalized provider search response."""

    query: str
    page: int
    page_size: int
    total_results: int | None = None
    papers: list[Paper] = Field(default_factory=list)
    next_cursor_mark: str | None = None


class TrialLocation(BaseModel):
    """A public study location from ClinicalTrials.gov."""

    facility: str | None = None
    status: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class ClinicalTrial(BaseModel):
    """Normalized ClinicalTrials.gov study metadata."""

    nct_id: str = Field(..., min_length=1)
    brief_title: str
    official_title: str | None = None
    overall_status: str
    phases: list[str] = Field(default_factory=list)
    study_type: str | None = None
    brief_summary: str | None = None
    interventions: list[str] = Field(default_factory=list)
    sponsor: str | None = None
    enrollment: int | None = None
    start_date: str | None = None
    completion_date: str | None = None
    last_update: str | None = None
    locations: list[TrialLocation] = Field(default_factory=list)
    source_url: HttpUrl

    @property
    def countries(self) -> list[str]:
        return sorted({location.country for location in self.locations if location.country})

    @property
    def status_label(self) -> str:
        return self.overall_status.replace("_", " ").title()


class ClinicalTrialResponse(BaseModel):
    """Normalized response from the ClinicalTrials.gov API v2."""

    total_results: int | None = None
    studies: list[ClinicalTrial] = Field(default_factory=list)
    next_page_token: str | None = None
