from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Sequence

from labs.protein_intelligence import (
    BIONEMO_PREFLIGHT_VERSION,
    CommandResult,
    inspect_bionemo_environment,
)
from labs.protein_intelligence import __main__ as protein_cli


GPU_COMMAND = (
    "nvidia-smi",
    "--query-gpu=name,driver_version,compute_cap,memory.total",
    "--format=csv,noheader",
)
DOCKER_VERSION_COMMAND = ("docker", "version", "--format", "{{json .}}")
DOCKER_INFO_COMMAND = ("docker", "info", "--format", "{{json .Runtimes}}")
CHECKED_AT = datetime(2026, 7, 19, 14, 0, tzinfo=timezone.utc)


class FakeRunner:
    def __init__(self, responses: dict[tuple[str, ...], CommandResult]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, command: Sequence[str]) -> CommandResult:
        key = tuple(command)
        self.calls.append(key)
        return self.responses.get(key, CommandResult(available=False))


def _docker_version(*, server_os: str = "linux", version: str = "29.1.3") -> str:
    return json.dumps(
        {
            "Client": {"Version": "29.1.3", "Os": "windows"},
            "Server": {"Version": version, "Os": server_os},
        }
    )


def _healthy_runner(gpu_name: str = "NVIDIA A100") -> FakeRunner:
    return FakeRunner(
        {
            GPU_COMMAND: CommandResult(
                returncode=0,
                stdout=f"{gpu_name}, 591.86, 8.0, 40960 MiB",
            ),
            DOCKER_VERSION_COMMAND: CommandResult(
                returncode=0,
                stdout=_docker_version(),
            ),
            DOCKER_INFO_COMMAND: CommandResult(
                returncode=0,
                stdout=json.dumps({"nvidia": {"path": "nvidia-container-runtime"}}),
            ),
        }
    )


def _checks(report: object) -> dict[str, object]:
    return {check.check_id: check for check in report.checks}


def test_preflight_records_healthy_facts_without_claiming_execution() -> None:
    runner = _healthy_runner()
    report = inspect_bionemo_environment(
        runner=runner,
        host_system="Linux",
        host_architecture="x86_64",
        image_reference="nvcr.io/example/bionemo@sha256:" + "a" * 64,
        checked_at=CHECKED_AT,
    )
    checks = _checks(report)

    assert report.schema_version == BIONEMO_PREFLIGHT_VERSION
    assert report.overall_status == "review-required"
    assert checks["host_os"].status == "passed"
    assert checks["driver"].status == "passed"
    assert checks["bf16_capability"].status == "passed"
    assert checks["docker_engine"].status == "passed"
    assert checks["container_toolkit"].status == "passed"
    assert checks["immutable_image"].status == "passed"
    assert checks["gpu_container_probe"].status == "not-checked"
    assert report.network_calls_made is False
    assert report.credentials_inspected is False
    assert report.container_started is False


def test_windows_host_with_stopped_docker_is_blocked_but_keeps_gpu_facts() -> None:
    runner = FakeRunner(
        {
            GPU_COMMAND: CommandResult(
                returncode=0,
                stdout="NVIDIA GeForce RTX 5070 Ti, 591.86, 12.0, 16303 MiB",
            ),
            DOCKER_VERSION_COMMAND: CommandResult(
                returncode=1,
                stdout=json.dumps({"Client": {"Version": "29.1.3"}, "Server": None}),
                stderr="failed to connect to the Docker Desktop Linux engine",
            ),
        }
    )
    report = inspect_bionemo_environment(
        runner=runner,
        host_system="Windows",
        host_architecture="AMD64",
        checked_at=CHECKED_AT,
    )
    checks = _checks(report)

    assert report.overall_status == "blocked"
    assert checks["host_os"].status == "warning"
    assert checks["nvidia_gpu"].evidence["name"] == "NVIDIA GeForce RTX 5070 Ti"
    assert checks["bf16_capability"].status == "passed"
    assert checks["documented_gpu_model"].status == "warning"
    assert checks["docker_engine"].status == "blocked"
    assert checks["container_toolkit"].status == "not-checked"
    assert DOCKER_INFO_COMMAND not in runner.calls


def test_missing_gpu_and_old_driver_are_blocking() -> None:
    missing_runner = FakeRunner(
        {
            GPU_COMMAND: CommandResult(available=False),
            DOCKER_VERSION_COMMAND: CommandResult(
                returncode=0,
                stdout=_docker_version(),
            ),
            DOCKER_INFO_COMMAND: CommandResult(returncode=0, stdout='{"nvidia": {}}'),
        }
    )
    missing_report = inspect_bionemo_environment(
        runner=missing_runner,
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )

    old_driver_runner = _healthy_runner()
    old_driver_runner.responses[GPU_COMMAND] = CommandResult(
        returncode=0,
        stdout="NVIDIA A100, 535.54, 8.0, 40960 MiB",
    )
    old_driver_report = inspect_bionemo_environment(
        runner=old_driver_runner,
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )

    assert missing_report.overall_status == "blocked"
    assert _checks(missing_report)["nvidia_gpu"].status == "blocked"
    assert old_driver_report.overall_status == "blocked"
    assert _checks(old_driver_report)["driver"].status == "blocked"


def test_moving_image_tag_is_rejected() -> None:
    report = inspect_bionemo_environment(
        runner=_healthy_runner(),
        host_system="Linux",
        host_architecture="x86_64",
        image_reference="nvcr.io/example/bionemo:latest",
        checked_at=CHECKED_AT,
    )

    assert report.overall_status == "blocked"
    assert _checks(report)["immutable_image"].status == "blocked"


def test_preflight_runs_only_fixed_read_only_commands() -> None:
    runner = _healthy_runner()
    inspect_bionemo_environment(
        runner=runner,
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )

    assert runner.calls == [
        GPU_COMMAND,
        DOCKER_VERSION_COMMAND,
        DOCKER_INFO_COMMAND,
    ]
    command_text = " ".join(" ".join(command) for command in runner.calls)
    assert " login " not in f" {command_text} "
    assert " pull " not in f" {command_text} "
    assert " run " not in f" {command_text} "


def test_cli_preflight_outputs_json_and_strict_status(monkeypatch, capsys) -> None:
    report = inspect_bionemo_environment(
        runner=_healthy_runner(),
        host_system="Linux",
        host_architecture="x86_64",
        checked_at=CHECKED_AT,
    )
    monkeypatch.setattr(
        protein_cli,
        "inspect_bionemo_environment",
        lambda **_kwargs: report,
    )

    assert protein_cli.main(["bionemo-preflight"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["schema_version"] == BIONEMO_PREFLIGHT_VERSION
    assert payload["credentials_inspected"] is False

    assert protein_cli.main(["bionemo-preflight", "--strict"]) == 3
