from __future__ import annotations

import hashlib
from datetime import date
from typing import Iterable, Literal, Mapping

from labs.protein_intelligence.targets import ProteinTarget, get_protein_target


ProviderType = Literal[
    "mock",
    "nvidia_nim",
    "bionemo",
    "alphafold",
    "uniprot",
    "nvidia_blueprint",
    "other",
]

VALID_PROVIDER_TYPES = {
    "mock",
    "nvidia_nim",
    "bionemo",
    "alphafold",
    "uniprot",
    "nvidia_blueprint",
    "other",
}
VALID_STATUSES = {"planned", "generated", "failed"}
REQUIRED_TOP_LEVEL_KEYS = {
    "schema_version",
    "experiment_id",
    "status",
    "provider_type",
    "purpose",
    "model",
    "inputs",
    "runtime",
    "outputs",
    "evaluation",
    "safety",
}


class BlueprintManifestValidationError(ValueError):
    """Raised when a Blueprint experiment manifest violates the lab contract."""


def planned_blueprint_manifest(
    target_name: str,
    *,
    provider_type: ProviderType = "mock",
    planned_at: date | None = None,
) -> dict[str, object]:
    """Create a planned manifest without executing a model or provider."""

    if provider_type not in VALID_PROVIDER_TYPES:
        raise ValueError(f"Unknown provider type: {provider_type}")
    target = get_protein_target(target_name)
    manifest_date = planned_at or date.today()
    return {
        "schema_version": "blueprint-experiment-manifest.v1",
        "experiment_id": f"blueprint-{provider_type}-{target.symbol.lower()}",
        "status": "planned",
        "provider_type": provider_type,
        "purpose": (
            "Plan a bounded Digital Biology Blueprint-style experiment while "
            "recording inputs, runtime expectations, outputs, limitations, "
            "and safety boundaries before any live provider is used."
        ),
        "model": _model_payload(provider_type),
        "inputs": [_target_input_payload(target, manifest_date)],
        "runtime": {
            "interface": "not-run",
            "container": "not-selected",
            "hardware": "not-selected",
            "parameters": {},
            "requires_live_provider": provider_type != "mock",
        },
        "outputs": {
            "path": f"outputs/blueprint-experiments/{provider_type}/{target.symbol.lower()}/",
            "artifact_type": "planned",
            "generated_at": None,
            "confidence_measures": [],
        },
        "evaluation": {
            "method": "manifest planning review before execution",
            "limitations": [
                "This is a plan only; no model, NIM, BioNeMo, AlphaFold, or Blueprint execution has occurred.",
                "The manifest does not contain biological findings or clinical conclusions.",
            ],
        },
        "safety": safety_boundary(provider_type),
    }


def mock_blueprint_manifest(
    target_name: str,
    *,
    generated_at: date | None = None,
    points: int = 8,
) -> dict[str, object]:
    """Generate a deterministic mock output manifest for offline tests."""

    if points <= 0:
        raise ValueError("Mock output point count must be positive.")
    target = get_protein_target(target_name)
    run_date = generated_at or date.today()
    values = _mock_confidence_values(target, points)
    return {
        "schema_version": "blueprint-experiment-manifest.v1",
        "experiment_id": f"blueprint-mock-{target.symbol.lower()}",
        "status": "generated",
        "provider_type": "mock",
        "purpose": (
            "Exercise the Blueprint experiment manifest and provenance plumbing "
            "with deterministic fixture output. This is not a scientific model run."
        ),
        "model": {
            "provider": "mock",
            "name": "deterministic-blueprint-fixture",
            "version": "0.1",
            "licence": "fixture-only; replace before real provider use",
        },
        "inputs": [_target_input_payload(target, run_date)],
        "runtime": {
            "interface": "offline-fixture",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {
                "points": points,
                "seed": target.identifiers["uniprot"],
            },
            "requires_live_provider": False,
        },
        "outputs": {
            "path": f"outputs/blueprint-experiments/mock/{target.symbol.lower()}/mock-confidence.json",
            "artifact_type": "mock_structure_confidence",
            "generated_at": run_date.isoformat(),
            "confidence_measures": [
                {
                    "name": "mock_confidence",
                    "description": "Deterministic fixture values for plumbing tests only.",
                    "values": values,
                    "mean": round(sum(values) / len(values), 6),
                }
            ],
        },
        "evaluation": {
            "method": "fixture shape, determinism, and manifest completeness checks",
            "limitations": [
                "Mock confidence values are not pLDDT, PAE, structural evidence, or biological predictions.",
                "No NIM, BioNeMo, AlphaFold, Blueprint, or GPU workflow was executed.",
                "No treatment, diagnosis, trial suitability, efficacy, or safety claim is produced.",
            ],
        },
        "safety": safety_boundary("mock"),
    }


