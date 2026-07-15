from __future__ import annotations

import json
from pathlib import Path

from labs.blueprint_experiments.registry import (
    build_blueprint_registry,
    records_for_target,
    registry_payload,
    write_registry,
)


def test_blueprint_registry_indexes_valid_example_manifest() -> None:
    example = (
        Path(__file__).parents[1]
        / "labs"
        / "blueprint_experiments"
        / "examples"
        / "mock-htt-manifest.json"
    )

    records = build_blueprint_registry((example,))

    assert len(records) == 1
    record = records[0]
    assert record.valid is True
    assert record.experiment_id == "blueprint-mock-htt"
    assert record.status == "generated"
    assert record.provider_type == "mock"
    assert record.target_symbols == ("HTT",)
    assert record.artifact_type == "mock_structure_confidence"
    assert record.output_path == "outputs/blueprint-experiments/mock/htt/mock-confidence.json"
    assert record.model_provider == "mock"
    assert record.model_name == "deterministic-blueprint-fixture"
    assert record.requires_live_provider is False
    assert len(record.checksum) == 64


def test_blueprint_registry_records_invalid_manifest_without_crashing(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"schema_version": "wrong"}), encoding="utf-8")

    records = build_blueprint_registry((tmp_path,))

    assert len(records) == 1
    assert records[0].valid is False
    assert records[0].status == "invalid"
    assert records[0].provider_type == "unknown"
    assert "missing keys" in records[0].error


def test_registry_payload_counts_valid_and_invalid_records(tmp_path: Path) -> None:
    valid = (
        Path(__file__).parents[1]
        / "labs"
        / "blueprint_experiments"
        / "examples"
        / "mock-htt-manifest.json"
    )
    invalid = tmp_path / "invalid.json"
    invalid.write_text("not-json", encoding="utf-8")

    payload = registry_payload(build_blueprint_registry((valid, invalid)))

    assert payload["schema_version"] == "blueprint-manifest-registry.v1"
    assert payload["record_count"] == 2
    assert payload["valid_count"] == 1
    assert payload["invalid_count"] == 1
    assert "provenance only" in payload["safety"]["claim_boundary"]


def test_records_for_target_filters_case_insensitively() -> None:
    example_dir = (
        Path(__file__).parents[1]
        / "labs"
        / "blueprint_experiments"
        / "examples"
    )
    records = build_blueprint_registry((example_dir,))

    assert records_for_target(records, "htt") == records
    assert records_for_target(records, "BDNF") == ()


def test_write_registry_creates_stable_json_file(tmp_path: Path) -> None:
    example = (
        Path(__file__).parents[1]
        / "labs"
        / "blueprint_experiments"
        / "examples"
        / "mock-htt-manifest.json"
    )
    destination = tmp_path / "registry.json"

    write_registry(build_blueprint_registry((example,)), destination)

    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["record_count"] == 1
    assert payload["records"][0]["experiment_id"] == "blueprint-mock-htt"


def test_blueprint_registry_cli_indexes_examples() -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "index-manifests",
            "labs/blueprint_experiments/examples",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["record_count"] == 1
    assert payload["records"][0]["target_symbols"] == ["HTT"]
