"""Validation helpers for v0.7 report JSON contracts."""

from __future__ import annotations

from typing import Iterable, Mapping


class ReportValidationError(ValueError):
    """Raised when a report payload violates the v0.7 contract."""


TARGET_REPORT_SCHEMA = "protein-target-report.v1"
MAPPING_BATCH_SCHEMA = "protein-entity-mapping-batch.v1"
REGISTRY_SCHEMA = "protein-manifest-registry.v1"
VALID_INTERPRETATION_STATUSES = {
    "literature-and-lab-provenance",
    "literature-provenance-only",
    "lab-provenance-only",
    "no-local-provenance",
}


def validate_target_report(report: Mapping[str, object]) -> None:
    """Validate a protein target report produced by ``reports.py``."""

    _require_schema(report, TARGET_REPORT_SCHEMA)
    _require_keys(report, ("target", "literature", "lab_artifacts", "interpretation"))

    target = _object(report["target"], "target")
    _require_keys(target, ("entity_id", "symbol", "name", "organism", "identifiers"))

    literature = _object(report["literature"], "literature")
    _require_keys(literature, ("mapped_entity_count", "mappings", "source_count", "sources"))
    _count_matches(literature, "mapped_entity_count", "mappings")
    _count_matches(literature, "source_count", "sources")

    lab_artifacts = _object(report["lab_artifacts"], "lab_artifacts")
    _require_keys(lab_artifacts, ("manifest_count", "manifests"))
    _count_matches(lab_artifacts, "manifest_count", "manifests")

    interpretation = _object(report["interpretation"], "interpretation")
    _require_keys(interpretation, ("status", "claim_boundary"))
    if interpretation["status"] not in VALID_INTERPRETATION_STATUSES:
        raise ReportValidationError(f"Unknown interpretation status: {interpretation['status']}")
    _require_claim_boundary(str(interpretation["claim_boundary"]))


def validate_mapping_batch(payload: Mapping[str, object]) -> None:
    """Validate the map-entities CLI output."""

    _require_schema(payload, MAPPING_BATCH_SCHEMA)
    _require_keys(payload, ("input_count", "mapping_count", "mappings", "safety"))
    _count_matches(payload, "mapping_count", "mappings")
    safety = _object(payload["safety"], "safety")
    _require_keys(safety, ("claim_boundary",))
    _require_claim_boundary(str(safety["claim_boundary"]))


def validate_registry_payload(payload: Mapping[str, object]) -> None:
    """Validate the index-manifests CLI output."""

    _require_schema(payload, REGISTRY_SCHEMA)
    _require_keys(payload, ("record_count", "records", "safety"))
    _count_matches(payload, "record_count", "records")
    safety = _object(payload["safety"], "safety")
    _require_keys(safety, ("claim_boundary",))
    _require_claim_boundary(str(safety["claim_boundary"]))


def report_summary(report: Mapping[str, object]) -> dict[str, object]:
    """Return a compact target-report summary after validation."""

    validate_target_report(report)
    target = _object(report["target"], "target")
    literature = _object(report["literature"], "literature")
    lab_artifacts = _object(report["lab_artifacts"], "lab_artifacts")
    interpretation = _object(report["interpretation"], "interpretation")
    return {
        "schema_version": report["schema_version"],
        "symbol": target["symbol"],
        "mapped_entity_count": literature["mapped_entity_count"],
        "manifest_count": lab_artifacts["manifest_count"],
        "interpretation_status": interpretation["status"],
    }


def _require_schema(payload: Mapping[str, object], expected: str) -> None:
    actual = payload.get("schema_version")
    if actual != expected:
        raise ReportValidationError(f"Expected schema_version {expected!r}, got {actual!r}.")


def _require_keys(payload: Mapping[str, object], keys: Iterable[str]) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise ReportValidationError(f"Missing required keys: {', '.join(missing)}")


def _object(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ReportValidationError(f"{name} must be an object.")
    return value


def _array(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise ReportValidationError(f"{name} must be an array.")
    return value


def _count_matches(payload: Mapping[str, object], count_key: str, array_key: str) -> None:
    count = payload[count_key]
    records = _array(payload[array_key], array_key)
    if not isinstance(count, int):
        raise ReportValidationError(f"{count_key} must be an integer.")
    if count != len(records):
        raise ReportValidationError(
            f"{count_key}={count} does not match {array_key} length {len(records)}."
        )


def _require_claim_boundary(value: str) -> None:
    normalized = value.casefold()
    required_fragments = ("not", "claim")
    if not all(fragment in normalized for fragment in required_fragments):
        raise ReportValidationError("Claim boundary must explicitly say outputs are not claims.")
