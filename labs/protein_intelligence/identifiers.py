from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

from labs.protein_intelligence.targets import DatabaseName, ProteinTarget, PROTEIN_TARGETS


IdentifierField = DatabaseName | Literal["entity_id", "symbol"]


@dataclass(frozen=True)
class IdentifierResolution:
    """Result of resolving a query against the bounded local target catalogue."""

    query: str
    normalized_query: str
    status: Literal["resolved", "unresolved"]
    matched_field: IdentifierField | None
    target: ProteinTarget | None

    @property
    def resolved(self) -> bool:
        return self.target is not None


def normalize_identifier_query(value: str) -> str:
    """Normalize a lookup value for exact catalogue matching."""

    return value.strip().casefold()


def _target_candidates(target: ProteinTarget) -> list[tuple[IdentifierField, str]]:
    return [
        ("entity_id", target.entity_id),
        ("symbol", target.symbol),
        *target.identifiers.items(),
    ]


def resolve_protein_identifier(value: str) -> IdentifierResolution:
    """Resolve a target by exact symbol, entity ID, UniProt, HGNC, or NCBI Gene ID."""

    normalized = normalize_identifier_query(value)
    if not normalized:
        return IdentifierResolution(
            query=value,
            normalized_query=normalized,
            status="unresolved",
            matched_field=None,
            target=None,
        )

    for target in PROTEIN_TARGETS:
        for field, candidate in _target_candidates(target):
            if normalized == normalize_identifier_query(candidate):
                return IdentifierResolution(
                    query=value,
                    normalized_query=normalized,
                    status="resolved",
                    matched_field=field,
                    target=target,
                )

    return IdentifierResolution(
        query=value,
        normalized_query=normalized,
        status="unresolved",
        matched_field=None,
        target=None,
    )


def identifier_resolution_manifest(
    value: str,
    *,
    resolved_at: date | None = None,
) -> dict[str, object]:
    """Create a provenance manifest for local identifier resolution."""

    resolution = resolve_protein_identifier(value)
    manifest_date = resolved_at or date.today()
    input_record: dict[str, object] = {
        "query": resolution.query,
        "normalized_query": resolution.normalized_query,
        "resolved_at": manifest_date.isoformat(),
        "catalogue": "labs.protein_intelligence.targets.PROTEIN_TARGETS",
    }
    output_record: dict[str, object] = {
        "resolved": resolution.resolved,
        "matched_field": resolution.matched_field,
        "target": None,
    }
    if resolution.target:
        output_record["target"] = {
            "entity_id": resolution.target.entity_id,
            "symbol": resolution.target.symbol,
            "name": resolution.target.name,
            "organism": resolution.target.organism,
            "identifiers": resolution.target.identifiers,
        }

    return {
        "schema_version": "0.1",
        "experiment_id": f"identifier-resolution-{resolution.normalized_query or 'empty'}",
        "status": "retrieved" if resolution.resolved else "failed",
        "purpose": (
            "Resolve a local target identifier before sequence retrieval, "
            "embedding, or structure experiments."
        ),
        "component_type": "identifier_resolution",
        "model": {
            "provider": "none",
            "name": "bounded-local-target-catalogue",
            "version": "0.1",
            "licence": "repository MIT; source database terms apply to identifiers",
        },
        "inputs": [input_record],
        "runtime": {
            "interface": "local-catalogue",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {"match_mode": "exact"},
        },
        "outputs": {
            "path": None,
            "confidence_measures": [],
            "generated_at": manifest_date.isoformat(),
            "resolution": output_record,
        },
        "evaluation": {
            "method": "exact match against the bounded v0.6 lab target catalogue",
            "limitations": [
                "Identifier resolution is limited to configured lab targets.",
                "No fuzzy matching, synonym expansion, ontology merge, or biological claim is produced.",
            ],
        },
    }
