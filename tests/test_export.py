import csv
from io import StringIO

from hra.export import (
    paper_text_filename,
    paper_to_text,
    papers_to_bibtex,
    papers_to_csv,
    trials_to_csv,
)
from hra.models import Author, ClinicalTrial, Paper


def test_csv_export_contains_source_and_publication_types() -> None:
    paper = Paper(
        id="1",
        title="A study",
        authors=[Author(full_name="Ada Example")],
        publication_types=["Journal Article", "Review"],
        source_url="https://europepmc.org/article/MED/1",
    )

    rows = list(csv.DictReader(StringIO(papers_to_csv([paper]))))

    assert rows[0]["title"] == "A study"
    assert rows[0]["publication_types"] == "Journal Article; Review"
    assert rows[0]["source_url"].endswith("/MED/1")


def test_bibtex_export_includes_source_url() -> None:
    paper = Paper(
        id="1",
        title="A study",
        year=2025,
        authors=[Author(full_name="Ada Example")],
        source_url="https://europepmc.org/article/MED/1",
    )

    result = papers_to_bibtex([paper])

    assert "@article{Example20251" in result
    assert "url = {https://europepmc.org/article/MED/1}" in result


def test_trial_csv_export_includes_registry_source() -> None:
    trial = ClinicalTrial(
        nct_id="NCT12345678",
        brief_title="Study",
        overall_status="RECRUITING",
        source_url="https://clinicaltrials.gov/study/NCT12345678",
    )

    rows = list(csv.DictReader(StringIO(trials_to_csv([trial]))))

    assert rows[0]["nct_id"] == "NCT12345678"
    assert rows[0]["source_url"].endswith("/NCT12345678")


def test_single_paper_text_export_includes_abstract_and_sources() -> None:
    paper = Paper(
        id="MED/1",
        title="A study",
        pmid="12345",
        abstract="The study abstract.",
        source_url="https://europepmc.org/article/MED/12345",
        open_access_pdf_url="https://europepmc.org/articles/PMC1?pdf=render",
    )

    result = paper_to_text(paper)

    assert "The study abstract." in result
    assert "Source: https://europepmc.org/article/MED/12345" in result
    assert "Open-access PDF:" in result
    assert paper_text_filename(paper) == "hra-paper-12345.txt"
