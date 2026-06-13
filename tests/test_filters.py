from hra.filters import filter_papers, sort_papers_by_year, timeline_counts
from hra.models import Paper


def test_filter_papers_by_tag_year_and_open_access() -> None:
    papers = [
        Paper(id="1", title="A", year=2025, is_open_access=True, tags=["biomarkers"]),
        Paper(id="2", title="B", year=2023, is_open_access=True, tags=["biomarkers"]),
        Paper(id="3", title="C", year=2025, is_open_access=False, tags=["clinical trials"]),
    ]

    filtered = filter_papers(
        papers,
        selected_tags=["biomarkers"],
        year_range=(2024, 2026),
        open_access_only=True,
    )

    assert [paper.id for paper in filtered] == ["1"]


def test_sort_papers_by_year_puts_newest_first() -> None:
    papers = [
        Paper(id="old", title="Old", year=2001),
        Paper(id="new", title="New", year=2025),
        Paper(id="unknown", title="Unknown"),
    ]

    sorted_papers = sort_papers_by_year(papers)

    assert [paper.id for paper in sorted_papers] == ["new", "old", "unknown"]


def test_timeline_counts_groups_by_year() -> None:
    papers = [
        Paper(id="1", title="A", year=2024),
        Paper(id="2", title="B", year=2024),
        Paper(id="3", title="C", year=2025),
        Paper(id="4", title="D"),
    ]

    assert timeline_counts(papers) == [
        {"year": 2024, "papers": 2},
        {"year": 2025, "papers": 1},
    ]
