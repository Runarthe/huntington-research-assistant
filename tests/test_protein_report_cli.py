from __future__ import annotations

import json
from pathlib import Path

from labs.protein_intelligence.report_cli import (
    build_mapping_payload,
    build_registry_payload,
    build_report_payload,
    load_json_records,
)
from labs.protein_intelligence.targets import PROTEIN_TARGETS, planned_sequence_manifest


def test_load_json_records_accepts_single_object(tmp_path: Path) -> None:
    path = tmp_path / "entity.json"
    path.write_text(json.dumps({"id": "protein-huntingtin", "label": "HTT"}), encoding="utf-8")

    records = load_json_records(str(path))

    assert records == ({"id": "protein-huntingtin", "label": "HTT"},)


def test_load_json_records_accepts_array_and_ignores_non_objects(tmp_path: Path) -> None:
    path = tmp_path / "entities.json"
    path.write_text(
        json.dumps(
            [
                {"id": "protein-bdnf", "label": "BDNF"},
                "not-an-object",
            ]
        ),
        encoding="utf-8",
    )

    records = load_json_records(str(path))

    assert records == ({"id": "protein-bdnf", "label": "BDNF"},)


def test_build_mapping_payload_is_offline_and_claim_bounded(tmp_path: Path) -> None:
    path = tmp_path / "entities.json"
    path.write_text(
        json.dumps(
            [
                {"id": "protein-huntingtin", "label": "huntingtin", "aliases": ["HTT"]},
                {"id": "unknown", "label": "not mapped"},
            ]
        ),
        encoding="utf-8",
    )

    payload = build_mapping_payload(str(path))

    assert payload["input_count"] == 2
    assert payload["mapping_count"] == 1
    assert payload["mappings"][0]["target"]["symbol"] == "HTT"
    assert "not biological claims" in payload["safety"]["claim_boundary"]


def test_build_registry_payload_indexes_directory(tmp_path: Path) -> None:
    manifest_path = tmp_path / "planned-bdnf.json"
    manifest_path.write_text(json.dumps(planned_sequence_manifest(PROTEIN_TARGETS[1])), encoding="utf-8")

    payload = build_registry_payload((str(tmp_path),))

    assert payload["record_count"] == 1
    assert payload["records"][0]["target_symbols"] == ("BDNF",)


def test_build_report_payload_combines_entities_manifests_and_sources(tmp_path: Path) -> None:
    entities_path = tmp_path / "entities.json"
    sources_path = tmp_path / "sources.json"
    manifest_path = tmp_path / "planned-htt.json"
    entities_path.write_text(json.dumps([{"id": "protein-huntingtin", "label": "HTT"}]), encoding="utf-8")
    sources_path.write_text(json.dumps([{"id": "pmid:1", "title": "HTT paper", "matched_terms": ["HTT"]}]), encoding="utf-8")
    manifest_path.write_text(json.dumps(planned_sequence_manifest(PROTEIN_TARGETS[0])), encoding="utf-8")

    report = build_report_payload(
        "HTT",
        entity_path=str(entities_path),
        manifest_paths=(str(manifest_path),),
        source_path=str(sources_path),
    )

    assert report["target"]["symbol"] == "HTT"
    assert report["literature"]["mapped_entity_count"] == 1
    assert report["literature"]["source_count"] == 1
    assert report["lab_artifacts"]["manifest_count"] == 1


def test_build_report_payload_can_return_validated_summary(tmp_path: Path) -> None:
    entities_path = tmp_path / "entities.json"
    manifest_path = tmp_path / "planned-htt.json"
    entities_path.write_text(json.dumps([{"id": "protein-huntingtin", "label": "HTT"}]), encoding="utf-8")
    manifest_path.write_text(json.dumps(planned_sequence_manifest(PROTEIN_TARGETS[0])), encoding="utf-8")

    summary = build_report_payload(
        "HTT",
        entity_path=str(entities_path),
        manifest_paths=(str(manifest_path),),
        summary=True,
    )

    assert summary == {
        "schema_version": "protein-target-report.v1",
        "symbol": "HTT",
        "mapped_entity_count": 1,
        "manifest_count": 1,
        "interpretation_status": "literature-and-lab-provenance",
    }
