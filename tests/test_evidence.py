import csv
import io

from hra.evidence import (
    evidence_profiles_to_csv,
    extract_evidence_profile,
)
from hra.models import CorrectionNotice, Paper


def test_evidence_profile_detects_design_contexts_and_exact_passages() -> None:
    paper = Paper(
        id="trial-1",
        source_provider="PubMed",
        title="A randomized controlled trial in Huntington disease",
        publication_types=["Randomized Controlled Trial", "Journal Article"],
        abstract=(
            "We enrolled 40 participants in a randomized controlled trial. "
            "Results: We found that the measured biomarker changed after 12 weeks. "
            "The study was limited by a small sample and further research is needed."
        ),
        source_url="https://pubmed.ncbi.nlm.nih.gov/123/",
    )

    profile = extract_evidence_profile(paper)

    assert profile.study_design == "randomized_controlled_trial"
    assert profile.research_contexts == ["human_participants"]
    assert profile.outcome_passages == [
        "Results: We found that the measured biomarker changed after 12 weeks."
    ]
    assert profile.limitation_passages == [
        "The study was limited by a small sample and further research is needed."
    ]
    assert profile.source_url == "https://pubmed.ncbi.nlm.nih.gov/123/"


def test_evidence_profile_does_not_invent_missing_passages() -> None:
    paper = Paper(
        id="review-1",
        title="Review of Huntington disease models",
        publication_types=["Review"],
        abstract="This review discusses mouse models and patient-derived cell lines.",
        correction_notices=[CorrectionNotice(notice_type="Erratum in")],
    )

    profile = extract_evidence_profile(paper)

    assert profile.study_design == "review"
    assert profile.research_contexts == ["human_participants", "animal_model", "cell_or_tissue_model"]
    assert profile.outcome_passages == []
    assert profile.limitation_passages == []
    assert profile.has_correction is True


def test_review_metadata_wins_over_clinical_trial_mentions() -> None:
    paper = Paper(
        id="review-2",
        title="Review of emerging Huntington interventions",
        publication_types=["Review", "Journal Article"],
        abstract="This review discusses several ongoing clinical trials.",
    )

    assert extract_evidence_profile(paper).study_design == "review"


def test_evidence_profile_classifies_preclinical_work() -> None:
    paper = Paper(
        id="model-1",
        title="Huntingtin knockdown in mice",
        publication_types=["Journal Article"],
        abstract="We observed lower aggregate burden in mice and cultured neuronal cells.",
    )

    profile = extract_evidence_profile(paper)

    assert profile.study_design == "preclinical_study"
    assert profile.research_contexts == ["animal_model", "cell_or_tissue_model"]


def test_evidence_profile_keeps_unclassified_human_work_neutral() -> None:
    paper = Paper(
        id="human-1",
        title="DNA methylation in Huntington disease brain tissue",
        publication_types=["Journal Article"],
        abstract="We profiled samples from 20 Huntington disease and 22 control donors.",
    )

    profile = extract_evidence_profile(paper)

    assert profile.study_design == "human_study"
    assert profile.research_contexts == ["human_participants"]


def test_background_patient_mention_does_not_create_human_study_context() -> None:
    paper = Paper(
        id="mouse-1",
        title="Mutant huntingtin in BACHD mice",
        publication_types=["Journal Article"],
        abstract=(
            "Patients with Huntington disease have motor and cognitive changes. "
            "We reduced mutant huntingtin expression in BACHD mice."
        ),
    )

    profile = extract_evidence_profile(paper)

    assert profile.study_design == "preclinical_study"
    assert profile.research_contexts == ["animal_model"]


def test_molecular_experiment_is_used_as_a_conservative_fallback() -> None:
    paper = Paper(
        id="lab-1",
        title="Silencing of human HTT by CRISPR/dCas9 epigenetic editing",
        publication_types=["Journal Article"],
        abstract="We targeted DNA methylation at the HTT locus and observed gene silencing.",
    )

    profile = extract_evidence_profile(paper)

    assert profile.study_design == "laboratory_study"
    assert profile.research_contexts == ["molecular_experiment"]


def test_evidence_csv_preserves_sources_and_passages() -> None:
    profile = extract_evidence_profile(
        Paper(
            id="p1",
            title="Biomarker study",
            abstract="We found a measurable association.",
            source_url="https://europepmc.org/article/MED/1",
        )
    )

    rows = list(csv.DictReader(io.StringIO(evidence_profiles_to_csv([profile]))))

    assert rows[0]["source_url"] == "https://europepmc.org/article/MED/1"
    assert rows[0]["outcome_passages"] == "We found a measurable association."
