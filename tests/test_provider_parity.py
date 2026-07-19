from datetime import date

from labs.protein_intelligence import (
    LocalESM2Config,
    PROTEIN_TARGETS,
    build_provider_parity_report,
    fixture_sequence_record,
    normalize_embedding_manifest,
    planned_bionemo_esm2_manifest,
    planned_local_esm2_manifest,
    validate_manifest,
)


def _plans() -> tuple[dict[str, object], dict[str, object]]:
    record = fixture_sequence_record(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 19))
    config = LocalESM2Config(window_start=2, window_length=8, device="cpu")
    return (
        planned_local_esm2_manifest(record, config, planned_at=date(2026, 7, 19)),
        planned_bionemo_esm2_manifest(record, config, planned_at=date(2026, 7, 19)),
    )


def test_bionemo_plan_reuses_exact_local_sequence_selection() -> None:
    local_plan, bionemo_plan = _plans()

    validate_manifest(bionemo_plan)
    assert bionemo_plan["status"] == "planned"
    assert bionemo_plan["inputs"] == local_plan["inputs"]
    assert bionemo_plan["runtime"]["parameters"]["silent_truncation"] is False
    assert bionemo_plan["runtime"]["parameters"]["include_embeddings"] is True
    assert "not asserted" in bionemo_plan["evaluation"]["limitations"][1]


def test_normalized_contract_exposes_only_provenance_fields() -> None:
    local_plan, _ = _plans()

    descriptor = normalize_embedding_manifest(local_plan)

    assert descriptor.schema_version == "protein-embedding-artifact.v1"
    assert descriptor.input.window_start == 2
    assert descriptor.input.window_end == 9
    assert descriptor.preprocessing.silent_truncation is False
    assert descriptor.output.vector_checksum is None
    assert "vector" not in descriptor.model_dump(mode="json")["output"]


def test_planned_provider_report_separates_matches_from_unknowns() -> None:
    local_plan, bionemo_plan = _plans()

    report = build_provider_parity_report(
        local_plan,
        bionemo_plan,
        generated_at=date(2026, 7, 19),
    )
    checks = {check.field: check for check in report.checks}

    assert report.overall_status == "input-compatible-plan-only"
    assert report.readiness["input_contract_ready"] is True
    assert report.readiness["candidate_provider_executed"] is False
    assert checks["selected_sequence_checksum"].status == "matched"
    assert checks["sequence_window"].status == "matched"
    assert checks["model_identity"].status == "different"
    assert checks["checkpoint_weight_identity"].status == "not-comparable"
    assert checks["embedding_dimensions"].status == "not-available"
    assert checks["vector_checksum"].status == "not-available"


def test_changed_candidate_input_fails_the_input_contract() -> None:
    local_plan, bionemo_plan = _plans()
    bionemo_plan["inputs"][0]["selected_sequence_checksum"] = "sha256:different"

    report = build_provider_parity_report(local_plan, bionemo_plan)

    assert report.overall_status == "review-required"
    assert report.readiness["input_contract_ready"] is False
