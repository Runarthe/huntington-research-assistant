from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

from labs.blueprint_experiments.manifests import (
    BlueprintManifestValidationError,
    manifest_summary,
    mock_blueprint_manifest,
    planned_blueprint_manifest,
    validate_blueprint_manifest,
)


def test_planned_blueprint_manifest_is_gated_and_claim_bounded() -> None:
    manifest = planned_blueprint_manifest(
        "HTT",
        provider_type="nvidia_nim",
        planned_at=date(2026, 7, 15),
    )

    validate_blueprint_manifest(manifest)

    assert manifest["status"] == "planned"
    assert manifest["provider_type"] == "nvidia_nim"
    assert manifest["runtime"]["requires_live_provider"] is True
    assert "not medical advice" in manifest["safety"]["claim_boundary"]
    assert "P42858" == manifest["inputs"][0]["identifiers"]["uniprot"]


def test_mock_blueprint_manifest_is_deterministic_and_offline() -> None:
    first = mock_blueprint_manifest("HTT", generated_at=date(2026, 7, 15), points=4)
    second = mock_blueprint_manifest("HTT", generated_at=date(2026, 7, 15), points=4)

    validate_blueprint_manifest(first)

    values = first["outputs"]["confidence_measures"][0]["values"]
    assert first == second
    assert first["provider_type"] == "mock"
    assert first["runtime"]["requires_live_provider"] is False
    assert len(values) == 4
    assert "not pLDDT" in first["evaluation"]["limitations"][0]


def test_blueprint_manifest_validation_rejects_missing_safety() -> None:
    manifest = mock_blueprint_manifest("BDNF", generated_at=date(2026, 7, 15))
    del manifest["safety"]

    with pytest.raises(BlueprintManifestValidationError, match="safety"):
        validate_blueprint_manifest(manifest)


def test_manifest_summary_reports_compact_fields() -> None:
    manifest = mock_blueprint_manifest("NEFL", generated_at=date(2026, 7, 15), points=2)

    assert manifest_summary(manifest) == {
        "schema_version": "blueprint-experiment-manifest.v1",
        "experiment_id": "blueprint-mock-nefl",
        "status": "generated",
        "provider_type": "mock",
        "input_count": 1,
        "artifact_type": "mock_structure_confidence",
    }


def test_example_manifest_is_valid() -> None:
    path = (
        Path(__file__).parents[1]
        / "labs"
        / "blueprint_experiments"
        / "examples"
        / "mock-htt-manifest.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    validate_blueprint_manifest(payload)
    assert payload["experiment_id"] == "blueprint-mock-htt"


def test_blueprint_cli_plan_and_validate(tmp_path: Path) -> None:
    plan_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "plan",
            "HTT",
            "--provider-type",
            "bionemo",
            "--date",
            "2026-07-15",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    manifest_path = tmp_path / "planned.json"
    manifest_path.write_text(plan_result.stdout, encoding="utf-8")

    validate_result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "validate-manifest",
            str(manifest_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    summary = json.loads(validate_result.stdout)
    assert summary["provider_type"] == "bionemo"
    assert summary["status"] == "planned"


def test_blueprint_cli_run_mock() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "run-mock",
            "HTT",
            "--date",
            "2026-07-15",
            "--points",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    validate_blueprint_manifest(payload)
    assert payload["outputs"]["confidence_measures"][0]["values"] == [
        0.467647,
        0.669608,
        0.732353,
    ]


def test_blueprint_cli_describe_provider() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "describe-provider",
            "nvidia_nim",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["provider_type"] == "nvidia_nim"
    assert payload["implemented"] is False
    assert payload["live_enabled"] is False


def test_blueprint_cli_provider_config_skeleton() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "provider-config",
            "bionemo",
            "--execution-mode",
            "planned",
            "--credentials-env-var",
            "BIONEMO_API_KEY",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["provider_type"] == "bionemo"
    assert payload["execution_mode"] == "planned"
    assert payload["credentials_env_var"] == "BIONEMO_API_KEY"


def test_blueprint_cli_rejects_unreviewed_live_config() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "labs.blueprint_experiments",
            "provider-config",
            "bionemo",
            "--execution-mode",
            "live",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "requires an explicit reviewed config" in result.stderr
