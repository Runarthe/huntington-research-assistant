from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from hra.models import Paper


def filter_papers(
    papers: Iterable[Paper],
    selected_tags: list[str] | None = None,
    year_range: tuple[int, int] | None = None,
    open_access_only: bool = False,
) -> list[Paper]:
    """Apply lightweight client-side filters to retrieved papers."""

    selected = set(selected_tags or [])
    filtered: list[Paper] = []
    for paper in papers:
        if selected and not selected.intersection(paper.tags):
            continue
        if year_range and paper.year is not None:
            start_year, end_year = year_range
            if paper.year < start_year or paper.year > end_year:
                continue
        if year_range and paper.year is None:
            continue
        if open_access_only and paper.is_open_access is not True:
            continue
        filtered.append(paper)
    return filtered


def sort_papers_by_year(papers: Iterable[Paper], descending: bool = True) -> list[Paper]:
    return sorted(
        papers,
        key=lambda paper: (paper.year is not None, paper.year or 0, paper.title.lower()),
        reverse=descending,
    )


def timeline_counts(papers: Iterable[Paper]) -> list[dict[str, int]]:
    counts = Counter(paper.year for paper in papers if paper.year is not None)
    return [{"year": year, "papers": counts[year]} for year in sorted(counts)]
