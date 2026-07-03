from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable
from urllib.error import URLError
from urllib.request import urlopen

from labs.protein_intelligence.targets import (
    ProteinTarget,
    fasta_sha256,
    parse_fasta_sequence,
)


class SequenceRetrievalError(RuntimeError):
    """Raised when a protein sequence cannot be retrieved or parsed."""


@dataclass(frozen=True)
class ProteinSequenceRecord:
    target: ProteinTarget
    accession: str
    sequence: str
    checksum: str
    source_url: str
    retrieved_at: date

    @property
    def sequence_length(self) -> int:
        return len(self.sequence)


Fetcher = Callable[[str], str]


def http_text_fetcher(url: str, *, timeout_seconds: float = 20) -> str:
    """Fetch text from a URL using the standard library."""

    try:
        with urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310
            return response.read().decode("utf-8")
    except (OSError, UnicodeDecodeError, URLError) as exc:
        raise SequenceRetrievalError(f"Could not retrieve sequence from {url}") from exc


def retrieve_uniprot_sequence(
    target: ProteinTarget,
    *,
    fetcher: Fetcher = http_text_fetcher,
    retrieved_at: date | None = None,
) -> ProteinSequenceRecord:
    """Retrieve and normalize a UniProt FASTA sequence for a target."""

    try:
        fasta_text = fetcher(target.uniprot_fasta_url)
        sequence = parse_fasta_sequence(fasta_text)
    except ValueError as exc:
        raise SequenceRetrievalError(
            f"Retrieved FASTA for {target.symbol} was invalid."
        ) from exc

    return ProteinSequenceRecord(
        target=target,
        accession=target.identifiers["uniprot"],
        sequence=sequence,
        checksum=fasta_sha256(fasta_text),
        source_url=target.uniprot_url,
        retrieved_at=retrieved_at or date.today(),
    )


def sequence_manifest(record: ProteinSequenceRecord) -> dict[str, object]:
    """Create a completed retrieval manifest from a sequence record."""

    return {
        "schema_version": "0.1",
        "experiment_id": f"sequence-retrieval-{record.target.symbol.lower()}",
        "status": "retrieved",
        "purpose": (
            "Retrieve an authoritative protein sequence as input provenance "
            "for later embedding or structure experiments."
        ),
        "component_type": "sequence_retrieval",
        "model": {
            "provider": "none",
            "name": "authoritative-database-record",
            "version": "not-applicable",
            "licence": "record source database terms before use",
        },
        "inputs": [
            {
                "identifier": record.accession,
                "entity_id": record.target.entity_id,
                "symbol": record.target.symbol,
                "organism": record.target.organism,
                "source_url": record.source_url,
                "fasta_url": record.target.uniprot_fasta_url,
                "retrieved_at": record.retrieved_at.isoformat(),
                "checksum": record.checksum,
                "sequence_length": record.sequence_length,
            }
        ],
        "runtime": {
            "interface": "http-download",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {},
        },
        "outputs": {
            "path": f"outputs/sequence-retrieval/{record.target.symbol.lower()}/",
            "confidence_measures": [],
            "generated_at": record.retrieved_at.isoformat(),
        },
        "evaluation": {
            "method": "manual identifier and checksum review before model use",
            "limitations": [
                "Sequence retrieval is provenance setup only.",
                "No embedding, structure, function, or clinical claim is produced.",
            ],
        },
    }
