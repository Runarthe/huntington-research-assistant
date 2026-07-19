from __future__ import annotations

import hashlib
import io
import json
import zipfile
from datetime import date, datetime, timezone
from typing import Sequence

import pytest

from labs.protein_intelligence import (
    BIONEMO_RECIPES_BASE_REFERENCE,
    BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES,
    BIONEMO_RECIPES_READINESS_VERSION,
    CommandResult,
    LocalESM2Config,
    build_bionemo_recipes_execution_bundle,
    fixture_sequence_record,
    get_protein_target,
    inspect_bionemo_recipes_readiness,
)
from labs.protein_intelligence.bionemo_recipes_execution import (
    BioNeMoRuntimeArtifact,
)
from labs.protein_intelligence import bionemo_recipes_readiness as readiness
from labs.protein_intelligence import __main__ as protein_cli


CHECKED_AT = datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc)
GPU_COMMAND = (
    "nvidia-smi",
    "--query-gpu=name,driver_version,compute_cap,memory.total",
    "--format=csv,noheader",
)
DOCKER_VERSION_COMMAND = ("docker", "version", "--format", "{{json .}}")
DOCKER_INFO_COMMAND = (
    "docker",
    "info",
    "--format",
    "{{range $name, $runtime := .Runtimes}}{{$name}}{{println}}{{end}}",
)
CONTEXT_COMMAND = (
    "docker",
    "context",
    "inspect",
    "--format",
    "{{json .Endpoints.docker.Host}}",
)
IMAGE_COMMAND = (
    "docker",
    "image",
    "inspect",
    BIONEMO_RECIPES_BASE_REFERENCE,
    "--format",
    "{{.Id}}|{{.Os}}|{{.Architecture}}|{{json .RepoDigests}}",
)


class FakeRunner:
    def __init__(self, responses: dict[tuple[str, ...], CommandResult]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, command: Sequence[str]) -> CommandResult:
        key = tuple(command)
        self.calls.append(key)
        return self.responses.get(key, CommandResult(available=False))


def _bundle() -> bytes:
    record = fixture_sequence_record(
        get_protein_target("HTT"),
        retrieved_at=date(2026, 7, 20),
    )
    return build_bionemo_recipes_execution_bundle(
        record,
        LocalESM2Config(max_residues=BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES),
        planned_at=date(2026, 7, 20),
    )


def _healthy_runner(*, image_local: bool = True) -> FakeRunner:
    responses = {
        GPU_COMMAND: CommandResult(
            returncode=0,
            stdout="NVIDIA A100, 591.86, 8.0, 40960 MiB",
        ),
        DOCKER_VERSION_COMMAND: CommandResult(
            returncode=0,
            stdout=json.dumps(
                {
                    "Client": {"Version": "29.1.3", "Os": "linux"},
                    "Server": {"Version": "29.1.3", "Os": "linux"},
                }
            ),
        ),
        DOCKER_INFO_COMMAND: CommandResult(
            returncode=0,
            stdout="io.containerd.runc.v2\nnvidia\nrunc",
        ),
        CONTEXT_COMMAND: CommandResult(
            returncode=0,
            stdout=json.dumps("unix:///var/run/docker.sock"),
        ),
    }
    if image_local:
        responses[IMAGE_COMMAND] = CommandResult(
            returncode=0,
            stdout=(
                "sha256:"
                + "b" * 64
                + "|linux|amd64|"
                + json.dumps([BIONEMO_RECIPES_BASE_REFERENCE])
            ),
        )
    return FakeRunner(responses)


def _checks(report: object) -> dict[str, object]:
    return {check.check_id: check for check in report.checks}


def test_readiness_requires_terms_base_and_artifacts() -> None:
    runner = _healthy_runner(image_local=False)
    report = inspect_bionemo_recipes_readiness(
        _bundle(),
        runner=runner,
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )
    checks = _checks(report)

    assert report.schema_version == BIONEMO_RECIPES_READINESS_VERSION
    assert report.status == "review-required"
    assert checks["fixture_bundle"].status == "passed"
    assert checks["terms_review"].status == "review-required"
    assert checks["exact_base_image"].status == "review-required"
    assert checks["locked_artifacts"].status == "review-required"
    assert report.network_calls_made is False
    assert report.image_pulled is False
    assert report.container_started is False
    assert report.model_imported is False
    assert report.model_executed is False


def test_readiness_rejects_remote_docker_before_image_inspection() -> None:
    runner = _healthy_runner()
    runner.responses[CONTEXT_COMMAND] = CommandResult(
        returncode=0,
        stdout=json.dumps("tcp://example.invalid:2376"),
    )

    report = inspect_bionemo_recipes_readiness(
        _bundle(),
        runner=runner,
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )

    assert report.status == "blocked"
    assert _checks(report)["local_docker_endpoint"].status == "blocked"
    assert IMAGE_COMMAND not in runner.calls


def test_readiness_rejects_tampered_bundle() -> None:
    original = _bundle()
    with zipfile.ZipFile(io.BytesIO(original)) as source:
        contents = {name: source.read(name) for name in source.namelist()}
    contents["fixture.json"] += b" "
    rewritten = io.BytesIO()
    with zipfile.ZipFile(rewritten, "w") as output:
        for name, content in contents.items():
            output.writestr(name, content)

    report = inspect_bionemo_recipes_readiness(
        rewritten.getvalue(),
        runner=_healthy_runner(),
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )

    assert report.status == "blocked"
    assert _checks(report)["fixture_bundle"].status == "blocked"


