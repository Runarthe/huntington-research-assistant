from __future__ import annotations

from typing import Iterable


VALID_STATUSES = {"planned", "retrieved", "generated", "failed"}
REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "experiment_id",
    "status",
    "purpose",
    "component_type",
    "model",
    "inputs",
    "runtime",
    "outputs",
    "evaluation",
}


class ManifestValidationError(ValueError):
    """Raised when a lab manifest is structurally invalid."""


def _missing_keys(mapping: dict[str, object], keys: Iterable[str]) -> list[str]:
    return sorted(key for key in keys if key not in mapping)


def validate_manifest(manifest: dict[str, object]) -> None:
    """Validate the structural contract shared by lab manifests."""

    missing = _missing_keys(manifest, REQUIRED_TOP_LEVEL_KEYS)
    if missing:
        raise ManifestValidationError(f"Manifest missing keys: {', '.join(missing)}")

    status = manifest["status"]
    if status not in VALID_STATUSES:
        raise ManifestValidationError(f"Unknown manifest status: {status!r}")

    inputs = manifest["inputs"]
    if not isinstance(inputs, list) or not inputs:
        raise ManifestValidationError("Manifest must contain at least one input.")

    model = manifest["model"]
    if not isinstance(model, dict):
        raise ManifestValidationError("Manifest model must be an object.")
    missing_model = _missing_keys(model, {"provider", "name", "version", "licence"})
    if missing_model:
        raise ManifestValidationError(
            f"Manifest model missing keys: {', '.join(missing_model)}"
        )

    evaluation = manifest["evaluation"]
    if not isinstance(evaluation, dict):
        raise ManifestValidationError("Manifest evaluation must be an object.")
    limitations = evaluation.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        raise ManifestValidationError(
            "Manifest evaluation must include at least one limitation."
        )


def manifest_summary(manifest: dict[str, object]) -> dict[str, object]:
    """Return a compact summary after validating a manifest."""

    validate_manifest(manifest)
    return {
        "experiment_id": manifest["experiment_id"],
        "status": manifest["status"],
        "component_type": manifest["component_type"],
        "input_count": len(manifest["inputs"]),
    }