def uniprot_sequence_blueprint_manifest(
    target_name: str,
    *,
    sequence_length: int,
    checksum: str,
    generated_at: date | None = None,
) -> dict[str, object]:
    """Create a Blueprint-compatible manifest for public UniProt retrieval."""

    if sequence_length <= 0:
        raise ValueError("Sequence length must be positive.")
    target = get_protein_target(target_name)
    run_date = generated_at or date.today()
    return {
        "schema_version": "blueprint-experiment-manifest.v1",
        "experiment_id": f"blueprint-uniprot-{target.symbol.lower()}",
        "status": "generated",
        "provider_type": "uniprot",
        "purpose": (
            "Record public UniProt sequence retrieval as input provenance for "
            "future scientific-AI lab workflows."
        ),
        "model": {
            "provider": "uniprot",
            "name": "UniProtKB FASTA record",
            "version": "public database record",
            "licence": "review UniProt terms before downstream reuse",
        },
        "inputs": [_target_input_payload(target, run_date)],
        "runtime": {
            "interface": "public-http-fasta",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {
                "sequence_length": sequence_length,
                "checksum": checksum,
            },
            "requires_live_provider": True,
        },
        "outputs": {
            "path": f"outputs/blueprint-experiments/uniprot/{target.symbol.lower()}/sequence-manifest.json",
            "artifact_type": "public_sequence_metadata",
            "generated_at": run_date.isoformat(),
            "confidence_measures": [],
        },
        "evaluation": {
            "method": "identifier, sequence length, and checksum provenance review",
            "limitations": [
                "UniProt retrieval records source provenance only.",
                "No embedding, structure prediction, function prediction, or clinical claim is produced.",
            ],
        },
        "safety": safety_boundary("uniprot"),
    }


def manifest_summary(manifest: Mapping[str, object]) -> dict[str, object]:
    """Return a compact summary after validating a Blueprint manifest."""

    validate_blueprint_manifest(manifest)
    outputs = manifest["outputs"]
    return {
        "schema_version": manifest["schema_version"],
        "experiment_id": manifest["experiment_id"],
        "status": manifest["status"],
        "provider_type": manifest["provider_type"],
        "input_count": len(manifest["inputs"]),
        "artifact_type": outputs.get("artifact_type") if isinstance(outputs, dict) else None,
    }


def validate_blueprint_manifest(manifest: Mapping[str, object]) -> None:
    """Validate the structural and safety contract for v0.8 lab manifests."""

    missing = _missing_keys(manifest, REQUIRED_TOP_LEVEL_KEYS)
    if missing:
        raise BlueprintManifestValidationError(
            f"Manifest missing keys: {', '.join(missing)}"
        )
    if manifest["status"] not in VALID_STATUSES:
        raise BlueprintManifestValidationError(
            f"Unknown manifest status: {manifest['status']!r}"
        )
    if manifest["provider_type"] not in VALID_PROVIDER_TYPES:
        raise BlueprintManifestValidationError(
            f"Unknown provider type: {manifest['provider_type']!r}"
        )
    _validate_model(manifest["model"])
    _validate_inputs(manifest["inputs"])
    _validate_runtime(manifest["runtime"])
    _validate_outputs(manifest["outputs"])
    _validate_evaluation(manifest["evaluation"])
    _validate_safety(manifest["safety"])


def safety_boundary(provider_type: str) -> dict[str, object]:
    """Return the required claim boundary for Blueprint lab artifacts."""

    return {
        "provider_type": provider_type,
        "claim_boundary": (
            "This artifact is for scientific-AI engineering practice and provenance "
            "navigation only. It is not medical advice, clinical evidence, a treatment "
            "recommendation, or a validated biomedical finding."
        ),
        "disallowed_uses": [
            "diagnosis",
            "treatment recommendations",
            "personalized health guidance",
            "trial matching or eligibility interpretation",
            "claims about safety, efficacy, causality, or clinical suitability",
        ],
    }


