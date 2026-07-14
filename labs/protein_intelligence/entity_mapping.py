"""Map literature entities onto curated protein lab targets.

This module is deliberately deterministic and catalogue-backed. It does not
infer biological relevance; it only records why an entity can be connected to a
known protein target.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .targets import PROTEIN_TARGETS, ProteinTarget


@dataclass(frozen=True)
class LiteratureEntity:
    """Small adapter shape for entities produced by the public app."""

    entity_id: str
    label: str
    aliases: tuple[str, ...] = ()
    entity_type: str | None = None


@dataclass(frozen=True)
class ProteinEntityMapping:
    """A deterministic connection between a literature entity and lab target."""

    entity: LiteratureEntity
    target: ProteinTarget
    match_method: str
    confidence: str
    matched_value: str
    warnings: tuple[str, ...] = ()


def map_entity_to_target(
    entity: LiteratureEntity | Mapping[str, object],
    targets: Iterable[ProteinTarget] = PROTEIN_TARGETS,
) -> ProteinEntityMapping | None:
    """Return the best curated protein mapping for an entity, if one exists."""

    normalized = _coerce_entity(entity)
    candidates = list(_candidate_values(normalized))
    matches: list[ProteinEntityMapping] = []

    for target in targets:
        target_values = _target_lookup_values(target)
        for value, method in candidates:
            if _norm(value) in target_values:
                matches.append(
                    ProteinEntityMapping(
                        entity=normalized,
                        target=target,
                        match_method=method,
                        confidence=_confidence_for(method),
                        matched_value=value,
                    )
                )
                break

    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    preferred = sorted(matches, key=lambda mapping: _method_rank(mapping.match_method))[0]
    return ProteinEntityMapping(
        entity=preferred.entity,
        target=preferred.target,
        match_method=preferred.match_method,
        confidence=preferred.confidence,
        matched_value=preferred.matched_value,
        warnings=(
            "Multiple protein targets matched this entity; selected the highest-priority deterministic match.",
        ),
    )


def map_entities_to_targets(
    entities: Iterable[LiteratureEntity | Mapping[str, object]],
    targets: Iterable[ProteinTarget] = PROTEIN_TARGETS,
) -> tuple[ProteinEntityMapping, ...]:
    """Map all resolvable entities and drop unmapped entities."""

    mappings = [map_entity_to_target(entity, targets) for entity in entities]
    return tuple(mapping for mapping in mappings if mapping is not None)


def mapping_manifest(mapping: ProteinEntityMapping) -> dict[str, object]:
    """Create a report-safe mapping record without model or medical claims."""

    return {
        "schema_version": "protein-entity-mapping.v1",
        "status": "completed",
        "purpose": "Map a literature entity to a curated protein target.",
        "entity": {
            "id": mapping.entity.entity_id,
            "label": mapping.entity.label,
            "aliases": list(mapping.entity.aliases),
            "type": mapping.entity.entity_type,
        },
        "target": {
            "entity_id": mapping.target.entity_id,
            "symbol": mapping.target.symbol,
            "name": mapping.target.name,
            "organism": mapping.target.organism,
            "identifiers": dict(mapping.target.identifiers),
        },
        "match": {
            "method": mapping.match_method,
            "confidence": mapping.confidence,
            "matched_value": mapping.matched_value,
            "warnings": list(mapping.warnings),
        },
        "safety": {
            "claim_boundary": "This mapping is catalogue provenance, not biological or medical evidence.",
        },
    }


def _coerce_entity(entity: LiteratureEntity | Mapping[str, object]) -> LiteratureEntity:
    if isinstance(entity, LiteratureEntity):
        return entity
    aliases = entity.get("aliases", ())
    return LiteratureEntity(
        entity_id=str(entity.get("entity_id") or entity.get("id") or ""),
        label=str(entity.get("label") or entity.get("name") or ""),
        aliases=tuple(str(alias) for alias in aliases if alias),
        entity_type=str(entity.get("entity_type") or entity.get("type") or "") or None,
    )


def _candidate_values(entity: LiteratureEntity) -> Iterable[tuple[str, str]]:
    yield entity.entity_id, "entity_id"
    yield entity.label, "label"
    for alias in entity.aliases:
        yield alias, "alias"


def _target_lookup_values(target: ProteinTarget) -> set[str]:
    return {
        _norm(target.entity_id),
        _norm(target.symbol),
        _norm(target.name),
        *(_norm(value) for value in target.identifiers.values()),
    }


def _confidence_for(method: str) -> str:
    if method == "entity_id":
        return "curated"
    if method in {"label", "alias"}:
        return "exact"
    return "candidate"


def _method_rank(method: str) -> int:
    return {"entity_id": 0, "label": 1, "alias": 2}.get(method, 9)


def _norm(value: object) -> str:
    return str(value).strip().casefold()
