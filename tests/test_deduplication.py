from hra.deduplication import deduplicate_papers
from hra.models import Paper


def test_deduplicate_papers_merges_by_pmid() -> None:
    europe_pmc = Paper(
        id="1",
        source_provider="Europe PMC",
        title="A Huntington biomarker study",
        pmid="123",
        citation_count=5,
        tags=["biomarkers"],
    )
    pubmed = Paper(
        id="pubmed:123",
        source_provider="PubMed",
        title="A Huntington biomarker study",
        pmid="123",
        doi="10.1000/example",
        tags=["genetics"],
    )

    papers = deduplicate_papers([europe_pmc, pubmed])

    assert len(papers) == 1
    assert papers[0].doi == "10.1000/example"
    assert papers[0].citation_count == 5
    assert papers[0].source_provider == "Europe PMC + PubMed"
    assert papers[0].tags == ["biomarkers", "genetics"]


def test_deduplicate_papers_merges_by_doi_url() -> None:
    papers = deduplicate_papers(
        [
            Paper(id="1", title="First", doi="10.1000/example"),
            Paper(id="2", title="Second", doi="https://doi.org/10.1000/example"),
        ]
    )

    assert len(papers) == 1


def test_deduplicate_papers_uses_title_and_year_fallback() -> None:
    papers = deduplicate_papers(
        [
            Paper(
                id="1",
                title="A long enough Huntington disease paper title",
                year=2026,
            ),
            Paper(
                id="2",
                title="A long enough Huntington disease paper title.",
                year=2026,
            ),
        ]
    )

    assert len(papers) == 1
