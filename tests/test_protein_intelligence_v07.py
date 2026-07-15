from __future__ import annotations

import json
from pathlib import Path

from labs.protein_intelligence.entity_mapping import (
    LiteratureEntity,
    map_entities_to_targets,
    map_entity_to_target,
    mapping_manifest,
)
from labs.protein_intelligence.registry import (
    build_manifest_registry,
    records_for_target,
)
from labs.protein_intelligence.reports import build_target_report
from labs.protein_intelligence.targets import PROTEIN_TARGETS, planned_sequence_manifest


def test_entity_mapping_accepts_curated_entity_id() -> None:
    entity = LiteratureEntity(
        entity_id="protein-huntingtin",
        label="huntingtin",
        aliases=("HTT",),
        entity_type="protein",
    )

    mapping = map_entity_to_target(entity)

    assert mapping is not None
    assert mapping.target.symbol == "HTT"
    assert mapping.match_method == "entity_id"
    assert mapping.confidence == "curated"


def test_entity_mapping_accepts_alias_without_generating_claims() -> None:
    entity = {"id": "entity-1", "label": "neurofilament light", "aliases": ["NEFL"]}

    mapping = map_entity_to_target(entity)
    assert mapping is not None

    manifest = mapping_manifest(mapping)
    assert manifest["target"]["symbol"] == "NEFL"
    assert manifest["safety"]["claim_boundary"].endswith("not biological or medical evidence.")


def test_unmapped_entity_is_dropped_from_batch_mapping() -> None:
    mappings = map_entities_to_targets(
        (
            LiteratureEntity(entity_id="protein-bdnf", label="BDNF"),
            LiteratureEntity(entity_id="gene-unknown", label="not a target"),
        )
    )

    assert len(mappings) == 1
    assert mappings[0].target.symbol == "BDNF"


def test_manifest_registry_indexes_valid_and_invalid_manifests(tmp_path: Path) -> None:
    valid_path = tmp_path / "sequence.json"
    invalid_path = tmp_path / "invalid.json"
    valid_path.write_text(
        json.dumps(planned_sequence_manifest(PROTEIN_TARGETS[0])),
        encoding="utf-8",
    )
    invalid_path.write_text(json.dumps({"status": "completed"}), encoding="utf-8")

    records = build_manifest_registry((tmp_path,))

    assert len(records) == 2
    assert records_for_target(records, "HTT")[0].valid is True
    assert [record for record in records if not record.valid][0].status == "invalid"


def test_target_report_links_literature_mapping_and_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "bdnf-sequence.json"
    manifest_path.write_text(
        json.dumps(planned_sequence_manifest(PROTEIN_TARGETS[1])),
        encoding="utf-8",
    )
    registry = build_manifest_registry((manifest_path,))
    entities = (
        LiteratureEntity(
            entity_id="protein-bdnf",
            label="brain-derived neurotrophic factor",
            aliases=("BDNF",),
            entity_type="protein",
        ),
    )

    report = build_target_report(
        "BDNF",
        entities=entities,
        manifest_records=registry,
        source_records=(
            {
                "id": "pmid:1",
                "title": "BDNF and Huntington disease",
                "year": 2026,
                "source_url": "https://example.test/bdnf",
                "matched_terms": ("BDNF",),
                "evidence_passages": ("BDNF was measured in this fixture.",),
            },
        ),
    )

    assert report["target"]["symbol"] == "BDNF"
    assert report["literature"]["mapped_entity_count"] == 1
    assert report["literature"]["source_count"] == 1
    assert report["literature"]["sources"][0]["source_url"] == "https://example.test/bdnf"
    assert report["literature"]["sources"][0]["evidence_passages"] == [
        "BDNF was measured in this fixture."
    ]
    assert report["lab_artifacts"]["manifest_count"] == 1
    assert report["interpretation"]["status"] == "literature-and-lab-provenance"
    assert "does not assert therapeutic relevance" in report["interpretation"]["claim_boundary"]


def test_target_report_can_be_lab_only(tmp_path: Path) -> None:
    manifest_path = tmp_path / "nefl-sequence.json"
    manifest_path.write_text(json.dumps(planned_sequence_manifest(PROTEIN_TARGETS[2])), encoding="utf-8")

    report = build_target_report("NEFL", manifest_records=build_manifest_registry((manifest_path,)))

    assert report["target"]["symbol"] == "NEFL"
    assert report["interpretation"]["status"] == "lab-provenance-only"
