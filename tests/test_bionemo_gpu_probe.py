from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Sequence

from labs.protein_intelligence import (
    BIONEMO_GPU_PROBE_VERSION,
    BioNeMoGPUProbeReport,
    CommandResult,
    is_immutable_image_reference,
    run_bionemo_gpu_probe,
)
from labs.protein_intelligence import __main__ as protein_cli


IMAGE = "nvcr.io/nvidia/bionemo@sha256:" + "a" * 64
CHECKED_AT = datetime(2026, 7, 19, 16, 0, tzinfo=timezone.utc)
CONTEXT_COMMAND = (
    "docker",
    "context",
    "inspect",
    "--format",
    "{{json .Endpoints.docker.Host}}",
)
INSPECTION_COMMAND = (
    "docker",
    "image",
    "inspect",
    "--format",
    "{{.Id}}|{{.Os}}|{{.Architecture}}",
    IMAGE,
)
CONTAINER_COMMAND = (
    "docker",
    "run",
    "--rm",
    "--pull",
    "never",
    "--gpus",
    "all",
    "--network",
    "none",
    "--read-only",
    "--pids-limit",
    "64",
    "--cap-drop",
    "ALL",
    "--security-opt",
    "no-new-privileges",
    "--entrypoint",
    "nvidia-smi",
    IMAGE,
    "--query-gpu=name,driver_version,compute_cap,memory.total",
    "--format=csv,noheader",
)


class FakeRunner:
    def __init__(self, responses: dict[tuple[str, ...], CommandResult]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, command: Sequence[str]) -> CommandResult:
        key = tuple(command)
        self.calls.append(key)
        return self.responses.get(key, CommandResult(available=False))


def _healthy_runner() -> FakeRunner:
    return FakeRunner(
        {
            CONTEXT_COMMAND: CommandResult(
                returncode=0,
                stdout=json.dumps("npipe:////./pipe/dockerDesktopLinuxEngine"),
            ),
            INSPECTION_COMMAND: CommandResult(
                returncode=0,
                stdout="sha256:local-image|linux|amd64",
            ),
            CONTAINER_COMMAND: CommandResult(
                returncode=0,
                stdout="NVIDIA A100, 591.86, 8.0, 40960 MiB",
            ),
        }
    )


def test_probe_rejects_moving_tags_without_running_docker() -> None:
    runner = FakeRunner({})
    report = run_bionemo_gpu_probe(
        "nvcr.io/nvidia/bionemo:latest",
        confirmed=True,
        runner=runner,
        checked_at=CHECKED_AT,
    )

    assert report.status == "blocked"
    assert report.container_run_attempted is False
    assert runner.calls == []
    assert is_immutable_image_reference(IMAGE) is True
    assert is_immutable_image_reference("nvcr.io/nvidia/bionemo:latest") is False


def test_probe_requires_explicit_confirmation() -> None:
    runner = _healthy_runner()
    report = run_bionemo_gpu_probe(
        IMAGE,
        runner=runner,
        checked_at=CHECKED_AT,
    )

    assert report.status == "not-run"
    assert report.confirmation_given is False
    assert report.container_command == CONTAINER_COMMAND
    assert runner.calls == []


def test_probe_does_not_pull_when_exact_image_is_missing() -> None:
    runner = FakeRunner(
        {
            CONTEXT_COMMAND: CommandResult(
                returncode=0,
                stdout=json.dumps("unix:///var/run/docker.sock"),
            ),
            INSPECTION_COMMAND: CommandResult(
                returncode=1,
                stderr="No such image",
            )
        }
    )
    report = run_bionemo_gpu_probe(
        IMAGE,
        confirmed=True,
        runner=runner,
        checked_at=CHECKED_AT,
    )

    assert report.status == "blocked"
    assert report.local_image_found is False
    assert report.container_run_attempted is False
    assert runner.calls == [CONTEXT_COMMAND, INSPECTION_COMMAND]


def test_probe_blocks_remote_docker_context_before_image_inspection() -> None:
    runner = FakeRunner(
        {
            CONTEXT_COMMAND: CommandResult(
                returncode=0,
                stdout=json.dumps("ssh://gpu-host.example"),
            )
        }
    )
    report = run_bionemo_gpu_probe(
        IMAGE,
        confirmed=True,
        runner=runner,
        checked_at=CHECKED_AT,
    )

    assert report.status == "blocked"
    assert report.local_image_found is False
    assert report.container_run_attempted is False
    assert report.evidence["docker_endpoint"] == "ssh://gpu-host.example"
    assert runner.calls == [CONTEXT_COMMAND]


def test_probe_runs_only_the_fixed_network_disabled_gpu_command() -> None:
    runner = _healthy_runner()
    report = run_bionemo_gpu_probe(
        IMAGE,
        confirmed=True,
        runner=runner,
        checked_at=CHECKED_AT,
    )

    assert report.schema_version == BIONEMO_GPU_PROBE_VERSION
    assert report.status == "passed"
    assert report.local_image_found is True
    assert report.container_run_attempted is True
    assert report.container_completed is True
    assert report.gpu_visible is True
    assert report.network_calls_made is False
    assert report.credentials_inspected is False
    assert report.model_executed is False
    assert report.evidence["gpu_name"] == "NVIDIA A100"
    assert runner.calls == [CONTEXT_COMMAND, INSPECTION_COMMAND, CONTAINER_COMMAND]
    assert CONTAINER_COMMAND[CONTAINER_COMMAND.index("--pull") + 1] == "never"
    assert CONTAINER_COMMAND[CONTAINER_COMMAND.index("--network") + 1] == "none"
    assert "login" not in CONTAINER_COMMAND
    assert "-v" not in CONTAINER_COMMAND
    assert "--mount" not in CONTAINER_COMMAND


def test_probe_records_container_failure_without_claiming_gpu_visibility() -> None:
    runner = _healthy_runner()
    runner.responses[CONTAINER_COMMAND] = CommandResult(
        returncode=125,
        stderr="could not select device driver with capabilities: [[gpu]]",
    )
    report = run_bionemo_gpu_probe(
        IMAGE,
        confirmed=True,
        runner=runner,
        checked_at=CHECKED_AT,
    )

    assert report.status == "blocked"
    assert report.container_run_attempted is True
    assert report.container_completed is False
    assert report.gpu_visible is False
    assert "could not select" in str(report.evidence["error"])


def test_cli_probe_is_dry_until_confirmation(monkeypatch, capsys) -> None:
    dry_report = run_bionemo_gpu_probe(IMAGE, checked_at=CHECKED_AT)
    passed_report = BioNeMoGPUProbeReport(
        checked_at=CHECKED_AT,
        status="passed",
        summary="Fixture GPU probe passed.",
        image_reference=IMAGE,
        confirmation_given=True,
        local_image_found=True,
        container_run_attempted=True,
        container_completed=True,
        gpu_visible=True,
    )

    assert protein_cli.main(["bionemo-gpu-probe", "--image", IMAGE]) == 3
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "not-run"

    monkeypatch.setattr(
        protein_cli,
        "run_bionemo_gpu_probe",
        lambda *_args, **_kwargs: passed_report,
    )
    assert (
        protein_cli.main(
            [
                "bionemo-gpu-probe",
                "--image",
                IMAGE,
                "--confirm-local-container",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["status"] == "passed"
    assert dry_report.model_executed is False
