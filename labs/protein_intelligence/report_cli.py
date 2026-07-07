"""Offline CLI helpers for v0.7 protein target reports.

This module is intentionally separate from ``__main__`` so the reporting slice
can be applied after v0.6 without brittle patch context. A later cleanup can
wire these commands into the package-level CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, Mapping

from .entity_mapping import map_entities_to_targets, mapping_manifest
from .registry import build_manifest_registry, registry_payload
from .reports import build_target_report


def load_json_records(path: str | None) -> tuple[Mapping[str, object], ...]:
    """Load a JSON array or single JSON object from disk."""

    if not path:
        return ()
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        return (payload,)
    if isinstance(payload, list):
        return tuple(item for item in payload if isinstance(item, dict))
    raise ValueError("Expected JSON object or array of objects.")


def build_mapping_payload(entity_path: str) -> dict[str, object]:
    """Map entity records to curated protein targets."""

    entities = load_json_records(entity_path)
    mappings = map_entities_to_targets(entities)
    return {
        "schema_version": "protein-entity-mapping-batch.v1",
        "input_count": len(entities),
        "mapping_count": len(mappings),
        "mappings": [mapping_manifest(mapping) for mapping in mappings],
        "safety": {
            "claim_boundary": "Mappings are deterministic catalogue provenance, not biological claims.",
        },
    }


def build_registry_payload(paths: Iterable[str]) -> dict[str, object]:
    """Index manifest paths and return registry JSON."""

    return registry_payload(build_manifest_registry(paths))


def build_report_payload(
    target: str,
    *,
    entity_path: str | None = None,
    manifest_paths: Iterable[str] = (),
    source_path: str | None = None,
) -> dict[str, object]:
    """Build one target report from optional local JSON inputs."""

    return build_target_report(
        target,
        entities=load_json_records(entity_path),
        manifest_records=build_manifest_registry(manifest_paths),
        source_records=load_json_records(source_path),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m labs.protein_intelligence.report_cli",
        description="Offline v0.7 protein target reporting helper.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    map_parser = subparsers.add_parser(
        "map-entities",
        help="Map local entity JSON records to curated protein targets.",
    )
    map_parser.add_argument("entities", help="Path to an entity JSON object or array.")

    registry_parser = subparsers.add_parser(
        "index-manifests",
        help="Index local manifest JSON files or directories.",
    )
    registry_parser.add_argument("paths", nargs="+", help="Manifest JSON file or directory paths.")

    report_parser = subparsers.add_parser(
        "target-report",
        help="Build a read-only protein target report.",
    )
    report_parser.add_argument("target", help="Target symbol, entity ID, or UniProt accession.")
    report_parser.add_argument(
        "--entities",
        help="Optional entity JSON object or array to map into the report.",
    )
    report_parser.add_argument(
        "--manifest-path",
        action="append",
        default=(),
        help="Optional manifest JSON file or directory. May be repeated.",
    )
    report_parser.add_argument(
        "--sources",
        help="Optional source-record JSON object or array for literature context.",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "map-entities":
            _write_json(build_mapping_payload(args.entities))
            return 0
        if args.command == "index-manifests":
            _write_json(build_registry_payload(args.paths))
            return 0
        if args.command == "target-report":
            _write_json(
                build_report_payload(
                    args.target,
                    entity_path=args.entities,
                    manifest_paths=args.manifest_path,
                    source_path=args.sources,
                )
            )
            return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"{exc}\n")

    parser.exit(2, "Unknown command.\n")
    return 2


def _write_json(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
