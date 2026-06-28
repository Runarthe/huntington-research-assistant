from __future__ import annotations

import re

from hra.models import Paper


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Deduplicate records while preserving useful metadata from later matches."""

    merged: list[Paper] = []
    index_by_key: dict[str, int] = {}

    for paper in papers:
        keys = _paper_keys(paper)
        existing_index = next(
            (index_by_key[key] for key in keys if key in index_by_key),
            None,
        )
        if existing_index is None:
            index_by_key.update({key: len(merged) for key in keys})
            merged.append(paper)
            continue

        merged[existing_index] = _merge_papers(merged[existing_index], paper)
        index_by_key.update({key: existing_index for key in keys})

    return merged


def _merge_papers(primary: Paper, secondary: Paper) -> Paper:
    updates = {}
    for field in (
        "title",
        "authors",
        "year",
        "journal",
        "doi",
        "pmid",
        "abstract",
        "source_url",
        "open_access_full_text_url",
        "open_access_pdf_url",
        "citation_count",
        "is_open_access",
    ):
        if not getattr(primary, field) and getattr(secondary, field):
            updates[field] = getattr(secondary, field)

    source_provider = _merged_provider_label(
        primary.source_provider,
        secondary.source_provider,
    )
    return primary.model_copy(
        update={
            **updates,
            "source_provider": source_provider,
            "tags": sorted(set(primary.tags) | set(secondary.tags)),
            "publication_types": sorted(
                set(primary.publication_types) | set(secondary.publication_types)
            ),
            "correction_notices": primary.correction_notices
            or secondary.correction_notices,
        }
    )


def _paper_keys(paper: Paper) -> list[str]:
    keys: list[str] = []
    if paper.pmid:
        keys.append(f"pmid:{paper.pmid.strip().lower()}")
    if paper.doi:
        keys.append(f"doi:{_normalize_doi(paper.doi)}")
    title_key = _title_year_key(paper)
    if title_key:
        keys.append(title_key)
    if not keys:
        keys.append(f"id:{paper.id}")
    return keys


def _normalize_doi(doi: str) -> str:
    value = doi.strip().lower()
    value = re.sub(r"^https?://(dx\.)?doi\.org/", "", value)
    return value.strip()


def _title_year_key(paper: Paper) -> str | None:
    normalized_title = re.sub(r"[^a-z0-9]+", " ", paper.title.lower()).strip()
    if len(normalized_title) < 20:
        return None
    year = paper.year or "unknown"
    return f"title-year:{normalized_title}:{year}"


def _merged_provider_label(first: str, second: str) -> str:
    values = []
    for value in (first, second):
        for part in value.split(" + "):
            if part and part not in values and part != "unknown":
                values.append(part)
    return " + ".join(values) if values else "unknown"
