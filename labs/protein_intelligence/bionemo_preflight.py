"""Non-networking host checks for the external BioNeMo workflow."""

from __future__ import annotations

import json
import platform
import re
import subprocess
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.protein_intelligence.bionemo_execution import (
    BIONEMO_PREREQUISITES_URL,
)


BIONEMO_PREFLIGHT_VERSION = "hra-bionemo-preflight.v1"
MINIMUM_DRIVER_MAJOR = 560
MINIMUM_DOCKER_VERSION = (19, 3)
DOCUMENTED_GPU_NAMES = (
    "H100",
    "L4",
    "L40",
    "A100",
    "A40",
    "A30",
    "A10",
    "A16",
    "A2",
    "RTX 6000",
    "RTX A6000",
    "RTX A5000",
    "RTX A4000",
)

CheckStatus = Literal["passed", "warning", "blocked", "not-checked"]
OverallStatus = Literal["ready", "review-required", "blocked"]


class CommandResult(BaseModel):
    """Sanitized output from one fixed diagnostic command."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    available: bool = True
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""


class BioNeMoPreflightCheck(BaseModel):
    """One reviewable environment check and its bounded evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    check_id: str
    status: CheckStatus
    summary: str
    evidence: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )
    blocking_when_failed: bool = False


class BioNeMoPreflightReport(BaseModel):
    """A non-secret host report; it is not proof that BioNeMo executed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_PREFLIGHT_VERSION
    checked_at: datetime
    overall_status: OverallStatus
    checks: tuple[BioNeMoPreflightCheck, ...]
    official_prerequisites: str = BIONEMO_PREREQUISITES_URL
    network_calls_made: bool = False
    credentials_inspected: bool = False
    container_started: bool = False
    limitations: tuple[str, ...] = (
        "The preflight does not authenticate to NGC, pull an image, or start a container.",
        "A detected GPU or Docker installation does not prove BioNeMo compatibility.",
        "This is engineering provenance, not biomedical or clinical evidence.",
    )


CommandRunner = Callable[[Sequence[str]], CommandResult]


def _bounded(value: str, limit: int = 300) -> str:
    return " ".join(value.split())[:limit]


def _default_runner(command: Sequence[str]) -> CommandResult:
    try:
        completed = subprocess.run(
            tuple(command),
            capture_output=True,
            check=False,
            text=True,
            timeout=8,
        )
    except FileNotFoundError:
        return CommandResult(available=False)
    except subprocess.TimeoutExpired:
        return CommandResult(
            available=True,
            returncode=None,
            stderr="Command timed out.",
        )
    return CommandResult(
        available=True,
        returncode=completed.returncode,
        stdout=completed.stdout.strip()[:16_000],
        stderr=_bounded(completed.stderr),
    )


def _check(
    check_id: str,
    status: CheckStatus,
    summary: str,
    *,
    evidence: dict[str, str | int | float | bool | None] | None = None,
    blocking: bool = False,
) -> BioNeMoPreflightCheck:
    return BioNeMoPreflightCheck(
        check_id=check_id,
        status=status,
        summary=summary,
        evidence=evidence or {},
        blocking_when_failed=blocking,
    )


def _version(value: str) -> tuple[int, ...]:
    match = re.search(r"\d+(?:\.\d+)+", value)
    return tuple(int(part) for part in match.group().split(".")) if match else ()


def _version_at_least(actual: tuple[int, ...], minimum: tuple[int, ...]) -> bool:
    width = max(len(actual), len(minimum))
    return actual + (0,) * (width - len(actual)) >= minimum + (0,) * (
        width - len(minimum)
    )


def _json_output(result: CommandResult) -> dict[str, object] | None:
    if not result.stdout:
        return None
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _gpu_facts(result: CommandResult) -> dict[str, str | float] | None:
    if not result.available or result.returncode != 0 or not result.stdout:
        return None
    parts = [part.strip() for part in result.stdout.splitlines()[0].split(",")]
    if len(parts) < 4:
        return None
    try:
        compute_capability = float(parts[-2])
    except ValueError:
        return None
    return {
        "name": ", ".join(parts[:-3]),
        "driver_version": parts[-3],
        "compute_capability": compute_capability,
        "memory": parts[-1],
    }


def _documented_gpu(name: str) -> bool:
    return any(
        re.search(rf"\b{re.escape(candidate)}\b", name, re.IGNORECASE)
        for candidate in DOCUMENTED_GPU_NAMES
    )


def inspect_bionemo_environment(
    *,
    runner: CommandRunner | None = None,
    host_system: str | None = None,
    host_architecture: str | None = None,
    image_reference: str | None = None,
    checked_at: datetime | None = None,
) -> BioNeMoPreflightReport:
    """Inspect fixed local facts without network, credentials, or containers."""

    run = runner or _default_runner
    system = host_system or platform.system()
    architecture = host_architecture or platform.machine()
    checks: list[BioNeMoPreflightCheck] = []

    if system.casefold() == "linux":
        checks.append(
            _check(
                "host_os",
                "passed",
                "The host reports Linux, matching the documented operating system.",
                evidence={"system": system},
            )
        )
    elif system.casefold() == "windows":
        checks.append(
            _check(
                "host_os",
                "warning",
                "The direct host is Windows; a reviewed x86 Linux container backend is required.",
                evidence={"system": system},
            )
        )
    else:
        checks.append(
            _check(
                "host_os",
                "blocked",
                "The documented BioNeMo operating system is x86 Linux.",
                evidence={"system": system},
                blocking=True,
            )
        )

    normalized_architecture = architecture.casefold()
    architecture_ok = normalized_architecture in {"x86_64", "amd64", "x64"}
    checks.append(
        _check(
            "architecture",
            "passed" if architecture_ok else "blocked",
            (
                "The architecture is compatible with the documented x86 requirement."
                if architecture_ok
                else "BioNeMo Framework documents an x86 Linux requirement."
            ),
            evidence={"architecture": architecture},
            blocking=True,
        )
    )

    gpu_result = run(
        (
            "nvidia-smi",
            "--query-gpu=name,driver_version,compute_cap,memory.total",
            "--format=csv,noheader",
        )
    )
    gpu = _gpu_facts(gpu_result)
    if gpu is None:
        checks.extend(
            (
                _check(
                    "nvidia_gpu",
                    "blocked",
                    "No usable NVIDIA GPU report was available from nvidia-smi.",
                    evidence={"tool_available": gpu_result.available},
                    blocking=True,
                ),
                _check(
                    "driver",
                    "not-checked",
                    "The NVIDIA driver version could not be checked.",
                ),
                _check(
                    "bf16_capability",
                    "not-checked",
                    "GPU compute capability could not be checked.",
                ),
                _check(
                    "documented_gpu_model",
                    "not-checked",
                    "The GPU model could not be compared with the documentation.",
                ),
            )
        )
    else:
        checks.append(
            _check(
                "nvidia_gpu",
                "passed",
                "nvidia-smi reported an NVIDIA GPU.",
                evidence={"name": gpu["name"], "memory": gpu["memory"]},
                blocking=True,
            )
        )
        driver = _version(str(gpu["driver_version"]))
        driver_ok = bool(driver) and driver[0] >= MINIMUM_DRIVER_MAJOR
        checks.append(
            _check(
                "driver",
                "passed" if driver_ok else "blocked",
                (
                    "The detected driver meets the documented minimum major version."
                    if driver_ok
                    else "The detected driver is below the documented minimum major version."
                ),
                evidence={
                    "driver_version": str(gpu["driver_version"]),
                    "minimum_major": MINIMUM_DRIVER_MAJOR,
                },
                blocking=True,
            )
        )
        compute_capability = float(gpu["compute_capability"])
        bf16_ok = compute_capability >= 8.0
        checks.append(
            _check(
                "bf16_capability",
                "passed" if bf16_ok else "blocked",
                (
                    "Compute capability meets the documented bfloat16 threshold."
                    if bf16_ok
                    else "Compute capability is below the documented bfloat16 threshold."
                ),
                evidence={
                    "compute_capability": compute_capability,
                    "minimum": 8.0,
                },
                blocking=True,
            )
        )
        gpu_is_documented = _documented_gpu(str(gpu["name"]))
        checks.append(
            _check(
                "documented_gpu_model",
                "passed" if gpu_is_documented else "warning",
                (
                    "The GPU model appears in the documented support matrix."
                    if gpu_is_documented
                    else "The GPU meets the compute threshold but its exact model is not listed in the reviewed support matrix."
                ),
                evidence={"name": str(gpu["name"])},
            )
        )

    docker_result = run(("docker", "version", "--format", "{{json .}}"))
    docker_payload = _json_output(docker_result)
    docker_server = (
        docker_payload.get("Server") if isinstance(docker_payload, dict) else None
    )
    docker_client = (
        docker_payload.get("Client") if isinstance(docker_payload, dict) else None
    )
    docker_ready = False
    if not docker_result.available:
        docker_summary = "Docker was not found."
        docker_evidence: dict[str, str | int | float | bool | None] = {
            "client_available": False
        }
    elif not isinstance(docker_server, dict):
        docker_summary = "The Docker client is installed, but its engine is unavailable."
        docker_evidence = {
            "client_available": True,
            "client_version": (
                str(docker_client.get("Version", ""))
                if isinstance(docker_client, dict)
                else ""
            ),
            "daemon_available": False,
            "error": _bounded(docker_result.stderr, 160),
        }
    else:
        server_version = str(docker_server.get("Version", ""))
        server_os = str(docker_server.get("Os", ""))
        docker_ready = _version_at_least(
            _version(server_version), MINIMUM_DOCKER_VERSION
        ) and server_os.casefold() == "linux"
        docker_summary = (
            "The Docker Linux engine meets the documented minimum version."
            if docker_ready
            else "Docker must expose a compatible Linux engine."
        )
        docker_evidence = {
            "client_version": (
                str(docker_client.get("Version", ""))
                if isinstance(docker_client, dict)
                else ""
            ),
            "server_version": server_version,
            "server_os": server_os,
        }
    checks.append(
        _check(
            "docker_engine",
            "passed" if docker_ready else "blocked",
            docker_summary,
            evidence=docker_evidence,
            blocking=True,
        )
    )

    if docker_ready:
        runtime_result = run(
            (
                "docker",
                "info",
                "--format",
                "{{range $name, $runtime := .Runtimes}}{{$name}}{{println}}{{end}}",
            )
        )
        runtime_names = {
            line.strip().casefold()
            for line in runtime_result.stdout.splitlines()
            if line.strip()
        }
        nvidia_runtime = (
            runtime_result.available
            and runtime_result.returncode == 0
            and "nvidia" in runtime_names
        )
        checks.append(
            _check(
                "container_toolkit",
                "passed" if nvidia_runtime else "warning",
                (
                    "Docker reports an NVIDIA runtime."
                    if nvidia_runtime
                    else "NVIDIA Container Toolkit was not verified from Docker runtime metadata."
                ),
                evidence={"nvidia_runtime_declared": nvidia_runtime},
            )
        )
    else:
        checks.append(
            _check(
                "container_toolkit",
                "not-checked",
                "Container Toolkit metadata requires a running Docker engine.",
            )
        )

    checks.append(
        _check(
            "gpu_container_probe",
            "not-checked",
            "The non-networking preflight does not start a GPU container.",
        )
    )

    if image_reference is None:
        checks.append(
            _check(
                "immutable_image",
                "not-checked",
                "No container image reference was supplied.",
            )
        )
    else:
        image_ok = re.fullmatch(
            r".+@sha256:[0-9a-fA-F]{64}", image_reference
        ) is not None
        checks.append(
            _check(
                "immutable_image",
                "passed" if image_ok else "blocked",
                (
                    "The image reference contains a complete immutable digest."
                    if image_ok
                    else "The image reference must end with a complete @sha256 digest."
                ),
                evidence={"immutable_digest": image_ok},
                blocking=True,
            )
        )

    blocking_failure = any(
        item.blocking_when_failed and item.status == "blocked" for item in checks
    )
    if blocking_failure:
        overall_status: OverallStatus = "blocked"
    elif any(item.status in {"warning", "not-checked"} for item in checks):
        overall_status = "review-required"
    else:
        overall_status = "ready"

    return BioNeMoPreflightReport(
        checked_at=checked_at or datetime.now(timezone.utc),
        overall_status=overall_status,
        checks=tuple(checks),
    )
