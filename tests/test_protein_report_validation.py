from __future__ import annotations

import pytest

from labs.protein_intelligence.report_validation import (
    ReportValidationError,
    report_summary,
    validate_mapping_batch,
    validate_registry_payload,
    validate_target_report,
)


def _target_report() -> dict[str, object]:
    return {
        "schema_version": "protein-target-report.v1",
        "target": {
            "entity_id": "protein-huntingtin",
            "symbol": "HTT",
            "name": "huntingtin",
            "organism": "Homo sapiens",
            "identifiers": {"uniprot": "P42858"},
        },
        "literature": {
            "mapped_entity_count": 0,
            "mappings": [],
            "source_count": 0,
            "sources": [],
        },
        "lab_artifacts": {
            "manifest_count": 0,
            "manifests": [],
        },
        "interpretation": {
            "status": "no-local-provenance",
            "claim_boundary": "This report is provenance only and does not make biomedical claims.",
        },
    }


def test_validate_target_report_accepts_valid_report() -> None:
    validate_target_report(_target_report())


def test_report_summary_returns_review_friendly_shape() -> None:
    assert report_summary(_target_report()) == {
        "schema_version": "protein-target-report.v1",
        "symbol": "HTT",
        "mapped_entity_count": 0,
        "manifest_count": 0,
        "interpretation_status": "no-local-provenance",
    }


def test_validate_target_report_rejects_unknown_interpretation_status() -> None:
    report = _target_report()
    report["interpretation"]["status"] = "interesting-looking"

    with pytest.raises(ReportValidationError, match="Unknown interpretation status"):
        validate_target_report(report)


def test_validate_target_report_rejects_count_mismatch() -> None:
    report = _target_report()
    report["lab_artifacts"]["manifest_count"] = 1

    with pytest.raises(ReportValidationError, match="does not match"):
        validate_target_report(report)


def test_validate_mapping_batch_requires_claim_boundary() -> None:
    with pytest.raises(ReportValidationError, match="Claim boundary"):
        validate_mapping_batch(
            {
                "schema_version": "protein-entity-mapping-batch.v1",
                "input_count": 1,
                "mapping_count": 0,
                "mappings": [],
                "safety": {"claim_boundary": "Looks useful."},
            }
        )


def test_validate_registry_payload_accepts_empty_registry() -> None:
    validate_registry_payload(
        {
            "schema_version": "protein-manifest-registry.v1",
            "record_count": 0,
            "records": [],
            "safety": {
                "claim_boundary": "Registry output is provenance only, not biomedical claims.",
            },
        }
    )


def test_validate_registry_payload_rejects_wrong_schema() -> None:
    with pytest.raises(ReportValidationError, match="Expected schema_version"):
        validate_registry_payload({"schema_version": "wrong"})
