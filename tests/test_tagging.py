from hra.models import Paper
from hra.tagging import tag_paper, tag_text


def test_tag_text_finds_gene_silencing_and_clinical_trial_terms() -> None:
    tags = tag_text(
        "Huntingtin lowering with an antisense oligonucleotide",
        "A randomized placebo clinical trial in adults with Huntington disease.",
    )

    assert "gene silencing / HTT lowering" in tags
    assert "clinical trials" in tags


def test_tag_paper_returns_copy_with_tags() -> None:
    paper = Paper(
        id="1",
        title="Exercise and physiotherapy in Huntington disease",
        abstract="Rehabilitation and balance training were studied.",
    )

    tagged = tag_paper(paper)

    assert tagged is not paper
    assert "exercise / physiotherapy" in tagged.tags
    assert paper.tags == []
