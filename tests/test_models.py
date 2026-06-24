from hra.models import Author, CorrectionNotice, Paper, SearchResponse


def test_paper_normalizes_empty_fields() -> None:
    paper = Paper(
        id="abc",
        title=" ",
        authors=[Author(full_name="Ada Example")],
        year="2024-01-10",
        citation_count="12",
        is_open_access="Y",
    )

    assert paper.title == "Untitled"
    assert paper.year == 2024
    assert paper.citation_count == 12
    assert paper.is_open_access is True
    assert paper.author_display == "Ada Example"


def test_paper_snippet_truncates_long_abstract() -> None:
    paper = Paper(id="abc", title="Title", abstract="word " * 100)

    assert len(paper.abstract_snippet) <= 350
    assert paper.abstract_snippet.endswith("...")


def test_search_response_defaults_to_empty_papers() -> None:
    response = SearchResponse(query="x", page=1, page_size=10)

    assert response.papers == []
    assert response.next_cursor_mark is None


def test_paper_surfaces_retraction_and_correction_metadata() -> None:
    paper = Paper(
        id="abc",
        publication_types=["Journal Article"],
        correction_notices=[
            CorrectionNotice(notice_type="Retraction in", id="123", source="MED"),
            CorrectionNotice(notice_type="Erratum in"),
        ],
    )

    assert paper.is_retracted is True
    assert paper.has_correction is True
    assert paper.correction_notices[0].source_url == "https://europepmc.org/article/MED/123"
