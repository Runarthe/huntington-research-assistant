"""Fail-closed readiness checks before a bounded BioNeMo Recipes build."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.protein_intelligence.bionemo_preflight import (
    BioNeMoPreflightReport,
    CommandResult,
    inspect_bionemo_environment,
)
from labs.protein_intelligence.bionemo_recipes_execution import (
    BIONEMO_RECIPES_BASE_REFERENCE,
    MODEL_ARTIFACTS,
    RUNTIME_WHEELS,
    BioNeMoRecipesExecutionError,
    validate_bionemo_recipes_execution_bundle,
)


BIONEMO_RECIPES_READINESS_VERSION = "hra-bionemo-recipes-readiness.v1"
ReadinessCheckStatus = Literal[
    "passed",
    "warning",
    "review-required",
    "blocked",
    "not-checked",
]
ReadinessStatus = Literal["ready-to-build", "review-required", "blocked"]


class BioNeMoRecipesReadinessCheck(BaseModel):
    """One pre-build condition with sanitized local evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    check_id: str
    status: ReadinessCheckStatus
    summary: str
    required_for_build: bool
    evidence: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class BioNeMoRecipesReadinessReport(BaseModel):
    """Evidence that a local directory is prepared, not that a model ran."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_RECIPES_READINESS_VERSION
    checked_at: datetime
    status: ReadinessStatus
    exact_base_reference: str = BIONEMO_RECIPES_BASE_REFERENCE
    terms_reviewed_user_declaration: bool
    checks: tuple[BioNeMoRecipesReadinessCheck, ...]
    host_preflight: BioNeMoPreflightReport
    commands: tuple[tuple[str, ...], ...]
    network_calls_made: bool = False
    credentials_inspected: bool = False
    image_pulled: bool = False
    container_started: bool = False
    model_imported: bool = False
    model_executed: bool = False
    limitations: tuple[str, ...] = (
        "The terms flag records only the user's declaration; HRA cannot provide legal advice or accept terms on the user's behalf.",
        "A ready-to-build report does not prove that the derived image builds or that the GPU can execute the model.",
        "No model output, biological interpretation, treatment relevance, or clinical meaning is produced.",
    )


ReadinessRunner = Callable[[Sequence[str]], CommandResult]


def _bounded(value: str, limit: int = 300) -> str:
    return " ".join(value.split())[:limit]


def _default_runner(command: Sequence[str]) -> CommandResult:
    environment = os.environ.copy()
    for name in (
        "DOCKER_HOST",
        "DOCKER_CONTEXT",
        "DOCKER_TLS_VERIFY",
        "DOCKER_CERT_PATH",
    ):
        environment.pop(name, None)
    try:
        completed = subprocess.run(
            tuple(command),
            capture_output=True,
            check=False,
            text=True,
            timeout=12,
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
        stdout=completed.stdout.strip()[:8_000],
        stderr=_bounded(completed.stderr),
    )


def _check(
    check_id: str,
    status: ReadinessCheckStatus,
    summary: str,
    *,
    required: bool,
    evidence: dict[str, str | int | float | bool | None] | None = None,
) -> BioNeMoRecipesReadinessCheck:
    return BioNeMoRecipesReadinessCheck(
        check_id=check_id,
        status=status,
        summary=summary,
        required_for_build=required,
        evidence=evidence or {},
    )


def _docker_endpoint(result: CommandResult) -> str | None:
    if not result.available or result.returncode != 0 or not result.stdout:
        return None
    value = result.stdout.strip()
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, str) else None
    return value


def _is_local_endpoint(endpoint: str) -> bool:
    return endpoint.casefold().startswith(("npipe://", "unix://"))


def _image_facts(result: CommandResult) -> dict[str, object] | None:
    if not result.available or result.returncode != 0 or not result.stdout:
        return None
    parts = result.stdout.splitlines()[0].split("|", maxsplit=3)
    if len(parts) != 4:
        return None
    try:
        repo_digests = json.loads(parts[3])
    except json.JSONDecodeError:
        return None
    if not isinstance(repo_digests, list):
        return None
    return {
        "image_id": parts[0].strip(),
        "os": parts[1].strip(),
        "architecture": parts[2].strip(),
        "repo_digests": [str(value) for value in repo_digests],
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_bionemo_recipes_artifact_directory(
    root: str | Path,
) -> dict[str, int]:
    """Verify exact local artifacts as data without importing or executing them."""

    directory = Path(root).expanduser().absolute()
    if directory.is_symlink() or not directory.is_dir():
        raise BioNeMoRecipesExecutionError(
            "Artifact root must be an existing, non-linked directory."
        )
    model_directory = directory / "model"
    wheel_directory = directory / "wheelhouse"
    for label, artifact_directory in (
        ("model", model_directory),
        ("wheelhouse", wheel_directory),
    ):
        if artifact_directory.is_symlink() or not artifact_directory.is_dir():
            raise BioNeMoRecipesExecutionError(
                f"Artifact {label} path must be an existing, non-linked directory."
            )

    model_bytes = 0
    wheel_bytes = 0
    for artifact in MODEL_ARTIFACTS:
        path = model_directory / artifact.filename
        if path.is_symlink() or not path.is_file():
            raise BioNeMoRecipesExecutionError(
                f"Missing or linked model artifact: {artifact.filename}"
            )
        if (
            artifact.size_bytes is not None
            and path.stat().st_size != artifact.size_bytes
        ):
            raise BioNeMoRecipesExecutionError(
                f"Model artifact size mismatch: {artifact.filename}"
            )
        if _sha256_file(path) != artifact.sha256:
            raise BioNeMoRecipesExecutionError(
                f"Model artifact checksum mismatch: {artifact.filename}"
            )
        model_bytes += path.stat().st_size

    for artifact in RUNTIME_WHEELS:
        path = wheel_directory / artifact.filename
        if path.is_symlink() or not path.is_file():
            raise BioNeMoRecipesExecutionError(
                f"Missing or linked runtime wheel: {artifact.filename}"
            )
        if (
            artifact.size_bytes is not None
            and path.stat().st_size != artifact.size_bytes
        ):
            raise BioNeMoRecipesExecutionError(
                f"Runtime wheel size mismatch: {artifact.filename}"
            )
        if _sha256_file(path) != artifact.sha256:
            raise BioNeMoRecipesExecutionError(
                f"Runtime wheel checksum mismatch: {artifact.filename}"
            )
        wheel_bytes += path.stat().st_size

    return {
        "model_file_count": len(MODEL_ARTIFACTS),
        "model_bytes": model_bytes,
        "wheel_file_count": len(RUNTIME_WHEELS),
        "wheel_bytes": wheel_bytes,
    }


def inspect_bionemo_recipes_readiness(
    bundle: bytes,
    *,
    artifact_root: str | Path | None = None,
    terms_reviewed: bool = False,
    runner: ReadinessRunner | None = None,
    host_system: str | None = None,
    host_architecture: str | None = None,
    checked_at: datetime | None = None,
) -> BioNeMoRecipesReadinessReport:
    """Inspect local build inputs without network calls, pulls, or containers."""

    run = runner or _default_runner
    timestamp = checked_at or datetime.now(timezone.utc)
    host_report = inspect_bionemo_environment(
        runner=run,
        host_system=host_system or platform.system(),
        host_architecture=host_architecture or platform.machine(),
        image_reference=BIONEMO_RECIPES_BASE_REFERENCE,
        checked_at=timestamp,
    )
    checks: list[BioNeMoRecipesReadinessCheck] = []
    host_blocked = host_report.overall_status == "blocked"
    checks.append(
        _check(
            "host_runtime",
            (
                "blocked"
                if host_blocked
                else (
                    "warning"
                    if host_report.overall_status == "review-required"
                    else "passed"
                )
            ),
            (
                "A blocking host prerequisite failed."
                if host_blocked
                else "Host prerequisites have no blocking failure; review retained warnings."
            ),
            required=True,
            evidence={"host_status": host_report.overall_status},
        )
    )

    try:
        bundle_manifest = validate_bionemo_recipes_execution_bundle(bundle)
    except BioNeMoRecipesExecutionError as exc:
        checks.append(
            _check(
                "fixture_bundle",
                "blocked",
                "The fixture bundle failed validation.",
                required=True,
                evidence={"error": _bounded(str(exc), 200)},
            )
        )
    else:
        checks.append(
            _check(
                "fixture_bundle",
                "passed",
                "The deterministic fixture bundle matches the reviewed contract.",
                required=True,
                evidence={
                    "experiment_id": str(bundle_manifest["experiment_id"]),
                    "size_bytes": len(bundle),
                },
            )
        )

    checks.append(
        _check(
            "terms_review",
            "passed" if terms_reviewed else "review-required",
            (
                "The user declared that applicable NVIDIA and model terms were reviewed."
                if terms_reviewed
                else "Review applicable NVIDIA and model terms before acquiring or building the image."
            ),
            required=True,
            evidence={"user_declaration": terms_reviewed},
        )
    )

    context_command = (
        "docker",
        "context",
        "inspect",
        "--format",
        "{{json .Endpoints.docker.Host}}",
    )
    image_command = (
        "docker",
        "image",
        "inspect",
        BIONEMO_RECIPES_BASE_REFERENCE,
        "--format",
        "{{.Id}}|{{.Os}}|{{.Architecture}}|{{json .RepoDigests}}",
    )
    commands: list[tuple[str, ...]] = [context_command]
    endpoint = _docker_endpoint(run(context_command))
    if endpoint is None:
        checks.append(
            _check(
                "local_docker_endpoint",
                "blocked",
                "A local Docker endpoint could not be verified.",
                required=True,
            )
        )
    elif not _is_local_endpoint(endpoint):
        checks.append(
            _check(
                "local_docker_endpoint",
                "blocked",
                "Remote Docker endpoints are forbidden for this fixture workflow.",
                required=True,
                evidence={"endpoint": _bounded(endpoint, 120)},
            )
        )
    else:
        checks.append(
            _check(
                "local_docker_endpoint",
                "passed",
                "Docker uses a local endpoint.",
                required=True,
                evidence={"endpoint": endpoint},
            )
        )
        commands.append(image_command)
        image_facts = _image_facts(run(image_command))
        if image_facts is None:
            checks.append(
                _check(
                    "exact_base_image",
                    "review-required",
                    "The exact reviewed base image is not present locally; this check does not pull it.",
                    required=True,
                    evidence={"reference": BIONEMO_RECIPES_BASE_REFERENCE},
                )
            )
        else:
            image_ok = (
                image_facts["os"] == "linux"
                and image_facts["architecture"] == "amd64"
                and BIONEMO_RECIPES_BASE_REFERENCE in image_facts["repo_digests"]
            )
            checks.append(
                _check(
                    "exact_base_image",
                    "passed" if image_ok else "blocked",
                    (
                        "The exact reviewed Linux/AMD64 base image is local."
                        if image_ok
                        else "The local image metadata does not match the reviewed base contract."
                    ),
                    required=True,
                    evidence={
                        "reference": BIONEMO_RECIPES_BASE_REFERENCE,
                        "image_id": str(image_facts["image_id"]),
                        "os": str(image_facts["os"]),
                        "architecture": str(image_facts["architecture"]),
                    },
                )
            )

    if artifact_root is None:
        checks.append(
            _check(
                "locked_artifacts",
                "review-required",
                "No artifact directory was supplied; model files and wheels were not checked.",
                required=True,
            )
        )
    else:
        try:
            artifact_facts = verify_bionemo_recipes_artifact_directory(artifact_root)
        except (OSError, BioNeMoRecipesExecutionError) as exc:
            checks.append(
                _check(
                    "locked_artifacts",
                    "blocked",
                    "The local artifact directory failed exact verification.",
                    required=True,
                    evidence={"error": _bounded(str(exc), 200)},
                )
            )
        else:
            checks.append(
                _check(
                    "locked_artifacts",
                    "passed",
                    "All exact model files and runtime wheels passed offline verification.",
                    required=True,
                    evidence=artifact_facts,
                )
            )

    required_checks = [item for item in checks if item.required_for_build]
    if any(item.status == "blocked" for item in required_checks):
        status: ReadinessStatus = "blocked"
    elif any(
        item.status in {"review-required", "not-checked"} for item in required_checks
    ):
        status = "review-required"
    else:
        status = "ready-to-build"

    return BioNeMoRecipesReadinessReport(
        checked_at=timestamp,
        status=status,
        terms_reviewed_user_declaration=terms_reviewed,
        checks=tuple(checks),
        host_preflight=host_report,
        commands=tuple(commands),
    )