def test_artifact_directory_verifies_exact_files_without_import(
    tmp_path, monkeypatch
) -> None:
    model_content = b"reviewed model file"
    wheel_content = b"reviewed wheel file"
    model_artifact = BioNeMoRuntimeArtifact(
        filename="model.bin",
        size_bytes=len(model_content),
        sha256=hashlib.sha256(model_content).hexdigest(),
    )
    wheel_artifact = BioNeMoRuntimeArtifact(
        filename="runtime.whl",
        size_bytes=len(wheel_content),
        sha256=hashlib.sha256(wheel_content).hexdigest(),
        package="runtime",
        version="1.0",
    )
    monkeypatch.setattr(readiness, "MODEL_ARTIFACTS", (model_artifact,))
    monkeypatch.setattr(readiness, "RUNTIME_WHEELS", (wheel_artifact,))
    (tmp_path / "model").mkdir()
    (tmp_path / "wheelhouse").mkdir()
    (tmp_path / "model" / model_artifact.filename).write_bytes(model_content)
    (tmp_path / "wheelhouse" / wheel_artifact.filename).write_bytes(wheel_content)

    facts = readiness.verify_bionemo_recipes_artifact_directory(tmp_path)

    assert facts == {
        "model_file_count": 1,
        "model_bytes": len(model_content),
        "wheel_file_count": 1,
        "wheel_bytes": len(wheel_content),
    }


def test_artifact_directory_rejects_linked_subdirectory(tmp_path, monkeypatch) -> None:
    content = b"locked"
    artifact = BioNeMoRuntimeArtifact(
        filename="locked.bin",
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
    )
    monkeypatch.setattr(readiness, "MODEL_ARTIFACTS", (artifact,))
    monkeypatch.setattr(readiness, "RUNTIME_WHEELS", ())
    actual_model_directory = tmp_path / "actual-model"
    actual_model_directory.mkdir()
    (actual_model_directory / artifact.filename).write_bytes(content)
    try:
        (tmp_path / "model").symlink_to(
            actual_model_directory, target_is_directory=True
        )
    except OSError as exc:
        pytest.skip(f"Directory symlinks are unavailable: {exc}")
    (tmp_path / "wheelhouse").mkdir()

    with pytest.raises(
        readiness.BioNeMoRecipesExecutionError, match="non-linked directory"
    ):
        readiness.verify_bionemo_recipes_artifact_directory(tmp_path)


def test_artifact_directory_rejects_wheel_size_mismatch(tmp_path, monkeypatch) -> None:
    expected = b"locked"
    wheel = BioNeMoRuntimeArtifact(
        filename="runtime.whl",
        size_bytes=len(expected),
        sha256=hashlib.sha256(expected + b"extra").hexdigest(),
        package="runtime",
        version="1.0",
    )
    monkeypatch.setattr(readiness, "MODEL_ARTIFACTS", ())
    monkeypatch.setattr(readiness, "RUNTIME_WHEELS", (wheel,))
    (tmp_path / "model").mkdir()
    (tmp_path / "wheelhouse").mkdir()
    (tmp_path / "wheelhouse" / wheel.filename).write_bytes(expected + b"extra")

    with pytest.raises(readiness.BioNeMoRecipesExecutionError, match="size mismatch"):
        readiness.verify_bionemo_recipes_artifact_directory(tmp_path)


def test_ready_to_build_requires_every_required_local_input(
    tmp_path, monkeypatch
) -> None:
    content = b"locked"
    artifact = BioNeMoRuntimeArtifact(
        filename="locked.bin",
        size_bytes=len(content),
        sha256=hashlib.sha256(content).hexdigest(),
        package="locked",
        version="1.0",
    )
    monkeypatch.setattr(readiness, "MODEL_ARTIFACTS", (artifact,))
    monkeypatch.setattr(readiness, "RUNTIME_WHEELS", (artifact,))
    (tmp_path / "model").mkdir()
    (tmp_path / "wheelhouse").mkdir()
    (tmp_path / "model" / artifact.filename).write_bytes(content)
    (tmp_path / "wheelhouse" / artifact.filename).write_bytes(content)

    runner = _healthy_runner()
    report = inspect_bionemo_recipes_readiness(
        _bundle(),
        artifact_root=tmp_path,
        terms_reviewed=True,
        runner=runner,
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )

    assert report.status == "ready-to-build"
    assert _checks(report)["exact_base_image"].status == "passed"
    assert _checks(report)["locked_artifacts"].status == "passed"
    command_text = " ".join(" ".join(command) for command in report.commands)
    assert " pull " not in f" {command_text} "
    assert " run " not in f" {command_text} "


def test_readiness_cli_prints_report_and_supports_strict_exit(
    tmp_path, monkeypatch, capsys
) -> None:
    report = inspect_bionemo_recipes_readiness(
        _bundle(),
        runner=_healthy_runner(image_local=False),
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )
    monkeypatch.setattr(
        protein_cli,
        "inspect_bionemo_recipes_readiness",
        lambda *_args, **_kwargs: report,
    )
    bundle_path = tmp_path / "bundle.zip"
    bundle_path.write_bytes(_bundle())
    args = ["bionemo-recipes-readiness", "--bundle", str(bundle_path)]

    assert protein_cli.main(args) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == BIONEMO_RECIPES_READINESS_VERSION
    assert payload["status"] == "review-required"

    assert protein_cli.main([*args, "--strict"]) == 3
