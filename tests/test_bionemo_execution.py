import io
import hashlib
import json
import zipfile
from datetime import date

import pytest

from labs.protein_intelligence import (
    BIONEMO_BUNDLE_VERSION,
    BIONEMO_CONTAINER_REFERENCE,
    BIONEMO_RESULT_VERSION,
    BioNeMoExecutionError,
    LocalESM2Config,
    PROTEIN_TARGETS,
    build_bionemo_execution_bundle,
    build_provider_parity_report,
    fixture_bionemo_result_manifest,
    fixture_sequence_record,
    load_bionemo_result_manifest,
    planned_bionemo_esm2_manifest,
    planned_bionemo_recipes_esm2_manifest,
    planned_local_esm2_manifest,
    validate_bionemo_execution_bundle,
)


def _inputs() -> tuple[object, LocalESM2Config, dict[str, object]]:
    record = fixture_sequence_record(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 19))
    config = LocalESM2Config(window_start=2, window_length=8, device="cpu")
    plan = planned_bionemo_esm2_manifest(record, config, planned_at=date(2026, 7, 19))
    return record, config, plan


def test_execution_bundle_is_deterministic_and_self_validating() -> None:
    record, config, _ = _inputs()

    first = build_bionemo_execution_bundle(
        record,
        config,
        planned_at=date(2026, 7, 19),
    )
    second = build_bionemo_execution_bundle(
        record,
        config,
        planned_at=date(2026, 7, 19),
    )
    manifest = validate_bionemo_execution_bundle(first)

    assert first == second
    assert manifest["schema_version"] == BIONEMO_BUNDLE_VERSION
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        assert archive.read("input.csv") == b"sequences\nATLEKLMK\n"
        run_script = archive.getinfo("run_container.sh")
        assert (run_script.external_attr >> 16) & 0o111
        run_script_content = archive.read("run_container.sh")
        assert b"--pull never" in run_script_content
        assert b'!= "${EXPECTED_BIONEMO_IMAGE}"' in run_script_content
        assert b"\r\n" not in run_script_content
        inside_script = archive.read("run_inside_container.sh")
        assert b"infer_esm2" in inside_script
        assert b"results/ is not empty" in inside_script
        assert b"rm -rf" not in inside_script
        execution = json.loads(archive.read("execution.json"))
        assert execution["security"]["contains_credentials"] is False
        assert execution["security"]["image_pull_policy"] == "never"
        assert (
            execution["container_review"]["immutable_reference"]
            == BIONEMO_CONTAINER_REFERENCE
        )
        assert execution["settings"]["checkpoint_tag"] == "esm2/650m:2.0"


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("tag", "moving-tag"),
        ("digest", "sha256:" + "0" * 64),
        (
            "immutable_reference",
            "nvcr.io/nvidia/clara/bionemo-framework@sha256:" + "0" * 64,
        ),
        ("status", "not-reviewed"),
    ),
)
def test_execution_bundle_rejects_changed_container_review(
    field: str,
    value: str,
) -> None:
    record, config, _ = _inputs()
    original = build_bionemo_execution_bundle(record, config)
    with zipfile.ZipFile(io.BytesIO(original)) as source:
        contents = {name: source.read(name) for name in source.namelist()}
    execution = json.loads(contents["execution.json"])
    execution["container_review"][field] = value
    contents["execution.json"] = json.dumps(execution, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    bundle_manifest = json.loads(contents["bundle-manifest.json"])
    bundle_manifest["files"]["execution.json"] = (
        "sha256:" + hashlib.sha256(contents["execution.json"]).hexdigest()
    )
    contents["bundle-manifest.json"] = json.dumps(bundle_manifest).encode("utf-8")
    rewritten = io.BytesIO()
    with zipfile.ZipFile(rewritten, "w") as output:
        for name, content in contents.items():
            output.writestr(name, content)

    with pytest.raises(BioNeMoExecutionError):
        validate_bionemo_execution_bundle(rewritten.getvalue())


def test_invalid_execution_archive_is_rejected() -> None:
    with pytest.raises(BioNeMoExecutionError, match="valid archive"):
        validate_bionemo_execution_bundle(b"not a zip")


def test_rechecksummed_input_tampering_still_fails_semantic_validation() -> None:
    record, config, _ = _inputs()
    original = build_bionemo_execution_bundle(record, config)
    with zipfile.ZipFile(io.BytesIO(original)) as source:
        contents = {name: source.read(name) for name in source.namelist()}
    contents["input.csv"] = b"sequences\nAAAAAAAA\n"
    bundle_manifest = json.loads(contents["bundle-manifest.json"])
    bundle_manifest["files"]["input.csv"] = (
        "sha256:" + hashlib.sha256(contents["input.csv"]).hexdigest()
    )
    contents["bundle-manifest.json"] = json.dumps(bundle_manifest).encode("utf-8")
    rewritten = io.BytesIO()
    with zipfile.ZipFile(rewritten, "w") as output:
        for name, content in contents.items():
            output.writestr(name, content)

    with pytest.raises(BioNeMoExecutionError, match="does not match its plan"):
        validate_bionemo_execution_bundle(rewritten.getvalue())


def test_fixture_result_exercises_import_contract_without_provider_claim() -> None:
    _, _, plan = _inputs()

    fixture = fixture_bionemo_result_manifest(plan, generated_at=date(2026, 7, 19))
    loaded = load_bionemo_result_manifest(
        json.dumps(fixture).encode("utf-8"),
        plan,
    )

    assert loaded["schema_version"] == BIONEMO_RESULT_VERSION
    assert loaded["runtime"]["interface"] == "fixture-validation"
    assert loaded["outputs"]["embedding"]["dimensions"] == 4
    assert "vector" not in loaded["outputs"]["embedding"]
    assert "No BioNeMo model" in loaded["evaluation"]["limitations"][0]


def test_import_rejects_result_for_another_sequence() -> None:
    _, _, plan = _inputs()
    fixture = fixture_bionemo_result_manifest(plan)
    fixture["inputs"][0]["selected_sequence_checksum"] = "sha256:different"

    with pytest.raises(BioNeMoExecutionError, match="sequence provenance"):
        load_bionemo_result_manifest(json.dumps(fixture).encode("utf-8"), plan)


def test_import_rejects_full_vector_payload() -> None:
    _, _, plan = _inputs()
    fixture = fixture_bionemo_result_manifest(plan)
    fixture["outputs"]["embedding"]["vector"] = [0.1]

    with pytest.raises(BioNeMoExecutionError, match="not the full embedding"):
        load_bionemo_result_manifest(json.dumps(fixture).encode("utf-8"), plan)


def test_generated_result_requires_immutable_container_provenance() -> None:
    _, _, plan = _inputs()
    result = fixture_bionemo_result_manifest(plan)
    result["runtime"]["interface"] = "bionemo-framework-container"
    result["runtime"]["container"] = "moving-tag:latest"

    with pytest.raises(BioNeMoExecutionError, match="immutable container digest"):
        load_bionemo_result_manifest(json.dumps(result).encode("utf-8"), plan)


def test_generated_result_rejects_incomplete_container_digest() -> None:
    _, _, plan = _inputs()
    result = fixture_bionemo_result_manifest(plan)
    result["runtime"]["interface"] = "bionemo-framework-container"
    result["runtime"]["container"] = "nvcr.io/example@sha256:not-a-digest"

    with pytest.raises(BioNeMoExecutionError, match="immutable container digest"):
        load_bionemo_result_manifest(json.dumps(result).encode("utf-8"), plan)


def test_recipes_result_accepts_only_exact_plan_and_immutable_container() -> None:
    record, config, _ = _inputs()
    plan = planned_bionemo_recipes_esm2_manifest(
        record,
        config,
        planned_at=date(2026, 7, 19),
    )
    result = fixture_bionemo_result_manifest(plan)
    result["runtime"]["interface"] = "bionemo-recipes-container"
    result["runtime"]["container"] = "local/hra-bionemo-recipes@sha256:" + "a" * 64

    loaded = load_bionemo_result_manifest(json.dumps(result).encode("utf-8"), plan)
    assert loaded["runtime"]["interface"] == "bionemo-recipes-container"

    result["runtime"]["container"] = "hra-bionemo-recipes:latest"
    with pytest.raises(BioNeMoExecutionError, match="immutable container digest"):
        load_bionemo_result_manifest(json.dumps(result).encode("utf-8"), plan)


def test_fixture_parity_is_not_reported_as_live_execution() -> None:
    record, config, plan = _inputs()
    local_plan = planned_local_esm2_manifest(
        record,
        config,
        planned_at=date(2026, 7, 19),
    )
    fixture = fixture_bionemo_result_manifest(plan, generated_at=date(2026, 7, 19))

    report = build_provider_parity_report(local_plan, fixture)
    checks = {check.field: check.status for check in report.checks}

    assert report.overall_status == "input-compatible-fixture"
    assert report.readiness["candidate_fixture_validated"] is True
    assert report.readiness["candidate_provider_executed"] is False
    assert report.readiness["output_comparison_available"] is False
    assert checks["embedding_dimensions"] == "not-available"
    assert checks["vector_checksum"] == "not-available"
