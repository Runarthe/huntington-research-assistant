from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from labs.protein_intelligence.embeddings import (
    MockEmbeddingProvider,
    embedding_manifest,
)
from labs.protein_intelligence.sequences import ProteinSequenceRecord
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

    plan_parser = subparsers.add_parser(
        "plan",
        help="Print a planned sequence-retrieval manifest.",
    )
    plan_parser.add_argument("target", help="Target symbol, entity ID, or UniProt ID.")
    plan_parser.add_argument("--date", help="ISO date to record in the manifest.")

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

    args = parser.parse_args(argv)

    try:
        if args.command == "list-targets":
            _write_json(list_targets())
            return 0
        if args.command == "plan":
            target = get_protein_target(args.target)
            _write_json(planned_sequence_manifest(target, retrieved_at=_date_arg(args.date)))
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
    except (KeyError, ValueError) as exc:
        parser.exit(2, f"{exc}\n")

    parser.exit(2, "Unknown command.\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
