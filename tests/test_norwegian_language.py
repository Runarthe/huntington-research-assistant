import json
from pathlib import Path

import pytest

from hra.norwegian_language import (
    SummaryIntegrityError,
    glossary_for_text,
    protect_glossary_for_translation,
    protect_identifiers_for_translation,
    restore_identifier_placeholders,
    validate_facts_against_source,
    validate_norwegian_summary,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "norwegian_summary_cases.json"


def test_curated_norwegian_evaluation_cases_pass_integrity_checks() -> None:
    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    for case in cases:
        validate_facts_against_source(case["facts"], case["source"])
        validate_norwegian_summary(
            case["facts"],
            case["summary"],
            case["source"],
        )


def test_fact_validation_rejects_an_invented_number() -> None:
    facts = {
        "studied": "The study included 80 people.",
        "found": "Not stated in the abstract.",
        "importance": "The study describes a cohort.",
        "limitations": "Not stated in the abstract.",
    }

    with pytest.raises(SummaryIntegrityError):
        validate_facts_against_source(facts, "The study included 40 people.")


def test_fact_validation_rejects_a_paraphrase_without_new_numbers() -> None:
    facts = {
        "studied": "The researchers investigated the HTT gene.",
        "found": "Not stated in the abstract.",
        "importance": "Not stated in the abstract.",
        "limitations": "Not stated in the abstract.",
    }

    with pytest.raises(SummaryIntegrityError):
        validate_facts_against_source(facts, "The study characterized HTT regulation.")


def test_render_validation_rejects_changed_identifier_case() -> None:
    facts = {
        "studied": "The study examined mHTT.",
        "found": "No numerical result was stated.",
        "importance": "The study examined a protein.",
        "limitations": "The abstract was limited.",
    }
    summary = (
        "## Hva undersøkte de?\nmhtt ble undersøkt.\n"
        "## Hva fant de?\nIngen tall ble oppgitt.\n"
        "## Hvorfor er det viktig?\nStudien undersøkte et protein.\n"
        "## Begrensninger og usikkerhet\nAbstraktet var begrenset."
    )

    with pytest.raises(SummaryIntegrityError):
        validate_norwegian_summary(facts, summary, "The study examined mHTT.")


def test_render_validation_rejects_personalized_advice() -> None:
    facts = {
        "studied": "The study examined exercise.",
        "found": "No outcome was stated.",
        "importance": "The study assessed feasibility.",
        "limitations": "The abstract was limited.",
    }
    summary = (
        "## Hva undersøkte de?\nStudien undersøkte trening.\n"
        "## Hva fant de?\nIngen utfall ble oppgitt.\n"
        "## Hvorfor er det viktig?\nDu bør trene mer.\n"
        "## Begrensninger og usikkerhet\nAbstraktet var begrenset."
    )

    with pytest.raises(SummaryIntegrityError):
        validate_norwegian_summary(facts, summary, "The study examined exercise.")


def test_render_validation_rejects_ht_t_as_the_disease_cause() -> None:
    facts = {
        "studied": "The study targeted HTT.",
        "found": "Not stated in the abstract.",
        "importance": "Not stated in the abstract.",
        "limitations": "Not stated in the abstract.",
    }
    summary = (
        "HTT, den genetiske årsaken til sykdommen, ble undersøkt. "
        "Hva fant de? Ikke oppgitt. Hvorfor er det viktig? Ikke oppgitt. "
        "Begrensninger og usikkerhet: Ikke oppgitt."
    )

    with pytest.raises(SummaryIntegrityError):
        validate_norwegian_summary(facts, summary, "The study targeted HTT.")


def test_glossary_returns_only_terms_present_in_source() -> None:
    glossary = glossary_for_text("Gene silencing reduced mutant huntingtin.")

    assert glossary["gene silencing"] == "gendemping"
    assert "mutant huntingtin" in glossary
    assert "placebo-controlled" not in glossary


def test_scientific_identifiers_are_protected_during_translation() -> None:
    facts = {
        "studied": "CRISPR-Cas9 targeted HTT.",
        "found": "ASOs reduced HTT expression.",
        "importance": "Not stated in the abstract.",
        "limitations": "Not stated in the abstract.",
    }

    protected, replacements = protect_identifiers_for_translation(facts)
    restored = restore_identifier_placeholders(protected, replacements)

    assert "CRISPR" not in "\n".join(protected.values())
    assert "Cas9" not in "\n".join(protected.values())
    assert restored == facts


def test_mutated_identifier_placeholder_is_rejected() -> None:
    sections = {
        "studied": "Modellen skrev __HRA_TERM_9__.",
        "found": "Ikke oppgitt.",
        "importance": "Ikke oppgitt.",
        "limitations": "Ikke oppgitt.",
    }

    with pytest.raises(SummaryIntegrityError):
        restore_identifier_placeholders(sections, {"__HRA_TERM_0__": "HTT"})


def test_curated_phrases_are_fixed_before_model_translation() -> None:
    facts = {
        "studied": "The review covered pre-clinical animal models.",
        "found": "It discussed molecular pathways and drug targets.",
        "importance": "Not stated in the abstract.",
        "limitations": "Not stated in the abstract.",
    }
    glossary = glossary_for_text("\n".join(facts.values()))

    protected, replacements = protect_glossary_for_translation(facts, glossary)
    restored = restore_identifier_placeholders(protected, replacements)

    combined = "\n".join(restored.values())
    assert "prekliniske dyremodeller" in combined
    assert "molekylære signalveier" in combined
    assert "målmolekyler for legemiddelutvikling" in combined