def _model_payload(provider_type: str) -> dict[str, object]:
    if provider_type == "mock":
        return {
            "provider": "mock",
            "name": "planned-offline-fixture",
            "version": "not-run",
            "licence": "fixture-only",
        }
    if provider_type == "uniprot":
        return {
            "provider": "uniprot",
            "name": "UniProtKB FASTA record",
            "version": "public database record",
            "licence": "review UniProt terms before downstream reuse",
        }
    return {
        "provider": provider_type,
        "name": "select-before-live-run",
        "version": "record-before-live-run",
        "licence": "record-governing-terms-before-use",
    }


def _target_input_payload(target: ProteinTarget, recorded_at: date) -> dict[str, object]:
    return {
        "entity_id": target.entity_id,
        "symbol": target.symbol,
        "name": target.name,
        "organism": target.organism,
        "identifiers": dict(target.identifiers),
        "source_url": target.uniprot_url,
        "recorded_at": recorded_at.isoformat(),
    }


def _mock_confidence_values(target: ProteinTarget, points: int) -> list[float]:
    seed = target.identifiers["uniprot"].encode("ascii")
    digest = hashlib.sha256(seed).digest()
    while len(digest) < points:
        digest += hashlib.sha256(seed + len(digest).to_bytes(4, "big")).digest()
    return [round(0.35 + (digest[index] / 255) * 0.5, 6) for index in range(points)]


def _missing_keys(mapping: Mapping[str, object], keys: Iterable[str]) -> list[str]:
    return sorted(key for key in keys if key not in mapping)


def _validate_model(model: object) -> None:
    if not isinstance(model, dict):
        raise BlueprintManifestValidationError("Manifest model must be an object.")
    missing = _missing_keys(model, {"provider", "name", "version", "licence"})
    if missing:
        raise BlueprintManifestValidationError(
            f"Manifest model missing keys: {', '.join(missing)}"
        )


def _validate_inputs(inputs: object) -> None:
    if not isinstance(inputs, list) or not inputs:
        raise BlueprintManifestValidationError("Manifest must include at least one input.")
    for input_record in inputs:
        if not isinstance(input_record, dict):
            raise BlueprintManifestValidationError("Manifest inputs must be objects.")
        missing = _missing_keys(input_record, {"entity_id", "symbol", "identifiers", "source_url"})
        if missing:
            raise BlueprintManifestValidationError(
                f"Manifest input missing keys: {', '.join(missing)}"
            )


def _validate_runtime(runtime: object) -> None:
    if not isinstance(runtime, dict):
        raise BlueprintManifestValidationError("Manifest runtime must be an object.")
    missing = _missing_keys(runtime, {"interface", "container", "hardware", "parameters"})
    if missing:
        raise BlueprintManifestValidationError(
            f"Manifest runtime missing keys: {', '.join(missing)}"
        )


def _validate_outputs(outputs: object) -> None:
    if not isinstance(outputs, dict):
        raise BlueprintManifestValidationError("Manifest outputs must be an object.")
    missing = _missing_keys(outputs, {"path", "artifact_type", "confidence_measures"})
    if missing:
        raise BlueprintManifestValidationError(
            f"Manifest outputs missing keys: {', '.join(missing)}"
        )


def _validate_evaluation(evaluation: object) -> None:
    if not isinstance(evaluation, dict):
        raise BlueprintManifestValidationError("Manifest evaluation must be an object.")
    limitations = evaluation.get("limitations")
    if not isinstance(limitations, list) or not limitations:
        raise BlueprintManifestValidationError(
            "Manifest evaluation must include at least one limitation."
        )


def _validate_safety(safety: object) -> None:
    if not isinstance(safety, dict):
        raise BlueprintManifestValidationError("Manifest safety must be an object.")
    claim_boundary = safety.get("claim_boundary")
    disallowed_uses = safety.get("disallowed_uses")
    if not isinstance(claim_boundary, str) or "not medical advice" not in claim_boundary:
        raise BlueprintManifestValidationError(
            "Manifest safety must include a non-medical claim boundary."
        )
    if not isinstance(disallowed_uses, list) or not disallowed_uses:
        raise BlueprintManifestValidationError(
            "Manifest safety must include disallowed uses."
        )
