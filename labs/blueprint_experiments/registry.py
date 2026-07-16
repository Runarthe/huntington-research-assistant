"""Index Blueprint experiment manifests without executing providers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from .manifests import (
    BlueprintManifestValidationError,
    manifest_summary,
    validate_blueprint_manifest,
)


@dataclass(frozen=True)
class BlueprintManifestRegistryRecord:
    """A compact provenance record for one Blueprint manifest file."""

    path: str
    checksum: str
    valid: bool
    experiment_id: str
    status: str
    provider_type: str
    target_symbols: tuple[str, ...]
    artifact_type: str | None = None
    output_path: str | None = None
    model_provider: str | None = None
    model_name: str | None = None
    requires_live_provider: bool | None = None
    error: str | None = None


def build_blueprint_registry(
    paths: Iterable[str | Path],
) -> tuple[BlueprintManifestRegistryRecord, ...]:
    """Build registry records from manifest JSON files or directories."""

    records = [_record_for_path(path) for path in _iter_manifest_paths(paths)]
    return tuple(sorted(records, key=lambda record: record.path))


def registry_payload(
    records: Iterable[BlueprintManifestRegistryRecord],
) -> dict[str, object]:
    """Return a JSON-serializable registry document."""

    materialized = tuple(records)
    valid_count = sum(1 for record in materialized if record.valid)
    return {
        "schema_version": "blueprint-manifest-registry.v1",
        "record_count": len(materialized),
        "valid_count": valid_count,
        "invalid_count": len(materialized) - valid_count,
        "records": [record.__dict__ for record in materialized],
        "safety": {
            "claim_boundary": (
                "Registry entries describe lab artifact provenance only. They are "
                "not biomedical findings, clinical evidence, treatment guidance, "
                "or provider capability claims."
            ),
        },
    }


def records_for_target(
    records: Iterable[BlueprintManifestRegistryRecord],
    symbol: str,
) -> tuple[BlueprintManifestRegistryRecord, ...]:
    """Return registry records that mention a target symbol."""

    wanted = symbol.casefold()
    return tuple(
        record
        for record in records
        if any(target.casefold() == wanted for target in record.target_symbols)
    )


def write_registry(
    records: Iterable[BlueprintManifestRegistryRecord],
    path: str | Path,
) -> None:
    """Write a stable registry JSON file."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(registry_payload(records), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _iter_manifest_paths(paths: Iterable[str | Path]) -> Iterable[Path]:
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            yield from sorted(path.rglob("*.json"))
        elif path.suffix == ".json":
            yield path


def _record_for_path(path: Path) -> BlueprintManifestRegistryRecord:
    raw = path.read_bytes()
    checksum = hashlib.sha256(raw).hexdigest()
    try:
        manifest = json.loads(raw.decode("utf-8"))
        if not isinstance(manifest, dict):
            raise BlueprintManifestValidationError("Manifest JSON must be an object.")
        validate_blueprint_manifest(manifest)
        summary = manifest_summary(manifest)
        return BlueprintManifestRegistryRecord(
            path=str(path),
            checksum=checksum,
            valid=True,
            experiment_id=str(summary["experiment_id"]),
            status=str(summary["status"]),
            provider_type=str(summary["provider_type"]),
            target_symbols=_target_symbols(manifest),
            artifact_type=_artifact_type(manifest),
            output_path=_output_path(manifest),
            model_provider=_model_provider(manifest),
            model_name=_model_name(manifest),
            requires_live_provider=_requires_live_provider(manifest),
        )
    except (json.JSONDecodeError, UnicodeDecodeError, BlueprintManifestValidationError) as error:
        return BlueprintManifestRegistryRecord(
            path=str(path),
            checksum=checksum,
            valid=False,
            experiment_id=path.stem,
            status="invalid",
            provider_type="unknown",
            target_symbols=(),
            error=str(error),
        )


def _target_symbols(manifest: Mapping[str, object]) -> tuple[str, ...]:
    inputs = manifest.get("inputs", [])
    symbols: list[str] = []
    if isinstance(inputs, list):
        for input_record in inputs:
            if isinstance(input_record, dict) and input_record.get("symbol"):
                symbols.append(str(input_record["symbol"]))
    return tuple(symbols)


def _artifact_type(manifest: Mapping[str, object]) -> str | None:
    outputs = manifest.get("outputs", {})
    if isinstance(outputs, dict) and outputs.get("artifact_type"):
        return str(outputs["artifact_type"])
    return None


def _output_path(manifest: Mapping[str, object]) -> str | None:
    outputs = manifest.get("outputs", {})
    if isinstance(outputs, dict) and outputs.get("path"):
        return str(outputs["path"])
    return None


def _model_provider(manifest: Mapping[str, object]) -> str | None:
    model = manifest.get("model", {})
    if isinstance(model, dict) and model.get("provider"):
        return str(model["provider"])
    return None


def _model_name(manifest: Mapping[str, object]) -> str | None:
    model = manifest.get("model", {})
    if isinstance(model, dict) and model.get("name"):
        return str(model["name"])
    return None


def _requires_live_provider(manifest: Mapping[str, object]) -> bool | None:
    runtime = manifest.get("runtime", {})
    if isinstance(runtime, dict) and isinstance(runtime.get("requires_live_provider"), bool):
        return bool(runtime["requires_live_provider"])
    return None
