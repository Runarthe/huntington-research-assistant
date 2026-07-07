"""Index protein-lab manifests without executing providers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .manifests import ManifestValidationError, manifest_summary, validate_manifest


@dataclass(frozen=True)
class ManifestRegistryRecord:
    """A compact, searchable record for a lab manifest file."""

    path: str
    checksum: str
    status: str
    component_type: str
    experiment_id: str
    target_symbols: tuple[str, ...]
    provider: str | None = None
    model_name: str | None = None
    valid: bool = True
    error: str | None = None


def build_manifest_registry(paths: Iterable[str | Path]) -> tuple[ManifestRegistryRecord, ...]:
    """Build registry records from explicit files or directories."""

    records: list[ManifestRegistryRecord] = []
    for manifest_path in _iter_manifest_paths(paths):
        records.append(_record_for_path(manifest_path))
    return tuple(sorted(records, key=lambda record: record.path))


def registry_payload(records: Iterable[ManifestRegistryRecord]) -> dict[str, object]:
    """Return a JSON-serializable registry document."""

    materialized = tuple(records)
    return {
        "schema_version": "protein-manifest-registry.v1",
        "record_count": len(materialized),
        "records": [record.__dict__ for record in materialized],
        "safety": {
            "claim_boundary": "Registry entries describe lab artifact provenance, not biomedical conclusions.",
        },
    }


def write_registry(records: Iterable[ManifestRegistryRecord], path: str | Path) -> None:
    """Write a stable registry JSON file."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(registry_payload(records), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def records_for_target(
    records: Iterable[ManifestRegistryRecord],
    symbol: str,
) -> tuple[ManifestRegistryRecord, ...]:
    """Filter registry records by target symbol."""

    wanted = symbol.casefold()
    return tuple(
        record
        for record in records
        if any(target.casefold() == wanted for target in record.target_symbols)
    )


def _iter_manifest_paths(paths: Iterable[str | Path]) -> Iterable[Path]:
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            yield from sorted(path.rglob("*.json"))
        elif path.suffix == ".json":
            yield path


def _record_for_path(path: Path) -> ManifestRegistryRecord:
    raw = path.read_bytes()
    checksum = hashlib.sha256(raw).hexdigest()
    try:
        manifest = json.loads(raw.decode("utf-8"))
        validate_manifest(manifest)
        summary = manifest_summary(manifest)
        return ManifestRegistryRecord(
            path=str(path),
            checksum=checksum,
            status=str(summary["status"]),
            component_type=str(summary["component_type"]),
            experiment_id=str(summary["experiment_id"]),
            target_symbols=_target_symbols(manifest),
            provider=_provider(manifest),
            model_name=_model_name(manifest),
        )
    except (json.JSONDecodeError, ManifestValidationError, UnicodeDecodeError) as error:
        return ManifestRegistryRecord(
            path=str(path),
            checksum=checksum,
            status="invalid",
            component_type="unknown",
            experiment_id=path.stem,
            target_symbols=(),
            valid=False,
            error=str(error),
        )


def _target_symbols(manifest: dict[str, object]) -> tuple[str, ...]:
    symbols: list[str] = []
    for input_record in manifest.get("inputs", []):
        if isinstance(input_record, dict) and input_record.get("symbol"):
            symbols.append(str(input_record["symbol"]))
    return tuple(symbols)


def _provider(manifest: dict[str, object]) -> str | None:
    runtime = manifest.get("runtime", {})
    return str(runtime.get("provider")) if isinstance(runtime, dict) and runtime.get("provider") else None


def _model_name(manifest: dict[str, object]) -> str | None:
    model = manifest.get("model", {})
    return str(model.get("name")) if isinstance(model, dict) and model.get("name") else None
