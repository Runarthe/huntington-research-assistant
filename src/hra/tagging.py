from __future__ import annotations

from collections.abc import Iterable

from hra.models import Paper

TAG_KEYWORDS: dict[str, tuple[str, ...]] = {
    "gene silencing / HTT lowering": (
        "gene silencing",
        "htt lowering",
        "huntingtin lowering",
        "antisense oligonucleotide",
        "aso",
        "rna interference",
        "rnai",
        "sirna",
        "allele selective",
    ),
    "biomarkers": (
        "biomarker",
        "neurofilament",
        "nfl",
        "csf",
        "cerebrospinal",
        "imaging marker",
        "plasma",
    ),
    "clinical trials": (
        "clinical trial",
        "phase 1",
        "phase i",
        "phase 2",
        "phase ii",
        "phase 3",
        "phase iii",
        "randomized",
        "placebo",
    ),
    "neurodegeneration": (
        "neurodegeneration",
        "neuronal loss",
        "striatal",
        "cortex",
        "brain atrophy",
        "mitochondrial",
    ),
    "genetics": (
        "genetic",
        "cag repeat",
        "mutation",
        "inheritance",
        "genotype",
        "polyglutamine",
    ),
    "symptoms / care": (
        "symptom",
        "motor",
        "chorea",
        "caregiver",
        "quality of life",
        "palliative",
        "swallowing",
    ),
    "exercise / physiotherapy": (
        "exercise",
        "physiotherapy",
        "physical therapy",
        "rehabilitation",
        "aerobic",
        "balance training",
    ),
    "mental health": (
        "depression",
        "anxiety",
        "psychiatric",
        "suicide",
        "apathy",
        "irritability",
        "cognitive behavioral",
    ),
    "animal models": (
        "mouse model",
        "murine",
        "transgenic mice",
        "rat model",
        "animal model",
        "zebrafish",
        "drosophila",
    ),
}


def tag_text(title: str | None, abstract: str | None) -> list[str]:
    """Assign simple rule-based tags from title and abstract text."""

    haystack = f"{title or ''} {abstract or ''}".lower()
    tags = [
        tag
        for tag, keywords in TAG_KEYWORDS.items()
        if any(keyword in haystack for keyword in keywords)
    ]
    return tags


def tag_paper(paper: Paper) -> Paper:
    """Return a copy of a paper with rule-based tags attached."""

    return paper.model_copy(update={"tags": tag_text(paper.title, paper.abstract)})


def tag_papers(papers: Iterable[Paper]) -> list[Paper]:
    return [tag_paper(paper) for paper in papers]
