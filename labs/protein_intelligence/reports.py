"""Read-only protein target reports for the research assistant."""

from __future__ import annotations

from typing import Iterable, Mapping

from .entity_mapping import (
    LiteratureEntity,
    ProteinEntityMapping,
    map_entities_to_targets,
    mapping_manifest,
)
from .registry import ManifestRegistryRecord, records_for_target
from .targets import ProteinTarget, get_protein_target


def build_target_report(
    target_name: str,
    entities: Iterable[LiteratureEntity | Mapping[str, object]] = (),
    manifest_records: Iterable[ManifestRegistryRecord] = (),
    source_records: Iterable[Mapping[str, object]] = (),
) -> dict[str, object]:
    """Build a deterministic target report without running live retrieval."""

    target = get_protein_target(target_name)
    mappings = tuple(
        mapping
        for mapping in map_entities_to_targets(entities)
        if mapping.target.entity_id == target.entity_id
    )
    records = records_for_target(manifest_records, target.symbol)
    sources = tuple(source_records)

    return {
        "schema_version": "protein-target-report.v1",
        "target": _target_payload(target),
        "literature": {
            "mapped_entity_count": len(mappings),
            "mappings": [mapping_manifest(mapping) for mapping in mappings],
            "source_count": len(sources),
            "sources": [_source_payload(source) for source in sources],
        },
        "lab_artifacts": {
            "manifest_count": len(records),
            "manifests": [_registry_payload(record) for record in records],
        },
        "interpretation": {
            "status": _interpretation_status(mappings, records),
            "claim_boundary": "This report links curated literature and lab provenance only. It is not a biomedical claim and does not assert therapeutic relevance, causality, efficacy, or clinical suitability.",
        },
    }


def build_all_target_reports(
    entities: Iterable[LiteratureEntity | Mapping[str, object]],
    manifest_records: Iterable[ManifestRegistryRecord] = (),
    source_records_by_symbol: Mapping[str, Iterable[Mapping[str, object]]] | None = None,
) -> tuple[dict[str, object], ...]:
    """Build reports for every target that has literature or lab provenance."""

    source_records_by_symbol = source_records_by_symbol or {}
    mappings = map_entities_to_targets(entities)
    symbols = {mapping.target.symbol for mapping in mappings}
    symbols.update(
        symbol
        for record in manifest_records
        for symbol in record.target_symbols
    )
    return tuple(
        build_target_report(
            symbol,
            entities=entities,
            manifest_records=manifest_records,
            source_records=source_records_by_symbol.get(symbol, ()),
        )
        for symbol in sorted(symbols)
    )


def _target_payload(target: ProteinTarget) -> dict[str, object]:
    return {
        "entity_id": target.entity_id,
        "symbol": target.symbol,
        "name": target.name,
        "organism": target.organism,
        "identifiers": dict(target.identifiers),
        "uniprot_url": target.uniprot_url,
        "notes": target.notes,
    }


def _source_payload(source: Mapping[str, object]) -> dict[str, object]:
    return {
        "id": source.get("id") or source.get("source_id"),
        "title": source.get("title"),
        "year": source.get("year"),
        "source_url": source.get("source_url"),
        "matched_terms": list(source.get("matched_terms", ())),
        "evidence_passages": list(source.get("evidence_passages", ())),
    }


def _registry_payload(record: ManifestRegistryRecord) -> dict[str, object]:
    return {
        "path": record.path,
        "checksum": record.checksum,
        "status": record.status,
        "component_type": record.component_type,
        "experiment_id": record.experiment_id,
        "target_symbols": list(record.target_symbols),
        "provider": record.provider,
        "model_name": record.model_name,
        "valid": record.valid,
        "error": record.error,
    }


def _interpretation_status(
    mappings: tuple[ProteinEntityMapping, ...],
    records: tuple[ManifestRegistryRecord, ...],
) -> str:
    if mappings and records:
        return "literature-and-lab-provenance"
    if mappings:
        return "literature-provenance-only"
    if records:
        return "lab-provenance-only"
    return "no-local-provenance"
