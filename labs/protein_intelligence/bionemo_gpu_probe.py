"""Explicit, local-only GPU container probe for the BioNeMo lab."""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.protein_intelligence.bionemo_preflight import CommandResult


BIONEMO_GPU_PROBE_VERSION = "hra-bionemo-gpu-probe.v1"
IMMUTABLE_IMAGE_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9._:/-]*[a-z0-9])?@sha256:[0-9a-f]{64}$"
)
ProbeStatus = Literal["passed", "blocked", "not-run"]


class BioNeMoGPUProbeReport(BaseModel):
    """Provenance for one bounded GPU-container diagnostic."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_GPU_PROBE_VERSION
    checked_at: datetime
    status: ProbeStatus
    summary: str
    image_reference: str
    confirmation_given: bool
    local_image_found: bool = False
    container_run_attempted: bool = False
    container_completed: bool = False
    gpu_visible: bool = False
    context_command: tuple[str, ...] = ()
    inspection_command: tuple[str, ...] = ()
    container_command: tuple[str, ...] = ()
    evidence: dict[str, str | int | float | bool | None] = Field(
        default_factory=dict
    )
    pull_policy: Literal["never"] = "never"
    container_network: Literal["none"] = "none"
    network_calls_made: bool = False
    credentials_inspected: bool = False
    model_executed: bool = False
    limitations: tuple[str, ...] = (
        "Passing this probe confirms only that a reviewed local image can see the GPU.",
        "The probe does not authenticate, pull an image, execute BioNeMo, or load a model.",
        "GPU visibility does not establish BioNeMo support, scientific validity, or clinical meaning.",
    )


ProbeRunner = Callable[[Sequence[str]], CommandResult]


def is_immutable_image_reference(image_reference: str) -> bool:
    """Return whether a conservative Docker reference includes a full digest."""

    return IMMUTABLE_IMAGE_PATTERN.fullmatch(image_reference.strip()) is not None


def _bounded(value: str, limit: int = 300) -> str:
    return " ".join(value.split())[:limit]


def _default_runner(command: Sequence[str]) -> CommandResult:
    environment = os.environ.copy()
    docker_overrides = (
        "DOCKER_HOST",
        "DOCKER_CONTEXT",
        "DOCKER_TLS_VERIFY",
        "DOCKER_CERT_PATH",
    )
    for name in docker_overrides:
        environment.pop(name, None)
    try:
        completed = subprocess.run(
            tuple(command),
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
            env=environment,
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
        stdout=completed.stdout.strip()[:4_000],
        stderr=_bounded(completed.stderr),
    )


def _inspection_facts(result: CommandResult) -> tuple[str, str, str] | None:
    if not result.available or result.returncode != 0 or not result.stdout:
        return None
    parts = result.stdout.splitlines()[0].split("|", maxsplit=2)
    if len(parts) != 3:
        return None
    return parts[0].strip(), parts[1].strip(), parts[2].strip()


def _docker_endpoint(result: CommandResult) -> str | None:
    if not result.available or result.returncode != 0 or not result.stdout:
        return None
    value = result.stdout.strip()
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return None
        return parsed if isinstance(parsed, str) else None
    return value


def _is_local_docker_endpoint(endpoint: str) -> bool:
    return endpoint.casefold().startswith(("npipe://", "unix://"))


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
        "gpu_name": ", ".join(parts[:-3]),
        "driver_version": parts[-3],
        "compute_capability": compute_capability,
        "memory": parts[-1],
    }


def run_bionemo_gpu_probe(
    image_reference: str,
    *,
    confirmed: bool = False,
    runner: ProbeRunner | None = None,
    checked_at: datetime | None = None,
) -> BioNeMoGPUProbeReport:
    """Run one fixed GPU diagnostic against an already-local immutable image.

    The command cannot pull, has no container network, mounts no host path, and
    overrides the image entrypoint with ``nvidia-smi``. BioNeMo is not executed.
    """

    image = image_reference.strip()
    timestamp = checked_at or datetime.now(timezone.utc)
    if not is_immutable_image_reference(image):
        return BioNeMoGPUProbeReport(
            checked_at=timestamp,
            status="blocked",
            summary="The image must be identified by a complete immutable digest.",
            image_reference=image,
            confirmation_given=confirmed,
        )

    context_command = (
        "docker",
        "context",
        "inspect",
        "--format",
        "{{json .Endpoints.docker.Host}}",
    )
    inspection_command = (
        "docker",
        "image",
        "inspect",
        "--format",
        "{{.Id}}|{{.Os}}|{{.Architecture}}",
        image,
    )
    container_command = (
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
        image,
        "--query-gpu=name,driver_version,compute_cap,memory.total",
        "--format=csv,noheader",
    )
    if not confirmed:
        return BioNeMoGPUProbeReport(
            checked_at=timestamp,
            status="not-run",
            summary="Explicit confirmation is required before a local container starts.",
            image_reference=image,
            confirmation_given=False,
            context_command=context_command,
            inspection_command=inspection_command,
            container_command=container_command,
        )

    run = runner or _default_runner
    context_result = run(context_command)
    docker_endpoint = _docker_endpoint(context_result)
    if docker_endpoint is None or not _is_local_docker_endpoint(docker_endpoint):
        return BioNeMoGPUProbeReport(
            checked_at=timestamp,
            status="blocked",
            summary="The active Docker endpoint must be a local socket or named pipe.",
            image_reference=image,
            confirmation_given=True,
            context_command=context_command,
            inspection_command=inspection_command,
            container_command=container_command,
            evidence={
                "docker_endpoint": docker_endpoint or "unavailable",
                "error": _bounded(context_result.stderr),
            },
        )

    inspection_result = run(inspection_command)
    inspection = _inspection_facts(inspection_result)
    if inspection is None:
        return BioNeMoGPUProbeReport(
            checked_at=timestamp,
            status="blocked",
            summary="The exact immutable image was not found in the local Docker store.",
            image_reference=image,
            confirmation_given=True,
            context_command=context_command,
            inspection_command=inspection_command,
            container_command=container_command,
            evidence={
                "docker_endpoint": docker_endpoint,
                "docker_available": inspection_result.available,
                "error": _bounded(inspection_result.stderr),
            },
        )

    image_id, image_os, image_architecture = inspection
    evidence: dict[str, str | int | float | bool | None] = {
        "image_id": image_id,
        "image_os": image_os,
        "image_architecture": image_architecture,
        "docker_endpoint": docker_endpoint,
    }
    if image_os.casefold() != "linux" or image_architecture.casefold() not in {
        "amd64",
        "x86_64",
    }:
        return BioNeMoGPUProbeReport(
            checked_at=timestamp,
            status="blocked",
            summary="The local image must target x86 Linux.",
            image_reference=image,
            confirmation_given=True,
            local_image_found=True,
            context_command=context_command,
            inspection_command=inspection_command,
            container_command=container_command,
            evidence=evidence,
        )

    container_result = run(container_command)
    gpu = _gpu_facts(container_result)
    if gpu is None:
        evidence["error"] = _bounded(container_result.stderr)
        return BioNeMoGPUProbeReport(
            checked_at=timestamp,
            status="blocked",
            summary="The local container did not return a usable NVIDIA GPU report.",
            image_reference=image,
            confirmation_given=True,
            local_image_found=True,
            container_run_attempted=True,
            container_completed=container_result.returncode == 0,
            context_command=context_command,
            inspection_command=inspection_command,
            container_command=container_command,
            evidence=evidence,
        )

    evidence.update(gpu)
    return BioNeMoGPUProbeReport(
        checked_at=timestamp,
        status="passed",
        summary="The reviewed local image completed the fixed GPU visibility check.",
        image_reference=image,
        confirmation_given=True,
        local_image_found=True,
        container_run_attempted=True,
        container_completed=True,
        gpu_visible=True,
        context_command=context_command,
        inspection_command=inspection_command,
        container_command=container_command,
        evidence=evidence,
    )
