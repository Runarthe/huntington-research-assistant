from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from labs.protein_intelligence.embeddings import (
    MockEmbeddingProvider,
    embedding_manifest,
)
from labs.protein_intelligence.bionemo_preflight import (
    inspect_bionemo_environment,
)
from labs.protein_intelligence.bionemo_gpu_probe import run_bionemo_gpu_probe
from labs.protein_intelligence.bionemo_image_review import reviewed_bionemo_container
from labs.protein_intelligence.bionemo_recipes_review import (
    reviewed_bionemo_recipes_path,
)
from labs.protein_intelligence.manifests import (
    ManifestValidationError,
    manifest_summary,
)
from labs.protein_intelligence.sequences import (
    ProteinSequenceRecord,
    SequenceRetrievalError,
    failed_sequence_manifest,
    retrieve_uniprot_sequence,
    sequence_manifest,
)
from labs.protein_intelligence.targets import (
    PROTEIN_TARGETS,
    get_protein_target,
    planned_sequence_manifest,
    parse_fasta_sequence,
)


def _date_arg(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _write_json(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def validate_manifest_file(path: str) -> dict[str, object]:
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ManifestValidationError("Manifest JSON must be an object.")
    return manifest_summary(manifest)


def list_targets() -> list[dict[str, object]]:
    return [
        {
            "entity_id": target.entity_id,
            "symbol": target.symbol,
            "name": target.name,
            "organism": target.organism,
            "identifiers": target.identifiers,
            "uniprot_url": target.uniprot_url,
        }
        for target in PROTEIN_TARGETS
    ]


def build_mock_embedding_manifest(
    target_name: str,
    *,
    sequence: str,
    generated_at: date | None,
    dimensions: int,
) -> dict[str, object]:
    target = get_protein_target(target_name)
    sequence_text = sequence.upper()
    record = ProteinSequenceRecord(
        target=target,
        accession=target.identifiers["uniprot"],
        sequence=sequence_text,
        checksum=f"fixture:{len(sequence_text)}-aa",
        source_url=target.uniprot_url,
        retrieved_at=generated_at or date.today(),
    )
    embedding = MockEmbeddingProvider(
        dimensions=dimensions,
        generated_at=generated_at,
    ).embed(record)
    return embedding_manifest(embedding)


def build_retrieval_manifest(
    target_name: str,
    *,
    live: bool,
    attempted_at: date | None,
) -> dict[str, object]:
    target = get_protein_target(target_name)
    if not live:
        return failed_sequence_manifest(
            target,
            reason="Live retrieval disabled. Pass --live to call UniProt.",
            attempted_at=attempted_at,
        )
    try:
        return sequence_manifest(
            retrieve_uniprot_sequence(target, retrieved_at=attempted_at)
        )
    except SequenceRetrievalError as exc:
        return failed_sequence_manifest(
            target,
            reason=str(exc),
            attempted_at=attempted_at,
        )


def _sequence_from_args(sequence: str, fasta_file: str | None) -> str:
    if not fasta_file:
        return sequence
    return parse_fasta_sequence(
        open(fasta_file, encoding="utf-8").read()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m labs.protein_intelligence",
        description="Offline-safe Protein Intelligence Lab manifest helper.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-targets", help="List configured protein targets.")
    subparsers.add_parser(
        "bionemo-image-review",
        help="Print the offline reviewed BioNeMo container provenance record.",
    )
    subparsers.add_parser(
        "bionemo-recipes-review",
        help="Print the plan-only review of the maintained BioNeMo Recipes path.",
    )

    plan_parser = subparsers.add_parser(
        "plan",
        help="Print a planned sequence-retrieval manifest.",
    )
    plan_parser.add_argument("target", help="Target symbol, entity ID, or UniProt ID.")
    plan_parser.add_argument("--date", help="ISO date to record in the manifest.")

    retrieve_parser = subparsers.add_parser(
        "retrieve",
        help="Print a sequence retrieval manifest. Requires --live for network.",
    )
    retrieve_parser.add_argument("target", help="Target symbol, entity ID, or UniProt ID.")
    retrieve_parser.add_argument("--date", help="ISO date to record in the manifest.")
    retrieve_parser.add_argument(
        "--live",
        action="store_true",
        help="Call UniProt. Without this flag, emit a failed manifest instead.",
    )

    mock_parser = subparsers.add_parser(
        "mock-embed",
        help="Print a mock embedding manifest from an inline fixture sequence.",
    )
    mock_parser.add_argument("target", help="Target symbol, entity ID, or UniProt ID.")
    mock_parser.add_argument(
        "--sequence",
        default="ACDEFGHIKLMNPQRSTVWY",
        help="Fixture amino-acid sequence. Defaults to a short alphabetic sequence.",
    )
    mock_parser.add_argument(
        "--fasta-file",
        help="Read a fixture FASTA file instead of using --sequence.",
    )
    mock_parser.add_argument("--date", help="ISO date to record in the manifest.")
    mock_parser.add_argument(
        "--dimensions",
        type=int,
        default=8,
        help="Mock vector dimensions.",
    )

    validate_parser = subparsers.add_parser(
        "validate-manifest",
        help="Validate a lab manifest JSON file and print a compact summary.",
    )
    validate_parser.add_argument("path", help="Path to manifest JSON.")

    preflight_parser = subparsers.add_parser(
        "bionemo-preflight",
        help="Inspect local BioNeMo prerequisites without network or containers.",
    )
    preflight_parser.add_argument(
        "--image",
        help="Optionally validate an immutable container image reference.",
    )
    preflight_parser.add_argument(
        "--strict",
        action="store_true",
        help="Return exit code 3 unless every preflight check is complete.",
    )

    gpu_probe_parser = subparsers.add_parser(
        "bionemo-gpu-probe",
        help="Run a fixed GPU diagnostic in an already-local immutable image.",
    )
    gpu_probe_parser.add_argument(
        "--image",
        required=True,
        help="Exact local image reference ending in @sha256:<64 hex characters>.",
    )
    gpu_probe_parser.add_argument(
        "--confirm-local-container",
        action="store_true",
        help="Explicitly allow the fixed, network-disabled diagnostic container.",
    )

    args = parser.parse_args(argv)

    try:
        if args.command == "list-targets":
            _write_json(list_targets())
            return 0
        if args.command == "bionemo-image-review":
            _write_json(reviewed_bionemo_container().model_dump(mode="json"))
            return 0
        if args.command == "bionemo-recipes-review":
            _write_json(reviewed_bionemo_recipes_path().model_dump(mode="json"))
            return 0
        if args.command == "plan":
            target = get_protein_target(args.target)
            _write_json(planned_sequence_manifest(target, retrieved_at=_date_arg(args.date)))
            return 0
        if args.command == "retrieve":
            _write_json(
                build_retrieval_manifest(
                    args.target,
                    live=args.live,
                    attempted_at=_date_arg(args.date),
                )
            )
            return 0
        if args.command == "mock-embed":
            _write_json(
                build_mock_embedding_manifest(
                    args.target,
                    sequence=_sequence_from_args(args.sequence, args.fasta_file),
                    generated_at=_date_arg(args.date),
                    dimensions=args.dimensions,
                )
            )
            return 0
        if args.command == "validate-manifest":
            _write_json(validate_manifest_file(args.path))
            return 0
        if args.command == "bionemo-preflight":
            report = inspect_bionemo_environment(image_reference=args.image)
            _write_json(report.model_dump(mode="json"))
            return 3 if args.strict and report.overall_status != "ready" else 0
        if args.command == "bionemo-gpu-probe":
            report = run_bionemo_gpu_probe(
                args.image,
                confirmed=args.confirm_local_container,
            )
            _write_json(report.model_dump(mode="json"))
            return 0 if report.status == "passed" else 3
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"{exc}\n")

    parser.exit(2, "Unknown command.\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
