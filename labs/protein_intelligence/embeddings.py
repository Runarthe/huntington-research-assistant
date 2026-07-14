from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Protocol

from labs.protein_intelligence.sequences import ProteinSequenceRecord


@dataclass(frozen=True)
class ProteinEmbeddingRecord:
    sequence_record: ProteinSequenceRecord
    provider: str
    model_name: str
    model_version: str
    vector: tuple[float, ...]
    generated_at: date

    @property
    def dimensions(self) -> int:
        return len(self.vector)


class ProteinEmbeddingProvider(Protocol):
    provider: str
    model_name: str
    model_version: str

    def embed(self, record: ProteinSequenceRecord) -> ProteinEmbeddingRecord:
        """Embed a protein sequence into a model-specific vector."""


class MockEmbeddingProvider:
    """Deterministic fixture provider for tests and manifest wiring."""

    provider = "mock"
    model_name = "deterministic-sequence-fixture"
    model_version = "0.1"

    def __init__(self, dimensions: int = 8, generated_at: date | None = None) -> None:
        if dimensions <= 0:
            raise ValueError("Embedding dimensions must be positive.")
        self.dimensions = dimensions
        self.generated_at = generated_at or date.today()

    def embed(self, record: ProteinSequenceRecord) -> ProteinEmbeddingRecord:
        seed = record.sequence.encode("ascii")
        digest = hashlib.sha256(seed).digest()
        while len(digest) < self.dimensions:
            digest += hashlib.sha256(
                seed + len(digest).to_bytes(4, byteorder="big")
            ).digest()
        values = tuple(
            round(digest[index] / 255, 6)
            for index in range(self.dimensions)
        )
        return ProteinEmbeddingRecord(
            sequence_record=record,
            provider=self.provider,
            model_name=self.model_name,
            model_version=self.model_version,
            vector=values,
            generated_at=self.generated_at,
        )


def embedding_manifest(record: ProteinEmbeddingRecord) -> dict[str, object]:
    """Create a manifest for an embedding output without interpreting it."""

    target = record.sequence_record.target
    return {
        "schema_version": "0.1",
        "experiment_id": f"protein-embedding-{target.symbol.lower()}",
        "status": "generated",
        "purpose": (
            "Generate a protein embedding fixture while preserving input and "
            "model provenance."
        ),
        "component_type": "foundation_model",
        "model": {
            "provider": record.provider,
            "name": record.model_name,
            "version": record.model_version,
            "licence": "fixture-only; replace before real model use",
        },
        "inputs": [
            {
                "identifier": record.sequence_record.accession,
                "entity_id": target.entity_id,
                "symbol": target.symbol,
                "organism": target.organism,
                "source_url": record.sequence_record.source_url,
                "retrieved_at": record.sequence_record.retrieved_at.isoformat(),
                "checksum": record.sequence_record.checksum,
                "sequence_length": record.sequence_record.sequence_length,
            }
        ],
        "runtime": {
            "interface": "mock-provider",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {
                "dimensions": record.dimensions,
            },
        },
        "outputs": {
            "path": f"outputs/protein-embedding/{target.symbol.lower()}/",
            "confidence_measures": [],
            "generated_at": record.generated_at.isoformat(),
        },
        "evaluation": {
            "method": "fixture shape and provenance checks only",
            "limitations": [
                "Mock embeddings are deterministic test vectors.",
                "No biological similarity, function, structure, or clinical claim is produced.",
            ],
        },
    }


def failed_embedding_manifest(
    sequence_record: ProteinSequenceRecord,
    *,
    provider: str,
    model_name: str,
    model_version: str,
    reason: str,
    attempted_at: date | None = None,
) -> dict[str, object]:
    """Create a manifest for a failed embedding attempt."""

    failure_date = attempted_at or date.today()
    target = sequence_record.target
    return {
        "schema_version": "0.1",
        "experiment_id": f"protein-embedding-{target.symbol.lower()}",
        "status": "failed",
        "purpose": (
            "Generate a protein embedding while preserving input and model "
            "provenance."
        ),
        "component_type": "foundation_model",
        "model": {
            "provider": provider,
            "name": model_name,
            "version": model_version,
            "licence": "record governing terms before real model use",
        },
        "inputs": [
            {
                "identifier": sequence_record.accession,
                "entity_id": target.entity_id,
                "symbol": target.symbol,
                "organism": target.organism,
                "source_url": sequence_record.source_url,
                "retrieved_at": sequence_record.retrieved_at.isoformat(),
                "checksum": sequence_record.checksum,
                "sequence_length": sequence_record.sequence_length,
            }
        ],
        "runtime": {
            "interface": "provider-adapter",
            "container": "record-if-used",
            "hardware": "record-before-running",
            "parameters": {},
        },
        "outputs": {
            "path": None,
            "confidence_measures": [],
            "generated_at": failure_date.isoformat(),
        },
        "evaluation": {
            "method": "failure captured without interpreting model output",
            "limitations": [
                reason,
                "No biological similarity, function, structure, or clinical claim is produced.",
            ],
        },
    }
